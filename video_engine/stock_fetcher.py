"""
Stock Video Fetcher.
Retrieves free HD vertical (9:16) stock video footage from Pexels API if API key is provided.
Falls back gracefully if not configured.
"""

import os
import requests

def fetch_pexels_clip(query: str, api_key: str, output_path: str, min_duration: int = 15):
    """
    Search Pexels for a vertical video clip matching the query.
    Returns the downloaded path or None.
    """
    if not api_key:
        return None

    headers = {"Authorization": api_key}
    url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=5"

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            videos = data.get("videos", [])
            for vid in videos:
                # Find vertical 1080x1920 or 720x1280 video files
                video_files = vid.get("video_files", [])
                for vf in video_files:
                    width = vf.get("width", 0)
                    height = vf.get("height", 0)
                    if height > width:  # vertical
                        dl_url = vf.get("link")
                        if dl_url:
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            v_res = requests.get(dl_url, stream=True, timeout=30)
                            with open(output_path, "wb") as f:
                                for chunk in v_res.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            return output_path
    except Exception as e:
        print(f"[StockFetcher] Error fetching Pexels clip: {e}")

    return None
