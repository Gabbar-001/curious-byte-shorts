"""
AI Trend & Topic Explorer for Curious Byte Unique.
Mines real-time internet discoveries, Reddit science feeds, ScienceDaily, and Phys.org:
- r/todayilearned RSS
- r/Damnthatsinteresting RSS
- r/science RSS
- r/space RSS
- ScienceDaily Top Science RSS
- Phys.org Space News RSS

Filters against historical topics in output/history_topics.json to ensure 100% uniqueness.
Classifies topics into channel content pillars and prepares prioritized candidates.
"""

import os
import re
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict

HISTORY_FILE = os.path.join("output", "history_topics.json")
CANDIDATE_OUTPUT_FILE = os.path.join("output", "candidate_topics.json")

RSS_FEEDS = [
    {
        "name": "r/todayilearned",
        "url": "https://www.reddit.com/r/todayilearned/.rss",
        "type": "atom",
        "pillar": "Dark Science & Human Body Mysteries"
    },
    {
        "name": "r/space",
        "url": "https://www.reddit.com/r/space/.rss",
        "type": "atom",
        "pillar": "Space & Universal Paradoxes"
    },
    {
        "name": "r/science",
        "url": "https://www.reddit.com/r/science/.rss",
        "type": "atom",
        "pillar": "Mind-Bending Physics & Perception Anomalies"
    },
    {
        "name": "ScienceDaily",
        "url": "https://www.sciencedaily.com/rss/top/science.xml",
        "type": "rss",
        "pillar": "Catastrophic Earth & Natural Anomalies"
    },
    {
        "name": "Phys.org Space",
        "url": "https://phys.org/rss-feed/space-news/",
        "type": "rss",
        "pillar": "Space & Universal Paradoxes"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def load_history_titles() -> set:
    titles = set()
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    t = item.get("topic", "")
                    if t:
                        titles.add(t.lower().strip())
        except Exception:
            pass
    return titles

def clean_title(title: str) -> str:
    clean = re.sub(r'^(TIL\s*:?|TIL\s+that\s+|TIL\s+how\s+|YSK\s*:?|YSK\s+that\s+)', '', title, flags=re.IGNORECASE)
    clean = re.sub(r'\[.*?\]|\(.*?\)', '', clean)
    clean = clean.strip()
    return clean

def score_topic_virality(title: str) -> int:
    score = 60
    t_lower = title.lower()
    high_virality_keywords = [
        "never", "impossible", "banned", "secret", "deadly", "ancient", "discovered",
        "infinite", "deepest", "burning", "immortal", "bizarre", "paradox", "terrifying",
        "million years", "billion", "radiation", "black hole", "destroy", "survive"
    ]
    for kw in high_virality_keywords:
        if kw in t_lower:
            score += 6
    return min(score, 98)

def fetch_feed_candidates(feed_info: Dict, existing_titles: set) -> List[Dict]:
    candidates = []
    try:
        resp = requests.get(feed_info["url"], headers=HEADERS, timeout=8)
        if resp.status_code != 200:
            return []

        root = ET.fromstring(resp.content)
        if feed_info["type"] == "atom":
            # Atom format (Reddit)
            entries = root.findall("{http://www.w3.org/2005/Atom}entry")
            for entry in entries:
                t_elem = entry.find("{http://www.w3.org/2005/Atom}title")
                link_elem = entry.find("{http://www.w3.org/2005/Atom}link")
                if t_elem is not None and t_elem.text:
                    ctitle = clean_title(t_elem.text)
                    if len(ctitle) < 25 or len(ctitle) > 160:
                        continue
                    norm = ctitle.lower()
                    if any(h in norm or norm in h for h in existing_titles):
                        continue
                    link = link_elem.attrib.get("href", "") if link_elem is not None else ""
                    score = score_topic_virality(ctitle)
                    candidates.append({
                        "source": feed_info["name"],
                        "pillar": feed_info["pillar"],
                        "topic": ctitle,
                        "viral_potential_score": score,
                        "source_url": link
                    })
        else:
            # RSS format (ScienceDaily, Phys.org)
            items = root.findall(".//item")
            for item in items:
                t_elem = item.find("title")
                link_elem = item.find("link")
                if t_elem is not None and t_elem.text:
                    ctitle = clean_title(t_elem.text)
                    if len(ctitle) < 20 or len(ctitle) > 140:
                        continue
                    norm = ctitle.lower()
                    if any(h in norm or norm in h for h in existing_titles):
                        continue
                    link = link_elem.text if link_elem is not None else ""
                    score = score_topic_virality(ctitle)
                    candidates.append({
                        "source": feed_info["name"],
                        "pillar": feed_info["pillar"],
                        "topic": ctitle,
                        "viral_potential_score": score,
                        "source_url": link
                    })
    except Exception as e:
        pass
    return candidates

def mine_trending_topics() -> List[Dict]:
    """
    Executes live trend mining across Reddit science RSS, ScienceDaily, Phys.org.
    Filters historical topics and saves ranked candidates.
    """
    print("[TrendExplorer] Mining trending science and mystery topics across verified RSS feeds...")
    existing = load_history_titles()
    print(f"[TrendExplorer] Loaded {len(existing)} past topics to avoid duplication.")

    all_candidates = []
    for f in RSS_FEEDS:
        cands = fetch_feed_candidates(f, existing)
        all_candidates.extend(cands)
        print(f"[TrendExplorer] Discovered {len(cands)} fresh candidates from {f['name']}.")

    # Sort candidates by viral potential score descending
    all_candidates.sort(key=lambda x: x.get("viral_potential_score", 0), reverse=True)

    # Persist pool
    os.makedirs(os.path.dirname(CANDIDATE_OUTPUT_FILE), exist_ok=True)
    with open(CANDIDATE_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.now().isoformat(),
            "total_candidates": len(all_candidates),
            "candidates": all_candidates[:60]
        }, f, indent=2)

    print(f"[TrendExplorer] Successfully saved top {min(len(all_candidates), 60)} candidates to '{CANDIDATE_OUTPUT_FILE}'.")
    return all_candidates[:60]

if __name__ == "__main__":
    candidates = mine_trending_topics()
    print("\n--- TOP CANDIDATE DISCOVERIES ---")
    for c in candidates[:5]:
        print(f" • [Score {c['viral_potential_score']}] [{c['pillar'][:25]}] {c['topic'][:80]}...")
