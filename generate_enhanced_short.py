"""
Production Generator for Curious Byte Unique.
Generates 1 Complete Short with all 3 Viral Enhancements:
1. Split-Testing Hook (A/B testing)
2. Transition Whoosh SFX & 3-way audio mastering
3. Auto-Pinned Debate Comment & high-CTR description
4. Frame extraction for visual showcase
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# UTF-8 stdout
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
from video_engine.ai_visualizer import get_ffmpeg
from uploader.youtube_uploader import upload_short
from run_daily import load_settings

def generate_enhanced_short():
    settings = load_settings()
    channel_name = settings.get("channel_name", "CURIOUS BYTE")
    date_str = datetime.now().strftime("%Y-%m-%d")

    print("\n" + "="*70)
    print("  🚀 CURIOUS BYTE UNIQUE — GENERATING ENHANCED 3D SHORT")
    print("  • Engine: True 3D Broadcast Animations (NASA 4K)")
    print("  • Audio: 3-Way Hollywood Mix (Voiceover + Ambient Pad + Whoosh SFX)")
    print("  • Hook: Split-Testing Active Variant (A/B Testing)")
    print("  • Comment: Auto-Pinned Engagement Question")
    print("="*70 + "\n")

    # 1. Topic & Script with Split-Testing Hook & Debate Question
    print("[1/5] Selecting next topic & generating viral enhancements...")
    short_data = get_next_short()
    short_id = short_data["id"]
    title = short_data["title"]

    print(f"\n  🎯 Topic Category : {short_data['category']}")
    print(f"  🎬 Title          : {title}")
    print(f"  🔬 A/B Variant    : [{short_data['active_hook_variant']}] ({'Curiosity Question' if short_data['active_hook_variant'] == 'A' else 'Revelation Claim'})")
    print(f"  ⚡ Active Hook    : \"{short_data['hook']}\"")
    print(f"  💬 Debate Q       : \"{short_data['debate_question']}\"")

    # 2. Voiceover & Subtitles
    print("\n[2/5] Synthesizing neural voiceover & millisecond subtitle timestamps...")
    audio_assets = synthesize_short(
        short_data,
        voice=settings.get("voice", "en-US-ChristopherNeural"),
        rate=settings.get("voice_rate", "+4%")
    )
    print(f"  ✓ Voiceover: {audio_assets['audio_path']}")
    print(f"  ✓ Subtitles: {audio_assets['sub_path']}")

    # 3. Render 3D Video with Kinetic Captions & Transition Whooshes
    print("\n[3/5] Rendering 1080x1920 60fps 3D Short with Transition SFX...")
    output_video_path = os.path.join("output", "videos", f"{date_str}_{short_id}_enhanced.mp4")
    rendered_video = render_true3d_short(
        short_data=short_data,
        audio_path=audio_assets["audio_path"],
        srt_path=audio_assets["sub_path"],
        output_video_path=output_video_path,
        channel_name=channel_name
    )

    # 4. High-CTR Thumbnails
    print("\n[4/5] Generating custom 16:9 thumbnail & 9:16 cover...")
    thumbs = generate_short_thumbnails(short_data, video_path=rendered_video, date_str=date_str)
    print(f"  ✓ 16:9 Thumbnail : {thumbs['horizontal_16x9']}")
    print(f"  ✓ 9:16 Cover     : {thumbs['vertical_9x16']}")

    # 5. Extract Sample Frames for Visual Presentation
    print("\n[5/5] Extracting visual showcase frames...")
    preview_frames_dir = os.path.join("output", "preview_frames", f"{date_str}_{short_id}")
    os.makedirs(preview_frames_dir, exist_ok=True)
    ffmpeg_bin = get_ffmpeg()

    frame_timestamps = [2.0, 8.0, 15.0, 24.0, 32.0]
    extracted_frames = []
    for idx, sec in enumerate(frame_timestamps, 1):
        frame_file = os.path.join(preview_frames_dir, f"frame_{idx}_{int(sec)}s.jpg")
        cmd_frame = [
            ffmpeg_bin, "-y",
            "-ss", f"{sec:.1f}",
            "-i", rendered_video,
            "-frames:v", "1",
            "-q:v", "2",
            frame_file
        ]
        res = subprocess.run(cmd_frame, capture_output=True)
        if os.path.exists(frame_file):
            extracted_frames.append(frame_file)

    # 6. Upload Attempt to YouTube
    print("\n[6/6] Attempting YouTube upload with scheduled debate comment...")
    video_url = None
    try:
        video_url = upload_short(
            video_file_path=rendered_video,
            title=title,
            description=short_data["description"],
            tags=short_data["tags"],
            privacy_status=settings.get("upload_privacy", "private"),
            thumbnail_path=thumbs.get("horizontal_16x9"),
            debate_question=short_data.get("debate_question")
        )
    except Exception as e:
        err = str(e)
        if "uploadlimitexceeded" in err.lower():
            print("\n  ⚠️ YouTube 24-hour upload limit currently active while Advanced Features are pending.")
            print(f"  Video file is preserved locally at: {rendered_video}")
        else:
            print(f"  [Upload Note] {e}")

    print("\n" + "="*70)
    print("  🎉 ENHANCED 3D SHORT GENERATION COMPLETED!")
    print(f"  Video File    : {os.path.abspath(rendered_video)}")
    print(f"  File Size     : {os.path.getsize(rendered_video)/(1024*1024):.2f} MB")
    print(f"  Thumbnail     : {os.path.abspath(thumbs['horizontal_16x9'])}")
    print(f"  A/B Variant   : [{short_data['active_hook_variant']}]")
    print(f"  Debate Q      : {short_data['debate_question']}")
    if video_url:
        print(f"  YouTube URL   : {video_url}")
    print("="*70 + "\n")

    return {
        "short_data": short_data,
        "video_path": rendered_video,
        "thumbnails": thumbs,
        "preview_frames": extracted_frames,
        "video_url": video_url
    }

if __name__ == "__main__":
    generate_enhanced_short()
