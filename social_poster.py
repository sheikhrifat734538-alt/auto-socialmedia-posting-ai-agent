import os
import time
from playwright.sync_api import sync_playwright
import config
from telegram_notifier import send_telegram_error, send_telegram_message

USER_DATA_DIR = os.path.join(config.SESSION_DIR, "playwright_profile")

def open_interactive_login():
    """
    Opens a visible browser window so the user can log in to:
    - YouTube Studio (https://studio.youtube.com)
    - TikTok (https://www.tiktok.com/login)
    - Facebook (https://www.facebook.com)
    Once logged in, cookies/session data are saved to config.SESSION_DIR.
    """
    print("\n=======================================================")
    print("[*] STARTING INTERACTIVE LOGIN MODE")
    print("=======================================================")
    print("This will open a Chromium browser window. Please manually log in to:")
    print("1. https://studio.youtube.com (YouTube Studio)")
    print("2. https://www.tiktok.com/login (TikTok Creator Portal)")
    print("3. https://www.facebook.com (Facebook Business/Profile Page)")
    print("\nAfter logging in, close the browser window. Your login sessions will be saved.")
    print("=======================================================\n")
    
    with sync_playwright() as p:
        # Launch browser with persistent context
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled", "--disable-web-security", "--no-sandbox"]
        )
        
        # Open login pages for YouTube, TikTok, and Facebook in separate tabs
        platforms = [
            ("https://studio.youtube.com", "YouTube Studio"),
            ("https://www.tiktok.com/login", "TikTok"),
            ("https://www.facebook.com", "Facebook")
        ]
        pages = []
        for url, name in platforms:
            print(f"[+] Opening {name}...")
            p = context.new_page()
            p.goto(url)
            pages.append(p)
        # Keep browser open until the user closes all tabs manually
        while pages:
            for p in pages[:]:
                try:
                    _ = p.title()
                except Exception:
                    pages.remove(p)
            time.sleep(1)
        print("[+] All login tabs closed. Sessions saved successfully!")

def upload_to_youtube(video_path: str, caption: str) -> bool:
    """Automates uploading a short video to YouTube Shorts."""
    print("[+] Starting YouTube Shorts upload automation...")
    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=True,
                viewport={"width": 1280, "height": 800},
                args=["--disable-blink-features=AutomationControlled", "--disable-web-security", "--no-sandbox"]
            )
            page = context.new_page()
            page.goto("https://studio.youtube.com")
            page.wait_for_load_state("networkidle")
            
            # Check if we are logged in (look for upload button or avatar)
            if "login" in page.url or page.locator("a[href*='accounts.google']").count() > 0:
                print("[-] YouTube: Not logged in. Run 'python social_poster.py --login' to log in.")
                context.close()
                return False
                
            # Click the Create/Upload button with fallbacks
            create_btn = page.locator("#create-icon, button[aria-label*='Create'], button:has-text('Create')").first
            create_btn.click()
            
            upload_btn = page.locator("#text-item-0, ytcp-menu-item-upload-video, paper-item:has-text('Upload videos')").first
            upload_btn.click()
            
            page.wait_for_selector("input[type='file']")
            
            # Upload file
            file_input = page.locator("input[type='file']")
            file_input.set_input_files(video_path)
            print("[+] YouTube: Video file uploaded. Filling details...")
            
            # Fill title and description with fallbacks
            page.wait_for_selector("#textbox[aria-label*='Title'], div[id='textbox'][contenteditable='true']")
            title_box = page.locator("#textbox[aria-label*='Title'], div[id='textbox'][contenteditable='true']").first
            title_box.clear()
            title_box.fill(caption[:100])  # YouTube title limit
            
            # Next buttons through Wizard
            for _ in range(3):
                next_btn = page.locator("#next-button, button:has-text('Next')").first
                next_btn.click()
                time.sleep(2)
                
            # Set to public
            public_radio = page.locator("tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button:has-text('Public')").first
            public_radio.click()
            
            # Publish
            done_btn = page.locator("#done-button, button:has-text('Publish'), button:has-text('Save')").first
            done_btn.click()
            time.sleep(5)
            print("[+] YouTube Shorts published successfully!")
            context.close()
            return True
            
        except Exception as e:
            error_msg = f"YouTube upload failed: {e}"
            print(f"[-] {error_msg}")
            send_telegram_error(error_msg, "YouTube Poster")
            return False

def upload_to_tiktok(video_path: str, caption: str) -> bool:
    """Automates uploading a video to TikTok Creator Portal."""
    print("[+] Starting TikTok upload automation...")
    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=True,
                viewport={"width": 1280, "height": 800},
                args=["--disable-blink-features=AutomationControlled", "--disable-web-security", "--no-sandbox"]
            )
            page = context.new_page()
            page.goto("https://www.tiktok.com/creator-center/upload?lang=en")
            page.wait_for_load_state("networkidle")
            
            time.sleep(5) # wait for page hydration
            if "login" in page.url or page.locator("text=Log in").count() > 0:
                print("[-] TikTok: Not logged in. Run 'python social_poster.py --login' to log in.")
                context.close()
                return False
                
            # Wait for iframe or upload input
            iframe = page.frame_locator("iframe[src*='upload']")
            if iframe.locator("input[type='file']").count() > 0:
                file_input = iframe.locator("input[type='file']")
            else:
                file_input = page.locator("input[type='file']")
                
            file_input.set_input_files(video_path)
            print("[+] TikTok: Video file uploaded. Adding caption...")
            
            # Caption editing
            time.sleep(5) # wait for upload process
            caption_box = page.locator("div[class*='editor'], div[contenteditable='true'][aria-label*='caption']").first
            caption_box.clear()
            caption_box.fill(caption)
            
            # Click post
            post_btn = page.locator("button:has-text('Post'), button[type='submit']").first
            post_btn.click()
            time.sleep(5)
            print("[+] TikTok video published successfully!")
            context.close()
            return True
            
        except Exception as e:
            error_msg = f"TikTok upload failed: {e}"
            print(f"[-] {error_msg}")
            send_telegram_error(error_msg, "TikTok Poster")
            return False

def upload_to_facebook(video_path: str, caption: str) -> bool:
    """Automates uploading a Reel to Facebook Page/Profile."""
    print("[+] Starting Facebook Reels upload automation...")
    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=True,
                viewport={"width": 1280, "height": 800},
                args=["--disable-blink-features=AutomationControlled", "--disable-web-security", "--no-sandbox"]
            )
            page = context.new_page()
            page.goto("https://business.facebook.com/latest/reels_composer")
            page.wait_for_load_state("networkidle")
            
            if "login" in page.url:
                print("[-] Facebook: Not logged in. Run 'python social_poster.py --login' to log in.")
                context.close()
                return False
                
            # Upload video file
            page.wait_for_selector("input[type='file']")
            file_input = page.locator("input[type='file']").first
            file_input.set_input_files(video_path)
            print("[+] Facebook: Video uploading...")
            
            # Caption
            caption_box = page.locator("div[aria-label*='Describe your reel'], div[contenteditable='true']").first
            caption_box.fill(caption)
            
            # Next buttons through Meta Composer wizard
            for _ in range(2):
                next_btn = page.locator("button:has-text('Next'), button[aria-label*='Next']").first
                next_btn.click()
                time.sleep(2)
            
            # Click Publish
            publish_btn = page.locator("button:has-text('Publish'), button:has-text('Share'), button[aria-label*='Publish']").first
            publish_btn.click()
            time.sleep(10)
            print("[+] Facebook Reel published successfully!")
            context.close()
            return True
            
        except Exception as e:
            error_msg = f"Facebook upload failed: {e}"
            print(f"[-] {error_msg}")
            send_telegram_error(error_msg, "Facebook Poster")
            return False

def post_to_all(video_path: str, caption: str, target_platforms: list = None) -> list:
    """
    Attempts to upload the video to specific target platforms (defaults to all three).
    Returns a list of successfully posted platforms.
    """
    if target_platforms is None:
        target_platforms = ["youtube", "tiktok", "facebook"]
        
    successful_platforms = []
    
    # 1. YouTube Shorts
    if "youtube" in target_platforms:
        if upload_to_youtube(video_path, caption):
            successful_platforms.append("youtube")
        
    # 2. TikTok
    if "tiktok" in target_platforms:
        if upload_to_tiktok(video_path, caption):
            successful_platforms.append("tiktok")
        
    # 3. Facebook Reels
    if "facebook" in target_platforms:
        if upload_to_facebook(video_path, caption):
            successful_platforms.append("facebook")
        
    return successful_platforms

if __name__ == "__main__":
    import sys
    # Command line args to manually login
    if "--login" in sys.argv:
        open_interactive_login()
    else:
        print("Run with '--login' to log into your social media accounts first.")
        print("Example: python social_poster.py --login")
