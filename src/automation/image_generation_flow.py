"""
LangGraph Flow for Automated Image Generation with User Satisfaction Loop
Focuses specifically on iterative image generation until user is satisfied
"""

import asyncio
import json
import os
import sys
from typing import Annotated, Dict, Any, List, Optional, Literal
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_services.comfyApi import ComfyUIClient


# ================================
# STATE DEFINITION
# ================================

class ImageGenerationState(TypedDict):
    """State for iterative image generation workflow"""
    
    # Core workflow
    messages: Annotated[List[BaseMessage], add_messages]
    current_stage: Literal["input", "analyzing", "generating", "reviewing", "complete"]
    user_satisfied: bool
    
    # Character and prompt data
    character_name: str
    character_description: str
    target_style: str
    target_platform: str
    
    # Generation attempts
    positive_prompts: List[str]
    negative_prompts: List[str]
    generated_images: List[Dict[str, Any]]
    generation_attempts: int
    max_attempts: int
    
    # User feedback
    feedback_history: List[Dict[str, Any]]
    improvement_suggestions: List[str]
    
    # Final selection
    selected_image: Optional[str]
    final_prompt_used: Optional[str]


# ================================
# TOOLS DEFINITION
# ================================

@tool
def analyze_character_requirements(user_input: str) -> str:
    """
    Analyze user input to extract character requirements for image generation.
    
    Args:
        user_input: User description of desired AI influencer character
        
    Returns:
        JSON string with extracted character details
    """
    
    # Extract key information from user input
    analysis = {
        "character_extracted": True,
        "suggested_name": "AI_Influencer",
        "age_range": "25-35",
        "gender": "unspecified",
        "profession": "influencer",
        "style": "professional",
        "setting": "modern",
        "platform": "instagram",
        "key_features": [],
        "missing_info": []
    }
    
    # Simple keyword analysis (in production, use LLM for better extraction)
    input_lower = user_input.lower()
    
    # Age detection
    if "young" in input_lower or "20" in input_lower:
        analysis["age_range"] = "20-28"
    elif "30" in input_lower or "mature" in input_lower:
        analysis["age_range"] = "30-40"
    
    # Gender detection
    if any(word in input_lower for word in ["woman", "female", "girl", "lady"]):
        analysis["gender"] = "female"
    elif any(word in input_lower for word in ["man", "male", "boy", "guy"]):
        analysis["gender"] = "male"
    
    # Profession detection
    if "tech" in input_lower or "entrepreneur" in input_lower:
        analysis["profession"] = "tech entrepreneur"
    elif "fitness" in input_lower or "gym" in input_lower:
        analysis["profession"] = "fitness trainer"
    elif "fashion" in input_lower or "style" in input_lower:
        analysis["profession"] = "fashion blogger"
    elif "business" in input_lower:
        analysis["profession"] = "business professional"
    
    # Style detection
    if "casual" in input_lower:
        analysis["style"] = "casual"
    elif "formal" in input_lower or "professional" in input_lower:
        analysis["style"] = "professional"
    elif "trendy" in input_lower or "fashionable" in input_lower:
        analysis["style"] = "fashionable"
    
    return json.dumps(analysis)


@tool
def generate_character_image(
    character_description: str,
    style: str = "professional",
    platform: str = "instagram",
    seed: int = None,
    character_name: str = "AI_Influencer"
) -> str:
    """
    Generate character image using ComfyUI with enhanced prompts.
    
    Args:
        character_description: Description of the character to generate
        style: Style preference (professional, casual, trendy)
        platform: Target platform (instagram, linkedin, tiktok)
        seed: Random seed for consistent generation
        character_name: Character name for file naming
        
    Returns:
        JSON string with generation results
    """
    
    try:
        # Initialize ComfyUI client
        client = ComfyUIClient()
        
        # Check server status
        if not client.check_server():
            return json.dumps({
                "success": False,
                "error": "ComfyUI server not running",
                "suggestion": "Please start ComfyUI on localhost:8188"
            })
        
        # Enhance prompt based on style and platform
        enhanced_prompt = _enhance_prompt_for_platform(character_description, style, platform)
        
        # Generate consistent seed if not provided
        if seed is None:
            seed = _generate_character_seed(character_name)
        
        # Generate image
        saved_files = client.generate_image(
            positive_prompt=enhanced_prompt,
            negative_prompt=_get_platform_negative_prompt(platform),
            seed=seed,
            save_images=True,
            show_images=False
        )
        
        if saved_files:
            return json.dumps({
                "success": True,
                "image_paths": saved_files,
                "prompt_used": enhanced_prompt,
                "seed_used": seed,
                "style": style,
                "platform": platform,
                "character_name": character_name
            })
        else:
            return json.dumps({
                "success": False,
                "error": "No images generated",
                "suggestion": "Try adjusting the prompt or checking ComfyUI workflow"
            })
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Generation failed: {str(e)}",
            "suggestion": "Check ComfyUI server and workflow configuration"
        })


@tool
def collect_user_feedback(
    image_paths: List[str],
    generation_attempt: int,
    previous_feedback: str = ""
) -> str:
    """
    Collect user feedback on generated images.
    
    Args:
        image_paths: List of generated image file paths
        generation_attempt: Current attempt number
        previous_feedback: Previous feedback from user
        
    Returns:
        JSON string with user feedback
    """
    
    # In a real implementation, this would show images to user and collect input
    # For demo purposes, we'll simulate different types of feedback
    
    feedback_options = [
        {
            "satisfied": True,
            "feedback": "Perfect! The character looks exactly how I imagined.",
            "rating": 5,
            "selected_image": image_paths[0] if image_paths else None
        },
        {
            "satisfied": False,
            "feedback": "Good start, but the character looks too formal. Can we make them more casual and approachable?",
            "rating": 3,
            "improvements": ["more casual clothing", "friendlier expression", "less formal background"]
        },
        {
            "satisfied": False,
            "feedback": "The age doesn't look right. They appear too young for a business professional.",
            "rating": 2,
            "improvements": ["older appearance", "more mature features", "professional attire"]
        },
        {
            "satisfied": False,
            "feedback": "The lighting and quality are great, but the setting doesn't match the tech entrepreneur vibe.",
            "rating": 3,
            "improvements": ["modern tech environment", "startup office setting", "computer/tech props"]
        }
    ]
    
    # Simulate increasing satisfaction over attempts
    if generation_attempt >= 3:
        chosen_feedback = feedback_options[0]  # Satisfied after 3 attempts
    else:
        chosen_feedback = feedback_options[generation_attempt % len(feedback_options)]
    
    chosen_feedback["attempt_number"] = generation_attempt
    chosen_feedback["total_images"] = len(image_paths)
    
    return json.dumps(chosen_feedback)


@tool
def refine_prompt_based_on_feedback(
    original_prompt: str,
    user_feedback: str,
    improvement_suggestions: List[str],
    attempt_number: int
) -> str:
    """
    Refine the image generation prompt based on user feedback.
    
    Args:
        original_prompt: The original prompt that was used
        user_feedback: User's feedback on the generated image
        improvement_suggestions: List of specific improvements needed
        attempt_number: Current attempt number
        
    Returns:
        JSON string with refined prompt
    """
    
    # Analyze feedback and create improvements
    refinements = []
    
    if "casual" in user_feedback.lower():
        refinements.append("casual clothing, relaxed atmosphere, approachable expression")
    
    if "formal" in user_feedback.lower() and "too" in user_feedback.lower():
        refinements.append("less formal, more approachable, friendly demeanor")
    
    if "age" in user_feedback.lower() or "young" in user_feedback.lower():
        refinements.append("mature appearance, experienced professional look")
    
    if "tech" in user_feedback.lower() or "startup" in user_feedback.lower():
        refinements.append("modern tech environment, startup office, computer setup")
    
    if "lighting" in user_feedback.lower():
        refinements.append("professional studio lighting, well-lit, high quality")
    
    # Add improvement suggestions
    for suggestion in improvement_suggestions:
        if suggestion not in refinements:
            refinements.append(suggestion)
    
    # Create refined prompt
    if refinements:
        refined_prompt = f"{original_prompt}, {', '.join(refinements)}"
    else:
        # If no specific refinements, add general quality improvements
        refined_prompt = f"{original_prompt}, enhanced quality, professional photography"
    
    return json.dumps({
        "refined_prompt": refined_prompt,
        "improvements_added": refinements,
        "attempt_number": attempt_number,
        "original_prompt": original_prompt
    })


# Helper functions
def _enhance_prompt_for_platform(description: str, style: str, platform: str) -> str:
    """Enhance prompt based on target platform and style"""
    
    platform_enhancements = {
        "instagram": "instagram-worthy, social media ready, engaging pose, good lighting",
        "linkedin": "professional headshot, business appropriate, confident expression",
        "tiktok": "energetic, youthful, trendy, expressive, dynamic pose",
        "youtube": "presenter-friendly, camera-ready, professional but approachable"
    }
    
    style_enhancements = {
        "professional": "business attire, professional setting, confident demeanor",
        "casual": "casual wear, relaxed environment, friendly expression", 
        "trendy": "fashionable outfit, modern style, contemporary look",
        "artistic": "creative style, artistic background, expressive pose"
    }
    
    platform_enhance = platform_enhancements.get(platform, platform_enhancements["instagram"])
    style_enhance = style_enhancements.get(style, style_enhancements["professional"])
    
    return f"{description}, {style_enhance}, {platform_enhance}, high quality, photorealistic, 4k"


def _get_platform_negative_prompt(platform: str) -> str:
    """Get platform-specific negative prompts"""
    
    base_negative = (
        "worst quality, low quality, bad anatomy, bad hands, text, error, "
        "missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, "
        "signature, watermark, username, blurry, bad proportions"
    )
    
    platform_negatives = {
        "instagram": f"{base_negative}, unprofessional, poor lighting, cluttered background",
        "linkedin": f"{base_negative}, casual wear, inappropriate, unprofessional setting",
        "tiktok": f"{base_negative}, boring pose, static, overly formal",
        "youtube": f"{base_negative}, distracting background, poor presentation"
    }
    
    return platform_negatives.get(platform, base_negative)


def _generate_character_seed(character_name: str) -> int:
    """Generate consistent seed based on character name"""
    import hashlib
    
    hash_obj = hashlib.md5(character_name.encode())
    seed = int(hash_obj.hexdigest()[:8], 16) % 1000000
    return max(1, seed)


# ================================
# LANGGRAPH AGENT
# ================================

class ImageGenerationAgent:
    """LangGraph agent for iterative image generation with user satisfaction"""
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        self.model = ChatOpenAI(model=model_name, temperature=0.7)
        self.tools = [
            analyze_character_requirements,
            generate_character_image,
            collect_user_feedback,
            refine_prompt_based_on_feedback
        ]
        self.tool_node = ToolNode(self.tools)
        self.model_with_tools = self.model.bind_tools(self.tools)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for image generation"""
        
        workflow = StateGraph(ImageGenerationState)
        
        # Add nodes
        workflow.add_node("analyzer", self._analyzer_node)
        workflow.add_node("generator", self._generator_node)
        workflow.add_node("reviewer", self._reviewer_node)
        workflow.add_node("refiner", self._refiner_node)
        workflow.add_node("finalizer", self._finalizer_node)
        workflow.add_node("tools", self.tool_node)
        
        # Set entry point
        workflow.set_entry_point("analyzer")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "analyzer",
            self._should_continue_from_analyzer,
            {
                "proceed": "generator",
                "tools": "tools",
                "need_info": "analyzer"
            }
        )
        
        workflow.add_conditional_edges(
            "generator",
            self._should_continue_from_generator,
            {
                "review": "reviewer",
                "tools": "tools",
                "retry": "generator"
            }
        )
        
        workflow.add_conditional_edges(
            "reviewer",
            self._should_continue_from_reviewer,
            {
                "satisfied": "finalizer",
                "refine": "refiner",
                "tools": "tools",
                "max_attempts": "finalizer"
            }
        )
        
        workflow.add_conditional_edges(
            "refiner",
            self._should_continue_from_refiner,
            {
                "regenerate": "generator",
                "tools": "tools"
            }
        )
        
        # Tool connections
        workflow.add_edge("tools", "analyzer")
        workflow.add_edge("finalizer", END)
        
        return workflow.compile()
    
    async def _analyzer_node(self, state: ImageGenerationState) -> Dict[str, Any]:
        """Analyze user requirements for character generation"""
        
        system_message = """You are an AI character analysis expert. 

Your job is to analyze user input and extract detailed requirements for AI influencer image generation.

Use the analyze_character_requirements tool to process the user's description.
Ask clarifying questions if important details are missing:
- Character age and gender
- Professional field or niche
- Style preferences (casual, professional, trendy)
- Target platform (Instagram, LinkedIn, TikTok)
- Specific visual requirements

Be thorough but conversational in your analysis.
"""
        
        messages = [SystemMessage(content=system_message)] + state["messages"]
        response = await self.model_with_tools.ainvoke(messages)
        
        return {
            "messages": [response],
            "current_stage": "analyzing"
        }
    
    async def _generator_node(self, state: ImageGenerationState) -> Dict[str, Any]:
        """Generate character images based on requirements"""
        
        attempt_num = state.get("generation_attempts", 0) + 1
        
        system_message = f"""You are an expert AI image generation coordinator.

Current task: Generate image for {state.get('character_name', 'AI Influencer')}
Attempt: {attempt_num} of {state.get('max_attempts', 5)}

Character details:
- Description: {state.get('character_description', 'Not specified')}
- Style: {state.get('target_style', 'professional')}
- Platform: {state.get('target_platform', 'instagram')}

Use the generate_character_image tool to create high-quality images.

{'Consider previous feedback and make improvements.' if attempt_num > 1 else 'Focus on creating professional, engaging imagery.'}
"""
        
        messages = [SystemMessage(content=system_message)] + state["messages"][-3:]
        response = await self.model_with_tools.ainvoke(messages)
        
        return {
            "messages": [response],
            "current_stage": "generating",
            "generation_attempts": attempt_num
        }
    
    async def _reviewer_node(self, state: ImageGenerationState) -> Dict[str, Any]:
        """Collect user feedback on generated images"""
        
        system_message = f"""You are reviewing generated images with the user.

Generated images: {len(state.get('generated_images', []))} images
Attempt: {state.get('generation_attempts', 1)}

Show the user the generated images and collect their feedback using the collect_user_feedback tool.

Ask specific questions:
1. Does the character match their vision?
2. Any aspects that need adjustment?
3. Are they satisfied with this result?

Be encouraging and constructive in your feedback collection.
"""
        
        messages = [SystemMessage(content=system_message)] + state["messages"][-2:]
        response = await self.model_with_tools.ainvoke(messages)
        
        return {
            "messages": [response],
            "current_stage": "reviewing"
        }
    
    async def _refiner_node(self, state: ImageGenerationState) -> Dict[str, Any]:
        """Refine prompts based on user feedback"""
        
        system_message = """You are a prompt refinement specialist.

Your job is to analyze user feedback and improve the image generation prompt.

Use the refine_prompt_based_on_feedback tool to create better prompts that address the user's concerns.

Focus on specific, actionable improvements that will make the next generation better.
"""
        
        messages = [SystemMessage(content=system_message)] + state["messages"][-3:]
        response = await self.model_with_tools.ainvoke(messages)
        
        return {
            "messages": [response],
            "current_stage": "generating"
        }
    
    async def _finalizer_node(self, state: ImageGenerationState) -> Dict[str, Any]:
        """Finalize the image generation process"""
        
        selected_image = state.get("selected_image") or (
            state["generated_images"][-1].get("image_paths", [None])[0] 
            if state.get("generated_images") else None
        )
        
        total_attempts = state.get("generation_attempts", 0)
        
        completion_message = f"""
🎉 Image Generation Complete!

Character: {state.get('character_name', 'AI Influencer')}
✅ Final Image: {selected_image}
📊 Total Attempts: {total_attempts}
🎨 Style: {state.get('target_style', 'professional')}
📱 Platform: {state.get('target_platform', 'instagram')}

{'User satisfaction achieved!' if state.get('user_satisfied') else 'Maximum attempts reached - using best result.'}

Your AI influencer character image is ready! 🚀
"""
        
        return {
            "messages": [AIMessage(content=completion_message)],
            "current_stage": "complete",
            "user_satisfied": True,
            "selected_image": selected_image
        }
    
    # Conditional logic
    def _should_continue_from_analyzer(self, state: ImageGenerationState) -> str:
        """Determine next step after analysis"""
        last_message = state["messages"][-1]
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        if (state.get("character_name") and state.get("character_description")):
            return "proceed"
        
        return "need_info"
    
    def _should_continue_from_generator(self, state: ImageGenerationState) -> str:
        """Determine next step after generation"""
        last_message = state["messages"][-1]
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        if state.get("generated_images"):
            return "review"
        
        return "retry"
    
    def _should_continue_from_reviewer(self, state: ImageGenerationState) -> str:
        """Determine next step after review"""
        last_message = state["messages"][-1]
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        if state.get("user_satisfied", False):
            return "satisfied"
        
        if state.get("generation_attempts", 0) >= state.get("max_attempts", 5):
            return "max_attempts"
        
        return "refine"
    
    def _should_continue_from_refiner(self, state: ImageGenerationState) -> str:
        """Determine next step after refinement"""
        last_message = state["messages"][-1]
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        return "regenerate"
    
    # Public API
    async def generate_character_images(
        self, 
        user_input: str,
        max_attempts: int = 5
    ) -> Dict[str, Any]:
        """Main entry point for character image generation"""
        
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "current_stage": "input",
            "user_satisfied": False,
            "character_name": "",
            "character_description": "",
            "target_style": "professional",
            "target_platform": "instagram",
            "positive_prompts": [],
            "negative_prompts": [],
            "generated_images": [],
            "generation_attempts": 0,
            "max_attempts": max_attempts,
            "feedback_history": [],
            "improvement_suggestions": [],
            "selected_image": None,
            "final_prompt_used": None
        }
        
        print("🎨 Starting AI Character Image Generation...")
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "character_name": final_state.get("character_name"),
            "selected_image": final_state.get("selected_image"),
            "total_attempts": final_state.get("generation_attempts", 0),
            "user_satisfied": final_state.get("user_satisfied", False),
            "all_images": final_state.get("generated_images", [])
        }


# ================================
# USAGE EXAMPLES
# ================================

async def example_tech_influencer():
    """Example: Generate a tech influencer"""
    
    agent = ImageGenerationAgent()
    
    user_request = """
    I want to create an AI influencer for my tech startup. 
    
    She should be a young professional woman, around 28-30 years old, 
    confident and approachable. I want her in modern business casual attire, 
    maybe in a contemporary office or co-working space setting.
    
    The style should be professional but friendly, suitable for LinkedIn 
    and Instagram posts about technology and entrepreneurship.
    """
    
    print("🚀 Generating Tech Influencer...")
    result = await agent.generate_character_images(user_request, max_attempts=3)
    
    print(f"\n✅ Generation Complete!")
    print(f"Character: {result['character_name']}")
    print(f"Final Image: {result['selected_image']}")
    print(f"Attempts: {result['total_attempts']}")
    print(f"Satisfied: {result['user_satisfied']}")
    
    return result


async def example_fitness_influencer():
    """Example: Generate a fitness influencer"""
    
    agent = ImageGenerationAgent()
    
    user_request = """
    Create a fitness influencer character for my wellness brand.
    
    Male, athletic build, around 25-28 years old, motivational and energetic.
    He should be in workout attire, in a modern gym setting with good lighting.
    
    The style should be inspiring and professional, suitable for Instagram 
    fitness content and YouTube workout videos.
    """
    
    print("🏋️ Generating Fitness Influencer...")
    result = await agent.generate_character_images(user_request, max_attempts=4)
    
    print(f"\n✅ Generation Complete!")
    print(f"Character: {result['character_name']}")
    print(f"Final Image: {result['selected_image']}")
    
    return result


async def example_fashion_influencer():
    """Example: Generate a fashion influencer"""
    
    agent = ImageGenerationAgent()
    
    user_request = """
    I need a fashion blogger character for my style brand.
    
    Female, early 20s, trendy and stylish. She should be wearing a fashionable 
    outfit that's current and Instagram-worthy. Urban background or chic studio setting.
    
    Style should be trendy, fashionable, and perfect for fashion and lifestyle content.
    """
    
    print("👗 Generating Fashion Influencer...")
    result = await agent.generate_character_images(user_request, max_attempts=3)
    
    print(f"\n✅ Generation Complete!")
    print(f"Character: {result['character_name']}")
    print(f"Final Image: {result['selected_image']}")
    
    return result


# Simple function interface for direct usage
def generate_ai_character_simple(description: str, max_attempts: int = 3) -> str:
    """Simple synchronous interface for character generation"""
    
    async def _generate():
        agent = ImageGenerationAgent()
        result = await agent.generate_character_images(description, max_attempts)
        return result.get("selected_image", "No image generated")
    
    return asyncio.run(_generate())


if __name__ == "__main__":
    async def main():
        print("🎨 AI Character Image Generation Automation")
        print("=" * 50)
        
        # Test different influencer types
        print("\n1. Tech Influencer Generation...")
        tech_result = await example_tech_influencer()
        
        print("\n2. Fitness Influencer Generation...")
        fitness_result = await example_fitness_influencer()
        
        print("\n3. Fashion Influencer Generation...")
        fashion_result = await example_fashion_influencer()
        
        print("\n🎉 All examples completed!")
        
        # Test simple interface
        print("\n4. Testing simple interface...")
        simple_result = generate_ai_character_simple(
            "Create a business consultant, professional and trustworthy"
        )
        print(f"Simple result: {simple_result}")
    
    asyncio.run(main())
