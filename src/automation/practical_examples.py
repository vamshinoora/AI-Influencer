"""
Practical Example: Generate AI Influencer for Different Business Types
Shows how to use the image generation automation for real business scenarios
"""

import sys
import os

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_services.comfyApi import ComfyUIClient


def generate_business_influencers():
    """Generate influencers for different business types"""
    
    print("🏢 Business AI Influencer Generator")
    print("=" * 50)
    
    # Initialize client
    client = ComfyUIClient()
    
    # Check server
    if not client.check_server():
        print("❌ ComfyUI server not running. Please start ComfyUI on localhost:8188")
        return
    
    # Different business scenarios
    business_scenarios = [
        {
            "business_type": "Tech Startup",
            "character_name": "TechSarah",
            "description": "professional female tech entrepreneur, age 28-32, modern startup office, laptop setup, casual blazer, confident smile, innovative atmosphere, high quality",
            "use_case": "LinkedIn posts about tech trends and startup insights"
        },
        {
            "business_type": "Fitness Brand",
            "character_name": "FitCoach",
            "description": "athletic male fitness trainer, age 26-30, modern gym environment, workout attire, motivational pose, energetic expression, professional lighting, high quality",
            "use_case": "Instagram workout videos and fitness motivation"
        },
        {
            "business_type": "Fashion Brand",
            "character_name": "StyleGuru",
            "description": "fashionable female model, age 22-28, trendy outfit, chic urban background, confident pose, stylish expression, fashion photography, high quality",
            "use_case": "Instagram fashion posts and style recommendations"
        },
        {
            "business_type": "Consulting Firm",
            "character_name": "BusinessMentor",
            "description": "professional business consultant, age 35-40, executive office, formal business attire, trustworthy expression, authoritative presence, high quality",
            "use_case": "LinkedIn business advice and consulting services"
        },
        {
            "business_type": "Wellness Brand",
            "character_name": "WellnessCoach",
            "description": "wellness coach, female, age 30-35, peaceful natural setting, comfortable yoga attire, serene expression, mindful atmosphere, high quality",
            "use_case": "Instagram wellness tips and mindfulness content"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(business_scenarios, 1):
        print(f"\n{i}. Generating {scenario['character_name']} for {scenario['business_type']}")
        print(f"   Use case: {scenario['use_case']}")
        print(f"   Character: {scenario['description'][:60]}...")
        
        try:
            # Generate with consistent seed for reproducibility
            seed = hash(scenario['character_name']) % 100000
            
            saved_files = client.generate_image(
                positive_prompt=scenario['description'],
                seed=seed,
                save_images=True,
                show_images=False
            )
            
            if saved_files:
                result = {
                    "business_type": scenario['business_type'],
                    "character_name": scenario['character_name'],
                    "image_path": saved_files[0],
                    "use_case": scenario['use_case'],
                    "seed": seed,
                    "success": True
                }
                results.append(result)
                print(f"   ✅ Generated: {saved_files[0]}")
            else:
                result = {
                    "business_type": scenario['business_type'],
                    "character_name": scenario['character_name'],
                    "success": False,
                    "error": "No image generated"
                }
                results.append(result)
                print(f"   ❌ Failed to generate image")
                
        except Exception as e:
            result = {
                "business_type": scenario['business_type'],
                "character_name": scenario['character_name'],
                "success": False,
                "error": str(e)
            }
            results.append(result)
            print(f"   ❌ Error: {e}")
    
    # Summary report
    print(f"\n📊 Generation Summary")
    print("=" * 30)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print(f"\n🎉 Successfully Generated Characters:")
        for result in successful:
            print(f"   • {result['character_name']} ({result['business_type']})")
            print(f"     📁 {result['image_path']}")
            print(f"     🎯 {result['use_case']}")
    
    if failed:
        print(f"\n⚠️ Failed Generations:")
        for result in failed:
            print(f"   • {result['character_name']}: {result['error']}")
    
    return results


def demonstrate_iterative_improvement():
    """Demonstrate how to iteratively improve a character"""
    
    print(f"\n🔄 Iterative Character Improvement Demo")
    print("=" * 50)
    
    client = ComfyUIClient()
    
    if not client.check_server():
        print("❌ ComfyUI server not running")
        return
    
    # Start with basic business professional
    base_prompt = "business professional, office setting"
    character_name = "IterativeChar"
    
    improvements = [
        "confident expression, professional attire",
        "modern tech office, laptop visible",
        "friendly smile, approachable demeanor", 
        "high quality lighting, photorealistic"
    ]
    
    print(f"Starting with: {base_prompt}")
    
    current_prompt = base_prompt
    
    for i, improvement in enumerate(improvements, 1):
        print(f"\n--- Iteration {i} ---")
        print(f"Adding: {improvement}")
        
        current_prompt = f"{current_prompt}, {improvement}"
        print(f"Current prompt: {current_prompt}")
        
        try:
            saved_files = client.generate_image(
                positive_prompt=current_prompt,
                seed=5000 + i,  # Different seed for each iteration
                save_images=True,
                show_images=False
            )
            
            if saved_files:
                print(f"✅ Generated iteration {i}: {saved_files[0]}")
            else:
                print(f"❌ Failed iteration {i}")
                
        except Exception as e:
            print(f"❌ Error in iteration {i}: {e}")
    
    print(f"\n🎯 Final optimized prompt: {current_prompt}")
    return current_prompt


def generate_platform_specific_variants():
    """Generate the same character optimized for different platforms"""
    
    print(f"\n📱 Platform-Specific Character Variants")
    print("=" * 50)
    
    client = ComfyUIClient()
    
    if not client.check_server():
        print("❌ ComfyUI server not running")
        return
    
    # Base character
    base_character = "female tech entrepreneur, age 28-30, confident expression"
    
    # Platform-specific optimizations
    platforms = {
        "LinkedIn": "professional business attire, corporate office, executive presence, business headshot style",
        "Instagram": "trendy business casual, modern coworking space, engaging pose, social media ready",
        "TikTok": "casual tech wear, dynamic pose, energetic expression, creative background", 
        "YouTube": "presenter-friendly attire, clean background, camera-ready, professional but approachable"
    }
    
    print(f"Base character: {base_character}")
    
    results = []
    
    for platform, optimization in platforms.items():
        print(f"\n📱 {platform} Version:")
        full_prompt = f"{base_character}, {optimization}, high quality"
        print(f"   Prompt: {full_prompt[:80]}...")
        
        try:
            # Use consistent seed + platform hash for reproducibility
            seed = 6000 + hash(platform) % 1000
            
            saved_files = client.generate_image(
                positive_prompt=full_prompt,
                seed=seed,
                save_images=True,
                show_images=False
            )
            
            if saved_files:
                results.append({
                    "platform": platform,
                    "image_path": saved_files[0],
                    "prompt": full_prompt,
                    "success": True
                })
                print(f"   ✅ Generated: {saved_files[0]}")
            else:
                results.append({
                    "platform": platform,
                    "success": False,
                    "error": "No image generated"
                })
                print(f"   ❌ Failed to generate")
                
        except Exception as e:
            results.append({
                "platform": platform,
                "success": False,
                "error": str(e)
            })
            print(f"   ❌ Error: {e}")
    
    # Summary
    successful_platforms = [r for r in results if r['success']]
    print(f"\n📊 Platform Variants Generated: {len(successful_platforms)}/{len(platforms)}")
    
    return results


if __name__ == "__main__":
    print("🎨 Practical AI Influencer Generation Examples")
    print("=" * 60)
    
    # Example 1: Business influencers
    business_results = generate_business_influencers()
    
    # Example 2: Iterative improvement
    improved_prompt = demonstrate_iterative_improvement()
    
    # Example 3: Platform variants
    platform_results = generate_platform_specific_variants()
    
    # Final summary
    print(f"\n" + "=" * 60)
    print("🏁 PRACTICAL EXAMPLES COMPLETE")
    print("=" * 60)
    
    total_generated = sum(1 for r in business_results if r['success'])
    platform_generated = sum(1 for r in platform_results if r['success'])
    
    print(f"🎉 Results:")
    print(f"   • Business Influencers: {total_generated}/5 generated")
    print(f"   • Platform Variants: {platform_generated}/4 generated")
    print(f"   • Iterative Improvements: 4 iterations completed")
    
    print(f"\n💡 Use Cases Demonstrated:")
    print(f"   • Tech startup social media")
    print(f"   • Fitness brand marketing")
    print(f"   • Fashion brand content")
    print(f"   • Business consulting")
    print(f"   • Wellness coaching")
    
    print(f"\n📁 All images saved to: data/generated/images/")
    print(f"🚀 Ready for integration with your business automation!")
