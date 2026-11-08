"""
Batch Generator & Uploader for YouTube Shorts.
Generates and uploads multiple Shorts sequentially:
1. Synthesizes neural voiceover and styled subtitles (Edge-TTS)
2. Downloads scene-matched visuals and creates animated Ken Burns sequences
3. Renders full-bleed 1080x1920 60fps MP4 with yellow subtitles
4. Generates 16:9 high-CTR thumbnail and 9:16 Shorts cover
5. Uploads to YouTube Data API v3 with attached thumbnail
6. Handles quota limits gracefully by retaining rendered videos on disk
"""

import os
import sys
import json
import time
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from generator.facts_library import FACTS_DATABASE
from generator.script_generator import load_history, save_history
from generator.voice_synthesizer import synthesize_short
from generator.thumbnail_generator import generate_short_thumbnails
from video_engine.ai_visualizer import generate_multi_scene_video
from uploader.youtube_uploader import upload_short
from uploader.cleanup_manager import cleanup_short_assets
from run_daily import load_settings

def run_batch(count: int = 12):
    settings = load_settings()
    history = load_history()
    used_ids = set(history)
    
    # Get all remaining facts from curated library
    remaining = [f for f in FACTS_DATABASE if f["id"] not in used_ids]
    
    if not remaining:
        print("[Batch] No unused curated facts left in library!")
        return

    to_process = remaining[:count]
    total = len(to_process)
    
    print("\n" + "="*65)
    print(f"  STARTING BATCH SHORTS GENERATION & UPLOAD: {total} VIDEOS")
    print(f"  Channel : {settings.get('channel_name', 'CURIOUS BYTE')} ({settings.get('channel_handle', '@CuriousByteShort')})")
    print(f"  Privacy : {settings.get('upload_privacy', 'private')}")
    print("="*65 + "\n")

    uploaded_count = 0
    quota_hit = False

    for idx, chosen in enumerate(to_process, 1):
        short_id = chosen["id"]
        category = chosen["category"]
        title = chosen["title"]
        date_str = datetime.now().strftime("%Y-%m-%d")

        print(f"\n>>> [{idx}/{total}] Processing: {title} ({category})")
        
        # 1. Build script data
        promo_cta = "Please subscribe, like, and share Curious Byte for more interesting facts like this!"
        script_text = (
            f"{chosen['hook']} ... "
            f"First: {chosen['facts'][0]} ... "
            f"Second: {chosen['facts'][1]} ... "
            f"Third: {chosen['facts'][2]} ... "
            f"{chosen['loop_outro']} ... "
            f"{promo_cta}"
        )

        short_data = {
            "id": short_id,
            "category": category,
            "date_created": date_str,
            "title": title,
            "description": chosen["description"],
            "tags": chosen["tags"],
            "keywords": chosen["keywords"],
            "hook": chosen["hook"],
            "facts": chosen["facts"],
            "loop_outro": chosen["loop_outro"],
            "promo_cta": promo_cta,
            "scene_prompts": chosen.get("scene_prompts", {}),
            "voiceover_text": script_text
        }

        # 2. Voiceover & Subtitles
        print("  [1/4] Synthesizing voiceover & subtitles...")
        audio_assets = synthesize_short(
            short_data,
            voice=settings.get("voice", "en-US-ChristopherNeural"),
            rate=settings.get("voice_rate", "+4%")
        )

        # 3. Render 1080x1920 video
        print("  [2/4] Downloading visual scenes & rendering animated video...")
        rendered_video_path = os.path.join("output", "videos", f"{date_str}_{short_id}.mp4")
        try:
            rendered_video_path = generate_multi_scene_video(
                short_data=short_data,
                audio_path=audio_assets["audio_path"],
                srt_path=audio_assets["sub_path"],
                output_video_path=rendered_video_path,
                channel_name=settings.get("channel_name", "CURIOUS BYTE")
            )
        except Exception as e:
            print(f"  [Render Error] {e}")
            continue

        # 4. Generate Thumbnails (16:9 & 9:16)
        print("  [3/4] Generating 16:9 thumbnail & 9:16 vertical cover...")
        try:
            thumbs = generate_short_thumbnails(
                short_data,
                video_path=rendered_video_path,
                date_str=date_str
            )
            thumb_16x9 = thumbs.get("horizontal_16x9")
        except Exception as e:
            print(f"  [Thumbnail Error] {e}")
            thumb_16x9 = None

        # 5. Upload to YouTube
        video_url = None
        if not quota_hit:
            print("  [4/4] Uploading to YouTube with attached thumbnail...")
            try:
                video_url = upload_short(
                    video_file_path=rendered_video_path,
                    title=short_data["title"],
                    description=short_data["description"],
                    tags=short_data["tags"],
                    privacy_status=settings.get("upload_privacy", "private"),
                    thumbnail_path=thumb_16x9
                )
                if video_url:
                    uploaded_count += 1
                    print(f"  ✓ Uploaded: {video_url}")
                    if settings.get("delete_local_files_after_upload", True):
                        cleanup_short_assets(
                            short_id=short_id,
                            video_path=rendered_video_path,
                            audio_path=audio_assets.get("audio_path"),
                            sub_path=audio_assets.get("sub_path"),
                            thumbnail_paths=[thumbs.get("horizontal_16x9"), thumbs.get("vertical_9x16")]
                        )
            except Exception as e:
                err_str = str(e).lower()
                if "quotaexceeded" in err_str or "quota" in err_str:
                    print("\n  ⚠️ YouTube API daily upload quota reached for today!")
                    print("  Videos will continue rendering locally so they can be uploaded tomorrow.\n")
                    quota_hit = True
                else:
                    print(f"  [Upload Error] {e}")
        else:
            print("  [4/4] Skipping upload (Daily YouTube API quota reached). Saved locally.")

        # Update history
        history.append(short_id)
        save_history(history)
        
        # Short cooldown between renders
        time.sleep(2)

    print("\n" + "="*65)
    print("  BATCH PROCESSING COMPLETED! 🎉")
    print(f"  Total Processed : {total}")
    print(f"  Uploaded to YT  : {uploaded_count}")
    print(f"  Stored on Disk  : {total}")
    print("="*65 + "\n")

if __name__ == "__main__":
    count = 12
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            pass
    run_batch(count=count)
