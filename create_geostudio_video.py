"""
Creates a high-retention Short in TheGeoCreates animation style:
- Fast 2.5s-3.5s micro-scene pacing (9 dynamic visual cuts)
- Center-screen kinetic word-by-word pop subtitles (active word glowing yellow)
- Ambient curiosity tension background pad ducked behind voiceover
- Branded outro card with Curious Byte logo and CTA
- Automated 16:9 thumbnail & 9:16 vertical cover generation
"""

import os
import sys
import json
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from generator.voice_synthesizer import synthesize_short
from generator.thumbnail_generator import generate_short_thumbnails
from video_engine.geostudio_visualizer import generate_geostudio_short

def create_geostudio_video():
    date_str = datetime.now().strftime("%Y-%m-%d")
    short_id = "geo_secrets_001"
    
    promo_cta = "Please subscribe, like, and share Curious Byte for more mind-blowing facts like this!"
    
    script_text = (
        "You think you know planet Earth? These 3 facts will completely break your sense of reality. "
        "First: Russia has a larger surface area than the entire dwarf planet Pluto! If you flattened Pluto, Russia would swallow it whole. "
        "Second: Point Nemo in the Pacific Ocean is so remote, the closest humans to you are astronauts aboard the International Space Station passing overhead. "
        "Third: Mount Kilimanjaro sits right on the scorching equator in Africa, yet its summit is permanently covered in freezing glaciers! "
        "Our world is far stranger than you ever imagined. "
        f"{promo_cta}"
    )

    short_data = {
        "id": short_id,
        "category": "World Secrets",
        "date_created": date_str,
        "title": "Mind-Blowing Earth Secrets You Had NO Idea Existed! 🌍 #Shorts",
        "description": (
            "Did you know Russia is bigger than the entire planet Pluto? Or that the closest humans to Point Nemo are in outer space?\n\n"
            "Subscribe to Curious Byte for your daily dose of mind-bending facts!\n\n"
            "#Shorts #CuriousByte #WorldFacts #Geography #ScienceFacts #MindBlowing"
        ),
        "tags": ["Shorts", "CuriousByte", "WorldFacts", "Geography", "EarthSecrets", "ScienceFacts"],
        "keywords": ["earth facts", "geography secrets", "pluto vs russia", "point nemo", "kilimanjaro"],
        "hook": "You think you know planet Earth? These 3 facts will completely break your sense of reality.",
        "voiceover_text": script_text,
        "multi_scene_prompts": [
            "3D photorealistic planet Earth spinning slowly in dark cosmos with glowing blue atmosphere",
            "holographic digital world map with continental borders glowing neon cyan",
            "satellite map of vast Russian landmass spanning from Eastern Europe across Siberian taiga to Pacific",
            "frozen icy alien surface of dwarf planet Pluto side by side with continent scale comparison",
            "satellite targeting reticle zooming deep into the empty vast South Pacific Ocean at Point Nemo",
            "International Space Station cupola window with astronaut looking down at curved blue Earth horizon",
            "blazing hot scorched African savannah landscape with intense solar heat haze and acacia trees",
            "majestic snow-capped glacial summit of Mount Kilimanjaro with massive blue ice walls",
            "ancient supercontinent Pangea with South America and Africa coastlines fitting together like puzzle pieces"
        ]
    }

    print("\n" + "="*65)
    print("  CREATING THEGEOCREATES-STYLE ANIMATED SHORT 🌍")
    print(f"  Title: {short_data['title']}")
    print("="*65)

    # 1. Voiceover & Subtitles
    print("\n[1/4] Synthesizing voiceover & subtitle timestamps...")
    audio_assets = synthesize_short(short_data, voice="en-US-ChristopherNeural", rate="+5%")
    print(f"  • Audio : {audio_assets['audio_path']}")
    print(f"  • Subs  : {audio_assets['sub_path']}")

    # 2. Render Video with GeoStudio Engine
    output_video_path = os.path.join("output", "videos", f"{date_str}_{short_id}.mp4")
    print("\n[2/4] Rendering 9-scene dynamic camera cuts, kinetic pop subtitles & ambient mix...")
    rendered_path = generate_geostudio_short(
        short_data=short_data,
        audio_path=audio_assets["audio_path"],
        srt_path=audio_assets["sub_path"],
        output_video_path=output_video_path,
        channel_name="CURIOUS BYTE"
    )

    # 3. Generate Thumbnails (16:9 & 9:16)
    print("\n[3/4] Generating high-CTR YouTube thumbnail & vertical cover...")
    thumbs = generate_short_thumbnails(short_data, video_path=rendered_path, date_str=date_str)
    print(f"  • 16:9 Thumbnail : {thumbs['horizontal_16x9']}")
    print(f"  • 9:16 Cover     : {thumbs['vertical_9x16']}")

    print("\n" + "="*65)
    print("  🎉 ANIMATED SHORT COMPLETED SUCCESSFULLY!")
    print(f"  Video Path : {os.path.abspath(rendered_path)}")
    print(f"  Thumbnail  : {os.path.abspath(thumbs['horizontal_16x9'])}")
    print("="*65 + "\n")

    return {
        "video_path": rendered_path,
        "thumbnails": thumbs
    }

if __name__ == "__main__":
    create_geostudio_video()
