"""
Daily YouTube Shorts Automation Pipeline.
Orchestrates:
1. Topic and script selection (preventing repeats)
2. AI neural voiceover generation & synchronized subtitle creation (Edge-TTS)
3. Invideo prompt generation & project initiation
4. Local video rendering (1080x1920 vertical format with styled subtitles)
5. Automated upload to YouTube as 'Private'/'Unlisted' for review
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from generator.script_generator import get_next_short
from generator.voice_synthesizer import synthesize_short
from generator.thumbnail_generator import generate_short_thumbnails
from invideo_studio.invideo_helper import InvideoStudio
from video_engine.ai_visualizer import generate_multi_scene_video
from video_engine.geostudio_visualizer import generate_geostudio_short
from video_engine.true3d_engine import render_true3d_short
from video_engine.local_renderer import render_short_video
from uploader.youtube_uploader import upload_short
from uploader.youtube_auth import TOKEN_FILE
from uploader.cleanup_manager import cleanup_short_assets

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "config", "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "channel_niche": "Interesting Facts & Trivia",
        "upload_privacy": "private",
        "voice": "en-US-ChristopherNeural",
        "voice_rate": "+4%",
        "auto_upload_on_generate": False
    }

def run_pipeline(force_upload: bool = False, skip_render: bool = False):
    settings = load_settings()
    date_str = datetime.now().strftime("%Y-%m-%d")

    print("\n" + "="*60)
    print(f"  STARTING DAILY YOUTUBE SHORTS PIPELINE - {date_str}")
    print("="*60)

    # 1. Generate Script & Metadata
    print("\n[Step 1/5] Selecting daily topic & generating script...")
    short_data = get_next_short()
    print(f"  • Category : {short_data['category']}")
    print(f"  • Title    : {short_data['title']}")
    print(f"  • Hook     : \"{short_data['hook']}\"")

    # 2. Synthesize Voiceover & Subtitles
    print("\n[Step 2/5] Synthesizing natural voiceover & subtitle timestamps...")
    audio_assets = synthesize_short(
        short_data,
        voice=settings.get("voice", "en-US-ChristopherNeural"),
        rate=settings.get("voice_rate", "+4%")
    )
    print(f"  • Audio file     : {audio_assets['audio_path']}")
    print(f"  • Subtitles file : {audio_assets['sub_path']}")

    # 3. Invideo Preparation
    print("\n[Step 3/5] Invideo AI Studio integration...")
    invideo = InvideoStudio()
    prompt_file = os.path.join("output", "invideo_prompts", f"{date_str}_{short_data['id']}.txt")
    invideo.generate_short_brief(short_data, prompt_file)
    print(f"  • Invideo Prompt saved: {prompt_file}")

    is_logged_in, msg = invideo.check_auth()
    if is_logged_in:
        print(f"  • Invideo CLI authenticated: {msg}")
    else:
        print(f"  • Note: Invideo CLI not logged in yet. (Run 'invideo auth login' when ready)")

    # 4. Render Video
    rendered_video_path = os.path.join("output", "videos", f"{date_str}_{short_data['id']}.mp4")
    if skip_render:
        print("\n[Step 4/5] Skipping local video render (--skip-render enabled).")
    else:
        print(f"\n[Step 4/5] Rendering multi-scene AI animated YouTube Short for '{settings.get('channel_name', 'CURIOUS BYTE')}'...")
        channel_title = settings.get("channel_name", "CURIOUS BYTE")
        engine_mode = settings.get("video_engine", "true3d")
        try:
            if engine_mode == "true3d":
                rendered_video_path = render_true3d_short(
                    short_data=short_data,
                    audio_path=audio_assets['audio_path'],
                    srt_path=audio_assets['sub_path'],
                    output_video_path=rendered_video_path,
                    channel_name=channel_title
                )
            elif engine_mode == "geostudio":
                rendered_video_path = generate_geostudio_short(
                    short_data=short_data,
                    audio_path=audio_assets['audio_path'],
                    srt_path=audio_assets['sub_path'],
                    output_video_path=rendered_video_path,
                    channel_name=channel_title
                )
            else:
                rendered_video_path = generate_multi_scene_video(
                    short_data=short_data,
                    audio_path=audio_assets['audio_path'],
                    srt_path=audio_assets['sub_path'],
                    output_video_path=rendered_video_path,
                    channel_name=channel_title
                )
        except Exception as e:
            print(f"[Engine Error] {e}. Falling back to standard renderer...")
            rendered_video_path = render_short_video(
                audio_path=audio_assets['audio_path'],
                sub_path=audio_assets['sub_path'],
                output_path=rendered_video_path,
                category=short_data['category']
            )

    # 4.5 Generate Thumbnails (16:9 for YouTube & 9:16 vertical cover)
    print("\n[Step 4.5/5] Generating high-CTR YouTube thumbnail & vertical Shorts cover...")
    thumbnails = generate_short_thumbnails(short_data, video_path=rendered_video_path, date_str=date_str)
    print(f"  • 16:9 Thumbnail : {thumbnails['horizontal_16x9']}")
    print(f"  • 9:16 Cover     : {thumbnails['vertical_9x16']}")

    # 5. YouTube Upload
    video_url = None
    should_upload = force_upload or settings.get("auto_upload_on_generate", False)
    
    print("\n[Step 5/5] YouTube Upload Status...")
    if should_upload and os.path.exists(rendered_video_path):
        privacy = settings.get("upload_privacy", "private")
        try:
            video_url = upload_short(
                video_file_path=rendered_video_path,
                title=short_data["title"],
                description=short_data["description"],
                tags=short_data["tags"],
                privacy_status=privacy,
                thumbnail_path=thumbnails.get("horizontal_16x9"),
                debate_question=short_data.get("debate_question")
            )
            if video_url and settings.get("delete_local_files_after_upload", True):
                cleanup_short_assets(
                    short_id=short_data["id"],
                    video_path=rendered_video_path,
                    audio_path=audio_assets.get("audio_path"),
                    sub_path=audio_assets.get("sub_path"),
                    thumbnail_paths=[thumbnails.get("horizontal_16x9"), thumbnails.get("vertical_9x16")]
                )
        except Exception as e:
            print(f"[YouTube Upload Error] {e}")
    else:
        if not os.path.exists(TOKEN_FILE):
            print("  • Automatic upload skipped: YouTube credentials not yet configured.")
            print("    (See setup_instructions.md to connect your YouTube channel)")
        else:
            print("  • Auto-upload is turned off in settings.json. Use '--upload' flag to publish.")

    print("\n" + "="*60)
    print("  DAILY SHORT GENERATION COMPLETE! 🎉")
    print("="*60)
    print(f"Topic        : {short_data['category']}")
    print(f"Title        : {short_data['title']}")
    if os.path.exists(rendered_video_path):
        print(f"Video File   : {os.path.abspath(rendered_video_path)}")
    print(f"Thumbnail    : {os.path.abspath(thumbnails['horizontal_16x9'])}")
    print(f"Shorts Cover : {os.path.abspath(thumbnails['vertical_9x16'])}")
    print(f"Invideo Text : {os.path.abspath(prompt_file)}")
    if video_url:
        print(f"YouTube URL  : {video_url} (Privacy: {settings.get('upload_privacy', 'private')})")
    print("="*60 + "\n")

    return {
        "short_data": short_data,
        "video_path": rendered_video_path,
        "thumbnails": thumbnails,
        "youtube_url": video_url
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and upload daily YouTube Short.")
    parser.add_argument("--upload", action="store_true", help="Force upload to YouTube after rendering")
    parser.add_argument("--skip-render", action="store_true", help="Skip video rendering and only generate audio & scripts")
    args = parser.parse_args()

    run_pipeline(force_upload=args.upload, skip_render=args.skip_render)
