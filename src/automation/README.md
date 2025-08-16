# Image Generation Automation

This module provides automated AI influencer image generation with user satisfaction loops using ComfyUI and LangGraph.

## 🎯 Features

- **Iterative Generation**: Generate images until user is satisfied
- **Smart Prompt Enhancement**: Automatically improve prompts based on feedback
- **Platform Optimization**: Tailor images for Instagram, LinkedIn, TikTok, etc.
- **Character Consistency**: Generate consistent characters with name-based seeding
- **LangGraph Integration**: Full workflow automation with decision trees

## 📁 Files

### Core Implementation
- `image_generation_flow.py` - Complete LangGraph workflow with user satisfaction loops
- `test_image_generation.py` - Test suite for ComfyUI integration
- `demo_image_generation.py` - Mock demo showing workflow concepts

### Key Components
- **ImageGenerationAgent**: Main LangGraph agent class
- **Tools**: Character analysis, image generation, feedback collection, prompt refinement
- **State Management**: Tracks generation attempts, feedback, and user satisfaction

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Start ComfyUI server
# Follow ComfyUI installation guide and start on localhost:8188
```

### 2. Basic Usage
```python
from automation.image_generation_flow import ImageGenerationAgent

# Create agent
agent = ImageGenerationAgent()

# Generate character
result = await agent.generate_character_images(
    "Create a tech influencer, professional woman, modern office setting",
    max_attempts=3
)

print(f"Generated: {result['selected_image']}")
```

### 3. Run Tests
```bash
# Test with ComfyUI server running
python src/automation/test_image_generation.py

# Run demo without server
python src/automation/demo_image_generation.py
```

## 🔄 Workflow Process

1. **Input Analysis**: Extract character requirements from user description
2. **Image Generation**: Create initial image using enhanced prompts
3. **User Review**: Collect feedback on generated image
4. **Refinement Loop**: Improve prompts based on feedback and regenerate
5. **Satisfaction Check**: Continue until user approves or max attempts reached
6. **Finalization**: Return selected image and generation summary

## 🛠 Configuration

### Character Types Supported
- Tech entrepreneurs
- Fitness influencers  
- Fashion bloggers
- Business professionals
- Custom character types

### Platform Optimization
- **Instagram**: Engaging poses, good lighting, social media ready
- **LinkedIn**: Professional headshots, business appropriate
- **TikTok**: Energetic, youthful, dynamic poses
- **YouTube**: Presenter-friendly, camera-ready

### Generation Parameters
- `max_attempts`: Maximum generation iterations (default: 5)
- `seed`: Random seed for consistency (auto-generated from name)
- `style`: Character style (professional, casual, trendy, artistic)
- `platform`: Target platform for optimization

## 🎨 Example Prompts

### Tech Influencer
```
"Professional female tech entrepreneur, age 28-30, modern office setting, 
business casual attire, confident smile, approachable expression, 
LinkedIn professional, high quality"
```

### Fitness Influencer
```
"Athletic male fitness trainer, age 25-28, gym environment, workout clothes, 
energetic pose, motivational expression, Instagram ready, high quality"
```

### Fashion Influencer
```
"Stylish female fashion blogger, age 22-26, trendy outfit, urban background, 
fashionable pose, confident style, Instagram fashion, high quality"
```

## 🔧 Advanced Usage

### Custom Character Generation
```python
# Generate with specific parameters
result = await agent.generate_character_images(
    user_input="Business consultant, trustworthy and experienced",
    max_attempts=3
)

# Access detailed results
print(f"Character: {result['character_name']}")
print(f"Attempts: {result['total_attempts']}")
print(f"All images: {result['all_images']}")
```

### Batch Generation
```python
character_types = [
    "Tech entrepreneur for LinkedIn",
    "Fitness trainer for Instagram", 
    "Fashion blogger for TikTok"
]

results = []
for char_desc in character_types:
    result = await agent.generate_character_images(char_desc)
    results.append(result)
```

## 🧪 Testing

### Test Categories
1. **Basic Generation**: Test core image generation functionality
2. **Iterative Refinement**: Test prompt improvement workflow
3. **User Feedback Loop**: Test satisfaction and regeneration logic

### Mock Testing
Run demo mode to test workflow without ComfyUI:
```bash
python src/automation/demo_image_generation.py
```

## 🔗 Integration

### With LangGraph
The system is built on LangGraph for workflow automation:
- State management for generation attempts
- Conditional routing based on user satisfaction
- Tool integration for all generation steps

### With ComfyUI
Direct integration with ComfyUI for high-quality image generation:
- Stable Diffusion XL model support
- WebSocket communication for real-time progress
- Professional prompt enhancement

## 📈 Future Enhancements

- **Speech Generation**: Add text-to-speech for character voices
- **Video Creation**: Combine images and speech into videos
- **Character Memory**: Remember user preferences across sessions
- **Style Transfer**: Apply different artistic styles to generated characters
- **Multi-angle Generation**: Generate multiple poses/angles of same character

## 🤝 Contributing

1. Test your changes with both mock and real ComfyUI
2. Ensure all tests pass
3. Add examples for new features
4. Update documentation

## 📝 Notes

- Requires ComfyUI server running on localhost:8188
- Generation quality depends on ComfyUI model and settings
- User feedback currently simulated - integrate with real UI for production
- LangGraph dependencies are optional for basic functionality
