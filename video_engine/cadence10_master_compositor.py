"""
Master Compositor for Cadence-10 Shorts (Pipeline 2.0).
Coordinates the entire end-to-end rendering:
1. Synthesizes 8-10 stylized 3D CGI frames (Visual Director)
2. Animates each frame into 60fps dynamic motion with Double-Check Gate (Kinetic Animator)
3. Synthesizes voiceover & computes exact beat timings
4. Assembles 3-way Hollywood audio mix (Voice + Ambient + Whooshes on every cut)
5. Overlays restrained Hormozi yellow/white word-pop subtitles (max 1-2 emojis)
6. Outputs mastered 1080x1920 60fps MP4
"""

import os
import sys
import subprocess
from video_engine.ai_visualizer import get_ffmpeg
from video_engine.ai_visual_director import synthesize_scene_visuals
from video_engine.kinetic_animator_and_validator import animate_all_scenes
from video_engine.sound_and_subtitle_engine import (
    generate_voice_assets, get_audio_duration, compute_scene_durations,
    generate_restrained_hormozi_ass, build_hollywood_audio_mix
)

# UTF-8 stdout configuration for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def render_cadence10_short(concept_data: dict, output_video_path: str, channel_name: str = "CURIOUS BYTE") -> str:
    """
    Renders a complete Pipeline 2.0 Short with 8 to 10 matched scenes.
    """
    short_id = concept_data["id"]
    date_str = concept_data.get("date_created", "2026-11-07")
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
    ffmpeg = get_ffmpeg()

    print("\n" + "=" * 70)
    print(f"  🎬 RENDERING PIPELINE 2.0 SHORT (CADENCE-10): {concept_data['title']}")
    print(f"  • Viral Score : {concept_data.get('viral_score')}/100")
    print(f"  • Story Beats : {len(concept_data.get('story_beats', []))} Scenes")
    print(f"  • Quality Gate: Active Double-Check on all clips")
    print("=" * 70)

    # 1. Voiceover & Subtitles
    voice_path = os.path.join("output", "audio", f"{date_str}_{short_id}.mp3")
    srt_path = os.path.join("output", "audio", f"{date_str}_{short_id}.srt")
    ass_path = os.path.join("output", "audio", f"{date_str}_{short_id}.ass")

    print("\n[Step 1/5] Synthesizing Voiceover & Narrative Beat Durations...")
    generate_voice_assets(concept_data["full_voiceover_script"], voice_path, srt_path)
    total_audio_dur = get_audio_duration(voice_path)
    total_video_dur = total_audio_dur + 0.4  # Slight breathing room

    story_beats = concept_data.get("story_beats", [])
    num_scenes = len(story_beats)
    beat_durations = compute_scene_durations(total_video_dur, num_scenes)
    print(f"  ✓ Total Duration: {total_video_dur:.2f}s across {num_scenes} visual scenes")

    # 2. Visual Synthesis (8-10 scenes, 100% No Faces, No Text)
    print("\n[Step 2/5] Synthesizing 100% Stylized 3D CGI Scene Frames...")
    topic = concept_data.get("topic", "")
    scene_images = synthesize_scene_visuals(story_beats, short_id, topic=topic)

    # 3. Kinetic Animation & Double-Check Quality Gate
    print("\n[Step 3/5] Producing 60fps Dynamic Motion Clips with Double-Check Gate...")
    scene_clips = animate_all_scenes(scene_images, beat_durations, short_id)

    # 4. Hollywood Audio Mix & Hormozi Subtitles
    print("\n[Step 4/5] Mastering 3-Way Hollywood Audio & Hormozi Kinetic Subtitles...")
    mixed_audio = os.path.join("output", "audio", f"{date_str}_{short_id}_hollywood_mix.mp3")
    build_hollywood_audio_mix(voice_path, mixed_audio, total_video_dur, num_scenes=num_scenes)

    highlight_emojis = concept_data.get("highlight_emojis", {})
    generate_restrained_hormozi_ass(srt_path, ass_path, highlight_emojis=highlight_emojis)

    # 5. Master Video Assembly (Concatenate clips + Subtitles + Audio)
    print("\n[Step 5/5] Final Mastering: 1080x1920 60fps Video Assembly...")
    concat_txt_path = os.path.join("output", "temp_clips", short_id, "concat_list.txt")
    with open(concat_txt_path, "w", encoding="utf-8") as f:
        for clip in scene_clips:
            clean_path = os.path.abspath(clip).replace("\\", "/")
            f.write(f"file '{clean_path}'\n")

    # Use relative paths with forward slashes to avoid Windows drive-letter colon syntax issues in FFmpeg
    clean_ass = os.path.relpath(ass_path).replace("\\", "/")
    clean_concat = os.path.relpath(concat_txt_path).replace("\\", "/")

    cmd = [
        ffmpeg, "-y",
        "-f", "concat", "-safe", "0", "-i", clean_concat,
        "-i", mixed_audio,
        "-vf", f"ass={clean_ass}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-threads", "0",
        "-c:a", "aac", "-b:a", "192k",
        "-r", "60",
        "-shortest",
        output_video_path
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)
    vid_size_mb = os.path.getsize(output_video_path) / (1024 * 1024)
    print(f"\n🎉 Short Successfully Rendered: {output_video_path} ({vid_size_mb:.2f} MB)")
    return output_video_path
