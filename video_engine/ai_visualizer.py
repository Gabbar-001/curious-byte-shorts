"""
AI Visualizer & Multi-Scene Animator.
Produces scene-by-scene photorealistic AI visuals matching the script lines,
a dedicated branded promotional outro with channel logo,
and renders high-contrast, large, mobile-optimized YouTube Shorts subtitles via ASS.
"""

import os
import shutil
import urllib.parse
import subprocess
import requests
from PIL import Image, ImageDraw, ImageFont

FONTS_CONF = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "fonts.conf"))

def get_ffmpeg():
    p = shutil.which("ffmpeg")
    if p: return p
    fallback = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
    )
    if os.path.exists(fallback): return fallback
    return "ffmpeg"

def get_ffprobe():
    p = shutil.which("ffprobe")
    if p: return p
    fallback = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffprobe.exe"
    )
    if os.path.exists(fallback): return fallback
    return "ffprobe"

def get_audio_duration(audio_path: str) -> float:
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
        return 38.0

def ensure_promo_card(channel_name: str = "CURIOUS BYTE", handle: str = "@CuriousByteShort") -> str:
    """Creates a high-definition 1080x1920 promotional outro card with logo and CTA."""
    out_path = os.path.join("assets", "promo_outro_card.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    W, H = 1080, 1920
    card = Image.new("RGBA", (W, H), (7, 11, 20, 255))
    draw = ImageDraw.Draw(card)

    # Ambient radial glow behind the logo
    for r in range(500, 180, -20):
        alpha = int(28 * (1 - r / 500))
        draw.ellipse((W//2 - r, 580 - r, W//2 + r, 580 + r), fill=(56, 189, 248, alpha))

    # Channel Logo (High-resolution square with rounded corners)
    logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "channel_logo.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join("assets", "channel_logo.png")

    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = 400
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        logo_mask = Image.new("L", (logo_size, logo_size), 0)
        mask_draw = ImageDraw.Draw(logo_mask)
        mask_draw.rounded_rectangle((0, 0, logo_size, logo_size), radius=35, fill=255)
        
        logo_x = (W - logo_size) // 2
        logo_y = 380
        
        # Outer glowing neon cyan border
        draw.rounded_rectangle((logo_x - 6, logo_y - 6, logo_x + logo_size + 6, logo_y + logo_size + 6), radius=40, outline=(56, 189, 248, 255), width=6)
        card.paste(logo, (logo_x, logo_y), mask=logo_mask)

    # Fonts (Cross-platform resolution for Windows & Linux)
    candidates_bold = [
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "Arial Bold",
        "DejaVuSans-Bold"
    ]
    candidates_sub = [
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "Arial",
        "DejaVuSans"
    ]
    font_title = None
    font_btn = None
    for cand in candidates_bold:
        try:
            if cand.startswith("C:") or cand.startswith("/"):
                if os.path.exists(cand):
                    font_title = ImageFont.truetype(cand, 52)
                    font_btn = ImageFont.truetype(cand, 42)
                    break
            else:
                font_title = ImageFont.truetype(cand, 52)
                font_btn = ImageFont.truetype(cand, 42)
                break
        except Exception:
            continue
    if not font_btn:
        font_btn = ImageFont.load_default()
        font_title = font_btn

    font_sub = None
    for cand in candidates_sub:
        try:
            if cand.startswith("C:") or cand.startswith("/"):
                if os.path.exists(cand):
                    font_sub = ImageFont.truetype(cand, 34)
                    break
            else:
                font_sub = ImageFont.truetype(cand, 34)
                break
        except Exception:
            continue
    if not font_sub:
        font_sub = font_btn

    # Channel Name Headline
    title_text = channel_name.upper()
    tb = draw.textbbox((0, 0), title_text, font=font_title)
    draw.text(((W - (tb[2] - tb[0])) // 2, 820), title_text, font=font_title, fill=(255, 255, 255))

    # Red Subscribe Button
    btn_w, btn_h = 700, 96
    btn_x = (W - btn_w) // 2
    btn_y = 910
    draw.rounded_rectangle((btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), radius=48, fill=(225, 29, 72, 255))

    btn_text = "SUBSCRIBE • LIKE • SHARE"
    b_bbox = draw.textbbox((0, 0), btn_text, font=font_btn)
    b_w = b_bbox[2] - b_bbox[0]
    draw.text(((W - b_w)//2, btn_y + 24), btn_text, font=font_btn, fill=(255, 255, 255))

    # Channel Handle
    h_bbox = draw.textbbox((0, 0), handle, font=font_sub)
    h_w = h_bbox[2] - h_bbox[0]
    draw.text(((W - h_w)//2, 1030), handle, font=font_sub, fill=(148, 163, 184))

    card.save(out_path)
    return out_path

def fetch_ai_image(prompt: str, output_path: str, retries: int = 3) -> str:
    """Download an AI generated visual matching the prompt."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    styled_prompt = f"cinematic 8k, photorealistic, intense dramatic lighting, unreal engine 5, {prompt}"
    encoded = urllib.parse.quote(styled_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=1280&model=flux&nologo=true"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for attempt in range(retries):
        try:
            print(f"[AIVisualizer] Generating scene art: {prompt[:50]}...")
            r = requests.get(url, headers=headers, timeout=45)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(output_path, "wb") as f:
                    f.write(r.content)
                return output_path
        except Exception as e:
            print(f"[AIVisualizer] Attempt {attempt+1} retry: {e}")

    ffmpeg_bin = get_ffmpeg()
    fallback_cmd = [
        ffmpeg_bin, "-y",
        "-f", "lavfi", "-i", "color=c=0x0a1022:s=720x1280:d=1",
        "-vframes", "1", output_path
    ]
    subprocess.run(fallback_cmd, capture_output=True)
    return output_path

def render_ken_burns_clip(image_path: str, duration: float, output_clip_path: str, zoom_in: bool = True) -> str:
    """Animates a still 9:16 image into a dynamic camera movement clip."""
    ffmpeg_bin = get_ffmpeg()
    os.makedirs(os.path.dirname(output_clip_path), exist_ok=True)
    
    fps = 25
    total_frames = int(duration * fps) + 5
    
    if zoom_in:
        zoom_expr = "min(zoom+0.0012,1.28)"
    else:
        zoom_expr = "max(1.28-0.0012*on,1.0)"

    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1080x1920:fps={fps}"
    )

    cmd = [
        ffmpeg_bin, "-y",
        "-loop", "1",
        "-i", image_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "faster",
        "-pix_fmt", "yuv420p",
        "-t", f"{duration:.3f}",
        output_clip_path
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg Ken Burns failed: {res.stderr}")

    return output_clip_path

def srt_to_ass(srt_path: str, ass_path: str) -> str:
    """
    Converts an SRT file into an Advanced SubStation Alpha (.ass) file
    with native 1080x1920 canvas coordinates, smart multi-line wrapping,
    and high-impact YouTube Shorts bold yellow typography.
    """
    def to_ass_time(ts: str) -> str:
        h, m, s_ms = ts.strip().split(":")
        s, ms = s_ms.split(",")
        return f"{int(h)}:{m}:{s}.{ms[:2]}"

    def wrap_text(text: str, max_chars: int = 30) -> str:
        words = text.split()
        lines, cur, cur_len = [], [], 0
        for w in words:
            if cur_len + len(w) + (1 if cur else 0) > max_chars and cur:
                lines.append(" ".join(cur))
                cur = [w]
                cur_len = len(w)
            else:
                cur.append(w)
                cur_len += len(w) + (1 if cur else 0)
        if cur:
            lines.append(" ".join(cur))
        return r"\N".join(lines)

    ass_header = """[Script Info]
Title: Curious Byte Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,65,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,4.5,2.5,2,60,60,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    with open(srt_path, "r", encoding="utf-8") as f:
        raw_lines = [l.strip() for l in f if l.strip()]

    idx = 0
    while idx < len(raw_lines):
        if raw_lines[idx].isdigit():
            t_line = raw_lines[idx+1]
            txts = []
            idx += 2
            while idx < len(raw_lines) and not raw_lines[idx].isdigit():
                txts.append(raw_lines[idx])
                idx += 1
            s_str, e_str = t_line.split(" --> ")
            wrapped = wrap_text(" ".join(txts))
            events.append(f"Dialogue: 0,{to_ass_time(s_str)},{to_ass_time(e_str)},Default,,0,0,0,,{wrapped}")

    os.makedirs(os.path.dirname(ass_path), exist_ok=True)
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events))

    return ass_path

def generate_multi_scene_video(short_data: dict, audio_path: str, srt_path: str, output_video_path: str, channel_name: str = "CURIOUS BYTE") -> str:
    """
    Main visual orchestrator:
    1. Splits audio into visual scenes + promotional CTA outro scene
    2. Generates scene-specific AI visuals
    3. Animate each scene with Ken Burns motion
    4. Concat scenes into full track
    5. Converts subtitles to 1080x1920 ASS format with bold yellow text
    6. Overlays subtitles onto clean, unbordered cinematic footage
    """
    ffmpeg_bin = get_ffmpeg()
    total_duration = get_audio_duration(audio_path)
    
    short_id = short_data["id"]
    temp_dir = os.path.join("output", "temp_scenes", short_id)
    os.makedirs(temp_dir, exist_ok=True)

    # Ensure promotional outro card with exact logo is ready
    promo_card_path = ensure_promo_card(channel_name=channel_name, handle="@CuriousByteShort")

    # Promotional call to action duration
    promo_duration = 5.2
    content_duration = max(total_duration - promo_duration, 15.0)

    # 4 Content Scenes: Hook, Fact 1, Fact 2, Fact 3
    scene_keys = ["hook", "fact_1", "fact_2", "fact_3"]
    prompts = short_data.get("scene_prompts", {})

    default_prompts = {
        "hook": f"{short_data.get('category', 'cosmic')} mystery cinematic visual",
        "fact_1": f"{short_data['facts'][0][:60]} cinematic",
        "fact_2": f"{short_data['facts'][1][:60]} cinematic",
        "fact_3": f"{short_data['facts'][2][:60]} cinematic"
    }

    content_scene_durations = [
        content_duration * 0.24,
        content_duration * 0.26,
        content_duration * 0.25,
        content_duration * 0.25
    ]

    clip_paths = []
    print(f"\n[AIVisualizer] Creating animated script-matched scenes for '{short_data['title']}'...")

    # Render content scenes
    for i, key in enumerate(scene_keys):
        prompt_text = prompts.get(key, default_prompts[key])
        img_path = os.path.join(temp_dir, f"scene_{i}.jpg")
        clip_path = os.path.join(temp_dir, f"scene_{i}.mp4")

        if not os.path.exists(img_path):
            fetch_ai_image(prompt_text, img_path)

        zoom_in = (i % 2 == 0)
        print(f"  • Animating Scene {i+1}/5 ({content_scene_durations[i]:.1f}s, zoom_{'in' if zoom_in else 'out'})...")
        render_ken_burns_clip(img_path, content_scene_durations[i], clip_path, zoom_in=zoom_in)
        clip_paths.append(clip_path)

    # Render Promotional Outro Scene with Logo & CTA
    promo_clip_path = os.path.join(temp_dir, "scene_promo.mp4")
    print(f"  • Animating Scene 5/5: Channel Promotional Outro with Logo ({promo_duration:.1f}s)...")
    render_ken_burns_clip(promo_card_path, promo_duration + 0.6, promo_clip_path, zoom_in=True)
    clip_paths.append(promo_clip_path)

    # Concatenate all clips
    concat_list_file = os.path.join(temp_dir, "concat_list.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for p in clip_paths:
            f.write(f"file '{os.path.basename(p)}'\n")

    scenes_combined = os.path.join(temp_dir, "scenes_combined.mp4")
    concat_cmd = [
        ffmpeg_bin, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy",
        scenes_combined
    ]
    res_c = subprocess.run(concat_cmd, capture_output=True, text=True)
    if res_c.returncode != 0:
        raise RuntimeError(f"Concat failed: {res_c.stderr}")

    # Convert SRT to 1080x1920 ASS subtitles
    ass_path = os.path.join(temp_dir, f"{short_id}.ass")
    srt_to_ass(srt_path, ass_path)

    # Final Composition:
    # 1. Full-bleed clean cinematic visuals (No clunky top blue bars!)
    # 2. Synchronized audio
    # 3. High-visibility bold yellow ASS subtitles right in the sweet spot
    print(f"[AIVisualizer] Composing final YouTube Short with bold mobile-optimized subtitles...")
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)

    env = os.environ.copy()
    if os.path.exists(FONTS_CONF):
        env["FONTCONFIG_FILE"] = FONTS_CONF

    rel_ass = os.path.relpath(ass_path).replace("\\", "/")

    final_cmd = [
        ffmpeg_bin, "-y",
        "-i", scenes_combined,
        "-i", audio_path,
        "-vf", f"ass={rel_ass}",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_video_path
    ]

    res_f = subprocess.run(final_cmd, env=env, capture_output=True, text=True)
    if res_f.returncode != 0:
        raise RuntimeError(f"Final composition failed: {res_f.stderr}")

    final_size_mb = os.path.getsize(output_video_path) / (1024 * 1024)
    print(f"\n[AIVisualizer] 🎉 Professional Short Completed: {output_video_path} ({final_size_mb:.2f} MB)")
    return output_video_path
