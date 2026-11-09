"""
Batch Generator for 10 High-Quality True3D YouTube Shorts.
For user review and verification:
- ZERO uploading (preview and verification only).
- Diverse multi-domain facts: Weird Science, Creepy Psychology, Zombie Parasites, Quantum Paradoxes,
  Gates of Hell, Ancient History, Lost Inventions, Brain Glitches, Animal Superpowers, Time Dilation.
- True3D high quality dynamic animations matching each specific fact.
- 3-Way Hollywood audio mix (Voiceover + Ambient Pad + Transition Whoosh SFX).
- Kinetic yellow/white pop subtitles.
- 16:9 & 9:16 Thumbnails.
- Preview frame extraction for artifact showcase.
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# UTF-8 stdout configuration for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from generator.facts_library import FACTS_DATABASE
from generator.script_generator import derive_enhancements
from generator.voice_synthesizer import synthesize_short
from generator.thumbnail_generator import generate_short_thumbnails
from video_engine.true3d_engine import render_true3d_short
from video_engine.ai_visualizer import get_ffmpeg

TARGET_FACT_IDS = [
    'science_weird_001',  # Kola Superdeep Borehole
    'psych_weird_001',    # Walking Corpse Syndrome (Cotard's Delusion)
    'nature_weird_001',   # Zombie Ant Cordyceps Fungus
    'physics_weird_001',  # Double Slit Quantum Paradox
    'earth_weird_001',    # Gates of Hell 50-Year Fire Crater
    'history_001',        # Mind-Bending Timelines (Cleopatra/Pyramids/Aztecs)
    'history_002',        # Ancient Roman Concrete & Pantheon
    'psych_001',          # Mandela Effect & Brain Glitches
    'nature_001',         # Real Animal Superpowers (Immortal Jellyfish, Tardigrade)
    'physics_001'         # Gravitational Time Dilation (Head ages faster than feet)
]

def prepare_fact_data(fact_item: dict, date_str: str = "2026-11-07") -> dict:
    hook_a, hook_b, debate_question = derive_enhancements(fact_item)
    active_variant = "B" if "B" in fact_item.get("id", "") or "weird" in fact_item.get("id", "") else "A"
    active_hook = hook_b if active_variant == "B" else hook_a
    promo_cta = "Hit subscribe to Curious Byte right now so you don't miss tomorrow's mystery, and drop a like if your mind was blown!"

    facts = fact_item["facts"]
    script_text = (
        f"{active_hook} ... "
        f"First: {facts[0]} ... "
        f"Second: {facts[1]} ... "
        f"Third: {facts[2]} ... "
        f"{fact_item['loop_outro']} ... "
        f"{promo_cta}"
    )

    from generator.ai_viral_intelligence import build_ultimate_viral_hashtags
    all_hashtags = build_ultimate_viral_hashtags(
        title=fact_item["title"],
        script=f"{fact_item.get('description', '')} {full_script}",
        topic=fact_item.get("topic", fact_item["title"]),
        max_tags=38
    )
    hashtag_line = " ".join(all_hashtags)

    enhanced_description = (
        f"💬 QUESTION OF THE DAY:\n{debate_question}\n"
        f"👇 Drop your opinion below! We reply to the top comments!\n\n"
        f"{fact_item.get('description', '')}\n\n"
        f"🔴 HIT SUBSCRIBE to Curious Byte for daily mind-blowing facts:\n"
        f"https://www.youtube.com/@CuriousByteShort?sub_confirmation=1\n\n"
        f"{hashtag_line}"
    )

    short_data = {
        "id": fact_item["id"],
        "category": fact_item["category"],
        "date_created": date_str,
        "title": fact_item["title"],
        "description": enhanced_description,
        "tags": fact_item.get("tags", []),
        "keywords": fact_item.get("keywords", []),
        "hook": active_hook,
        "hook_a": hook_a,
        "hook_b": hook_b,
        "active_hook_variant": active_variant,
        "debate_question": debate_question,
        "facts": facts,
        "loop_outro": fact_item["loop_outro"],
        "promo_cta": promo_cta,
        "scene_prompts": fact_item.get("scene_prompts", {}),
        "voiceover_text": script_text
    }

    # Save metadata JSON
    meta_path = os.path.join("output", "metadata", f"{date_str}_{fact_item['id']}.json")
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(short_data, f, indent=2)

    return short_data

def extract_preview_frames(video_path: str, short_id: str, artifact_dir: str):
    """Extracts 3 preview frames for visual verification."""
    ffmpeg = get_ffmpeg()
    os.makedirs(artifact_dir, exist_ok=True)
    
    # Extract at 3s (Hook), 15s (Fact 1), and 25s (Fact 2)
    timestamps = [(3.0, "hook"), (15.0, "fact1"), (25.0, "fact2")]
    extracted = []
    for ts, label in timestamps:
        out_name = f"preview_{short_id}_{label}.jpg"
        out_file = os.path.join(artifact_dir, out_name)
        cmd = [
            ffmpeg, "-y", "-ss", str(ts), "-i", video_path,
            "-vframes", "1", "-q:v", "2", out_file
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
                extracted.append(out_name)
        except Exception as e:
            print(f"    Frame extract error ({label}): {e}")
    return extracted

def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    channel_name = "CURIOUS BYTE"
    artifact_dir = r"C:\Users\mr_un\.gemini\antigravity\brain\31dbdc28-6e65-4aea-b4ff-10347b1bb1c0"

    print("=" * 75)
    print("  🚀 CURIOUS BYTE UNIQUE — 10 SHORTS BATCH GENERATION (REVIEW MODE)")
    print("  • Mode: Generation Only (NO UPLOADING)")
    print("  • Total Target Shorts: 10")
    print("  • Video Engine: True3D Dynamic 1080x1920 60fps")
    print("  • Audio: 3-Way Hollywood Mix (Voiceover + Ambient Pad + Whoosh SFX)")
    print("  • Verification: Preview frame extraction for inspection")
    print("=" * 75 + "\n")

    results = []

    for idx, fid in enumerate(TARGET_FACT_IDS, start=1):
        print(f"\n[{idx}/10] ========================================================")
        item = next((f for f in FACTS_DATABASE if f["id"] == fid), None)
        if not item:
            print(f"  ❌ Error: Fact ID '{fid}' not found in database!")
            continue

        print(f"  📌 ID       : {fid}")
        print(f"  🏷️  Category : {item['category']}")
        print(f"  🎬 Title    : {item['title']}")

        # 1. Prepare Script & Metadata
        short_data = prepare_fact_data(item, date_str)
        print(f"  ⚡ Hook     : \"{short_data['hook']}\"")
        print(f"  💬 Debate Q : \"{short_data['debate_question']}\"")

        # 2. Voiceover & Millisecond Subtitles
        audio_path = os.path.join("output", "audio", f"{date_str}_{fid}.mp3")
        srt_path = os.path.join("output", "audio", f"{date_str}_{fid}.srt")

        if not (os.path.exists(audio_path) and os.path.exists(srt_path)):
            print("  🎙️ Synthesizing Neural Speech & Timestamps...")
            audio_assets = synthesize_short(short_data)
            audio_path = audio_assets["audio_path"]
            srt_path = audio_assets["sub_path"]
        else:
            print(f"  ✓ Reusing existing audio: {audio_path}")

        # 3. Render High Quality True3D Video
        output_video_path = os.path.join("output", "videos", f"{date_str}_{fid}.mp4")
        print(f"  🎥 Rendering True3D 60fps Short: {output_video_path}...")
        
        try:
            rendered_video = render_true3d_short(
                short_data=short_data,
                audio_path=audio_path,
                srt_path=srt_path,
                output_video_path=output_video_path,
                channel_name=channel_name
            )
            vid_size_mb = os.path.getsize(rendered_video) / (1024 * 1024)
            print(f"  ✅ Video Rendered: {vid_size_mb:.2f} MB")

            # 4. Generate Thumbnails
            print("  🎨 Generating 16:9 Thumbnail & 9:16 Shorts Cover...")
            thumbs = generate_short_thumbnails(short_data, rendered_video)
            print(f"  ✓ Thumbnails: {thumbs.get('horizontal_16x9')}")

            # 5. Extract Preview Frames
            print("  📸 Extracting Preview Frames for Review...")
            frames = extract_preview_frames(rendered_video, fid, artifact_dir)
            print(f"  ✓ Extracted {len(frames)} preview frames: {frames}")

            results.append({
                "id": fid,
                "title": short_data["title"],
                "category": short_data["category"],
                "video_path": rendered_video,
                "size_mb": round(vid_size_mb, 2),
                "thumbnails": thumbs,
                "preview_frames": frames,
                "status": "SUCCESS"
            })
        except Exception as e:
            print(f"  ❌ Render failed for {fid}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "id": fid,
                "title": short_data["title"],
                "category": short_data["category"],
                "status": f"FAILED: {e}"
            })

    print("\n" + "=" * 75)
    print("  🎉 10 SHORTS BATCH GENERATION COMPLETE!")
    print(f"  Total Success: {sum(1 for r in results if r['status'] == 'SUCCESS')} / {len(TARGET_FACT_IDS)}")
    print("=" * 75)

    # Save batch summary
    summary_path = os.path.join("output", "metadata", f"{date_str}_batch_10_review.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Summary saved: {summary_path}")

if __name__ == "__main__":
    main()
