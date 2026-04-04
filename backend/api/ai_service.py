import time
import random

def analyze_video_intent(platform_name):
    print(f"🤖 [MOCK AI] Sending {platform_name} video to Gemini...")
    
    # Pretend the AI is "thinking" for 2 seconds
    time.sleep(2) 
    
    # Randomly decide if it is a pirate or just a fan
    possible_results = ['Active Piracy', 'Fan Engagement']
    result = random.choice(possible_results)
    
    print(f"✅ [MOCK AI] Done! Gemini says this is: {result}")
    
    return result