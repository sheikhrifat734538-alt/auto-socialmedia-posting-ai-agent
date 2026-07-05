import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# Load env variables
load_dotenv(override=True)

print("==================================================")
# 1. Check Gemini configuration
api_key = os.getenv("GEMINI_API_KEY", "")
print(f"[Gemini Key] Loaded: Length = {len(api_key)}")
if len(api_key) > 8:
    print(f"[Gemini Key] Format Check: Starts with '{api_key[:6]}' ... Ends with '{api_key[-4:]}'")
else:
    print("[Gemini Key] Warning: Key is very short or empty!")

# 2. Check Telegram configuration
bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
print(f"[Telegram Bot Token] Loaded: Length = {len(bot_token)}")
if len(bot_token) > 10:
    print(f"[Telegram Bot Token] Format Check: Starts with '{bot_token[:10]}' ... Ends with '{bot_token[-4:]}'")
else:
    print("[Telegram Bot Token] Warning: Token is very short or empty!")
print(f"[Telegram Chat ID] Loaded: '{chat_id}'")

print("==================================================")
# 3. Test Telegram Connection
print("[*] Testing connection to Telegram API...")
if bot_token:
    test_url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        res = requests.get(test_url, timeout=10)
        print(f"[Telegram Response] Status Code: {res.status_code}")
        print(f"[Telegram Response] Body: {res.text}")
    except Exception as e:
        print(f"[Telegram Response] Connection Error: {e}")
else:
    print("[Telegram] Skip test: Token is empty.")

print("==================================================")
# 4. Test Gemini Connection
print("[*] Testing connection to Gemini API...")
if api_key:
    try:
        genai.configure(api_key=api_key)
        print("[Gemini] Configured. Listing available models...")
        models = genai.list_models()
        model_names = [m.name for m in models]
        print(f"[Gemini Response] Found models: {model_names[:5]} ... total {len(model_names)}")
    except Exception as e:
        print(f"[Gemini Response] Error listing models: {e}")
else:
    print("[Gemini] Skip test: Key is empty.")
print("==================================================")
