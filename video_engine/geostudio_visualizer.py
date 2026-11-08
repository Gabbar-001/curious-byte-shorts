"""
GeoStudio Visualizer Engine (TheGeoCreates Style).
Implements:
1. High-velocity visual pacing: 8-12 micro-scenes per video (2.5 - 3.5s cuts)
2. Directional Ken Burns camera moves (zoom-in, zoom-out, pan-left, pan-right)
3. Word-by-word kinetic pop subtitles (Impact bold centered, yellow highlight on spoken word)
4. Audio mastering: narration + ducked ambient curiosity pad + whoosh transition SFX
5. Branded outro card with Curious Byte logo and CTA
"""

import os
import re
import sys
import json
import time
import subprocess
import requests
import urllib.parse
from PIL import Image, ImageDraw, ImageFont

from video_engine.ai_visualizer import get_ffmpeg, get_ffprobe, ensure_promo_card
from video_engine.sound_designer import build_sfx_track

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

def to_ass_time(sec: float) -> str:
    hrs = int(sec // 3600)
    mins = int((sec % 3600) // 60)
    secs = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100:
        cs = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"

def parse_srt_to_seconds(time_str: str) -> float:
    # 00:00:01,234
    time_str = time_str.replace(",", ".")
    parts = time_str.split(":")
    return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])

def generate_kinetic_ass(srt_path: str, ass_path: str) -> str:
    """
    Parses SRT subtitle timestamps and converts into rapid 2-3 word kinetic captions
    positioned in the center/lower-middle of the screen (TheGeoCreates / CapCut style).
    """
    with open(srt_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    srt_entries = []
    idx = 0
    while idx < len(lines):
        if lines[idx].isdigit():
            t_line = lines[idx+1]
            txt_parts = []
            idx += 2
            while idx < len(lines) and not lines[idx].isdigit():
                txt_parts.append(lines[idx])
                idx += 1
            if " --> " in t_line:
                s_str, e_str = t_line.split(" --> ")
                s_sec = parse_srt_to_seconds(s_str)
                e_sec = parse_srt_to_seconds(e_str)
                full_text = " ".join(txt_parts).replace("\n", " ").strip()
                if full_text:
                    srt_entries.append((s_sec, e_sec, full_text))
        else:
            idx += 1

    dialogues = []
    for s_sec, e_sec, text in srt_entries:
        words = text.split()
        if not words:
            continue
        
        # Split into small 2 to 3 word chunks for rapid kinetic flashing
        chunk_size = 2 if len(words) <= 6 else 3
        chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
        
        total_chars = sum(len(" ".join(c)) for c in chunks) or 1
        dur = max(0.4, e_sec - s_sec)
        
        curr_start = s_sec
        for c in chunks:
            c_text = " ".join(c).upper()
            c_weight = len(c_text) / total_chars
            c_dur = max(0.35, dur * c_weight)
            c_end = min(e_sec, curr_start + c_dur)
            
            # Word-level highlight inside the chunk
            sub_words = c_text.split()
            sub_dur = (c_end - curr_start) / len(sub_words)
            
            for w_idx in range(len(sub_words)):
                w_start = curr_start + (w_idx * sub_dur)
                w_end = curr_start + ((w_idx + 1) * sub_dur)
                
                # Active word gets bright yellow \c&H0000FFFF&, other words are pure white
                formatted = []
                for j, sw in enumerate(sub_words):
                    if j == w_idx:
                        formatted.append(f"{{\\c&H0000FFFF&}}{sw}")
                    else:
                        formatted.append(f"{{\\c&H00FFFFFF&}}{sw}")
                
                dialogue_text = " ".join(formatted)
                dialogues.append(f"Dialogue: 0,{to_ass_time(w_start)},{to_ass_time(w_end)},Kinetic,,0,0,0,,{dialogue_text}")
                
            curr_start = c_end

    header = """[Script Info]
Title: GeoStudio Kinetic Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kinetic,Impact,80,&H00FFFFFF,&H0000FFFF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,8,4,5,70,70,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    os.makedirs(os.path.dirname(ass_path), exist_ok=True)
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(dialogues))

    return ass_path

import urllib.request

def get_nasa_image(query: str) -> str:
    url = f"https://images-api.nasa.gov/search?q={urllib.parse.quote(query)}&media_type=image"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            items = data.get('collection', {}).get('items', [])
            for item in items[:3]:
                links = item.get('links', [])
                if links:
                    return links[0].get('href')
    except Exception:
        pass
    return None

def get_openverse_image(query: str) -> str:
    url = f"https://api.openverse.org/v1/images/?q={urllib.parse.quote(query)}&page_size=5"
    req = urllib.request.Request(url, headers={'User-Agent': 'CuriousByte/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            for res in data.get('results', []):
                u = res.get('url')
                if u and (u.endswith('.jpg') or u.endswith('.jpeg') or u.endswith('.png')):
                    return u
    except Exception:
        pass
    return None

def download_geo_image(prompt: str, output_path: str, width: int = 720, height: int = 1280, retries: int = 3) -> str:
    """Download photorealistic 3D, map, space or geographic visual from NASA, Openverse, or Pollinations."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Check if already successfully downloaded (>15KB)
    if os.path.exists(output_path) and os.path.getsize(output_path) > 15000:
        return output_path

    # 1. Try NASA Images API for cosmic, space, earth, planet, ocean
    url = None
    if any(k in prompt.lower() for k in ['space', 'earth', 'planet', 'pluto', 'iss', 'nasa', 'orbit', 'ocean', 'satellite']):
        print(f"[GeoStudio] Searching NASA Images API: {prompt[:45]}...")
        url = get_nasa_image(prompt)

    # 2. Try Openverse open catalog (800M+ CC/PD images)
    if not url:
        print(f"[GeoStudio] Searching Openverse visual catalog: {prompt[:45]}...")
        url = get_openverse_image(prompt)

    # 3. If URL found, download and format with PIL
    if url:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=12) as r:
                content = r.read()
                if len(content) > 10000:
                    with open(output_path, "wb") as f:
                        f.write(content)
                    # Convert to RGB JPEG format
                    img = Image.open(output_path).convert("RGB")
                    img.save(output_path, "JPEG", quality=92)
                    print(f"  ✓ Downloaded 3D realistic visual ({len(content)} bytes)")
                    return output_path
        except Exception as e:
            print(f"[GeoStudio] Download retry: {e}")

    # 4. Fallback to broad keyword search on Openverse
    words = [w for w in re.findall(r'\b[a-z]{3,}\b', prompt.lower()) if w not in {'photorealistic', 'cinematic', '8k', 'view', 'shot', 'macro'}]
    broad = " ".join(words[:2]) if words else "universe"
    url = get_openverse_image(broad)
    if url:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                content = r.read()
                if len(content) > 10000:
                    with open(output_path, "wb") as f:
                        f.write(content)
                    img = Image.open(output_path).convert("RGB")
                    img.save(output_path, "JPEG", quality=92)
                    return output_path
        except Exception:
            pass

    # 5. Guaranteed Fallback Canvas: Never let pipeline fail on missing visual
    if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
        canvas = Image.new("RGB", (1080, 1920), color=(14, 18, 28))
        draw = ImageDraw.Draw(canvas)
        for y in range(1920):
            ratio = y / 1920.0
            r = int(12 + 18 * (1 - abs(ratio - 0.5) * 2))
            g = int(16 + 24 * (1 - abs(ratio - 0.5) * 2))
            b = int(26 + 42 * (1 - abs(ratio - 0.5) * 2))
            draw.line([(0, y), (1080, y)], fill=(r, g, b))
        canvas.save(output_path, "JPEG", quality=92)

    return output_path

def render_dynamic_camera_clip(image_path: str, duration: float, output_path: str, motion_type: str = "zoom_in") -> str:
    """
    Renders dynamic Ken Burns camera motion with various camera directions:
    - zoom_in (1.0 -> 1.30)
    - zoom_out (1.30 -> 1.0)
    - pan_up / pan_down
    """
    ffmpeg_bin = get_ffmpeg()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fps = 25
    total_frames = int(duration * fps) + 5

    if motion_type == "zoom_in":
        zoom_expr = "min(pzoom+0.003,1.35)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif motion_type == "zoom_out":
        zoom_expr = "max(1.35-on*0.003,1.0)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif motion_type == "pan_left":
        zoom_expr = "1.25"
        x_expr = f"min(x+2, iw-iw/zoom)"
        y_expr = "ih/2-(ih/zoom/2)"
    else:  # pan_right
        zoom_expr = "1.25"
        x_expr = f"max(iw-iw/zoom-on*2, 0)"
        y_expr = "ih/2-(ih/zoom/2)"

    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={total_frames}:s=1080x1920:fps={fps},"
        f"setsar=1,format=yuv420p"
    )

    cmd = [
        ffmpeg_bin, "-y",
        "-loop", "1",
        "-i", image_path,
        "-vf", vf,
        "-t", f"{duration:.3f}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "22",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path

def ensure_ambient_audio(duration: float, output_path: str) -> str:
    """Synthesize subtle curiosity tension drone pad."""
    ffmpeg_bin = get_ffmpeg()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [
        ffmpeg_bin, "-y",
        "-f", "lavfi", "-i", f"anoisesrc=d={duration+5}:c=pink:r=44100:a=0.025,lowpass=f=320",
        "-f", "lavfi", "-i", f"sine=f=110:d={duration+5},volume=0.035",
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first[out]",
        "-map", "[out]",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path

def generate_geostudio_short(short_data: dict, audio_path: str, srt_path: str, output_video_path: str, channel_name: str = "CURIOUS BYTE") -> str:
    """
    Master GeoStudio Video Engine:
    1. Breaks down script into 9 to 12 micro-scenes (2.5s - 3.5s)
    2. Downloads high-res cinematic geography/space/nature visuals
    3. Animates with alternating directional Ken Burns camera moves
    4. Concat all micro-scenes with branded outro card
    5. Burns in center kinetic word-by-word yellow/white subtitles
    6. Masters audio: mixes voiceover + ducked ambient pad + transition whoosh SFX
    """
    ffmpeg_bin = get_ffmpeg()
    ffprobe_bin = get_ffprobe()
    
    # 1. Measure voice duration
    cmd = [ffprobe_bin, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    total_audio_duration = float(res.stdout.strip()) if res.stdout.strip() else 40.0
    
    short_id = short_data["id"]
    temp_dir = os.path.join(OUTPUT_DIR, "temp_geostudio", short_id)
    os.makedirs(temp_dir, exist_ok=True)

    # 2. Get scene prompt list
    scene_prompts = short_data.get("multi_scene_prompts", [])
    if not scene_prompts:
        # Fallback to standard prompts
        p = short_data.get("scene_prompts", {})
        scene_prompts = [
            p.get("hook", "3D Earth rotating in dark space"),
            p.get("scene_1", "satellite map view of continent"),
            p.get("scene_2", "extreme geographical anomaly landscape"),
            p.get("scene_3", "cosmic view from orbit"),
            p.get("outro", "ancient continental tectonic puzzle")
        ]

    # Calculate micro-scene durations (last 5.0s is reserved for promotional outro card)
    promo_duration = 5.2
    content_duration = max(10.0, total_audio_duration - promo_duration)
    scene_dur = content_duration / len(scene_prompts)

    print(f"\n[GeoStudio] Producing high-velocity Short: {len(scene_prompts)} micro-scenes ({scene_dur:.1f}s each) + Branded Outro...")

    # 3. Generate micro-scene clips
    scene_clips = []
    motions = ["zoom_in", "zoom_out", "pan_left", "pan_right"]

    for i, prompt in enumerate(scene_prompts):
        img_path = os.path.join(temp_dir, f"scene_{i}.jpg")
        clip_path = os.path.join(temp_dir, f"scene_{i}.mp4")
        
        download_geo_image(prompt, img_path, width=720, height=1280)
        motion = motions[i % len(motions)]
        print(f"  • Animating Micro-Scene {i+1}/{len(scene_prompts)} ({scene_dur:.1f}s, {motion})...")
        render_dynamic_camera_clip(img_path, scene_dur, clip_path, motion_type=motion)
        scene_clips.append(clip_path)

    # 4. Branded Promotional Outro Card
    print(f"  • Animating Scene {len(scene_prompts)+1}: Branded Neon Outro Card ({promo_duration:.1f}s)...")
    promo_card_path = ensure_promo_card(channel_name=channel_name)
    promo_clip_path = os.path.join(temp_dir, "scene_promo.mp4")
    render_dynamic_camera_clip(promo_card_path, promo_duration, promo_clip_path, motion_type="zoom_in")
    scene_clips.append(promo_clip_path)

    # 5. Concatenate video clips
    concat_list = os.path.join(temp_dir, "concat_list.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for clip in scene_clips:
            f.write(f"file '{os.path.basename(clip)}'\n")

    combined_video = os.path.join(temp_dir, "scenes_combined.mp4")
    cmd_concat = [
        ffmpeg_bin, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        combined_video
    ]
    subprocess.run(cmd_concat, cwd=temp_dir, capture_output=True, check=True)

    # 6. Generate Kinetic Word-by-Word Subtitles
    ass_path = os.path.join(temp_dir, f"{short_id}_kinetic.ass")
    generate_kinetic_ass(srt_path, ass_path)

    # 7. Synthesize ambient curiosity pad & transition whoosh SFX track
    ambient_audio_path = os.path.join(temp_dir, "ambient_pad.mp3")
    ensure_ambient_audio(total_audio_duration, ambient_audio_path)

    cut_timestamps = [target_dur * (i + 1) for i in range(len(scene_prompts))]
    sfx_audio_path = os.path.join(temp_dir, "transition_whoosh_sfx.mp3")
    build_sfx_track(cut_timestamps, total_audio_duration, sfx_audio_path)

    # 8. Master audio (3-way Hollywood audio mix) & burn kinetic subtitles
    print("[GeoStudio] Mastering 3-way audio (narration + ambient pad + transition whoosh SFX) & burning kinetic pop subtitles...")
    
    env = os.environ.copy()
    fonts_conf = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "fonts.conf"))
    env["FONTCONFIG_FILE"] = fonts_conf

    ass_arg = os.path.abspath(ass_path).replace("\\", "/")
    if len(ass_arg) > 2 and ass_arg[1] == ":":
        ass_arg = ass_arg[0] + "\\:" + ass_arg[2:]

    # Audio mixing: Voiceover at 1.0 volume, ambient pad at 0.14 volume, transition whooshes at 0.35 volume
    audio_filter = "[1:a]volume=1.0[v_voice];[2:a]volume=0.14[v_bg];[3:a]volume=0.35[v_sfx];[v_voice][v_bg][v_sfx]amix=inputs=3:duration=first[aout]"
    video_filter = f"subtitles='{ass_arg}'"

    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
    cmd_master = [
        ffmpeg_bin, "-y",
        "-i", combined_video,
        "-i", audio_path,
        "-i", ambient_audio_path,
        "-i", sfx_audio_path,
        "-filter_complex", f"[0:v]{video_filter}[vout];{audio_filter}",
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{total_audio_duration:.3f}",
        output_video_path
    ]

    subprocess.run(cmd_master, env=env, capture_output=True, check=True)
    size_mb = os.path.getsize(output_video_path) / (1024 * 1024)
    print(f"\n[GeoStudio] 🎉 Studio Short Successfully Rendered: {output_video_path} ({size_mb:.2f} MB)")
    return output_video_path
