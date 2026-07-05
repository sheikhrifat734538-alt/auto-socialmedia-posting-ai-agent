import os
import sys
import time
import schedule
import config
from trend_analyzer import generate_video_concept
from video_generator import compile_video
from social_poster import post_to_all
from telegram_notifier import send_telegram_message, send_telegram_success, send_telegram_error
import queue_manager

# Ensure terminal outputs support Bengali Unicode characters without crashing
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass


def run_cycle():
    """
    Executes a single workflow cycle:
    1. Check queue and upload any pending/failed videos.
    2. Brainstorm viral topic & script in Bengali (Gemini API with Live Search)
    3. Download background assets and compile vertical video (edge-tts + MoviePy)
    4. Save to queue and attempt upload.
    5. Notify the user via Telegram on success or error.
    """
    print("\n[+] STARTING AUTO CONTENT CREATION & POSTING CYCLE...")
    send_telegram_message("🤖 <b>AI Content Creator:</b> Starting video generation cycle...")
    
    # Step 0: Process any pending items in the queue first
    try:
        pending_uploads = queue_manager.get_pending_uploads()
        if pending_uploads:
            print(f"[+] Found {len(pending_uploads)} pending uploads in the queue. Processing them first...")
            for item in pending_uploads:
                send_telegram_message(f"🔄 <b>AI Poster:</b> Retrying pending upload for: <i>{item['title']}</i> on {', '.join(item['platforms'])}...")
                successes = post_to_all(item["video_path"], item["caption"], item["platforms"])
                for platform in item["platforms"]:
                    status = "success" if platform in successes else "failed"
                    queue_manager.update_status(item["filename"], platform, status)
                if successes:
                    send_telegram_success(f"Retried: {item['title']}", [p.capitalize() for p in successes])
    except Exception as qe:
        print(f"[-] Error processing queue: {qe}")
        
    try:
        # Step 1: Analyze trend and write Bengali script
        concept = generate_video_concept()
        title_slug = concept["title"].lower().replace(" ", "_")
        video_filename = f"{title_slug}_{int(time.time())}.mp4"
        
        # Step 2: Compile the video
        send_telegram_message(f"🎬 <b>AI Video Editor:</b> Generating visuals and audio for concept: <i>{concept['title']}</i>...")
        video_path = compile_video(concept, video_filename)
        
        # Step 3: Post to social media
        send_telegram_message("🚀 <b>AI Social Poster:</b> Video compilation finished. Initiating auto-upload process...")
        caption = f"{concept['script'][:150]}... #viral #trending #bangla #facts"
        
        # Add to queue database first as pending
        queue_manager.add_to_queue(video_filename, concept["title"], caption)
        
        # Attempt upload to all three platforms
        successful_platforms = post_to_all(video_path, caption)
        
        # Update status based on upload results
        for platform in ["youtube", "tiktok", "facebook"]:
            status = "success" if platform in successful_platforms else "failed"
            queue_manager.update_status(video_filename, platform, status)
            
        # Step 4: Success Telegram notification
        send_telegram_success(concept["title"], [p.capitalize() for p in successful_platforms])
        print("[+] Cycle completed successfully!")
        
    except Exception as e:
        error_msg = f"Cycle execution failed: {e}"
        print(f"[-] {error_msg}")
        raise e

def run_cycle_with_retry(max_retries=3, delay_seconds=120):
    """
    Wraps the run_cycle with an automatic self-healing retry mechanism.
    If an error occurs, it alerts Telegram, waits, and retries.
    """
    for attempt in range(1, max_retries + 1):
        try:
            run_cycle()
            return  # Success! Exit retry loop.
        except Exception as e:
            print(f"[-] Attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                retry_msg = (
                    f"⚠️ <b>Bot Warning (Attempt {attempt}/{max_retries} failed)</b>\n"
                    f"Error: <code>{e}</code>\n"
                    f"🔄 Bot is self-healing. Retrying automatically in {delay_seconds} seconds..."
                )
                send_telegram_message(retry_msg)
                time.sleep(delay_seconds)
            else:
                final_error = f"All {max_retries} attempts failed. Last error: {e}"
                send_telegram_error(final_error, "Main Loop Retry Coordinator")

def start_schedule():
    """Schedules the bot to run at configured times everyday."""
    print(f"[+] Bot scheduled to run everyday at:")
    print(f"    - Morning:   {config.MORNING_POST_TIME}")
    print(f"    - Afternoon: {config.AFTERNOON_POST_TIME}")
    print(f"    - Evening:   {config.EVENING_POST_TIME}")
    
    schedule.every().day.at(config.MORNING_POST_TIME).do(run_cycle_with_retry)
    schedule.every().day.at(config.AFTERNOON_POST_TIME).do(run_cycle_with_retry)
    schedule.every().day.at(config.EVENING_POST_TIME).do(run_cycle_with_retry)
    
    send_telegram_message("🤖 <b>AI Automation Bot is ONLINE!</b>\nWatching trends and scheduled to upload 3 times daily with Auto-Retry.")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Validate configurations first
    config.validate_config()
    
    # Check arguments
    if "--test-run" in sys.argv:
        print("[*] Running immediate manual test cycle...")
        run_cycle_with_retry()
    elif "--login" in sys.argv:
        print("[*] Launching browser login helper...")
        from social_poster import open_interactive_login
        open_interactive_login()
    else:
        print("[*] Starting scheduler mode (runs 3 times a day)...")
        start_schedule()

