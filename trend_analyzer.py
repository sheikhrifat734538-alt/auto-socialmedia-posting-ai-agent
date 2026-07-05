import os
import json
import re
import sys
import google.generativeai as genai
import config
from telegram_notifier import send_telegram_error
import api_key_manager

# Ensure terminal outputs support Bengali Unicode characters without crashing
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass


def _try_generate_with_key(api_key: str, prompt: str) -> dict | None:
    """
    Attempt to generate content using a specific API key.
    Returns the parsed concept dict on success, or None on failure.
    If a 429 rate limit error is detected, the key is marked for 24-hour cooldown.
    """
    key_id = f"...{api_key[-8:]}"
    
    try:
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            tools=['google_search_retrieval']
        )
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
            print(f"[+] Concept generated successfully with key {key_id}: {data['title']}")
            return data
        else:
            print(f"[!] Key {key_id}: Invalid JSON structure. Skipping...")
            return None

    except Exception as e:
        error_str = str(e)
        
        # Check if this is a 429 rate limit error
        if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
            print(f"[⏸] Key {key_id}: Rate limit (429) hit! Putting on 24-hour cooldown.")
            api_key_manager.mark_key_exhausted(api_key)
        else:
            print(f"[!] Key {key_id}: Error — {e}")
        
        return None


def generate_video_concept() -> dict:
    """
    Uses Gemini AI to generate a viral vertical short video concept,
    complete with a Bengali script and English image prompts for the visuals.
    
    API Key Strategy:
    - Try keys sequentially (Key 1 → Key 2 → Key 3 → ...)
    - If a key gets 429 rate limit: put it on 24-hour cooldown & try next key
    - Skip keys that are already on cooldown (saves time)
    - If ALL keys exhausted: use fallback offline concept
    
    Returns a dictionary with: title, script, and image_prompts.
    """
    prompt = """
You are a viral social media growth expert. First, perform a search to find the latest real-time trending news, viral facts, or popular space/history/psychology topics that are currently generating high interest.
Based on the trending search findings, generate a highly engaging vertical short video concept (YouTube Shorts, TikTok, Facebook Reels) that is likely to go viral.

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
    # Load all keys and filter out cooled-down ones
    keys = api_key_manager._load_keys()
    state = api_key_manager._load_state()
    
    if not keys:
        print("[-] No API keys configured in .env!")
        return get_fallback_concept()
    
    # Separate active vs cooldown keys
    active_keys = []
    cooldown_count = 0
    
    for key in keys:
        if api_key_manager._is_key_on_cooldown(key, state):
            cooldown_count += 1
        else:
            active_keys.append(key)
    
    total = len(keys)
    print(f"\n[🔑] API Key Status: {len(active_keys)}/{total} active, {cooldown_count}/{total} on cooldown")
    
    if not active_keys:
        print("[✗] ALL API keys are on cooldown! Using fallback concept.")
        send_telegram_error("All API keys exhausted (on 24h cooldown). Using fallback.", "API Key Manager")
        return get_fallback_concept()
    
    # Try each active key sequentially
    for i, key in enumerate(active_keys):
        key_id = f"...{key[-8:]}"
        print(f"[→] Trying key #{i+1}/{len(active_keys)}: {key_id}")
        
        result = _try_generate_with_key(key, prompt)
        
        if result is not None:
            return result
        
        # If this key failed but wasn't rate-limited, still try next
        print(f"[→] Key {key_id} failed. Moving to next...")
    
    # All active keys failed
    print("[✗] All active API keys failed. Using fallback concept.")
    send_telegram_error(
        f"All {len(active_keys)} active keys failed. {cooldown_count} keys on cooldown. Using fallback.",
        "API Key Manager"
    )
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
    print("=" * 50)
    print("  Trend Analyzer — API Key Rotation Test")
    print("=" * 50)
    
    concept = generate_video_concept()
    print("\n--- Generated Concept ---")
    print(f"Title: {concept['title']}")
    print(f"Script: {concept['script']}")
    print(f"Prompts: {concept['image_prompts']}")
