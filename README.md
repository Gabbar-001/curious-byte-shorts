# 🎬 Curious Byte: Automated YouTube Shorts Pipeline

An automated, daily YouTube Shorts generation and upload system customized for **Curious Byte Unique** (`@CuriousByteShort`).

---

## 🚀 Features

- **Dual Fact Generation Engine**:
  - **Curated Viral Library**: Pre-built with verified high-retention topics across Space, Deep Sea, Psychology, Ancient History, Biology, and Physics.
  - **Infinite Google Gemini AI Generator**: Dynamically writes fresh viral scripts on the fly or batch-generates 30+ new topics into your library in seconds.
- **Natural AI Voiceover**: Microsoft Edge Neural TTS (`en-US-ChristopherNeural`) for deep, engaging documentary narration—100% free with no limits.
- **Scene-by-Scene AI Visuals**: 4 script-matched 8K AI visuals per video with dynamic Ken Burns camera moves (alternating push-in / pull-out).
- **Branded Promotional Outro**: Official Curious Byte logo with glowing neon cyan border, `SUBSCRIBE • LIKE • SHARE` button, and spoken narrator CTA.
- **Mobile-Optimized Subtitles**: Large, bold, bright yellow text (`FontSize=65`) with pure black outline and drop shadow via native 1080x1920 ASS formatting.
- **Direct YouTube Upload**: Resumable chunk upload directly to your channel as **Private** (or Unlisted) for your review before going public.
- **Duplicate Prevention**: Tracks used fact IDs in `output/history.json`.

---

## 📁 Project Structure

```
d:\Youtube Shorts\
├── assets\
│   ├── channel_logo.png       # Official Curious Byte circular logo
│   └── promo_outro_card.png   # 1080x1920 animated outro card with CTA
├── config\
│   ├── settings.json          # Main configuration
│   ├── .env                   # API keys (Gemini, YouTube, etc.)
│   ├── fonts.conf             # Windows font configuration
│   └── client_secrets.json    # Google OAuth credentials file
├── generator\
│   ├── facts_library.py       # Expanded curated facts database
│   ├── ai_script_generator.py # Google Gemini dynamic & batch script writer
│   ├── script_generator.py    # Main script selector & history tracker
│   └── voice_synthesizer.py   # Edge-TTS speech & subtitle generation
├── video_engine\
│   ├── ai_visualizer.py       # Multi-scene AI image generator & ASS subtitle compositor
│   └── local_renderer.py      # Fallback video renderer
├── uploader\
│   ├── youtube_auth.py        # YouTube OAuth browser login
│   └── youtube_uploader.py    # Chunked YouTube Shorts uploader
├── output\
│   ├── videos\                # Rendered 1080x1920 Shorts ready for upload
│   ├── audio\                 # Generated voiceovers and subtitle files
│   └── metadata\              # Saved JSON metadata (titles, descriptions, tags)
├── run_daily.py               # Main daily execution pipeline
├── setup_instructions.md      # Setup guide
└── README.md
```

---

## ⚡ Commands

### Generate Daily Short
```powershell
python run_daily.py
```

### Generate & Upload to YouTube as Private
```powershell
python run_daily.py --upload
```

### Batch Generate 30 Fresh Shorts with Gemini AI
```powershell
python -m generator.ai_script_generator --batch 30
```
