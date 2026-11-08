"""
Local Vertical Video Renderer.
Uses FFmpeg to produce crisp 1080x1920 YouTube Shorts:
- Syncs speech audio
- Burns centered high-visibility subtitles
- Adds header badge and background visuals
- Outputs ready-to-upload MP4
"""

import os
import shutil
import subprocess

FONTS_CONF = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "fonts.conf"))

def get_ffmpeg():
    """Locate FFmpeg executable."""
    p = shutil.which("ffmpeg")
    if p:
        return p
    fallback = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
    )
    if os.path.exists(fallback):
        return fallback
    return "ffmpeg"

def get_ffprobe():
    """Locate FFprobe executable."""
    p = shutil.which("ffprobe")
    if p:
        return p
    fallback = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffprobe.exe"
    )
    if os.path.exists(fallback):
        return fallback
    return "ffprobe"

def get_audio_duration(audio_path: str) -> float:
    """Get the duration of an audio file in seconds."""
    ffprobe = get_ffprobe()
    cmd = [
        ffprobe, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 35.0

def render_short_video(audio_path: str, sub_path: str, output_path: str, category: str = "FACT OF THE DAY") -> str:
    """
    Renders a vertical (1080x1920) YouTube Short video.
    """
    ffmpeg_bin = get_ffmpeg()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    duration = get_audio_duration(audio_path)
    total_duration = duration + 0.8  # Clean pause buffer

    # Set up environment with fontconfig to prevent libass crash on Windows
    env = os.environ.copy()
    if os.path.exists(FONTS_CONF):
        env["FONTCONFIG_FILE"] = FONTS_CONF

    # To avoid Windows path and space issues inside libass filter, convert to relative forward slashes
    rel_sub = os.path.relpath(sub_path).replace("\\", "/")
    
    # Clean category title for the header
    header_text = category.upper()
    font_file = "C\\:/Windows/Fonts/arial.ttf"

    # Filter graph:
    # 1. 1080x1920 deep cosmic navy background
    # 2. Modern glowing header box with category title
    # 3. Dynamic burned subtitles with bold styling, outline, and shadow
    vf_chain = (
        f"drawbox=x=140:y=240:w=800:h=90:color=0x2563eb@0.9:t=fill,"
        f"drawtext=fontfile='{font_file}':text='{header_text}':fontcolor=white:fontsize=42:x=(w-text_w)/2:y=264,"
        f"subtitles={rel_sub}:force_style='FontName=Arial,FontSize=26,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2.5,Shadow=2,Alignment=2,MarginV=360'"
    )

    cmd = [
        ffmpeg_bin, "-y",
        "-f", "lavfi", "-i", f"color=c=0x0b0f19:s=1080x1920:d={total_duration}",
        "-i", audio_path,
        "-vf", vf_chain,
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]

    print(f"[LocalRenderer] Rendering vertical 1080x1920 video to: {output_path}...")
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[LocalRenderer Error] {res.stderr}")
        raise RuntimeError(f"FFmpeg failed with exit code {res.returncode}")

    print(f"[LocalRenderer] Video rendered successfully! Size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
    return output_path
