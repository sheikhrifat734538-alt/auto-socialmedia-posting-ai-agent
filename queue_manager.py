import os
import json
import config

HISTORY_FILE = os.path.join(config.BASE_DIR, "upload_history.json")

def load_history() -> dict:
    """Loads the upload history database."""
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[-] Error loading history file: {e}")
        return {}

def save_history(history: dict):
    """Saves the upload history database."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[-] Error saving history file: {e}")

def add_to_queue(video_filename: str, title: str, caption: str):
    """Adds a new generated video to the upload queue."""
    history = load_history()
    history[video_filename] = {
        "title": title,
        "caption": caption,
        "youtube": "pending" if "youtube" in config.ACTIVE_PLATFORMS else "skipped",
        "tiktok": "pending" if "tiktok" in config.ACTIVE_PLATFORMS else "skipped",
        "facebook": "pending" if "facebook" in config.ACTIVE_PLATFORMS else "skipped"
    }
    save_history(history)
    print(f"[+] Video added to queue: {video_filename}")

def get_pending_uploads() -> list:
    """Returns a list of videos that have pending status for any platform.
    Each item is a dictionary containing video_path and pending platforms.
    """
    history = load_history()
    pending = []
    for filename, data in history.items():
        platforms_to_upload = []
        for platform in ["youtube", "tiktok", "facebook"]:
            if platform in config.ACTIVE_PLATFORMS:
                if data.get(platform, "pending") == "pending" or data.get(platform) == "failed":
                    platforms_to_upload.append(platform)
        
        if platforms_to_upload:
            video_path = os.path.join(config.OUTPUT_DIR, filename)
            # Only add if the file actually exists on disk
            if os.path.exists(video_path):
                pending.append({
                    "filename": filename,
                    "video_path": video_path,
                    "title": data.get("title", ""),
                    "caption": data.get("caption", ""),
                    "platforms": platforms_to_upload
                })
    return pending

def update_status(video_filename: str, platform: str, status: str):
    """Updates the status of a video for a specific platform."""
    history = load_history()
    if video_filename in history:
        history[video_filename][platform] = status
        save_history(history)
        print(f"[+] Updated status for {video_filename} on {platform} to: {status}")
        
        # Check if fully complete on all platforms to save space
        check_and_cleanup_completed(video_filename, history[video_filename])

def check_and_cleanup_completed(video_filename: str, data: dict):
    """Deletes the local video file if it succeeded or was skipped on all platforms."""
    if (data.get("youtube") in ("success", "skipped") and 
        data.get("tiktok") in ("success", "skipped") and 
        data.get("facebook") in ("success", "skipped")):
        video_path = os.path.join(config.OUTPUT_DIR, video_filename)
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
                print(f"[+] Deleted local video {video_filename} to save disk space.")
            except Exception as e:
                print(f"[-] Could not delete completed video file: {e}")
