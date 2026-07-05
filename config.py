import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv(override=True)

# API Keys & Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Scheduled Posting Times (24h format, e.g. "09:00")
MORNING_POST_TIME = os.getenv("MORNING_POST_TIME", "09:00")
AFTERNOON_POST_TIME = os.getenv("AFTERNOON_POST_TIME", "15:00")
EVENING_POST_TIME = os.getenv("EVENING_POST_TIME", "21:00")

# Active Social Media Platforms
ACTIVE_PLATFORMS = [p.strip().lower() for p in os.getenv("ACTIVE_PLATFORMS", "youtube,tiktok").split(",") if p.strip()]


# Workspace Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp_assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "generated_videos")
SESSION_DIR = os.path.join(BASE_DIR, "browser_sessions")

# Create directories if they do not exist
for directory in [TEMP_DIR, OUTPUT_DIR, SESSION_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

def validate_config():
    """Validates configuration settings and prints friendly checks."""
    missing = []
    if not GEMINI_API_KEY or "your_gemini" in GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if not TELEGRAM_BOT_TOKEN or "your_telegram" in TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_CHAT_ID or "your_telegram" in TELEGRAM_CHAT_ID:
        missing.append("TELEGRAM_CHAT_ID")
    
    if missing:
        print(f"[!] Warning: Missing or default environment variables: {', '.join(missing)}")
        print("[!] Make sure to update the .env file with your actual keys and tokens!")
        return False
    
    print("[+] Configuration loaded successfully and directories verified!")
    return True

if __name__ == "__main__":
    validate_config()
