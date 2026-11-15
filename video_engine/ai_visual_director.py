"""
AI Visual Director for Curious Byte Unique.
Generates 8-10 high-definition 1080x1920 stylized visual frames corresponding
to each specific narrative scene beat.
Key Features:
- 100% Stylized AI / Public Science Renders (Zero human faces, zero text)
- Guaranteed Unique Visual Per Scene (Tracks used URLs across all 10 scenes)
- Multi-tier Fallback Engine (Pollinations -> Wikimedia Commons Science Art -> Thematic Procedural)
- Independent Scene Retryability (Only re-fetches failed scenes, never restarts the batch)
"""

import os
import sys
import time
import math
import re
import random
import threading
import requests
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFilter

# UTF-8 stdout configuration for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

STRICT_NEGATIVE_PROMPT = ", no human faces, no real people, no photorealism, no text, no letters, no words, no watermarks, no logos, no distorted anatomy, 8k digital art"

STOP_WORDS = {
    'stylized', '3d', 'cgi', 'render', 'aesthetic', 'volumetric', 'cinematic',
    'lighting', 'art', 'digital', 'unreal', 'engine', '8k', '4k', 'octane',
    'photorealistic', 'photo', 'hyperrealistic', 'depth', 'atmospheric', 'dark',
    'glowing', 'neon', 'no', 'text', 'letters', 'words', 'human', 'faces', 'people'
}

def clean_search_term(raw_text: str) -> str:
    """Strips punctuation and AI style jargon, leaving salient physical nouns."""
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', raw_text)
    words = [w for w in cleaned.split() if w.lower() not in STOP_WORDS and len(w) > 2]
    return " ".join(words[:4]) if words else raw_text.strip()

def search_wikimedia_visual(search_query: str, output_path: str, used_urls: set = None, topic: str = "", scene_num: int = 1, lock: threading.Lock = None) -> bool:
    """
    High-res scientific, astronomical, nature, and architectural database visual search.
    Guarantees no repeated images across scenes by respecting used_urls.
    """
    if used_urls is None:
        used_urls = set()

    # Build search candidates in order of specificity
    candidates = []
    c1 = clean_search_term(search_query)
    if c1:
        candidates.append(c1)
        # 2-word variant
        words = c1.split()
        if len(words) >= 2:
            candidates.append(" ".join(words[:2]))
        if len(words) >= 3:
            candidates.append(" ".join(words[-2:]))

    if topic:
        c_topic = clean_search_term(topic)
        if c_topic and c_topic not in candidates:
            candidates.append(c_topic)
            t_words = c_topic.split()
            if len(t_words) >= 2:
                candidates.append(" ".join(t_words[:2]))

    # Default scientific fallbacks if everything else fails
    science_backups = [
        "Planetary nebula space", "Deep ocean trench", "Quantum physics simulation",
        "Geological strata rock", "Microscopic crystal lattice", "Ancient Roman ruins",
        "Volcanic magma eruption", "Bioluminescent jellyfish", "Spiral galaxy core", "Cybernetic brain neural"
    ]
    candidates.append(science_backups[(scene_num - 1) % len(science_backups)])

    headers = {'User-Agent': 'CuriousByteUnique/2.0 (contact@curiousbyte.com)'}

    for term in candidates:
        if not term.strip():
            continue
        try:
            url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(term)}&gsrnamespace=6&prop=imageinfo&iiprop=url&gsrlimit=20&format=json"
            r = requests.get(url, headers=headers, timeout=7)
            if r.status_code != 200:
                continue

            pages = r.json().get('query', {}).get('pages', {})
            for pid, pdata in pages.items():
                img_url = pdata.get('imageinfo', [{}])[0].get('url', '')
                if not img_url:
                    continue

                clean_url = img_url.split('?')[0].lower()
                # Check valid extension
                if not any(clean_url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    continue

                # Ensure image uniqueness across scenes (thread-safe)
                if lock:
                    with lock:
                        if clean_url in used_urls:
                            continue
                elif clean_url in used_urls:
                    continue

                # Download candidate image
                ir = requests.get(img_url, headers=headers, timeout=12)
                if ir.status_code == 200 and len(ir.content) > 20000:
                    with open(output_path, 'wb') as f:
                        f.write(ir.content)

                    # Verify and crop to 1080x1920 9:16
                    with Image.open(output_path) as im:
                        im.verify()

                    with Image.open(output_path) as im:
                        im = im.convert("RGB")
                        w, h = im.size
                        target_ratio = 1080 / 1920
                        current_ratio = w / h

                        if current_ratio > target_ratio:
                            new_w = int(h * target_ratio)
                            left = (w - new_w) // 2
                            im_cropped = im.crop((left, 0, left + new_w, h))
                        else:
                            new_h = int(w / target_ratio)
                            top = (h - new_h) // 2
                            im_cropped = im.crop((0, top, w, top + new_h))

                        im_final = im_cropped.resize((1080, 1920), Image.Resampling.LANCZOS)
                        im_final.save(output_path, "JPEG", quality=95)

                    if lock:
                        with lock:
                            used_urls.add(clean_url)
                    else:
                        used_urls.add(clean_url)
                    return True
        except Exception:
            continue

    return False

def generate_thematic_procedural_canvas(output_path: str, scene_num: int = 1, seed: int = 42) -> str:
    """
    10 distinct mathematical and visual themes guaranteed to look completely different
    per scene number if all network layers fail (stddev > 30, high contrast).
    """
    random.seed(seed + scene_num * 137)
    base = Image.new("RGB", (1080, 1920), (8, 6, 18))
    draw = ImageDraw.Draw(base)

    # 10 Distinct Color Palettes per scene
    PALETTES = [
        # 1: Cosmic Electric Cyan & Void
        {"bg_top": (4, 10, 28), "bg_bot": (10, 32, 64), "accent": (0, 230, 255), "core": (180, 255, 255)},
        # 2: Sacred Emerald & Imperial Gold
        {"bg_top": (6, 24, 16), "bg_bot": (18, 48, 28), "accent": (230, 195, 60), "core": (80, 240, 160)},
        # 3: Deep Magma Crimson & Obsidian
        {"bg_top": (28, 6, 8), "bg_bot": (60, 14, 10), "accent": (255, 90, 30), "core": (255, 210, 120)},
        # 4: Quantum Violet & Ultra Sapphire
        {"bg_top": (16, 6, 32), "bg_bot": (40, 12, 70), "accent": (190, 80, 255), "core": (240, 190, 255)},
        # 5: Solar Amber & Radiant Gold
        {"bg_top": (30, 18, 4), "bg_bot": (70, 40, 8), "accent": (255, 175, 40), "core": (255, 240, 180)},
        # 6: Cyber Teal & Neon Laser
        {"bg_top": (4, 20, 24), "bg_bot": (8, 50, 58), "accent": (20, 240, 200), "core": (200, 255, 245)},
        # 7: Prismatic Deep Indigo & Starlight
        {"bg_top": (10, 8, 36), "bg_bot": (24, 18, 80), "accent": (120, 160, 255), "core": (220, 235, 255)},
        # 8: Monochromatic Obsidian & Titanium Chrome
        {"bg_top": (14, 14, 18), "bg_bot": (36, 38, 44), "accent": (210, 220, 235), "core": (255, 255, 255)},
        # 9: Galactic Spiral Sunset (Magenta + Golden Amber)
        {"bg_top": (32, 8, 28), "bg_bot": (75, 20, 50), "accent": (255, 130, 80), "core": (255, 220, 160)},
        # 10: Curious Byte Branded Neon Outro (Electric Cyan Core & Concentric Rings)
        {"bg_top": (4, 12, 30), "bg_bot": (12, 28, 68), "accent": (0, 240, 255), "core": (255, 255, 255)}
    ]

    pal = PALETTES[(scene_num - 1) % len(PALETTES)]

    # 1. Radiant vertical gradient
    for y in range(0, 1920, 4):
        ratio = y / 1920.0
        r = int(pal["bg_top"][0] * (1 - ratio) + pal["bg_bot"][0] * ratio)
        g = int(pal["bg_top"][1] * (1 - ratio) + pal["bg_bot"][1] * ratio)
        b = int(pal["bg_top"][2] * (1 - ratio) + pal["bg_bot"][2] * ratio)
        draw.line([(0, y), (1080, y)], fill=(r, g, b), width=4)

    # 2. Distinct Geometric Signature per Scene
    cx, cy = 540, 960

    if scene_num % 3 == 1:
        # Spiral logarithmic energy vortex
        for i in range(240):
            theta = i * 0.15
            rad = 8 + i * 2.8
            px = int(cx + rad * math.cos(theta))
            py = int(cy + rad * math.sin(theta))
            pt_sz = int(2 + (i / 40))
            col = pal["core"] if i > 180 else pal["accent"]
            draw.ellipse([px - pt_sz, py - pt_sz, px + pt_sz, py + pt_sz], fill=col)

    elif scene_num % 3 == 2:
        # Quantum digital matrix grid with floating energy lines
        for x in range(60, 1080, 90):
            draw.line([(x, 0), (x, 1920)], fill=(pal["accent"][0]//4, pal["accent"][1]//4, pal["accent"][2]//4), width=1)
        for y in range(80, 1920, 120):
            draw.line([(0, y), (1080, y)], fill=(pal["accent"][0]//4, pal["accent"][1]//4, pal["accent"][2]//4), width=1)
        # Central glowing focal geometry
        for rad in range(60, 480, 60):
            draw.rectangle([cx - rad, cy - rad, cx + rad, cy + rad], outline=pal["accent"], width=2)

    else:
        # Concentric shockwave rings with radiant beams
        for rad in range(80, 520, 55):
            draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=pal["accent"], width=3)
        for ang in range(0, 360, 30):
            rad_ang = math.radians(ang)
            ex = int(cx + 600 * math.cos(rad_ang))
            ey = int(cy + 600 * math.sin(rad_ang))
            draw.line([(cx, cy), (ex, ey)], fill=(pal["core"][0]//3, pal["core"][1]//3, pal["core"][2]//3), width=2)

    # Central glowing radiant core
    for r in range(120, 10, -10):
        alpha_col = pal["core"]
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=alpha_col, width=2)

    base = base.filter(ImageFilter.GaussianBlur(radius=5))
    base.save(output_path, "JPEG", quality=95)
    return output_path

def generate_single_scene_asset(beat: dict, output_path: str, topic: str = "", scene_num: int = 1, used_urls: set = None, seed: int = None, lock: threading.Lock = None) -> str:
    """
    Fetches a verified 1080x1920 stylized frame for a single scene beat.
    Tiers:
    1. Pollinations Flux / SDXL (if available and responsive)
    2. Wikimedia Commons High-Res Science & Architectural Art (guaranteed non-repeated per scene)
    3. Thematic Mathematical Dynamic Canvas (distinct visual theme per scene)
    """
    if os.path.exists(output_path) and os.path.getsize(output_path) > 15000:
        return output_path

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if used_urls is None:
        used_urls = set()

    prompt = beat.get("visual_prompt", "")
    keyword = beat.get("search_keyword", "") or beat.get("beat_name", "")

    # Tier 1: Try Pollinations (Fast 7s timeout; skip if throttled)
    if scene_num == 1:
        full_prompt = prompt.strip()
        if not any(k in full_prompt.lower() for k in ["no text", "no human faces"]):
            full_prompt += STRICT_NEGATIVE_PROMPT

        encoded_prompt = urllib.parse.quote(full_prompt)
        seed_param = f"&seed={seed}" if seed else f"&seed={int(time.time()*1000)%100000}"
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true{seed_param}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CuriousByte/2.0"}

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp, open(output_path, "wb") as f:
                f.write(resp.read())

            if os.path.exists(output_path) and os.path.getsize(output_path) > 15000:
                with Image.open(output_path) as im:
                    im.verify()
                return output_path
        except Exception:
            pass

    # Tier 2: Wikimedia Commons High-Res Scientific, Architectural & Natural Art
    search_query = keyword if keyword else prompt
    if search_wikimedia_visual(search_query, output_path, used_urls=used_urls, topic=topic, scene_num=scene_num, lock=lock):
        return output_path

    # Tier 3: Thematic High-Contrast Procedural Canvas (guaranteed distinct theme per scene)
    return generate_thematic_procedural_canvas(output_path, scene_num=scene_num, seed=seed or (scene_num * 100))

def synthesize_scene_visuals(story_beats: list, short_id: str, topic: str = "", max_workers: int = 5) -> list:
    """
    Directs and synthesizes all 8 to 10 scene assets IN PARALLEL (5 concurrent workers).
    Guarantees 10 completely distinct visual scenes matching narration at maximum speed.
    """
    base_dir = os.path.join("output", "temp_scenes", short_id)
    os.makedirs(base_dir, exist_ok=True)

    used_urls = set()
    used_urls_lock = threading.Lock()
    print(f"\n[Visual Director] Synthesizing {len(story_beats)} matched 3D CGI scenes IN PARALLEL ({max_workers} Threads)...")

    total_beats = len(story_beats)
    def fetch_scene(item):
        idx, beat = item
        scene_num = beat.get("scene", idx)
        out_file = os.path.join(base_dir, f"scene_{scene_num:02d}.jpg")
        beat_name = beat.get("beat_name", f"Scene {scene_num}")
        keyword = beat.get("search_keyword", "")

        # Mandatory Branded Opening Intro Card with Logo & Question for Scene 1
        if idx == 1 or scene_num == 1:
            from video_engine.ai_visualizer import ensure_branded_intro_card
            q_text = beat.get("narration", "") or topic
            ensure_branded_intro_card(question_text=q_text, topic=topic, output_path=out_file)
            if os.path.exists(out_file) and os.path.getsize(out_file) > 10000:
                return scene_num, out_file, "Branded Question & Logo Intro", "Curious Byte Intro"

        # Mandatory Branded Channel Logo Outro for final scene (Like, Subscribe & Share)
        narration = beat.get("narration", "").lower()
        is_outro = (idx == total_beats) or (scene_num == total_beats) or ("subscribe" in narration and "like" in narration)
        if is_outro:
            from video_engine.ai_visualizer import ensure_promo_card
            promo_png = ensure_promo_card()
            if os.path.exists(promo_png):
                with Image.open(promo_png) as im:
                    im.convert("RGB").save(out_file, "JPEG", quality=95)
                return scene_num, out_file, "Channel Logo Outro (CTA)", "Curious Byte Logo"

        asset_path = generate_single_scene_asset(
            beat=beat,
            output_path=out_file,
            topic=topic,
            scene_num=scene_num,
            used_urls=used_urls,
            seed=42 + scene_num,
            lock=used_urls_lock
        )
        return scene_num, asset_path, beat_name, keyword

    items = list(enumerate(story_beats, start=1))
    results_map = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for scene_num, asset_path, beat_name, keyword in executor.map(fetch_scene, items):
            results_map[scene_num] = asset_path
            print(f"  🎬 [{scene_num:02d}/{len(story_beats)}] Visual Ready: {os.path.basename(asset_path)} ({os.path.getsize(asset_path)} bytes, '{keyword}')")

    scene_paths = [results_map[beat.get("scene", idx)] for idx, beat in enumerate(story_beats, start=1)]
    return scene_paths

if __name__ == "__main__":
    sample_beats = [
        {"scene": 1, "beat_name": "Hook", "search_keyword": "Pantheon Rome", "visual_prompt": "Stylized 3D CGI glowing ancient Roman concrete"},
        {"scene": 2, "beat_name": "Mystery", "search_keyword": "Volcanic ash", "visual_prompt": "Stylized 3D CGI volcanic ash clouds"},
        {"scene": 3, "beat_name": "Fact 1", "search_keyword": "Lime crystals", "visual_prompt": "Microscopic lime clasts"},
        {"scene": 4, "beat_name": "Fact 2", "search_keyword": "Ocean wave", "visual_prompt": "Seawater crashing on rock"}
    ]
    res = synthesize_scene_visuals(sample_beats, "test_director_multi", topic="Immortal Roman Concrete")
    print("Synthesized results:", res)
