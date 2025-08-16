"""
ComfyUI API Client for AI Influencer Project
Generates high-quality images using Stable Diffusion through ComfyUI
"""

import io
import json
import os
import sys
import uuid
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Any

import websocket
from PIL import Image


class ComfyUIClient:
    """Client for interacting with ComfyUI API"""
    
    def __init__(self, server_address: str = "127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        
    def check_server(self) -> bool:
        """Check if ComfyUI server is running"""
        try:
            url = f"http://{self.server_address}/system_stats"
            with urllib.request.urlopen(url, timeout=5) as response:
                return response.status == 200
        except Exception as e:
            print(f"❌ ComfyUI server not reachable at {self.server_address}")
            print(f"Error: {e}")
            print("💡 Make sure ComfyUI is running on localhost:8188")
            return False

    def check_connection(self) -> bool:
        """Check if ComfyUI server is running (alias for check_server)"""
        return self.check_server()

    def queue_prompt(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Queue a prompt for processing"""
        payload = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(payload).encode('utf-8')
        url = f"http://{self.server_address}/prompt"
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())

    def get_image(self, filename: str, subfolder: str, folder_type: str) -> bytes:
        """Download image from ComfyUI server"""
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        url = f"http://{self.server_address}/view?{url_values}"
        with urllib.request.urlopen(url) as response:
            return response.read()

    def get_history(self, prompt_id: str) -> Dict[str, Any]:
        """Get execution history for a prompt"""
        url = f"http://{self.server_address}/history/{prompt_id}"
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read())

    def get_images(self, ws: websocket.WebSocket, prompt: Dict[str, Any]) -> Dict[str, List[bytes]]:
        """Get generated images from ComfyUI"""
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        output_images = {}
        current_node = ""
        
        print(f"🎯 Prompt ID: {prompt_id}")
        print("⏳ Waiting for image generation...")
        
        # Wait for execution to complete
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['prompt_id'] == prompt_id:
                        if data['node'] is None:
                            print("✅ Generation complete!")
                            break  # Execution is done
                        else:
                            current_node = data['node']
                elif message['type'] == 'progress':
                    data = message['data']
                    if 'value' in data and 'max' in data:
                        progress = (data['value'] / data['max']) * 100
                        print(f"📊 Progress: {progress:.1f}%")
            else:
                # Handle SaveImageWebsocket nodes
                if current_node == 'save_image_websocket_node':
                    images_output = output_images.get(current_node, [])
                    images_output.append(out[8:])
                    output_images[current_node] = images_output
        
        # Get images from history for regular SaveImage nodes
        history = self.get_history(prompt_id)
        if prompt_id in history:
            for node_id in history[prompt_id]['outputs']:
                node_output = history[prompt_id]['outputs'][node_id]
                if 'images' in node_output:
                    images_output = []
                    for image in node_output['images']:
                        image_data = self.get_image(
                            image['filename'], 
                            image['subfolder'], 
                            image['type']
                        )
                        images_output.append(image_data)
                    output_images[node_id] = images_output

        return output_images

    def connect_websocket(self) -> websocket.WebSocket:
        """Connect to ComfyUI WebSocket"""
        ws = websocket.WebSocket()
        ws_url = f"ws://{self.server_address}/ws?clientId={self.client_id}"
        ws.connect(ws_url)
        return ws

    def load_workflow(self, workflow_path: str) -> Dict[str, Any]:
        """Load workflow from JSON file"""
        if not os.path.exists(workflow_path):
            raise FileNotFoundError(f"Workflow file not found: {workflow_path}")
        
        with open(workflow_path, "r", encoding="utf-8") as f:
            return json.loads(f.read())

    def save_images(self, images: Dict[str, List[bytes]], output_dir: str = "data/generated/images") -> List[str]:
        """Save generated images to disk"""
        saved_files = []
        os.makedirs(output_dir, exist_ok=True)
        
        for node_id in images:
            for i, image_data in enumerate(images[node_id]):
                image = Image.open(io.BytesIO(image_data))
                filename = f"comfyui_output_{node_id}_{i}.png"
                output_path = os.path.join(output_dir, filename)
                image.save(output_path)
                saved_files.append(output_path)
                print(f"💾 Saved: {output_path}")
        
        return saved_files

    def generate_image(
        self, 
        positive_prompt: str,
        negative_prompt: str = None,
        seed: int = 5,
        workflow_path: str = None,
        save_images: bool = True,
        show_images: bool = False
    ) -> List[str]:
        """Generate images using ComfyUI"""
        
        # Default workflow path
        if workflow_path is None:
            # Get the project root directory more reliably
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            workflow_path = os.path.join(project_root, "src", "ai_services", "workflows", "basicImageGenerator.json")
        
        # Default negative prompt
        if negative_prompt is None:
            negative_prompt = (
                "worst quality, low quality, bad anatomy, bad hands, error, "
                "missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, "
                "signature, watermark, username, blurry, bad proportions, extra limbs"
            )
        
        try:
            # Load workflow
            print(f"📂 Loading workflow from: {workflow_path}")
            print(f"📂 File exists: {os.path.exists(workflow_path)}")
            if not os.path.exists(workflow_path):
                raise FileNotFoundError(f"Workflow file not found: {workflow_path}")
            prompt = self.load_workflow(workflow_path)
            
            # Set prompts and parameters
            prompt["6"]["inputs"]["text"] = positive_prompt
            prompt["7"]["inputs"]["text"] = negative_prompt
            prompt["3"]["inputs"]["seed"] = seed
            
            print("🚀 Connecting to ComfyUI...")
            print(f"📡 Server: {self.server_address}")
            print(f"🔑 Client ID: {self.client_id}")
            print(f"🎨 Positive prompt: {positive_prompt[:100]}...")
            
            # Connect and generate
            ws = self.connect_websocket()
            print("✅ Connected to ComfyUI WebSocket")
            
            images = self.get_images(ws, prompt)
            ws.close()
            
            print(f"✅ Generated {len(images)} image sets")
            
            saved_files = []
            
            # Process images
            for node_id in images:
                print(f"📸 Node {node_id}: {len(images[node_id])} images")
                
                # Save images
                if save_images:
                    for i, image_data in enumerate(images[node_id]):
                        image = Image.open(io.BytesIO(image_data))
                        filename = f"comfyui_output_{node_id}_{i}.png"
                        output_path = f"data/generated/images/{filename}"
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        image.save(output_path)
                        saved_files.append(output_path)
                        print(f"💾 Saved: {output_path}")
                
                # Show images
                if show_images:
                    for image_data in images[node_id]:
                        image = Image.open(io.BytesIO(image_data))
                        image.show()
            
            return saved_files
            
        except Exception as e:
            print(f"❌ Error during image generation: {e}")
            raise


def main():
    """Main function for testing"""
    client = ComfyUIClient()
    
    # Check server
    if not client.check_server():
        print("🛑 Exiting: ComfyUI server is not running")
        sys.exit(1)
    
    # Example prompts
    positive_prompt = (
        "tech entrepreneur, age 28-32, modern workspace, laptop setup, "
        "casual button-down shirt, friendly expression, startup office environment, "
        "natural window lighting, photorealistic, 4k quality"
    )
    
    try:
        saved_files = client.generate_image(
            positive_prompt=positive_prompt,
            seed=5,
            save_images=True,
            show_images=True
        )
        
        print(f"\n🎉 Success! Generated {len(saved_files)} images")
        
    except Exception as e:
        print(f"❌ Failed to generate images: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()