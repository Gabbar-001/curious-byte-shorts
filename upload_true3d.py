"""
Upload script for the True 3D Realistic Animation Short.
Attempts upload and catches YouTube's 24-hour uploadLimitExceeded if the window is still locked.
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from uploader.youtube_uploader import upload_short
from uploader.cleanup_manager import cleanup_short_assets

def upload_3d():
    vid = "output/videos/2026-11-07_true3d_earth_001.mp4"
    thumb = "output/thumbnails/2026-11-07_true3d_earth_001_thumb_16x9.jpg"
    title = "Mind-Blowing Secrets About Planet Earth! 🌍 #Shorts"
    debate_q = "If you could look down at Earth from the ISS cupola for 24 hours, which continent would you be most excited to see?"
    desc = (
        f"💬 QUESTION OF THE DAY:\n{debate_q}\n"
        "👇 Drop your answer below! We reply to top comments!\n\n"
        "Did you know Russia has a larger surface area than the entire planet Pluto? "
        "Or that the closest humans to Point Nemo in the Pacific are astronauts in space?\n\n"
        "🔔 Subscribe to Curious Byte Unique for daily mind-blowing facts:\n"
        "https://www.youtube.com/@CuriousByteShort?sub_confirmation=1\n\n"
        "#Shorts #CuriousByte #EarthFacts #NASA #SpaceSecrets #ScienceFacts #3DAnimation"
    )
    tags = ["Shorts", "CuriousByte", "EarthFacts", "NASA", "SpaceSecrets", "ScienceFacts", "3DAnimation"]

    if not os.path.exists(vid):
        print(f"[Error] Video file not found: {vid}")
        return

    print("="*60)
    print("  UPLOADING TRUE 3D SHORT & CUSTOM THUMBNAIL TO YOUTUBE")
    print(f"  Video     : {os.path.abspath(vid)}")
    print(f"  Thumbnail : {os.path.abspath(thumb)}")
    print("="*60 + "\n")

    try:
        url = upload_short(
            video_file_path=vid,
            title=title,
            description=desc,
            tags=tags,
            privacy_status="private",
            thumbnail_path=thumb,
            debate_question=debate_q
        )
        if url:
            print("\n" + "="*60)
            print(f"  🎉 SUCCESS! Video is live on your channel:")
            print(f"  URL: {url}")
            print("="*60)
            cleanup_short_assets(
                short_id="true3d_earth_001",
                video_path=vid,
                audio_path="output/audio/2026-11-07_geo_secrets_001.mp3",
                sub_path="output/audio/2026-11-07_geo_secrets_001.srt",
                thumbnail_paths=[thumb, "output/thumbnails/2026-11-07_true3d_earth_001_cover_9x16.jpg"]
            )
    except Exception as e:
        err = str(e)
        if "uploadlimitexceeded" in err.lower():
            print("\n" + "!"*60)
            print("  ⚠️ YOUTUBE DAILY LIMIT REACHED (uploadLimitExceeded)")
            print("!"*60)
            print("YouTube limits channels to 10 video uploads in a 24-hour period.")
            print("We already successfully uploaded 10 videos today!")
            print("\nWhat to do:")
            print("1. As soon as your 24-hour window resets tomorrow, run:")
            print("   python upload_true3d.py")
            print("   or double-click run_daily.bat")
            print("2. To unlock higher daily limits permanently:")
            print("   Go to YouTube Studio -> Settings -> Channel -> Feature Eligibility")
            print("   and enable 'Advanced Features' (Video verification or channel history).")
            print("!"*60 + "\n")
        else:
            print(f"\n[Upload Error] {e}")

if __name__ == "__main__":
    upload_3d()
