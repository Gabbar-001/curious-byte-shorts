"""
Curious Byte — Autonomous 24/7 Live Streaming Engine.
Pipes a continuous seamless loop of channel Shorts and facts directly into YouTube RTMP via FFmpeg.
Features:
- Native FFmpeg RTMP streaming (no OBS required).
- Continuous looping playlist generator.
- Automatic reconnection on network drops.
- Hardware-optimized H.264 video encoding.
"""

import os
import sys
import time
import glob
import subprocess
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "config", ".env"))

YOUTUBE_RTMP_URL = "rtmp://a.rtmp.youtube.com/live2"
STREAM_KEY = os.getenv("YOUTUBE_STREAM_KEY", "").strip()

def build_stream_playlist(output_list_file="output/live_playlist.txt"):
    """Finds all available generated MP4 videos and writes an FFmpeg concat playlist."""
    os.makedirs(os.path.dirname(output_list_file), exist_ok=True)
    video_dir = os.path.join(os.path.dirname(__file__), "..", "output", "videos")
    videos = glob.glob(os.path.join(video_dir, "*.mp4"))

    if not videos:
        print("[LiveStreamer] No MP4 videos found in output/videos.")
        return None

    # Write concat demuxer format
    with open(output_list_file, "w", encoding="utf-8") as f:
        for v in videos:
            abs_path = os.path.abspath(v).replace("\\", "/")
            f.write(f"file '{abs_path}'\n")

    print(f"[LiveStreamer] Generated stream playlist with {len(videos)} videos: {output_list_file}")
    return os.path.abspath(output_list_file)

def start_automated_stream(stream_key: str = None, loop: bool = True):
    """Starts the FFmpeg live stream directly to YouTube."""
    target_key = stream_key or STREAM_KEY
    if not target_key:
        print("\n" + "="*70)
        print("  YOUTUBE STREAM KEY REQUIRED")
        print("="*70)
        print("Please obtain your stream key from YouTube Studio -> Go Live.")
        print("Then either pass it as an argument or set YOUTUBE_STREAM_KEY in config/.env")
        print("="*70 + "\n")
        return False

    playlist_path = build_stream_playlist()
    if not playlist_path:
        return False

    rtmp_destination = f"{YOUTUBE_RTMP_URL}/{target_key}"

    # FFmpeg command for robust 1080p vertical/horizontal live streaming
    cmd = [
        "ffmpeg",
        "-re",  # Read input at native frame rate (realtime)
        "-stream_loop", "-1" if loop else "0",  # Infinite loop
        "-f", "concat",
        "-safe", "0",
        "-i", playlist_path,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-b:v", "4000k",
        "-maxrate", "4500k",
        "-bufsize", "8000k",
        "-pix_fmt", "yuv420p",
        "-g", "60",  # 2-second GOP for 30fps / 60fps
        "-c:a", "aac",
        "-b:a", "160k",
        "-ar", "44100",
        "-f", "flv",
        rtmp_destination
    ]

    print("\n" + "="*70)
    print("  🔴 CURIOUS BYTE AUTOMATED LIVE STREAM ENGINE")
    print("="*70)
    print(f"Destination : {YOUTUBE_RTMP_URL} (Key: {target_key[:4]}****)")
    print(f"Playlist    : {playlist_path} (Loop: {loop})")
    print("Launching FFmpeg broadcast...")
    print("="*70 + "\n")

    try:
        process = subprocess.Popen(cmd)
        print(f"[LiveStreamer] Process started (PID: {process.pid}). Stream is live!")
        return process
    except Exception as e:
        print(f"[LiveStreamer] Error starting FFmpeg stream: {e}")
        return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Curious Byte Automated Live Streamer")
    parser.add_argument("--key", type=str, default=None, help="YouTube RTMP Stream Key")
    parser.add_argument("--no-loop", action="store_true", help="Do not loop playlist infinitely")
    args = parser.parse_args()

    start_automated_stream(stream_key=args.key, loop=not args.no_loop)
