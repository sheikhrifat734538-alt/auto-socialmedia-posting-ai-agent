import os
import re
import asyncio
import random
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont
import edge_tts
try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
except ImportError:
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
import config
from telegram_notifier import send_telegram_error

# URL for a free Bengali TTF font (to render subtitles correctly)
BENGALI_FONT_URL = "https://github.com/maateen/bengali-fonts/raw/master/SolaimanLipi/SolaimanLipi.ttf"
FONT_PATH = os.path.join(config.TEMP_DIR, "SolaimanLipi.ttf")

def download_bengali_font():
    """Downloads a Bengali TTF font if not already present."""
    if not os.path.exists(FONT_PATH):
        print("[+] Downloading Bengali font for subtitles...")
        try:
            response = requests.get(BENGALI_FONT_URL, timeout=30)
            if response.status_code == 200:
                with open(FONT_PATH, "wb") as f:
                    f.write(response.content)
                print("[+] Bengali font downloaded successfully.")
            else:
                print("[-] Failed to download Bengali font, subtitles might look default.")
        except Exception as e:
            print(f"[-] Error downloading font: {e}")

async def generate_bengali_voiceover(text: str, output_path: str):
    """
    Generates a natural-sounding Bengali voiceover using Microsoft Edge neural TTS.
    Uses 'bn-BD-NabanitaNeural' (realistic female voice) or 'bn-BD-PradeepNeural' (male).
    """
    print("[+] Generating Bengali Voiceover using Edge-TTS...")
    voice = "bn-BD-NabanitaNeural"  # Standard high quality Bengali neural voice
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    print(f"[+] Audio generated successfully: {output_path}")

def generate_ai_image(prompt: str, output_path: str) -> bool:
    """
    Generates a high-quality vertical 9:16 image using Pollinations AI (free, no API key).
    """
    print(f"[+] Generating AI Image for prompt: '{prompt[:40]}...'")
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        seed = random.randint(1, 999999)
        # 1080x1920 is standard portrait size for vertical short videos (9:16)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true&seed={seed}"
        
        response = requests.get(url, timeout=40)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"[+] Image saved: {output_path}")
            return True
        else:
            print(f"[-] Failed to generate image. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[-] Image generation error: {e}")
        return False

def add_subtitles_to_image(image_path: str, text: str, output_path: str):
    """
    Overlays a semi-transparent black bar and Bengali subtitle text onto an image.
    Uses PIL to bypass MoviePy's ImageMagick dependency.
    """
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img, "RGBA")
        width, height = img.size
        
        # Load Bengali font or fallback
        font_size = 48
        if os.path.exists(FONT_PATH):
            font = ImageFont.truetype(FONT_PATH, font_size)
        else:
            font = ImageFont.load_default()

        # Word wrapping helper for Bengali text
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            # Check width of the test line
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            if line_width > width - 100:  # 50px padding on each side
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        # Calculate bounding box for text overlay background
        line_height = font_size + 15
        box_height = len(lines) * line_height + 40
        box_y_start = height - box_height - 150  # Positioned slightly above the bottom
        
        # Draw semi-transparent black rectangle behind text
        draw.rectangle(
            [(40, box_y_start), (width - 40, box_y_start + box_height)],
            fill=(0, 0, 0, 160)
        )
        
        # Render text lines
        y_text = box_y_start + 20
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x_text = (width - text_width) / 2  # Center text
            draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255, 255))
            y_text += line_height
            
        img.save(output_path)
        print(f"[+] Text overlay added to: {output_path}")
    except Exception as e:
        print(f"[-] Failed to add subtitles: {e}")
        # Save original as fallback
        if image_path != output_path:
            img = Image.open(image_path)
            img.save(output_path)

def set_clip_duration(clip, duration):
    if hasattr(clip, "with_duration"):
        return clip.with_duration(duration)
    return clip.set_duration(duration)

def set_clip_audio(clip, audio):
    if hasattr(clip, "with_audio"):
        return clip.with_audio(audio)
    return clip.set_audio(audio)

def compile_video(concept: dict, video_filename: str) -> str:
    """
    Compiles generated voiceover audio and images into a final 9:16 MP4 video.
    Uses unique temporary file paths based on video_filename to prevent conflicts
    and cleans them up when finished.
    """
    download_bengali_font()
    
    # Extract unique base slug to keep temp files isolated
    base_slug = os.path.splitext(video_filename)[0]
    
    # 1. Paths setup
    audio_path = os.path.join(config.TEMP_DIR, f"{base_slug}_voiceover.mp3")
    output_video_path = os.path.join(config.OUTPUT_DIR, video_filename)
    
    # 2. Generate Voiceover
    asyncio.run(generate_bengali_voiceover(concept["script"], audio_path))
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError("Voiceover audio could not be generated.")
        
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    print(f"[+] Voiceover audio duration: {duration:.2f} seconds")
    
    # 3. Generate and Process Images
    image_prompts = concept["image_prompts"]
    num_images = len(image_prompts)
    duration_per_image = duration / num_images
    
    # Split Bengali script roughly into segments for subtitles
    script_sentences = [s.strip() for s in re.split(r'[।!?]', concept["script"]) if s.strip()]
    
    # Ensure we have enough sentences, pad if needed
    while len(script_sentences) < num_images:
        script_sentences.append("")
    
    processed_clips = []
    temp_img_paths = []
    
    for i in range(num_images):
        raw_img_path = os.path.join(config.TEMP_DIR, f"{base_slug}_raw_img_{i}.jpg")
        sub_img_path = os.path.join(config.TEMP_DIR, f"{base_slug}_sub_img_{i}.jpg")
        temp_img_paths.extend([raw_img_path, sub_img_path])
        
        # Download AI image
        success = generate_ai_image(image_prompts[i], raw_img_path)
        if not success:
            # Fallback placeholder image (plain colored image)
            print(f"[!] Generating color fallback image for index {i}")
            fallback_img = Image.new("RGB", (1080, 1920), color=(30, 30, 30))
            fallback_img.save(raw_img_path)
            
        # Draw subtitles
        subtitle_text = script_sentences[i] if i < len(script_sentences) else ""
        add_subtitles_to_image(raw_img_path, subtitle_text, sub_img_path)
        
        # Create MoviePy Image Clip
        img_clip = set_clip_duration(ImageClip(sub_img_path), duration_per_image)
        processed_clips.append(img_clip)
        
    # 4. Concatenate and render video
    print("[+] Concatenating clips and rendering final video...")
    final_video = concatenate_videoclips(processed_clips, method="compose")
    final_video = set_clip_audio(final_video, audio_clip)
    
    # Write video to output file
    # Using 24 fps for mobile speed and standard formatting
    temp_audio_render = os.path.join(config.TEMP_DIR, f"{base_slug}_temp-audio.m4a")
    final_video.write_videofile(
        output_video_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        temp_audiofile=temp_audio_render,
        remove_temp=True
    )
    
    # Close clips to free memory
    audio_clip.close()
    final_video.close()
    for clip in processed_clips:
        clip.close()
        
    # 5. Clean up temporary files to save space and prevent locks
    print("[+] Cleaning up temporary video generation files...")
    for path in [audio_path, temp_audio_render] + temp_img_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as ce:
                print(f"[!] Warning: Could not remove temporary file {path}: {ce}")
        
    print(f"[+] Final video successfully compiled and saved to: {output_video_path}")
    return output_video_path

if __name__ == "__main__":
    print("Testing Video Generator...")
    # Test concept
    test_concept = {
      "title": "Space Fact Test",
      "script": "মহাকাশে একটি গ্রহ রয়েছে যেখানে অনবরত কাঁচের বৃষ্টি হয়! এই গ্রহটির নাম এইচডি ১৮৯৭৩৩বি। এখানে বাতাস অত্যন্ত দ্রুত গতিতে প্রবাহিত হয়, যার ফলে কাঁচের টুকরোগুলো হড়হড় করে উড়ে বেড়ায়।",
      "image_prompts": [
        "cinematic space deep blue planet raining glass shards, glowing atmosphere, unreal engine 5 render",
        "close up view of tiny glass pieces flying sideways in a massive blue storm, extreme wind motion blur"
      ]
    }
    try:
        compile_video(test_concept, "test_space_video.mp4")
    except Exception as ex:
        print(f"Error compiling: {ex}")
