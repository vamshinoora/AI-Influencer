# LLM Prompt Optimization Setup

## Overview
The AI Influencer platform now includes LLM-based prompt optimization that enhances user prompts based on selected options (platform, style, quality, etc.) before generating images.

## Features
- **Intelligent Prompt Enhancement**: User prompts are automatically optimized using GPT models
- **Platform-Specific Optimization**: Prompts are tailored for Instagram, LinkedIn, TikTok, YouTube, etc.
- **Style-Aware Processing**: Image style preferences are incorporated into the final prompt
- **Quality Enhancement**: Technical photography terms and quality descriptors are added
- **Fallback Mode**: Works without API key using basic optimization

## Setup Instructions

### 1. Get OpenAI API Key
1. Visit https://platform.openai.com/api-keys
2. Create an account or sign in
3. Generate a new API key
4. Copy the key (starts with `sk-`)

### 2. Configure Environment
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add your OpenAI API key to `.env`:
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. Restart the application to load the new configuration

### 3. Usage
1. Enter your image description in the "Image Description" field
2. Select your preferred platform, style, and quality options
3. Click "🚀 Generate Image"
4. The system will:
   - Optimize your prompt using AI
   - Show both original and optimized prompts
   - Generate the image using the enhanced prompt

## Example Optimization

**Original Prompt:**
```
"A professional woman in business attire"
```

**Optimized Prompt (for LinkedIn + headshot + high quality):**
```
"Professional businesswoman, confident expression, high-quality corporate headshot, 
studio lighting, sharp focus, professional attire, modern office background, 
optimized for LinkedIn, masterpiece photography, ultra-detailed, photorealistic"
```

## Cost Considerations
- Uses GPT-3.5-turbo by default (cost-effective)
- Typical cost: ~$0.001-0.002 per optimization
- Fallback to basic optimization if no API key provided

## Troubleshooting

### No API Key
- Application works without API key using basic prompt enhancement
- Add OPENAI_API_KEY to enable advanced optimization

### API Errors
- Check API key validity
- Ensure sufficient OpenAI credits
- Verify internet connection

### Model Configuration
- Default model: `gpt-3.5-turbo`
- To use GPT-4, add to `.env`: `OPENAI_MODEL=gpt-4`
