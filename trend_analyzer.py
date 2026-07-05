import os
import json
import re
import google.generativeai as genai
import config
from telegram_notifier import send_telegram_error

# Configure Gemini API
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)

def generate_video_concept() -> dict:
    """
    Uses Gemini AI to generate a viral vertical short video concept, 
    complete with a Bengali script and English image prompts for the visuals.
    Returns a dictionary with: title, script, and image_prompts.
    """
    if not config.GEMINI_API_KEY:
        error_msg = "Gemini API key is not configured in .env!"
        print(f"[-] {error_msg}")
        return get_fallback_concept()

    prompt = """
You are a viral social media growth expert. Generate a highly engaging vertical short video concept (YouTube Shorts, TikTok, Facebook Reels) that is likely to go viral. 
Topics can include: amazing facts, mysterious stories, history secrets, life hacks, or psychological facts.

Requirements:
1. The script MUST be written in Bengali (বাংলা).
2. The script should be around 60-90 words long, suitable for a 30-50 second video.
3. It must start with a powerful hook, followed by 3 interesting points, and end with a call to action (like "subscribe for more").
4. Provide a list of exactly 4 visual image prompts in English. These prompts will be used in an AI image generator (like Pollinations/Stable Diffusion) to create background images. Each prompt should be descriptive, artistic, and cinematic.

Return your response strictly in the following JSON format. Make sure the JSON is valid and do not wrap it in anything other than markdown code block:
{
  "title": "A short descriptive title in English",
  "script": "The full spoken voiceover script in Bengali (বাংলা). Do not include any stage directions, parentheses, or scene descriptions here, only the words that will be spoken.",
  "image_prompts": [
    "cinematic, realistic image description 1 for the beginning",
    "cinematic, realistic image description 2 for point 1",
    "cinematic, realistic image description 3 for point 2",
    "cinematic, realistic image description 4 for the ending and call to action"
  ]
}
"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        # Parse JSON from response text
        response_text = response.text.strip()
        
        # Clean response if it's wrapped in markdown code blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        data = json.loads(response_text)
        
        # Validate structure
        if "title" in data and "script" in data and "image_prompts" in data:
            print(f"[+] Concept generated successfully: {data['title']}")
            return data
        else:
            raise ValueError("Invalid JSON structure returned from AI model.")

    except Exception as e:
        error_msg = f"Gemini generation error: {e}"
        print(f"[-] {error_msg}")
        send_telegram_error(error_msg, "Trend Analyzer")
        return get_fallback_concept()

def get_fallback_concept() -> dict:
    """Returns a pre-defined fallback concept in case the API fails."""
    print("[!] Using fallback offline concept...")
    return {
      "title": "Mysterious space facts",
      "script": "আপনি কি জানেন মহাকাশে এমন একটি গ্রহ আছে যা সম্পূর্ণ হীরা দিয়ে তৈরি? হ্যাঁ, এই গ্রহটির নাম ৫৫ ক্যানক্রি ই। এটি পৃথিবী থেকে প্রায় ৪০ আলোকবর্ষ দূরে অবস্থিত এবং এর আকার আমাদের পৃথিবীর চেয়ে দ্বিগুণ। বিজ্ঞানীদের মতে, এই গ্রহের তাপমাত্রা প্রায় ২০০০ ডিগ্রি সেলসিয়াস, যার কারণে এর কার্বন রূপান্তরিত হয়ে হীরাতে পরিণত হয়েছে। মহাকাশের এমন আরও অদ্ভুত রহস্য জানতে আমাদের পেজটি এখনই ফলো করুন!",
      "image_prompts": [
        "cinematic space view of a glowing diamond planet far away, ultra realistic, 4k",
        "close up of sparkling diamonds and crystals under extreme heat, glowing magma cracks, high detail",
        "astronaut looking at a futuristic diamond planet through spaceship window, deep space stars",
        "subscribe button glowing on a dark space background with nebulae, cinematic layout"
      ]
    }

if __name__ == "__main__":
    print("Testing Trend Analyzer...")
    concept = generate_video_concept()
    print("\n--- Generated Concept ---")
    print(f"Title: {concept['title']}")
    print(f"Script: {concept['script']}")
    print(f"Prompts: {concept['image_prompts']}")
