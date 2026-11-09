"""
Curious Byte Unique — Master Autonomous Pipeline 2.0 (High-Speed Parallel Edition).
Single Daily Execution Master Script:
1. Executes once per day with Smart-Resume (skips already-uploaded slots in milliseconds).
2. Parallel Visual Synthesis: 5 concurrent threads for 10 scene images (4x faster).
3. Parallel Kinetic Rendering: 4 concurrent FFmpeg workers for 60fps clips (4x faster).
4. Ultrafast Concat Assembly: Multi-threaded FFmpeg encoding (3x faster).
5. Mandatory CTA Outro: Explicitly commands viewers to Like, Subscribe & Share in Scene 10.
6. Automatically uploads and schedules each Short on YouTube (native 'publishAt' for auto-public release).
7. Automatically cleans up local MP4s, temporary scenes, and audio files post-upload to save disk space.
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta, timezone

# UTF-8 stdout configuration for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from generator.ai_viral_intelligence import generate_viral_short_concept
from video_engine.cadence10_master_compositor import render_cadence10_short
from generator.thumbnail_generator import generate_short_thumbnails
from uploader.youtube_uploader import upload_short
from uploader.cleanup_manager import cleanup_short_assets
from run_daily import load_settings

def load_already_scheduled_slots() -> set:
    history_file = os.path.join("output", "uploads_history.json")
    scheduled_set = set()
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                records = json.load(f)
                for r in records:
                    spa = r.get("scheduled_publish_at")
                    if spa:
                        scheduled_set.add(spa)
        except Exception:
            pass
    return scheduled_set

def execute_self_learning_cycle():
    """
    Step 0: Autonomous Channel Intelligence & Self-Learning Cycle.
    1. Ingests latest views and velocity metrics from YouTube.
    2. Mines audience comments & inquiry patterns.
    3. Mines live trending topics from Reddit science RSS, ScienceDaily, and Phys.org.
    4. Computes channel brain directive & hook/pillar weighting matrix.
    5. Analyzes underperformers and formulates title healing recommendations.
    """
    print("\n" + "=" * 75)
    print("  🧠 STEP 0: EXECUTING CHANNEL SELF-LEARNING & AUDIENCE INTELLIGENCE CYCLE")
    print("=" * 75)

    # 1. Performance Analyzer
    try:
        from analytics.performance_analyzer import analyze_channel_performance
        analyze_channel_performance()
    except Exception as e:
        print(f"  [Analytics Warning] Performance analysis: {e}")

    # 2. Competitor Viral Radar
    try:
        from analytics.competitor_radar import run_competitor_radar
        run_competitor_radar()
    except Exception as e:
        print(f"  [Analytics Warning] Competitor radar: {e}")

    # 3. Audience Comment Miner
    try:
        from analytics.audience_comment_miner import mine_audience_insights
        mine_audience_insights()
    except Exception as e:
        print(f"  [Analytics Warning] Audience mining: {e}")

    # 4. Trend Explorer
    try:
        from analytics.trend_explorer import mine_trending_topics
        mine_trending_topics()
    except Exception as e:
        print(f"  [Analytics Warning] Trend mining: {e}")

    # 5. Autonomous Decision Agent & Persistent Memory Ledger
    try:
        from analytics.autonomous_decision_agent import run_autonomous_decision_agent
        run_autonomous_decision_agent()
    except Exception as e:
        print(f"  [Analytics Warning] Autonomous decision agent: {e}")

    # 6. Channel Brain
    try:
        from analytics.channel_brain import update_channel_brain
        update_channel_brain()
    except Exception as e:
        print(f"  [Analytics Warning] Channel brain: {e}")

    # 5. Title Healer
    try:
        from analytics.title_healer import analyze_and_heal_underperformers
        analyze_and_heal_underperformers()
    except Exception as e:
        print(f"  [Analytics Warning] Title healing: {e}")

    print("=" * 75 + "\n")

def run_pipeline(count: int = 48, interval_minutes: int = 30, start_at: str = "midnight", start_delay_minutes: int = 30, auto_upload: bool = True, skip_learning: bool = False):
    settings = load_settings()
    channel_name = settings.get("channel_name", "CURIOUS BYTE")
    date_str = datetime.now().strftime("%Y-%m-%d")

    # IST timezone (UTC+5:30) used universally so GitHub Actions runners match local Indian Standard Time
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now_local = datetime.now(ist_tz)

    if start_at and start_at.lower() in ["tomorrow"]:
        base_start = (now_local + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif start_at and start_at.lower() in ["6pm", "18:00", "evening"]:
        base_start = now_local.replace(hour=18, minute=0, second=0, microsecond=0)
        if base_start < now_local - timedelta(minutes=5):
            base_start = base_start + timedelta(days=1)
    elif start_at and start_at.lower() in ["midnight", "12:00am", "00:00", "today_midnight"]:
        if now_local.hour >= 12:
            # If running in afternoon or evening (like 6 PM), schedule for tomorrow's 00:00 AM -> 11:30 PM
            base_start = (now_local + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # If running earlier in the day or catch-up, schedule starting from today's midnight
            base_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    elif start_at and start_at.lower() in ["now", "immediate", "auto"]:
        base_start = now_local + timedelta(minutes=start_delay_minutes)
    else:
        base_start = now_local + timedelta(minutes=start_delay_minutes)

    first_slot_str = base_start.strftime("%I:%M %p (%d %b)")
    last_slot = base_start + timedelta(minutes=(count - 1) * interval_minutes)
    last_slot_str = last_slot.strftime("%I:%M %p (%d %b)")

    already_scheduled = load_already_scheduled_slots()

    print("\n" + "=" * 75)
    print("  🚀 CURIOUS BYTE UNIQUE — HIGH-SPEED PARALLEL PIPELINE 2.0")
    print(f"  • Total Daily Slots : {count} Shorts")
    print(f"  • Publish Cadence   : 1 Short every {interval_minutes} minutes")
    print(f"  • Period Covered    : {first_slot_str} -> {last_slot_str}")
    print(f"  • Already Uploaded  : {len(already_scheduled)} slots (will be skipped automatically)")
    print(f"  • Parallel Engine   : 5 Threads (Image Fetch) | 4 FFmpeg Workers (60fps Clips)")
    print(f"  • CTA Guarantee     : Like, Subscribe & Share in Scene 10 + description")
    print(f"  • Release Mode      : 100% PUBLIC at scheduled time")
    print(f"  • Auto-Cleanup      : Yes (Deletes raw files immediately after upload)")
    print("=" * 75 + "\n")

    if not skip_learning:
        execute_self_learning_cycle()

    scheduled_results = []

    for i in range(count):
        target_time_local = base_start + timedelta(minutes=i * interval_minutes)
        target_time_utc = target_time_local.astimezone(timezone.utc)
        publish_at_iso = target_time_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        local_time_str = target_time_local.strftime("%I:%M %p (%d %b)")
        now_utc = datetime.now(timezone.utc)

        # Smart Resume: Skip already uploaded slots
        if publish_at_iso in already_scheduled:
            print(f"  ⏭️ Slot {i+1:02d}/{count} [{local_time_str}] Already uploaded to YouTube. Skipping...")
            continue

        # Determine if target is in the future (> 2 minutes away)
        if target_time_utc > now_utc + timedelta(minutes=2):
            schedule_note = f"Scheduled (Auto-Public at {local_time_str})"
            upload_publish_at = publish_at_iso
        else:
            schedule_note = "Immediate Public Release"
            upload_publish_at = None

        print(f"\n[{i+1:02d}/{count}] ===========================================================================")
        print(f"  📅 Target Slot: {local_time_str} -> {schedule_note}")

        # 1. AI Viral Concept Discovery (Score >= 75 & Verified Facts & Mandatory CTA)
        print("  [Step 1/5] Discovering high-scoring viral concept & verifying facts...")
        try:
            concept_data = generate_viral_short_concept(min_score=75)
        except Exception as e:
            print(f"  ❌ Concept discovery failed: {e}. Retrying next slot...")
            continue

        short_id = concept_data["id"]
        title = concept_data["title"]
        print(f"  📌 Title : {title}")
        print(f"  ⚡ Hook  : \"{concept_data.get('hooks', {}).get('selected_hook')}\"")

        # 2. Render 10-Scene Cadence Short with Parallel Directors & FFmpeg Workers
        output_video_path = os.path.join("output", "videos", f"{date_str}_{short_id}.mp4")
        print(f"  [Step 2/5] Rendering 1080x1920 60fps Short (Parallel 10 Scenes)...")
        try:
            rendered_video = render_cadence10_short(
                concept_data=concept_data,
                output_video_path=output_video_path,
                channel_name=channel_name
            )
        except Exception as e:
            print(f"  ❌ Video render failed: {e}")
            import traceback
            traceback.print_exc()
            continue

        # 3. Generate Custom Thumbnails
        print("  [Step 3/5] Generating 16:9 Thumbnail & 9:16 Shorts Cover...")
        thumbs = generate_short_thumbnails(concept_data, video_path=rendered_video, date_str=date_str)
        thumb_16x9 = thumbs.get("horizontal_16x9")

        # 4. Upload & Schedule on YouTube (Directly as Public at release time)
        video_url = None
        if auto_upload:
            print(f"  [Step 4/5] Uploading to YouTube ({schedule_note})...")
            try:
                video_url = upload_short(
                    video_file_path=rendered_video,
                    title=title,
                    description=concept_data["description"],
                    tags=concept_data["tags"],
                    privacy_status="public",
                    thumbnail_path=thumb_16x9,
                    publish_at=upload_publish_at,
                    debate_question=concept_data.get("debate_question")
                )
                if video_url:
                    print(f"  ✅ Uploaded & Scheduled on YouTube: {video_url} ({schedule_note})")
                    already_scheduled.add(publish_at_iso)
                    scheduled_results.append({
                        "id": short_id,
                        "title": title,
                        "url": video_url,
                        "release_time": local_time_str,
                        "viral_score": concept_data.get("viral_score"),
                        "status": "SCHEDULED_PUBLIC"
                    })
                else:
                    print("  ⚠️ Upload completed without returned URL. Saved locally.")
                    scheduled_results.append({
                        "id": short_id,
                        "title": title,
                        "video_path": rendered_video,
                        "release_time": local_time_str,
                        "status": "SAVED_LOCAL"
                    })
            except Exception as e:
                err = str(e)
                print(f"  ⚠️ YouTube API Notice: {e}")
                scheduled_results.append({
                    "id": short_id,
                    "title": title,
                    "video_path": rendered_video,
                    "release_time": local_time_str,
                    "status": f"LOCAL_SAVED ({e})"
                })
        else:
            print("  [Step 4/5] Auto-upload disabled. Video saved locally for inspection.")
            scheduled_results.append({
                "id": short_id,
                "title": title,
                "video_path": rendered_video,
                "release_time": local_time_str,
                "status": "LOCAL_SAVED"
            })

        # 5. Automatic Disk Cleanup (Deletes raw MP4s and temporary files post-upload)
        if auto_upload and video_url and settings.get("delete_local_files_after_upload", True):
            print("  [Step 5/5] Performing automatic disk cleanup...")
            cleanup_short_assets(
                short_id=short_id,
                video_path=rendered_video,
                audio_path=os.path.join("output", "audio", f"{date_str}_{short_id}.mp3"),
                sub_path=os.path.join("output", "audio", f"{date_str}_{short_id}.srt"),
                thumbnail_paths=[thumb_16x9, thumbs.get("vertical_9x16")]
            )
            print("  ✓ Local media files cleaned up successfully.")

        time.sleep(1)

    # Final Summary Report
    print("\n" + "=" * 75)
    print("  🎉 DAILY AUTONOMOUS EXECUTION COMPLETE!")
    print(f"  Processed in this run : {len(scheduled_results)} Shorts")
    print(f"  Cadence Period        : {first_slot_str} -> {last_slot_str} (Every {interval_minutes}m)")
    print("=" * 75)
    for idx, item in enumerate(scheduled_results, 1):
        rel = item.get("release_time", "Immediate")
        print(f"  {idx:02d}. [{rel}] {item['title']} -> {item.get('url', item.get('status'))}")
    print("=" * 75 + "\n")

    summary_path = os.path.join("output", "metadata", f"{date_str}_full_schedule_48.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(scheduled_results, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous High-Speed YouTube Shorts Pipeline 2.0")
    parser.add_argument("--count", type=int, default=48, help="Number of Shorts to schedule in this run (default: 48)")
    parser.add_argument("--interval", type=int, default=30, help="Minutes between each release (default: 30)")
    parser.add_argument("--start-at", type=str, default="midnight", help="Starting slot ('midnight' for 12:00 AM, or 'now')")
    parser.add_argument("--start-delay", type=int, default=30, help="Minutes before first video goes live if start-at is 'now'")
    parser.add_argument("--no-upload", action="store_true", help="Generate locally without uploading")
    parser.add_argument("--skip-learning", action="store_true", help="Skip Step 0 self-learning cycle")
    args = parser.parse_args()

    run_pipeline(
        count=args.count,
        interval_minutes=args.interval,
        start_at=args.start_at,
        start_delay_minutes=args.start_delay,
        auto_upload=not args.no_upload,
        skip_learning=args.skip_learning
    )
