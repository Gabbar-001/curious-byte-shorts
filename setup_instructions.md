# YouTube Shorts Automation Setup Guide (Curious Byte)

This guide walks you through connecting your **YouTube Channel**, **Google Gemini AI**, and **Invideo AI Studio** so you can generate and upload daily YouTube Shorts automatically.

---

## 1. Connecting Your YouTube Channel

To allow the automated pipeline to upload videos directly to your YouTube channel as **Private** (or Unlisted) for your review:

### Step 1: Create Google Cloud Project & Enable YouTube API
1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., `Curious-Byte-Shorts`).
3. In the search bar at the top, search for **YouTube Data API v3** and click **Enable**.

### Step 2: Configure OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** and click **Create**.
3. Fill in the App Name (e.g., `Curious Byte Bot`) and your email address.
4. Click **Save and Continue**.
5. Under **Scopes**, click **Add or Remove Scopes**, check `.../auth/youtube.upload`, and save.
6. Under **Test users**, add your own Google email address (the one that owns your YouTube channel).

### Step 3: Create OAuth Client Credentials
1. Go to **APIs & Services** > **Credentials**.
2. Click **Create Credentials** > **OAuth client ID**.
3. For Application type, choose **Desktop app**.
4. Click **Create**, then click **Download JSON**.
5. Rename the downloaded file to:
   ```
   client_secrets.json
   ```
6. Move `client_secrets.json` into the `d:\Youtube Shorts\config\` folder.

### Step 4: One-Time Channel Authentication
In your terminal, run:
```powershell
python uploader/youtube_auth.py
```
A browser window will open asking you to select your Google account and grant YouTube upload permissions. Once you click **Allow**, credentials will be saved into `config/token.json`.

---

## 2. Connecting Google Gemini API (For Unlimited AI Facts)

To unlock infinite AI script generation and on-demand batch writing:

1. Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Open `d:\Youtube Shorts\config\.env` and paste your key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
3. To batch-generate 30 brand new viral facts with AI visual prompts directly into your database:
   ```powershell
   python -m generator.ai_script_generator --batch 30
   ```

---

## 3. Daily Workflow & Commands

### Generate Today's Short (with Full Multi-Scene AI Video)
```powershell
python run_daily.py
```

### Generate & Upload Directly to YouTube as Private (Ready for Review)
```powershell
python run_daily.py --upload
```

### Fast Test Run (Script & Voiceover Only, Skip Video Rendering)
```powershell
python run_daily.py --skip-render
```

---

## 4. Setting Up Windows Daily Scheduled Task

To have Windows generate your YouTube Short automatically every morning at 10:00 AM:

1. Open **Task Scheduler** in Windows (`taskschd.msc`).
2. Click **Create Basic Task** on the right panel.
3. Name: `Curious Byte Daily Shorts`.
4. Trigger: **Daily** at `10:00 AM`.
5. Action: **Start a program**:
   - Program/script: `python`
   - Add arguments: `run_daily.py --upload`
   - Start in: `D:\Youtube Shorts`
6. Click **Finish**.
