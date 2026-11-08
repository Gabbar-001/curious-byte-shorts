"""
Batch Schedule Publisher for Curious Byte Unique.
Runs ONCE to generate N Shorts and schedules them on YouTube to release automatically:
- Uploads one Short every 30 minutes (or custom interval)
- Attaches high-CTR custom thumbnails
- Uses YouTube's native 'publishAt' scheduled premiere feature
- Deletes all local MP4s, images, and audio immediately after upload to save disk space
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta, timezone

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from generator.script_generator import get_next_short
from generator.voice_synthesizer import synthesize_short
from generator.thumbnail_generator import generate_short_thumbnails
from video_engine.true3d_engine import render_true3d_short
from video_engine.geostudio_visualizer import generate_geostudio_short
from uploader.youtube_uploader import upload_short
from uploader.cleanup_manager import cleanup_short_assets
from run_daily import load_settings

def schedule_batch(count: int = 10, interval_minutes: int = 30, start_delay_minutes: int = 30):
    settings = load_settings()
    engine_mode = settings.get("video_engine", "true3d")
    channel_name = settings.get("channel_name", "CURIOUS BYTE")
    
    now_utc = datetime.now(timezone.utc)
    
    print("\n" + "="*70)
    print(f"  CURIOUS BYTE — BATCH SCHEDULE PUBLISHER ({count} SHORTS)")
    print(f"  • Interval    : 1 Short every {interval_minutes} minutes")
    print(f"  • First Short : in {start_delay_minutes} minutes")
    print(f"  • Engine      : {engine_mode.upper()}")
    print(f"  • Auto-Clean  : Yes (Deletes local files immediately after upload)")
    print("="*70 + "\n")

    scheduled_list = []
    
    for i in range(count):
        target_time = now_utc + timedelta(minutes=start_delay_minutes + (i * interval_minutes))
        publish_at_iso = target_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        local_time_str = target_time.astimezone().strftime("%I:%M %p (%d %b)")

        print(f"\n>>> [{i+1}/{count}] Preparing Short scheduled for: {local_time_str} ({publish_at_iso})")

        # 1. Topic & Script
        print("  [1/5] Selecting fresh topic...")
        short_data = get_next_short()
        title = short_data["title"]
        short_id = short_data["id"]
        date_str = datetime.now().strftime("%Y-%m-%d")
        print(f"  • Title: {title}")

        # 2. Voiceover & Subtitles
        print("  [2/5] Synthesizing voiceover & subtitles...")
        audio_assets = synthesize_short(short_data, voice=settings.get("voice", "en-US-ChristopherNeural"), rate="+5%")

        # 3. Render Video
        print(f"  [3/5] Rendering {engine_mode.upper()} animated 1080x1920 Short...")
        rendered_video_path = os.path.join("output", "videos", f"{date_str}_{short_id}.mp4")
        try:
            if engine_mode == "true3d":
                rendered_video_path = render_true3d_short(
                    short_data=short_data,
                    audio_path=audio_assets["audio_path"],
                    srt_path=audio_assets["sub_path"],
                    output_video_path=rendered_video_path,
                    channel_name=channel_name
                )
            else:
                rendered_video_path = generate_geostudio_short(
                    short_data=short_data,
                    audio_path=audio_assets["audio_path"],
                    srt_path=audio_assets["sub_path"],
                    output_video_path=rendered_video_path,
                    channel_name=channel_name
                )
        except Exception as e:
            print(f"  [Render Error] {e}")
            continue

        # 4. Generate Thumbnails
        print("  [4/5] Generating custom 16:9 thumbnail...")
        thumbs = generate_short_thumbnails(short_data, video_path=rendered_video_path, date_str=date_str)
        thumb_16x9 = thumbs.get("horizontal_16x9")

        # 5. Upload to YouTube with Scheduled Publish Timestamp
        print(f"  [5/5] Uploading to YouTube & scheduling release at {local_time_str}...")
        video_url = None
        try:
            video_url = upload_short(
                video_file_path=rendered_video_path,
                title=title,
                description=short_data["description"],
                tags=short_data["tags"],
                privacy_status="private",
                thumbnail_path=thumb_16x9,
                publish_at=publish_at_iso,
                debate_question=short_data.get("debate_question")
            )
            if video_url:
                print(f"  ✓ Scheduled on YouTube: {video_url}")
                scheduled_list.append({
                    "title": title,
                    "url": video_url,
                    "release_time": local_time_str
                })

                # 6. Automatic Disk Cleanup (Deletes MP4, audio, thumbnails, and temp files)
                if settings.get("delete_local_files_after_upload", True):
                    cleanup_short_assets(
                        short_id=short_id,
                        video_path=rendered_video_path,
                        audio_path=audio_assets.get("audio_path"),
                        sub_path=audio_assets.get("sub_path"),
                        thumbnail_paths=[thumb_16x9, thumbs.get("vertical_9x16")]
                    )
        except Exception as e:
            err = str(e)
            if "uploadlimitexceeded" in err.lower():
                print("\n  ⚠️ YouTube 24-hour upload limit reached. Saved locally for next run.\n")
                break
            else:
                print(f"  [Upload Error] {e}")

        time.sleep(2)

    print("\n" + "="*70)
    print("  🎉 BATCH SCHEDULE COMPLETE!")
    print(f"  Successfully Scheduled : {len(scheduled_list)} Shorts (1 every {interval_minutes} mins)")
    print("="*70)
    for idx, item in enumerate(scheduled_list, 1):
        print(f"  {idx}. [{item['release_time']}] {item['title']} -> {item['url']}")
    print("="*70 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch generate and schedule YouTube Shorts every 30 minutes.")
    parser.add_argument("--count", type=int, default=10, help="Number of Shorts to schedule in this batch")
    parser.add_argument("--interval", type=int, default=30, help="Minutes between each scheduled upload (default: 30)")
    parser.add_argument("--start-delay", type=int, default=30, help="Minutes before the first video goes live (default: 30)")
    args = parser.parse_args()

    schedule_batch(count=args.count, interval_minutes=args.interval, start_delay_minutes=args.start_delay)
