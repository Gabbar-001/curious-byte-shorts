"""
Automated YouTube Thumbnail & Shorts Cover Generator.
Generates:
1. Standard 16:9 Thumbnail (1280x720) for YouTube search/desktop/API uploads.
2. Vertical 9:16 Shorts Cover (1080x1920) for mobile Shorts feed & social previews.

Features:
- High-CTR Impact typography with bold yellow/white fill, thick black strokes, and drop shadows.
- Cinematic contrast enhancement, dark gradient vignette for readable text.
- Curious Byte branded neon logo overlay.
- Frame extraction from rendered video or scene art.
"""

import os
import re
import subprocess
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from video_engine.ai_visualizer import get_ffmpeg

LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "channel_logo.png")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "thumbnails")

IMPACT_FONT = "impact.ttf"
ARIAL_BOLD = "arialbd.ttf"

def get_font(font_path: str, size: int):
    """Cross-platform font loader with Windows and Linux fallbacks."""
    # 1. Direct path check
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass

    # 2. Candidate paths based on font name
    is_impact = "impact" in font_path.lower()
    if is_impact:
        candidates = [
            r"C:\Windows\Fonts\impact.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/impact.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "Impact",
            "DejaVuSans-Bold"
        ]
    else:
        candidates = [
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\impact.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "Arial Bold",
            "DejaVuSans-Bold"
        ]

    for cand in candidates:
        try:
            if cand.startswith("C:") or cand.startswith("/"):
                if os.path.exists(cand):
                    return ImageFont.truetype(cand, size)
            else:
                return ImageFont.truetype(cand, size)
        except Exception:
            continue

    return ImageFont.load_default()

def extract_teaser_text(short_data: dict) -> tuple:
    """
    Extracts a high-impact, click-worthy teaser text from title and hook.
    Returns (category_badge, main_line_1, main_line_2)
    """
    category = short_data.get("category", "FACTS").upper()
    title = short_data.get("title", "")

    # Clean title
    clean = re.sub(r"#\S+", "", title)
    clean = re.sub(r"[?!.,]", "", clean).strip().upper()

    badge = f"⚡ {category}"

    words = clean.split()
    if len(words) <= 4:
        line1 = " ".join(words)
        line2 = "DON'T MISS THIS!"
    elif len(words) <= 7:
        mid = (len(words) + 1) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
    else:
        line1 = " ".join(words[:4])
        line2 = " ".join(words[4:8])

    return badge, line1, line2

def get_base_image_from_video_or_scene(short_data: dict, video_path: str = None) -> Image.Image:
    """Gets sharp visual frame from finished video, or temp scenes, or generates gradient."""
    short_id = short_data.get("id", "")
    
    # 1. Try extracting sharp frame from rendered video
    if video_path and os.path.exists(video_path):
        temp_frame = os.path.join(OUTPUT_DIR, f"temp_{short_id}.jpg")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        try:
            cmd = [
                get_ffmpeg(), "-y",
                "-ss", "1.5",
                "-i", video_path,
                "-vframes", "1",
                "-update", "1",
                temp_frame
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            if os.path.exists(temp_frame) and os.path.getsize(temp_frame) > 1000:
                img = Image.open(temp_frame).convert("RGBA")
                return img
        except Exception as e:
            print(f"[Thumbnail] Video frame extraction failed: {e}")

    # 2. Try temp scene image
    scene_path = os.path.join("output", "temp_scenes", short_id, "scene_0.jpg")
    if os.path.exists(scene_path) and os.path.getsize(scene_path) > 1000:
        try:
            return Image.open(scene_path).convert("RGBA")
        except Exception:
            pass

    # 3. Fallback: High-quality dark cosmic canvas
    w, h = 1080, 1920
    img = Image.new("RGBA", (w, h), (8, 12, 24, 255))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        ratio = y / h
        draw.line([(0, y), (w, y)], fill=(int(6 + 10 * ratio), int(10 + 20 * ratio), int(26 + 35 * ratio), 255))
    return img

def add_vignette_and_contrast(image: Image.Image, height_ratio: float = 0.5) -> Image.Image:
    """Enhance contrast and add dark bottom vignette for crisp text contrast."""
    enhancer = ImageEnhance.Contrast(image.convert("RGB"))
    enhanced = enhancer.enhance(1.25).convert("RGBA")

    w, h = enhanced.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Dark gradient at the bottom
    start_y = int(h * (1.0 - height_ratio))
    for y in range(start_y, h):
        alpha = int(230 * ((y - start_y) / (h - start_y)) ** 1.2)
        draw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))

    # Subtle top vignette
    for y in range(0, int(h * 0.22)):
        alpha = int(140 * (1.0 - (y / (h * 0.22))))
        draw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))

    return Image.alpha_composite(enhanced, overlay)

def draw_text_with_outline(draw, pos, text, font, fill_color, stroke_color, stroke_width, shadow_offset=(5, 5)):
    x, y = pos
    # Shadow
    draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=(0, 0, 0, 240), stroke_width=stroke_width, stroke_fill=(0, 0, 0, 240))
    # Outline & Text
    draw.text((x, y), text, font=font, fill=fill_color, stroke_width=stroke_width, stroke_fill=stroke_color)

def generate_youtube_thumbnail_16x9(short_data: dict, video_path: str = None, output_path: str = None) -> str:
    """Generates 1280x720 thumbnail for YouTube search, desktop and channel feeds."""
    w, h = 1280, 720
    if not output_path:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{short_data.get('id', 'short')}_thumb_16x9.jpg")

    base = get_base_image_from_video_or_scene(short_data, video_path)

    # Convert 9:16 vertical base into 16:9 cinematic background:
    # 1. Blurred full background
    blurred_bg = base.resize((w, h), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(18))
    
    # 2. Centered sharp subject
    aspect = base.width / base.height
    fg_h = h
    fg_w = int(fg_h * aspect)
    sharp_fg = base.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
    
    # Place sharp foreground on right side so text has clear room on left
    fg_x = w - fg_w - 40
    blurred_bg.paste(sharp_fg, (fg_x, 0), sharp_fg)

    comp = add_vignette_and_contrast(blurred_bg, height_ratio=0.65)
    draw = ImageDraw.Draw(comp)

    # Branded Logo in top left
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo.thumbnail((120, 120), Image.Resampling.LANCZOS)
            lw, lh = logo.size
            draw.ellipse([35, 25, 45 + lw, 35 + lh], fill=(0, 0, 0, 180))
            comp.paste(logo, (40, 30), logo)
        except Exception:
            pass

    badge, line1, line2 = extract_teaser_text(short_data)

    # Category Badge (Top)
    badge_font = get_font(ARIAL_BOLD, 28)
    badge_bbox = draw.textbbox((0, 0), badge, font=badge_font)
    bw = badge_bbox[2] - badge_bbox[0] + 32
    bh = badge_bbox[3] - badge_bbox[1] + 16
    bx, by = 45, 170
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(225, 29, 72, 240))  # Vivid red
    draw.text((bx + 16, by + 6), badge, font=badge_font, fill=(255, 255, 255))

    # Main Line 1 (Huge Neon Yellow)
    main_font = get_font(IMPACT_FONT, 86)
    draw_text_with_outline(
        draw=draw,
        pos=(45, 245),
        text=line1,
        font=main_font,
        fill_color=(255, 238, 0),
        stroke_color=(0, 0, 0),
        stroke_width=8,
        shadow_offset=(6, 6)
    )

    # Main Line 2 (Crisp Pure White)
    if line2:
        draw_text_with_outline(
            draw=draw,
            pos=(45, 355),
            text=line2,
            font=main_font,
            fill_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=8,
            shadow_offset=(6, 6)
        )

    # Bottom Callout Strip: "WATCH TILL THE END ⚡"
    sub_font = get_font(ARIAL_BOLD, 30)
    sub_text = "MIND-BLOWING FACT 🤯"
    draw_text_with_outline(
        draw=draw,
        pos=(45, 590),
        text=sub_text,
        font=sub_font,
        fill_color=(56, 189, 248),  # Neon Cyan
        stroke_color=(0, 0, 0),
        stroke_width=5,
        shadow_offset=(4, 4)
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    comp.convert("RGB").save(output_path, "JPEG", quality=95)
    print(f"[Thumbnail] 16:9 Thumbnail saved: {output_path}")
    return output_path

def generate_shorts_cover_9x16(short_data: dict, video_path: str = None, output_path: str = None) -> str:
    """Generates 1080x1920 vertical cover for YouTube Shorts & mobile display."""
    w, h = 1080, 1920
    if not output_path:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{short_data.get('id', 'short')}_cover_9x16.jpg")

    base = get_base_image_from_video_or_scene(short_data, video_path)
    if base.size != (w, h):
        base = base.resize((w, h), Image.Resampling.LANCZOS)

    comp = add_vignette_and_contrast(base, height_ratio=0.55)
    draw = ImageDraw.Draw(comp)

    # Logo at top center
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo.thumbnail((220, 220), Image.Resampling.LANCZOS)
            lw, lh = logo.size
            draw.ellipse([(w - lw) // 2 - 15, 80, (w + lw) // 2 + 15, 80 + lh + 30], fill=(0, 0, 0, 200))
            comp.paste(logo, ((w - lw) // 2, 95), logo)
        except Exception:
            pass

    badge, line1, line2 = extract_teaser_text(short_data)

    # Center Badge
    badge_font = get_font(ARIAL_BOLD, 42)
    badge_bbox = draw.textbbox((0, 0), badge, font=badge_font)
    bw = badge_bbox[2] - badge_bbox[0] + 44
    bh = badge_bbox[3] - badge_bbox[1] + 20
    bx = (w - bw) // 2
    by = h - 720
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=14, fill=(225, 29, 72, 245))
    draw.text((bx + 22, by + 8), badge, font=badge_font, fill=(255, 255, 255))

    # Center Teaser Text
    main_font = get_font(IMPACT_FONT, 108)
    
    bbox1 = draw.textbbox((0, 0), line1, font=main_font)
    w1 = bbox1[2] - bbox1[0]
    draw_text_with_outline(
        draw=draw,
        pos=((w - w1) // 2, h - 620),
        text=line1,
        font=main_font,
        fill_color=(255, 238, 0),
        stroke_color=(0, 0, 0),
        stroke_width=10,
        shadow_offset=(7, 7)
    )

    if line2:
        bbox2 = draw.textbbox((0, 0), line2, font=main_font)
        w2 = bbox2[2] - bbox2[0]
        draw_text_with_outline(
            draw=draw,
            pos=((w - w2) // 2, h - 480),
            text=line2,
            font=main_font,
            fill_color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=10,
            shadow_offset=(7, 7)
        )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    comp.convert("RGB").save(output_path, "JPEG", quality=95)
    print(f"[Thumbnail] 9:16 Shorts Cover saved: {output_path}")
    return output_path

def generate_short_thumbnails(short_data: dict, video_path: str = None, date_str: str = None) -> dict:
    """Master generator: generates both 16:9 thumbnail and 9:16 vertical cover."""
    if not date_str:
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")

    short_id = short_data.get("id", "short")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    h_path = os.path.join(OUTPUT_DIR, f"{date_str}_{short_id}_thumb_16x9.jpg")
    v_path = os.path.join(OUTPUT_DIR, f"{date_str}_{short_id}_cover_9x16.jpg")

    h_thumb = generate_youtube_thumbnail_16x9(short_data, video_path=video_path, output_path=h_path)
    v_cover = generate_shorts_cover_9x16(short_data, video_path=video_path, output_path=v_path)

    # Clean up temp frame if any
    temp_frame = os.path.join(OUTPUT_DIR, f"temp_{short_id}.jpg")
    if os.path.exists(temp_frame):
        try: os.remove(temp_frame)
        except Exception: pass

    return {
        "horizontal_16x9": h_thumb,
        "vertical_9x16": v_cover
    }
