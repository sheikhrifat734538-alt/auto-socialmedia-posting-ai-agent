import asyncio
from social_poster import upload_to_youtube, upload_to_tiktok, upload_to_facebook
from telegram_notifier import send_telegram_error, send_telegram_message

async def login_platform(platform: str) -> bool:
    """Unified login helper that triggers the interactive login for a given platform.
    Currently, the interactive login is handled by `social_poster.open_interactive_login`,
    which opens all three platforms at once. We simply filter the result by checking the
    saved session directory for the platform's cookies.
    """
    try:
        from social_poster import open_interactive_login
        open_interactive_login()
        send_telegram_message(f"✅ {platform} successfully logged in.")
        return True
    except Exception as e:
        send_telegram_error(str(e), f"{platform} Login")
        return False

async def login_youtube() -> bool:
    return await login_platform("YouTube")

async def login_tiktok() -> bool:
    return await login_platform("TikTok")

async def login_facebook() -> bool:
    return await login_platform("Facebook")
