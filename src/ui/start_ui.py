#!/usr/bin/env python3
"""
AI Influencer Platform - Startup Script
Launch the Streamlit web interface.
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['streamlit', 'pymongo', 'PIL']
    missing = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing dependencies:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n📦 Install with: pip install streamlit pymongo pillow")
        return False
    
    return True

def check_mongodb_connection():
    """Check MongoDB connection."""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from database.mongodb_manager import AIInfluencerDB
        
        db = AIInfluencerDB()
        connected = db.test_connection()
        
        if connected:
            print("✅ MongoDB Atlas connected")
        else:
            print("⚠️ MongoDB connection failed (will run in limited mode)")
        
        db.disconnect()
        return connected
        
    except Exception as e:
        print(f"⚠️ MongoDB check failed: {e}")
        return False

def check_comfyui():
    """Check ComfyUI connection."""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from ai_services.comfyApi import ComfyUIClient
        
        comfy = ComfyUIClient()
        connected = comfy.check_connection()
        
        if connected:
            print("✅ ComfyUI connected")
        else:
            print("⚠️ ComfyUI not available (will use mock mode)")
        
        return connected
        
    except Exception as e:
        print(f"⚠️ ComfyUI check failed: {e}")
        return False

def main():
    """Main startup function."""
    print("🚀 AI Influencer Platform - Starting Web UI")
    print("=" * 50)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        return False
    
    print("✅ Dependencies OK")
    
    # Check services
    print("\n🔧 Checking services...")
    mongodb_ok = check_mongodb_connection()
    comfyui_ok = check_comfyui()
    
    print(f"\n📊 System Status:")
    print(f"   MongoDB: {'✅' if mongodb_ok else '⚠️'}")
    print(f"   ComfyUI: {'✅' if comfyui_ok else '⚠️'}")
    
    # Launch Streamlit
    print(f"\n🌐 Starting Streamlit web interface...")
    print(f"📍 URL: http://localhost:8501")
    print(f"🔧 Control+C to stop")
    print("=" * 50)
    
    # Get the path to the Streamlit app
    app_path = os.path.join(os.path.dirname(__file__), 'streamlit_app.py')
    
    try:
        # Run Streamlit
        subprocess.run([
            'streamlit', 'run', app_path,
            '--server.port', '8501',
            '--server.address', 'localhost',
            '--browser.gatherUsageStats', 'false'
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down AI Influencer Platform")
    except FileNotFoundError:
        print("❌ Streamlit not found. Install with: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
