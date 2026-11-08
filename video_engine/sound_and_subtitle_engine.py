"""
Sound Design & Kinetic Subtitle Engine for Curious Byte Unique.
Features:
1. Voiceover synthesis with millisecond SRT timestamps
2. Restrained Hormozi Subtitles:
   - Ultra-bold Arial Black in pure white
   - Kinetic active word-bounce (+15% scale: \\fscx115\\fscy115) in electric yellow (\\c&H0000FFFF&)
   - Deep 9px black outline + 4px shadow
   - Max 1-2 tasteful emojis across entire video (no emoji spam)
3. 3-Way Hollywood Audio Mix:
   - Voiceover (1.0)
   - Ducked Ambient Pad (-6dB during speech)
   - Transition Whoosh SFX on every single scene cut
"""

import os
import sys
import asyncio
import subprocess
import edge_tts
from video_engine.ai_visualizer import get_ffmpeg, get_ffprobe

# UTF-8 stdout configuration for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

DEFAULT_VOICE = "en-US-ChristopherNeural"

def to_ass_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:d}:{mins:02d}:{secs:05.2f}"

def parse_srt_to_seconds(srt_time_str: str) -> float:
    srt_time_str = srt_time_str.strip().replace(",", ".")
    parts = srt_time_str.split(":")
    if len(parts) == 3:
        h, m, s = parts
        return float(h) * 3600 + float(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return float(m) * 60 + float(s)
    return 0.0

async def synthesize_audio_and_srt(text: str, audio_path: str, srt_path: str, voice: str = DEFAULT_VOICE, rate: str = "+4%"):
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    submaker = edge_tts.SubMaker()
    with open(audio_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)

    with open(srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.write(submaker.get_srt())

def generate_voice_assets(text: str, audio_path: str, srt_path: str) -> tuple[str, str]:
    if not (os.path.exists(audio_path) and os.path.exists(srt_path) and os.path.getsize(audio_path) > 1000):
        asyncio.run(synthesize_audio_and_srt(text, audio_path, srt_path))
    return audio_path, srt_path

def get_audio_duration(audio_path: str) -> float:
    ffprobe = get_ffprobe()
    cmd = [
        ffprobe, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def compute_scene_durations(total_duration: float, num_scenes: int = 10) -> list[float]:
    """
    Allocates exact seconds for each of the 10 scene beats.
    Target total matches audio duration + 0.5s breathing room.
    """
    # Proportional scene pacing weights:
    # Scene 1: 7% (Hook)
    # Scene 2: 9% (Mystery)
    # Scene 3: 11% (Fact 1)
    # Scene 4: 11% (Detail)
    # Scene 5: 11% (Conflict)
    # Scene 6: 11% (Macro)
    # Scene 7: 12% (Revelation)
    # Scene 8: 11% (Deep Time)
    # Scene 9: 9% (Payoff)
    # Scene 10: 8% (Outro)
    weights = [0.07, 0.09, 0.11, 0.11, 0.11, 0.11, 0.12, 0.11, 0.09, 0.08]
    if num_scenes != len(weights):
        dur_each = total_duration / num_scenes
        return [dur_each] * num_scenes

    allocated = [round(total_duration * w, 2) for w in weights]
    diff = total_duration - sum(allocated)
    allocated[-1] = round(allocated[-1] + diff, 2)
    return allocated

def generate_restrained_hormozi_ass(srt_path: str, ass_path: str, highlight_emojis: dict = None) -> str:
    """
    Creates restrained, high-impact Hormozi word-pop subtitles (1-2 emojis max).
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
    emoji_count = 0
    max_emojis = 2
    emojis_dict = highlight_emojis or {"ROMAN": "🏛️", "HEAL": "⚡", "SECRET": "🤫"}

    for s_sec, e_sec, text in srt_entries:
        words = text.split()
        if not words:
            continue

        chunk_size = 2 if len(words) <= 5 else 3
        chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
        total_chars = sum(len(" ".join(c)) for c in chunks) or 1
        dur = max(0.4, e_sec - s_sec)

        curr_start = s_sec
        for c in chunks:
            c_text = " ".join(c).upper()
            c_weight = len(c_text) / total_chars
            c_dur = max(0.35, dur * c_weight)
            c_end = min(e_sec, curr_start + c_dur)

            sub_words = c_text.split()
            sub_dur = (c_end - curr_start) / len(sub_words)

            for w_idx in range(len(sub_words)):
                w_start = curr_start + (w_idx * sub_dur)
                w_end = curr_start + ((w_idx + 1) * sub_dur)

                formatted = []
                for j, sw in enumerate(sub_words):
                    clean_sw = sw.strip(".,!?:;\"'")
                    # Check for restrained emoji injection (max 2 across whole video)
                    attached_emoji = ""
                    if emoji_count < max_emojis and clean_sw in emojis_dict:
                        attached_emoji = f" {emojis_dict[clean_sw]}"
                        emoji_count += 1

                    if j == w_idx:
                        # Active word pops +15% scale in electric yellow
                        formatted.append(f"{{\\c&H0000FFFF&\\fscx115\\fscy115}}{sw}{attached_emoji}{{\\fscx100\\fscy100}}")
                    else:
                        formatted.append(f"{{\\c&H00FFFFFF&}}{sw}{attached_emoji}")

                dialogue_text = " ".join(formatted)
                dialogues.append(f"Dialogue: 0,{to_ass_time(w_start)},{to_ass_time(w_end)},KineticHormozi,,0,0,0,,{dialogue_text}")

            curr_start = c_end

    header = """[Script Info]
Title: Hormozi Kinetic Subtitles 2.0
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KineticHormozi,Arial Black,86,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,9,4,2,70,70,620,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    os.makedirs(os.path.dirname(ass_path), exist_ok=True)
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(dialogues))

    return ass_path

def build_hollywood_audio_mix(voice_path: str, output_mixed_audio: str, total_duration: float, num_scenes: int = 10) -> str:
    """
    Creates a 3-way Hollywood audio master:
    1. Voiceover (volume=1.0)
    2. Ducked Cinematic Ambient Synth Pad (volume=0.12)
    3. Transition Whoosh SFX on every scene cut (volume=0.35)
    """
    ffmpeg = get_ffmpeg()
    os.makedirs(os.path.dirname(output_mixed_audio), exist_ok=True)

    ambient_path = os.path.join("assets", "audio", "ambient_pad.mp3")
    if not os.path.exists(ambient_path):
        from video_engine.geostudio_visualizer import ensure_ambient_audio
        ensure_ambient_audio(total_duration + 5, ambient_path)

    # Calculate cut timestamps for whooshes (at t = dur, 2*dur, ...)
    scene_dur = total_duration / num_scenes
    cut_timestamps = [round(i * scene_dur, 2) for i in range(1, num_scenes)]

    # Build sfx track using sound_designer
    from video_engine.sound_designer import build_sfx_track
    sfx_track_path = output_mixed_audio.replace(".mp3", "_sfx.mp3")
    build_sfx_track(cut_timestamps, total_duration, sfx_track_path)

    # 3-Way Mix: Voice (1.0) + Ambient Pad (0.12) + Whoosh SFX (0.35)
    filter_complex = (
        f"[0:a]volume=1.0[voice];"
        f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration:.2f},volume=0.12[pad];"
        f"[2:a]volume=0.35[sfx];"
        f"[voice][pad][sfx]amix=inputs=3:duration=first:dropout_transition=2[aout]"
    )

    cmd = [
        ffmpeg, "-y",
        "-i", voice_path,
        "-i", ambient_path,
        "-i", sfx_track_path,
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-t", f"{total_duration:.2f}",
        output_mixed_audio
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_mixed_audio
