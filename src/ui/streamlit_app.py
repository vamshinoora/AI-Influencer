#!/usr/bin/env python3
"""
AI Influencer Web UI
Simple Streamlit interface for user management and image generation.
"""

import streamlit as st
import sys
import os
import time
from datetime import datetime
from PIL import Image
import base64
from io import BytesIO

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from database.mongodb_manager import AIInfluencerDB
    from ai_services.comfyApi import ComfyUIClient
    
    # Import Azure LLM - no fallback
    from ai_services.llm import llm, is_llm_available
    LLM_AVAILABLE = is_llm_available()
    
    if LLM_AVAILABLE:
        print("✅ Azure OpenAI LLM initialized successfully")
    else:
        print("❌ Azure OpenAI LLM not available - check credentials")
    
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    st.error(f"Missing dependencies: {e}")
    st.error("Please install required packages: pip install streamlit pymongo")
    DEPENDENCIES_AVAILABLE = False
    LLM_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="AI Influencer Platform",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .persona-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .generation-card {
        background: #fff;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'current_user_id' not in st.session_state:
        st.session_state.current_user_id = None
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'db' not in st.session_state:
        if DEPENDENCIES_AVAILABLE:
            try:
                st.session_state.db = AIInfluencerDB()
                st.session_state.db_connected = st.session_state.db.test_connection()
            except Exception as e:
                st.session_state.db = None
                st.session_state.db_connected = False
        else:
            st.session_state.db = None
            st.session_state.db_connected = False
    
    if 'comfy' not in st.session_state:
        if DEPENDENCIES_AVAILABLE:
            try:
                st.session_state.comfy = ComfyUIClient()
                st.session_state.comfy_connected = st.session_state.comfy.check_connection()
            except Exception as e:
                print(f"ComfyUI initialization error: {e}")
                st.session_state.comfy = None
                st.session_state.comfy_connected = False
        else:
            st.session_state.comfy = None
            st.session_state.comfy_connected = False

def show_header():
    """Display the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🎭 AI Influencer Platform</h1>
        <p>Create, manage, and generate AI personas for your business</p>
    </div>
    """, unsafe_allow_html=True)

def show_connection_status():
    """Show connection status for services."""
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.session_state.get('db_connected', False):
            st.success("🔗 MongoDB Atlas Connected")
        else:
            st.error("❌ MongoDB Not Connected")
    
    with col2:
        if st.session_state.get('comfy_connected', False):
            st.success("🎨 ComfyUI Connected")
        else:
            st.warning("⚠️ ComfyUI Not Available")
    
    with col3:
        if st.button("🔄 Refresh"):
            # Refresh ComfyUI connection
            if st.session_state.get('comfy'):
                try:
                    st.session_state.comfy_connected = st.session_state.comfy.check_connection()
                    st.rerun()
                except Exception as e:
                    st.session_state.comfy_connected = False
                    st.error(f"ComfyUI check failed: {e}")
            
            # Refresh MongoDB connection
            if st.session_state.get('db'):
                try:
                    st.session_state.db_connected = st.session_state.db.test_connection()
                    st.rerun()
                except Exception as e:
                    st.session_state.db_connected = False
                    st.error(f"MongoDB check failed: {e}")

def user_registration():
    """User registration/login form."""
    st.header("👤 User Profile")
    
    if st.session_state.current_user_id:
        show_user_dashboard()
        return
    
    # Check if user exists
    with st.expander("🔐 Login with Existing Account", expanded=False):
        login_email = st.text_input("Email Address", key="login_email")
        if st.button("Login"):
            if login_email and st.session_state.db_connected:
                user = st.session_state.db.get_user(email=login_email)
                if user:
                    st.session_state.current_user_id = str(user['_id'])
                    st.session_state.current_user = user
                    st.success(f"Welcome back, {user['username']}!")
                    st.rerun()
                else:
                    st.error("User not found. Please register below.")
    
    # Registration form
    st.subheader("📝 Create New Account")
    
    with st.form("user_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username*", placeholder="your_business_name")
            email = st.text_input("Email*", placeholder="your@email.com")
            full_name = st.text_input("Full Name", placeholder="Your Full Name")
            business_type = st.selectbox("Business Type*", [
                "Select...", "E-commerce", "Fitness & Wellness", "Technology", 
                "Fashion & Beauty", "Food & Beverage", "Consulting", 
                "Real Estate", "Education", "Healthcare", "Other"
            ])
        
        with col2:
            target_audience = st.text_area("Target Audience", 
                placeholder="Describe your target audience...")
            preferred_platforms = st.multiselect("Preferred Platforms", [
                "Instagram", "LinkedIn", "TikTok", "YouTube", "Twitter", "Facebook"
            ])
            subscription_tier = st.selectbox("Subscription Tier", [
                "free", "premium", "enterprise"
            ])
        
        submitted = st.form_submit_button("Create Account", type="primary")
        
        if submitted:
            if not username or not email or business_type == "Select...":
                st.error("Please fill in all required fields (*)")
            elif not st.session_state.db_connected:
                st.error("Database not connected. Cannot create account.")
            else:
                # Create user
                user_data = {
                    "username": username,
                    "email": email,
                    "full_name": full_name,
                    "business_type": business_type,
                    "target_audience": target_audience,
                    "preferred_platforms": preferred_platforms,
                    "subscription_tier": subscription_tier
                }
                
                try:
                    user_id = st.session_state.db.create_user(user_data)
                    if user_id:
                        st.session_state.current_user_id = user_id
                        st.session_state.current_user = user_data
                        st.session_state.current_user['_id'] = user_id
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create account. Email might already exist.")
                except Exception as e:
                    st.error(f"Error creating account: {e}")

def show_user_dashboard():
    """Show user dashboard with personas and actions."""
    user = st.session_state.current_user
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### Welcome, {user['username']}! 👋")
        st.markdown(f"**Business**: {user.get('business_type', 'N/A')}")
    
    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.current_user_id = None
            st.session_state.current_user = None
            st.rerun()

def persona_management():
    """Persona creation and management."""
    if not st.session_state.current_user_id:
        st.warning("Please login first to manage personas.")
        return
    
    st.header("🎭 AI Personas")
    
    # Show existing personas
    if st.session_state.db_connected:
        personas = st.session_state.db.get_user_personas(st.session_state.current_user_id)
        
        if personas:
            st.subheader(f"Your Personas ({len(personas)})")
            for persona in personas:
                with st.container():
                    st.markdown(f"""
                    <div class="persona-card">
                        <h4>{persona['character_name']}</h4>
                        <p><strong>Style:</strong> {persona.get('style', 'N/A')} | 
                           <strong>Platform:</strong> {persona.get('target_platform', 'N/A')}</p>
                        <p>{persona.get('description', 'No description')}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Create new persona
    with st.expander("➕ Create New Persona", expanded=True):
        with st.form("persona_creation"):
            col1, col2 = st.columns(2)
            
            with col1:
                character_name = st.text_input("Character Name*", 
                    placeholder="Professional Sarah")
                description = st.text_area("Description*", 
                    placeholder="Confident business leader for LinkedIn content...")
                age_range = st.selectbox("Age Range", [
                    "18-25", "26-30", "31-35", "36-40", "41-45", "46-50", "50+"
                ])
                gender = st.selectbox("Gender", ["female", "male", "non-binary"])
                profession = st.text_input("Profession", 
                    placeholder="Business Executive")
            
            with col2:
                style = st.selectbox("Style*", [
                    "professional", "casual", "athletic", "creative", "elegant"
                ])
                target_platform = st.selectbox("Target Platform*", [
                    "instagram", "linkedin", "tiktok", "youtube", "twitter"
                ])
                personality_traits = st.multiselect("Personality Traits", [
                    "confident", "approachable", "authoritative", "friendly", 
                    "energetic", "calm", "innovative", "reliable"
                ])
                brand_voice = st.text_input("Brand Voice", 
                    placeholder="Professional yet approachable")
                content_themes = st.text_input("Content Themes", 
                    placeholder="leadership, innovation, growth (comma-separated)")
            
            # Visual preferences
            st.subheader("🎨 Visual Preferences")
            col3, col4 = st.columns(2)
            
            with col3:
                background_style = st.selectbox("Background Style", [
                    "modern office", "home office", "studio", "outdoor", 
                    "co-working space", "minimal", "luxury"
                ])
                lighting_preference = st.selectbox("Lighting", [
                    "natural", "soft", "bright", "dramatic", "warm"
                ])
            
            with col4:
                color_scheme = st.selectbox("Color Scheme", [
                    "professional blues", "warm neutrals", "vibrant colors", 
                    "monochrome", "earth tones", "pastel"
                ])
            
            submitted = st.form_submit_button("Create Persona", type="primary")
            
            if submitted:
                if not character_name or not description or not style or not target_platform:
                    st.error("Please fill in all required fields (*)")
                elif not st.session_state.db_connected:
                    st.error("Database not connected. Cannot create persona.")
                else:
                    persona_data = {
                        "user_id": st.session_state.current_user_id,
                        "character_name": character_name,
                        "description": description,
                        "age_range": age_range,
                        "gender": gender,
                        "profession": profession,
                        "style": style,
                        "target_platform": target_platform,
                        "personality_traits": personality_traits,
                        "brand_voice": brand_voice,
                        "content_themes": content_themes.split(',') if content_themes else [],
                        "background_style": background_style,
                        "lighting_preference": lighting_preference,
                        "color_scheme": color_scheme
                    }
                    
                    try:
                        persona_id = st.session_state.db.create_persona(persona_data)
                        if persona_id:
                            st.success(f"Persona '{character_name}' created successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to create persona.")
                    except Exception as e:
                        st.error(f"Error creating persona: {e}")

def image_generation():
    """Image generation interface."""
    if not st.session_state.current_user_id:
        st.warning("Please login first to generate images.")
        return
    
    st.header("🎨 Generate AI Images")
    
    # Get user personas
    personas = []
    if st.session_state.db_connected:
        personas = st.session_state.db.get_user_personas(st.session_state.current_user_id)
    
    if not personas:
        st.warning("Please create at least one persona before generating images.")
        return
    
    with st.form("image_generation"):
        # Persona selection
        persona_options = {p['character_name']: str(p['_id']) for p in personas}
        selected_persona_name = st.selectbox("Select Persona*", list(persona_options.keys()))
        selected_persona_id = persona_options[selected_persona_name]
        
        # Find selected persona details
        selected_persona = next(p for p in personas if str(p['_id']) == selected_persona_id)
        
        # Show persona details
        with st.expander("👤 Persona Details", expanded=False):
            st.write(f"**Style**: {selected_persona.get('style', 'N/A')}")
            st.write(f"**Platform**: {selected_persona.get('target_platform', 'N/A')}")
            st.write(f"**Description**: {selected_persona.get('description', 'N/A')}")
        
        # Generation parameters
        col1, col2 = st.columns(2)
        
        with col1:
            custom_prompt = st.text_area("Image Description", 
                placeholder="Describe what you want to generate...", 
                help="Enter your prompt for image generation")
            platform_override = st.selectbox("Platform Override", [
                "auto", "instagram", "linkedin", "tiktok", "youtube", "twitter"
            ])
        
        with col2:
            image_style = st.selectbox("Image Style", [
                "headshot", "full-body", "action-shot", "lifestyle", "product-focused"
            ])
            quality = st.selectbox("Quality", ["standard", "high", "ultra"])
        
        # Generation settings
        with st.expander("🔧 Advanced Settings", expanded=False):
            col3, col4 = st.columns(2)
            with col3:
                steps = st.slider("Generation Steps", 20, 50, 30)
                cfg_scale = st.slider("CFG Scale", 1.0, 15.0, 7.5)
            with col4:
                seed = st.number_input("Seed (0 for random)", 0, 999999, 0)
                width = st.selectbox("Width", [512, 768, 1024], index=2)
                height = st.selectbox("Height", [512, 768, 1024], index=2)
        
        submitted = st.form_submit_button("🚀 Generate Image", type="primary")
        
        if submitted:
            generate_image_process(
                selected_persona, custom_prompt, platform_override, 
                image_style, quality, steps, cfg_scale, seed, width, height
            )

def optimize_prompt_with_llm(user_prompt, platform, image_style, quality, width, height):
    """
    Use Azure LLM to optimize the user prompt based on selected options.
    """
    if not LLM_AVAILABLE:
        st.error("❌ Azure OpenAI LLM not available. Please check your credentials in .env file.")
        st.error("Required: AZURE_OPENAI_CLIENT_ID, AZURE_OPENAI_CLIENT_SECRET, AZURE_OPENAI_APP_KEY")
        return None
    
    # Create optimization prompt
    optimization_prompt = f"""
You are an expert prompt engineer for AI image generation systems like Stable Diffusion. 
Your task is to optimize prompts for better image generation results.

User's basic description: "{user_prompt}"

Target specifications:
- Platform: {platform}
- Image Style: {image_style}
- Quality: {quality}
- Dimensions: {width}x{height}

Platform-specific requirements:
- Instagram: High engagement, visually appealing, good lighting, social media ready
- LinkedIn: Professional, business appropriate, confident, trustworthy
- TikTok: Dynamic, trendy, energetic, eye-catching, youthful
- YouTube: Presenter-friendly, camera-ready, professional but approachable
- Twitter: Clear, impactful, works at small sizes, attention-grabbing

Image style requirements:
- Headshot: Focus on face, professional lighting, clear features, good composition
- Full-body: Complete figure, good posture, balanced composition, appropriate setting
- Action-shot: Dynamic pose, movement, energy, engaging composition
- Lifestyle: Natural setting, authentic feel, good lighting, relatable
- Product-focused: Clean background, good lighting, product prominence

Quality enhancements:
- Standard: Clean, well-lit, good composition
- High: Professional photography, studio quality, enhanced details
- Ultra: Masterpiece quality, perfect lighting, ultra-detailed, photorealistic

Please optimize the prompt by:
1. Enhancing the description with professional photography terms
2. Adding appropriate style and quality descriptors
3. Including platform-specific optimizations
4. Adding technical quality improvements
5. Ensuring the prompt will generate high-quality, engaging images

Return only the optimized prompt, no explanations.
"""
    
    try:
        # Use Azure LLM from llm.py
        response = llm.invoke(optimization_prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            optimized_prompt = response.content.strip()
        else:
            optimized_prompt = str(response).strip()
            
        return optimized_prompt
        
    except Exception as e:
        st.error(f"❌ Azure LLM optimization failed: {str(e)}")
        st.error("Please check your Azure OpenAI credentials and try again.")
        return None

def generate_image_process(persona, custom_prompt, platform_override, 
                          image_style, quality, steps, cfg_scale, seed, width, height):
    """Process image generation request."""
    
    # Use only the user-provided prompt
    if not custom_prompt or custom_prompt.strip() == "":
        st.error("Please enter a description for the image you want to generate.")
        return
    
    # Determine platform
    platform = platform_override if platform_override != "auto" else persona.get('target_platform', 'instagram')
    
    # Show generation progress
    progress_container = st.container()
    
    with progress_container:
        st.info("🎨 Optimizing prompt and generating your AI image...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Optimize prompt with LLM
            status_text.text("🤖 Optimizing prompt with Azure LLM...")
            progress_bar.progress(10)
            
            optimized_prompt = optimize_prompt_with_llm(
                custom_prompt.strip(), 
                platform, 
                image_style, 
                quality, 
                width, 
                height
            )
            
            # Check if LLM optimization failed
            if optimized_prompt is None:
                st.error("❌ Cannot proceed without Azure LLM. Please configure your credentials.")
                return
            
            # Show the optimized prompt to user
            with st.expander("🔍 View Optimized Prompt", expanded=False):
                st.write("**Original prompt:**")
                st.write(f'"{custom_prompt.strip()}"')
                st.write("**Optimized prompt:**")
                st.write(f'"{optimized_prompt}"')
            
            progress_bar.progress(20)
            
            if st.session_state.comfy_connected:
                # Real ComfyUI generation
                status_text.text("Connecting to ComfyUI...")
                progress_bar.progress(30)
                
                image_paths = st.session_state.comfy.generate_image(
                    positive_prompt=optimized_prompt,
                    seed=seed if seed > 0 else 5
                )
                
                progress_bar.progress(80)
                status_text.text("Processing generated image...")
                
                # Get the first generated image
                image_path = image_paths[0] if image_paths else None
                
                if image_path and os.path.exists(image_path):
                    # Store image in MongoDB
                    if st.session_state.db_connected:
                        image_id = st.session_state.db.store_image(image_path, {
                            "persona_id": str(persona['_id']),
                            "platform": platform,
                            "style": image_style,
                            "prompt": optimized_prompt,
                            "generation_type": "comfyui_sdxl"
                        })
                    else:
                        image_id = None
                    
                    # Log generation
                    if st.session_state.db_connected:
                        generation_data = {
                            "user_id": st.session_state.current_user_id,
                            "persona_id": str(persona['_id']),
                            "generation_type": "image",
                            "prompt_used": optimized_prompt,
                            "settings": {
                                "steps": steps,
                                "cfg_scale": cfg_scale,
                                "seed": seed,
                                "width": width,
                                "height": height
                            },
                            "platform_optimized": platform,
                            "generation_attempts": 1,
                            "user_satisfied": True,
                            "model_used": "stable-diffusion-xl",
                            "style_used": image_style,
                            "file_ids": [image_id] if image_id else [],
                            "file_paths": [image_path]
                        }
                        
                        generation_id = st.session_state.db.log_generation(generation_data)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Generation complete!")
                    
                    # Show generated image
                    st.success("🎉 Image generated successfully!")
                    
                    # Display image
                    image = Image.open(image_path)
                    st.image(image, caption=f"Generated for {persona['character_name']}", use_container_width=True)
                    
                    # Image details
                    with st.expander("📋 Generation Details"):
                        st.write(f"**Prompt**: {optimized_prompt}")
                        st.write(f"**Platform**: {platform}")
                        st.write(f"**Style**: {image_style}")
                        st.write(f"**Settings**: {steps} steps, CFG {cfg_scale}")
                        if image_id:
                            st.write(f"**Stored in Database**: ✅ (ID: {image_id})")
                    
                else:
                    st.error("❌ Image generation failed. Please try again.")
                    
            else:
                # Mock generation
                status_text.text("Running in mock mode...")
                progress_bar.progress(50)
                time.sleep(2)
                progress_bar.progress(100)
                status_text.text("✅ Mock generation complete!")
                
                # Create mock generation log
                if st.session_state.db_connected:
                    generation_data = {
                        "user_id": st.session_state.current_user_id,
                        "persona_id": str(persona['_id']),
                        "generation_type": "image",
                        "prompt_used": optimized_prompt,
                        "settings": {
                            "steps": steps,
                            "cfg_scale": cfg_scale,
                            "seed": seed,
                            "width": width,
                            "height": height
                        },
                        "platform_optimized": platform,
                        "generation_attempts": 1,
                        "user_satisfied": True,
                        "model_used": "stable-diffusion-xl-mock",
                        "style_used": image_style
                    }
                    
                    generation_id = st.session_state.db.log_generation(generation_data)
                    st.success("🎭 Mock generation logged to database!")
                
                st.info("🎨 ComfyUI not available. Generated mock entry in database.")
                st.write(f"**Would generate**: {optimized_prompt}")
                
        except Exception as e:
            progress_bar.progress(0)
            status_text.text("")
            st.error(f"❌ Generation error: {e}")

def generation_history():
    """Show user's generation history."""
    if not st.session_state.current_user_id:
        st.warning("Please login first to view generation history.")
        return
    
    st.header("📜 Generation History")
    
    if not st.session_state.db_connected:
        st.error("Database not connected. Cannot load history.")
        return
    
    # Get generation history
    try:
        history = st.session_state.db.get_generation_history(
            st.session_state.current_user_id, limit=20
        )
        
        if not history:
            st.info("No generations yet. Create some images to see them here!")
            return
        
        st.subheader(f"Recent Generations ({len(history)})")
        
        for i, gen in enumerate(history):
            with st.container():
                st.markdown(f"""
                <div class="generation-card">
                    <h5>Generation #{i+1}</h5>
                    <p><strong>Platform:</strong> {gen.get('platform_optimized', 'N/A')} | 
                       <strong>Style:</strong> {gen.get('style_used', 'N/A')} | 
                       <strong>Model:</strong> {gen.get('model_used', 'N/A')}</p>
                    <p><strong>Prompt:</strong> {gen.get('prompt_used', 'No prompt')[:100]}...</p>
                    <p><strong>Created:</strong> {gen.get('created_at', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show image if available
                if gen.get('file_ids'):
                    try:
                        image_data = st.session_state.db.get_image(gen['file_ids'][0])
                        if image_data:
                            image = Image.open(BytesIO(image_data))
                            st.image(image, width=300, caption=f"Generation #{i+1}")
                    except Exception as e:
                        st.warning(f"Could not load image: {e}")
                
                st.markdown("---")
                
    except Exception as e:
        st.error(f"Error loading generation history: {e}")

def analytics_dashboard():
    """Show user analytics dashboard."""
    if not st.session_state.current_user_id:
        st.warning("Please login first to view analytics.")
        return
    
    st.header("📊 Analytics Dashboard")
    
    if not st.session_state.db_connected:
        st.error("Database not connected. Cannot load analytics.")
        return
    
    try:
        analytics = st.session_state.db.get_user_analytics(st.session_state.current_user_id)
        
        if not analytics:
            st.info("No analytics data available yet.")
            return
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        user_info = analytics.get('user_info', {})
        gen_stats = analytics.get('generation_stats', {})
        
        with col1:
            st.metric("Total Generations", gen_stats.get('total', 0))
        
        with col2:
            st.metric("Total Personas", user_info.get('total_personas', 0))
        
        with col3:
            st.metric("Image Generations", gen_stats.get('images', 0))
        
        with col4:
            st.metric("Recent Activity", gen_stats.get('recent_activity', 0))
        
        # Platform distribution
        platform_stats = analytics.get('platform_distribution', [])
        if platform_stats:
            st.subheader("📱 Platform Distribution")
            
            # Create simple bar chart data
            platforms = [stat['_id'] for stat in platform_stats if stat['_id']]
            counts = [stat['count'] for stat in platform_stats if stat['_id']]
            
            if platforms:
                chart_data = {platform: count for platform, count in zip(platforms, counts)}
                st.bar_chart(chart_data)
        
        # Recent generations
        recent_gens = analytics.get('recent_generations', [])
        if recent_gens:
            st.subheader("🕒 Recent Activity")
            
            for gen in recent_gens[:5]:
                satisfied = "✅" if gen.get('satisfied', False) else "⚠️"
                st.write(f"{satisfied} {gen.get('type', 'image')} - {gen.get('created_at', 'Unknown')}")
        
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

def main():
    """Main application."""
    if not DEPENDENCIES_AVAILABLE:
        st.error("Required dependencies not available. Please install: pip install streamlit pymongo")
        st.stop()
    
    initialize_session_state()
    show_header()
    show_connection_status()
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    
    pages = {
        "👤 User Profile": user_registration,
        "🎭 Manage Personas": persona_management,
        "🎨 Generate Images": image_generation,
        "📜 Generation History": generation_history,
        "📊 Analytics": analytics_dashboard
    }
    
    selected_page = st.sidebar.radio("Go to", list(pages.keys()))
    
    # Show current user info in sidebar
    if st.session_state.current_user_id:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Current User")
        st.sidebar.write(f"**{st.session_state.current_user.get('username', 'Unknown')}**")
        st.sidebar.write(f"Business: {st.session_state.current_user.get('business_type', 'N/A')}")
    
    # Run selected page
    pages[selected_page]()

if __name__ == "__main__":
    main()
