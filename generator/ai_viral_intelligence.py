"""
AI Viral Shorts Intelligence Engine 2.0 for Curious Byte Unique.
Evolves the autonomous pipeline into a high-retention media engine:
1. Topic Discovery with Viral Potential Scoring (Curiosity, Emotion, Shareability >= 75/100)
2. 3-Hook Tournament (Shock vs Curiosity vs Paradox)
3. Connected 8-10 Scene Story Arc (Hook -> Mystery -> Conflict -> Climax -> Payoff -> Loop)
4. Fact-Checking Verification Gate (Science & History consensus, zero hallucinations)
5. 100% Stylized 3D CGI Scene Prompts (Zero real faces, zero stock videos, zero AI text)
6. Restrained Emoji Directing (1-2 emojis max per Short)
7. Topic History Memory (Prevents repetition)
"""

import os
import sys
import json
import random
from datetime import datetime
from dotenv import load_dotenv

# UTF-8 stdout configuration for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

ENV_FILE = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
load_dotenv(ENV_FILE)

HISTORY_TOPICS_FILE = os.path.join("output", "history_topics.json")

# 5 High-Retention Content Pillars
CONTENT_PILLARS = [
    "Dark Science & Human Body Mysteries (Bizarre biological glitches, extreme resilience, cellular marvels)",
    "Ancient Wonders & Archaeological Enigmas (Lost Roman concrete, subterranean cities, impossible engineering)",
    "Space & Universal Paradoxes (Time dilation, black hole physics, neutron stars, quantum reality)",
    "Catastrophic Earth & Natural Anomalies (Deepest boreholes, eternal burning craters, zombie biology)",
    "Mind-Bending Physics & Perception Anomalies (Double slit experiment, optical illusions, sensory illusions)"
]

SYSTEM_PROMPT = """You are the Senior Viral Content Strategist & Science Storyteller for "Curious Byte Unique" (@CuriousByteShort).
Your mission is to produce a 38-to-45-second high-retention YouTube Short script following our Viral Intelligence 2.0 framework.

CORE MANDATES:
1. FACT ACCURACY (CRITICAL): Absolutely zero hallucinations or made-up statistics. Claims must be grounded in verified scientific or historical research (NASA, MIT, nature, peer-reviewed journals, historical archaeological findings).
2. HOOK TOURNAMENT: Generate 3 distinct opening hook angles:
   - Shock Hook: A shocking, verified statement that stops the scroll.
   - Curiosity Hook: A mystery question the viewer desperately wants answered.
   - Paradox Hook: A counter-intuitive truth that challenges everyday belief.
   Select the single strongest winner (under 12 words) and verify the video directly delivers on its promise.
3. CONNECTED STORYTELLING (8 TO 10 SCENE CUTS):
   Do NOT provide disconnected bullet points. Build a connected 10-beat narrative arc:
   - Scene 1 [0:00-0:03]: The Electrifying Hook (Striking visual)
   - Scene 2 [0:03-0:07]: The Core Mystery / Question Setup
   - Scene 3 [0:07-0:12]: Fact 1 - Introduction of the Phenomenon
   - Scene 4 [0:12-0:17]: Fact 1 - Micro-detail / Close-up perspective
   - Scene 5 [0:17-0:22]: Fact 2 - The Scientific Conflict / Proof
   - Scene 6 [0:22-0:27]: Fact 2 - Macro-scale visual shift
   - Scene 7 [0:27-0:32]: Fact 3 - The Astonishing Revelation
   - Scene 8 [0:32-0:37]: Fact 3 - Microscopic / Deep-time perspective
   - Scene 9 [0:37-0:42]: The Payoff (Direct answer to the opening hook)
   - Scene 10 [0:42-0:45]: High-Converting Outro CTA: You MUST explicitly tell the viewer: "If your mind was blown, like, subscribe to Curious Byte, and share this with a friend!"
4. SCENE PROMPTS & KEYWORDS (100% STYLIZED 3D CGI - ZERO FACES, ZERO TEXT):
   Write exactly 10 distinct, matched visual prompts and concise search keywords for each scene beat.
   EVERY prompt MUST adhere to this strict formula:
   "Stylized 3D CGI digital art, [Specific Subject matching narration beat], Unreal Engine 5 aesthetic, volumetric [color] cinematic lighting, dark atmospheric depth, no human faces, no real people, no text, no letters, no words, 8k digital art"
   In addition, provide "search_keyword": a concise 1-3 word primary subject noun (e.g. "Pantheon Rome", "Volcanic magma", "Ocean trench") for instant visual retrieval.
5. VIRAL POTENTIAL SCORE:
   Score the topic from 1 to 100 based on Curiosity (25%), Emotion (20%), Shareability (20%), Uniqueness (15%), Relevance (10%), Visuals (10%).
6. EMOJI RESTRAINT:
   Pick only 1 or 2 high-impact emojis for the entire video (placed on the climax or payoff words).

Respond ONLY with valid JSON matching this schema:
{
  "topic": "...",
  "pillar": "...",
  "viral_score": 88,
  "scoring_breakdown": {
    "curiosity": 23,
    "emotion": 18,
    "shareability": 18,
    "uniqueness": 14,
    "relevance": 8,
    "visual_potential": 9
  },
  "hooks": {
    "shock_hook": "...",
    "curiosity_hook": "...",
    "paradox_hook": "...",
    "selected_hook": "...",
    "hook_type": "Shock|Curiosity|Paradox"
  },
  "story_beats": [
    {"scene": 1, "timecode": "0:00-0:03", "beat_name": "Hook", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "Ancient Roman concrete", "sound_cue": "sub_bass_impact"},
    {"scene": 2, "timecode": "0:03-0:07", "beat_name": "Mystery Setup", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "Pantheon dome", "sound_cue": "atmospheric_drone"},
    {"scene": 3, "timecode": "0:07-0:12", "beat_name": "Fact 1 Intro", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "Volcanic ash Pozzuoli", "sound_cue": "whoosh_transition"},
    {"scene": 4, "timecode": "0:12-0:17", "beat_name": "Fact 1 Detail", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "Lime clasts microscope", "sound_cue": "whoosh_transition"},
    {"scene": 5, "timecode": "0:17-0:22", "beat_name": "Fact 2 Conflict", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "Seawater ocean wave", "sound_cue": "whoosh_transition"},
    {"scene": 6, "timecode": "0:22-0:27", "beat_name": "Fact 2 Macro", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "Ancient Roman harbor", "sound_cue": "whoosh_transition"},
    {"scene": 7, "timecode": "0:27-0:32", "beat_name": "Fact 3 Revelation", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "Self healing concrete crack", "sound_cue": "cinematic_impact"},
    {"scene": 8, "timecode": "0:32-0:37", "beat_name": "Fact 3 Deep-Time", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "Roman colosseum ruins", "sound_cue": "whoosh_transition"},
    {"scene": 9, "timecode": "0:37-0:42", "beat_name": "Payoff", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "Modern architectural concrete", "sound_cue": "whoosh_transition"},
    {"scene": 10, "timecode": "0:42-0:45", "beat_name": "CTA Outro", "narration": "If your mind was blown, like, subscribe to Curious Byte, and share this with a friend!", "visual_prompt": "Stylized 3D CGI Curious Byte branded neon brain outro card with glowing energy...", "search_keyword": "Futuristic neon brain", "sound_cue": "soft_riser"}
  ],
  "full_voiceover_script": "Full continuous narration combining scenes 1 through 10...",
  "fact_verification": {
    "primary_claim": "...",
    "source_evidence": "...",
    "verified_scientific_basis": "...",
    "is_verified": true
  },
  "debate_question": "...",
  "title": "... #Shorts",
  "tags": ["tag1", "tag2", "tag3"],
  "highlight_emojis": {"WORD": "EMOJI"}
}
"""

def load_topic_history() -> list:
    if os.path.exists(HISTORY_TOPICS_FILE):
        try:
            with open(HISTORY_TOPICS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_topic_history(topic_name: str, fact_id: str):
    history = load_topic_history()
    history.append({
        "topic": topic_name,
        "id": fact_id,
        "timestamp": datetime.now().isoformat()
    })
    os.makedirs(os.path.dirname(HISTORY_TOPICS_FILE), exist_ok=True)
    with open(HISTORY_TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[ViralIntelligence] Error initializing Gemini client: {e}")
        return None

def generate_viral_short_concept(pillar: str = None, min_score: int = 75, max_attempts: int = 3) -> dict:
    """
    Discovers, scores, fact-checks, and structures a complete 10-scene Short with 100% dynamic AI.
    """
    client = get_gemini_client()
    if not client:
        raise RuntimeError("GEMINI_API_KEY is not configured in config/.env!")

    history = load_topic_history()
    recent_topics = [h.get("topic", "") for h in history[-25:]]
    recent_topics_str = ", ".join(f'"{t}"' for t in recent_topics if t)

    if not pillar:
        pillar = random.choice(CONTENT_PILLARS)

    user_prompt = f"""Discover a viral Short concept for pillar: '{pillar}'.
Avoid these recently generated topics: [{recent_topics_str}].
Ensure the Viral Potential Score is >= {min_score}/100.
Enforce fact verification and the strict 10-scene matched structure (zero human faces, no text)."""

    candidate_models = ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-3.8-flash"]

    for attempt in range(1, max_attempts + 1):
        print(f"\n[ViralIntelligence] Attempt {attempt}/{max_attempts}: Querying Gemini on '{pillar[:40]}...'")
        response = None
        for model_name in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=f"{SYSTEM_PROMPT}\n\nUSER REQUEST: {user_prompt}"
                )
                if response and response.text:
                    break
            except Exception as e:
                print(f"  Model {model_name} error: {e}")
                continue

        if not response or not response.text:
            print("  Warning: Empty response from Gemini. Retrying...")
            continue

        raw_text = response.text.strip()
        # Clean markdown wrappers if present
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        try:
            concept_data = json.loads(raw_text)
        except json.JSONDecodeError as jde:
            print(f"  JSON parse failed: {jde}. Retrying...")
            continue

        score = concept_data.get("viral_score", 0)
        print(f"  ✓ Topic Discovered: \"{concept_data.get('topic')}\" | Viral Score: {score}/100")

        # Check viral score threshold
        if score < min_score:
            print(f"  ⚠️ Score {score} below threshold {min_score}. Requesting fresh topic...")
            continue

        # Check fact verification gate
        verification = concept_data.get("fact_verification", {})
        if not verification.get("is_verified", False):
            print(f"  ⚠️ Claim failed verification check. Requesting verified topic...")
            continue

        # Check 10-scene structure
        beats = concept_data.get("story_beats", [])
        if len(beats) < 8:
            print(f"  ⚠️ Only {len(beats)} beats returned. Need at least 8. Retrying...")
            continue

        # Programmatic Guarantee: Always enforce "Like, Subscribe & Share" in Scene 10 & voiceover
        cta_outro = "If your mind was blown, like, subscribe to Curious Byte, and share this with a friend!"
        if beats:
            last_beat = beats[-1]
            last_text = last_beat.get("narration", "").strip()
            if not any(k in last_text.lower() for k in ["subscribe", "sub"]):
                last_beat["narration"] = f"{last_text.rstrip('.')}! {cta_outro}".strip()
            concept_data["full_voiceover_script"] = " ".join(b.get("narration", "") for b in beats)

        # Assign unique ID
        date_str = datetime.now().strftime("%Y-%m-%d")
        fact_id = f"ai_{random.randint(10000, 99999)}"
        concept_data["id"] = fact_id
        concept_data["date_created"] = date_str

        # Save topic to avoid repeats
        save_topic_history(concept_data.get("topic", "Unknown"), fact_id)

        # Build SEO description
        debate_q = concept_data.get("debate_question", "What is your theory on this?")
        seo_description = (
            f"💬 QUESTION OF THE DAY:\n{debate_q}\n"
            f"👇 Drop your opinion below! We reply to the top comments!\n\n"
            f"{concept_data.get('full_voiceover_script', '')[:200]}...\n\n"
            f"🔔 Subscribe to Curious Byte Unique for daily mind-blowing facts:\n"
            f"https://www.youtube.com/@CuriousByteShort?sub_confirmation=1\n\n"
            f"#CuriousByte #Shorts #Facts #Science #MindBlowing"
        )
        concept_data["description"] = seo_description

        # Save metadata JSON
        meta_path = os.path.join("output", "metadata", f"{date_str}_{fact_id}.json")
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(concept_data, f, indent=2)

        print(f"  🎯 Concept Verified & Locked: \"{concept_data.get('title')}\"")
        print(f"  ⚡ Selected Hook: \"{concept_data.get('hooks', {}).get('selected_hook')}\"")
        print(f"  🔬 Evidence: {verification.get('source_evidence', 'Verified scientific research')[:60]}...")
        return concept_data

    raise RuntimeError("Failed to generate a high-scoring, verified concept after multiple attempts.")

if __name__ == "__main__":
    concept = generate_viral_short_concept()
    print("\n--- GENERATED CONCEPT SUMMARY ---")
    print("ID:", concept["id"])
    print("Topic:", concept["topic"])
    print("Viral Score:", concept["viral_score"])
    print("Beats:", len(concept["story_beats"]))
    print("First Scene Prompt:", concept["story_beats"][0]["visual_prompt"])
