import requests
import config

def send_telegram_message(message: str) -> bool:
    """
    Sends a text message to the configured Telegram chat/channel.
    Returns True if successful, False otherwise.
    """
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print(f"[Local Log] Telegram credentials not set. Message: {message}")
        return False

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[Telegram] Notification sent successfully!")
            return True
        else:
            print(f"[Telegram] Failed to send notification. Response: {response.text}")
            return False
    except Exception as e:
        print(f"[Telegram] Error sending message: {e}")
        return False

def send_telegram_error(error_msg: str, component: str = "General") -> bool:
    """Sends a standardized error notification to Telegram."""
    formatted_msg = (
        f"🚨 <b>AI বট ত্রুটি সতর্কবার্তা</b> 🚨\n\n"
        f"<b>কম্পোনেন্ট:</b> {component}\n"
        f"<b>ত্রুটি বিবরণ:</b>\n<code>{error_msg}</code>\n\n"
        f"⚠️ দয়া করে বটের অবস্থা পরীক্ষা করুন।"
    )
    return send_telegram_message(formatted_msg)

def send_telegram_success(video_title: str, platforms: list) -> bool:
    """Sends a standardized success notification when a video is published."""
    platforms_str = ", ".join(platforms) if platforms else "None (Saved Locally)"
    formatted_msg = (
        f"✅ <b>AI ভিডিও সফলভাবে প্রকাশিত হয়েছে!</b> 🎉\n\n"
        f"<b>ভিডিও শিরোনাম:</b> {video_title}\n"
        f"<b>আপলোড করা হয়েছে:</b> {platforms_str}\n\n"
        f"🚀 আরো ভালো কাজ করতে থাকুন!"
    )
    return send_telegram_message(formatted_msg)

if __name__ == "__main__":
    # Test message
    print("Testing Telegram Notifier...")
    send_telegram_message("🤖 <b>AI Bot is starting up!</b>\nHello from Antigravity bot. Notifications are working.")
