"""
AI Viral Shorts Intelligence Engine 4.0 (Autonomous Executive Producer Edition) for Curious Byte Unique.
Features:
1. Ingests Daily Autonomous Strategy Plan (output/daily_strategy_plan.json)
2. Ingests Competitor Viral Breakouts (output/competitor_viral_trends.json)
3. Ingests Channel Brain & Audience Cravings (output/channel_brain.json, output/audience_insights.json)
4. 6-Archetype Hook Tournament (Shock, Curiosity, Paradox, Negation, Micro-Story, Time-Pressure)
5. 5-Beat Micro-Story Retention Framework (10 Cinematic 3D CGI Scenes)
6. Infinite Loop Architecture (Scene 10 seamlessly loops back into Scene 1)
7. Debate-Bait Pinned Comment Engine (Forces comment section arguments for algorithmic push)
8. High-Contrast Dopamine Visual Palettes (Molten Amber, Electric Cyan, Abyssal Obsidian)
9. Dual Hashtag Engine (8-12 trending hashtags + spoken word-level hashtags)
"""

import os
import sys
import re
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
CHANNEL_BRAIN_FILE = os.path.join("output", "channel_brain.json")
AUDIENCE_INSIGHTS_FILE = os.path.join("output", "audience_insights.json")
CANDIDATE_TOPICS_FILE = os.path.join("output", "candidate_topics.json")
COMPETITOR_FILE = os.path.join("output", "competitor_viral_trends.json")
STRATEGY_PLAN_FILE = os.path.join("output", "daily_strategy_plan.json")

CONTENT_PILLARS = [
    "Everyday Human Body Glitches & Quirks (Phantom vibrations, doorway forgetting effect, hearing your recorded voice cringe, sleep twitch jerk, brain freeze)",
    "Hilarious Human Behavior & Everyday Psychology (Awkward elevator habits, grocery store shopping cart psychology, song earworms stuck in head, contagious yawning mystery)",
    "Bizarre Secrets Behind Daily Life Objects (Why airplane windows have tiny holes, QWERTY keyboard trap, why jeans have that tiny pocket, why price tags end in .99)",
    "Daily Food & Bodily Operation Mysteries (Why coffee makes you need the bathroom in 4 minutes, airplane food taste changes, knuckle cracking pop sound, cilantro soap gene)",
    "Weird Habits & Daily Human Mysteries (Waking up 1 minute before alarm, why mosquito bites itch 10x more after scratching, why your nose nostrils switch every 4 hours)"
]

SYSTEM_PROMPT_TEMPLATE = """You are the Senior Viral Content Strategist & Data-Driven Storyteller for "Curious Byte Unique" (@CuriousByteShort).
Your mission is to produce a 38-to-45-second viral YouTube Short script engineered for maximum retention, completion rate, and subscriber conversion.

{AI_DIRECTIVE_BLOCK}

EDITORIAL PIVOT MANDATE (HUMAN OPERATIONS & RELATABLE HUMOR FOCUS):
- STRICTLY FORBIDDEN: Do NOT pick abstract theoretical physics, quantum mechanics, obscure biochemistry, or abyssal deep oceans. Viewers find them too complex and unrelatable.
- MANDATORY FOCUS: Choose facts that are FUNNY, SURPRISING, ENTERTAINING, and directly connected to DAILY HUMAN OPERATIONS and relatable daily human experiences (things normal people do, feel, eat, see, and experience every single day).
- TONE: Funny, witty, relatable, and astonishing! The viewer must instantly think: "OMG, I do this every day and never knew why!"

CORE MANDATES:
1. FACT ACCURACY (CRITICAL): Absolutely zero hallucinations or made-up statistics. Claims must be grounded in verified scientific, psychological, or historical facts.
2. 6-ARCHETYPE HOOK TOURNAMENT:
   Generate exactly 6 distinct opening hook angles (each under 12 words):
   - Shock Hook: Visceral disbelief statement stopping the scroll immediately.
   - Curiosity Hook: Burning mystery question making scrolling impossible without an answer.
   - Paradox Hook: Counter-intuitive truth contradicting everyday intuition.
   - High-Stakes Negation Hook: Debunks a commonly held belief with dramatic stakes.
   - Micro-Story Mystery Hook: Fast cinematic teaser of an anomaly unfolding right now.
   - Time-Pressure Curiosity Hook: Urgent countdown or temporal shock ("In the next 60 seconds...").
   Score each from 0-100, select the single highest-scoring winner, and note which archetype won.
3. 5-BEAT MICRO-STORY RETENTION FRAMEWORK (EXACTLY 10 SCENE CUTS):
   Do NOT provide disconnected facts. Structure a seamless 10-beat narrative arc:
   - Scene 1 [0:00-0:03]: Beat 1A - The Electrifying Hook (Striking visual)
   - Scene 2 [0:03-0:07]: Beat 1B - The Core Mystery / Question Setup
   - Scene 3 [0:07-0:12]: Beat 2A - The Phenomenon Introduced
   - Scene 4 [0:12-0:17]: Beat 2B - Microscopic / Close-up perspective & mechanism
   - Scene 5 [0:17-0:22]: Beat 3A - The Scientific Conflict / Impossible Evidence
   - Scene 6 [0:22-0:27]: Beat 3B - Macro-scale visual shift & stakes
   - Scene 7 [0:27-0:32]: Beat 4A - The Astonishing Revelation
   - Scene 8 [0:32-0:37]: Beat 4B - Deep-time / Universal perspective
   - Scene 9 [0:37-0:42]: Beat 5A - The Payoff (Direct answer to the opening hook)
   - Scene 10 [0:42-0:45]: Beat 5B - Mandatory Outro CTA: You MUST explicitly say: "Hit subscribe to Curious Byte right now so you don't miss tomorrow's mystery, and drop a like if your mind was blown!"
4. INFINITE LOOP RE-WATCH MECHANISM:
   The transition from Scene 9 through Scene 10 must lead logically and tonally back into the opening words of Scene 1, encouraging re-watches.
5. DEBATE-BAIT PINNED COMMENT:
   Include "pinned_debate_comment": A controversial, thought-provoking question designed to start a battle of opinions in the comment section.
6. A/B TITLE TESTING SUITE:
   Generate 3 to 5 high-CTR alternative titles (under 60 characters each, including '#Shorts').
7. SCENE PROMPTS (100% STYLIZED 3D CGI - ZERO FACES, ZERO TEXT):
   Write exactly 10 distinct, matched visual prompts with Dopamine High-Contrast lighting (e.g. volumetric molten amber, bioluminescent cyan, abyssal obsidian).
   EVERY prompt MUST adhere to this formula:
   "Stylized 3D CGI digital art, [Specific Subject matching narration beat], Unreal Engine 5 aesthetic, volumetric [color] cinematic lighting, dark atmospheric depth, high contrast, no human faces, no real people, no text, no letters, no words, 8k digital art"
   In addition, provide "search_keyword": concise 1-3 word primary subject noun.
8. VIRAL POTENTIAL SCORE: Score from 1 to 100 based on Curiosity, Emotion, Shareability, and Visuals.
9. VIRAL HASHTAG & TREND DISCOVERY: Include "trending_viral_hashtags" (8 to 12 relevant hashtags).

Respond ONLY with valid JSON matching this schema:
{
  "topic": "...",
  "title": "... #Shorts",
  "title_variations": ["... #Shorts", "... #Shorts", "... #Shorts"],
  "trending_viral_hashtags": ["#Tag1", "#Tag2"],
  "pillar": "...",
  "viral_score": 88,
  "scoring_breakdown": {
    "curiosity": 23, "emotion": 18, "shareability": 18, "uniqueness": 14, "relevance": 8, "visual_potential": 9
  },
  "hooks": {
    "shock_hook": "...", "curiosity_hook": "...", "paradox_hook": "...", "negation_hook": "...", "micro_story_hook": "...", "time_pressure_hook": "...",
    "selected_hook": "...",
    "winning_archetype": "Shock Hook|Curiosity Hook|Paradox Hook|High-Stakes Negation|Micro-Story Mystery|Time-Pressure Curiosity"
  },
  "story_beats": [
    {"scene": 1, "timecode": "0:00-0:03", "beat_name": "Hook", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "...", "sound_cue": "sub_bass_impact"},
    {"scene": 2, "timecode": "0:03-0:07", "beat_name": "Mystery Setup", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "...", "sound_cue": "atmospheric_drone"},
    {"scene": 3, "timecode": "0:07-0:12", "beat_name": "Phenomenon Intro", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "...", "sound_cue": "whoosh_transition"},
    {"scene": 4, "timecode": "0:12-0:17", "beat_name": "Micro Mechanism", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "...", "sound_cue": "whoosh_transition"},
    {"scene": 5, "timecode": "0:17-0:22", "beat_name": "Scientific Conflict", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "...", "sound_cue": "whoosh_transition"},
    {"scene": 6, "timecode": "0:22-0:27", "beat_name": "Macro Visual Shift", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "...", "sound_cue": "whoosh_transition"},
    {"scene": 7, "timecode": "0:27-0:32", "beat_name": "Astonishing Revelation", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "...", "sound_cue": "cinematic_impact"},
    {"scene": 8, "timecode": "0:32-0:37", "beat_name": "Deep-Time Perspective", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "...", "sound_cue": "whoosh_transition"},
    {"scene": 9, "timecode": "0:37-0:42", "beat_name": "Payoff", "narration": "...", "visual_prompt": "Stylized 3D CGI...", "search_keyword": "...", "sound_cue": "whoosh_transition"},
    {"scene": 10, "timecode": "0:42-0:45", "beat_name": "CTA Outro", "narration": "Hit subscribe to Curious Byte right now so you don't miss tomorrow's mystery, and drop a like if your mind was blown!", "visual_prompt": "Stylized 3D CGI Curious Byte branded neon brain outro card with glowing energy...", "search_keyword": "Futuristic neon brain", "sound_cue": "soft_riser"}
  ],
  "full_voiceover_script": "Full continuous narration combining scenes 1 through 10...",
  "fact_verification": {
    "primary_claim": "...", "source_evidence": "...", "verified_scientific_basis": "...", "is_verified": true
  },
  "debate_question": "...",
  "pinned_debate_comment": "...",
  "highlight_emojis": {"WORD": "EMOJI"}
}
"""

def load_json_safe(path: str, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default

def save_topic_history(topic_name: str, fact_id: str):
    history = load_json_safe(HISTORY_TOPICS_FILE, [])
    history.append({
        "topic": topic_name,
        "id": fact_id,
        "timestamp": datetime.now().isoformat()
    })
    os.makedirs(os.path.dirname(HISTORY_TOPICS_FILE), exist_ok=True)
    with open(HISTORY_TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def select_intelligent_pillar(brain: dict, strategy: dict) -> str:
    """Selects pillar dynamically weighted by AI Executive Producer strategy."""
    strat_weights = strategy.get("strategic_pillar_weights", {})
    if strat_weights:
        pillars = list(strat_weights.keys())
        weights = [float(w) for w in strat_weights.values()]
        # Match to CONTENT_PILLARS if possible
        matched_pillars = []
        for p in pillars:
            m = next((cp for cp in CONTENT_PILLARS if p.lower() in cp.lower()), None)
            matched_pillars.append(m if m else p)
        return random.choices(matched_pillars, weights=weights, k=1)[0]

    pillar_perf = brain.get("pillar_performance", [])
    if pillar_perf:
        pillars = [p.get("pillar", "") for p in pillar_perf if p.get("pillar")]
        weights = [max(p.get("avg_views", 10), 10) ** 1.3 for p in pillar_perf if p.get("pillar")]
        if pillars and len(pillars) == len(weights):
            return random.choices(pillars, weights=weights, k=1)[0]

    return random.choice(CONTENT_PILLARS)

HASHTAG_STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
    'by', 'from', 'up', 'about', 'into', 'over', 'after', 'is', 'are', 'was', 'were',
    'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'shall', 'should', 'may', 'might', 'must', 'can', 'could', 'it', 'its',
    'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they', 'me',
    'him', 'her', 'us', 'them', 'my', 'your', 'his', 'their', 'our', 'what', 'which',
    'who', 'whom', 'whose', 'where', 'when', 'why', 'how', 'all', 'any', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'like', 'share',
    'subscribe', 'curious', 'byte', 'shorts'
}

NICHE_VIRAL_HASHTAGS = {
    'space': ['#SpaceFacts', '#Astronomy', '#Cosmos', '#Universe', '#NASA', '#BlackHole', '#Astrophysics', '#DeepSpace'],
    'physics': ['#QuantumPhysics', '#PhysicsFacts', '#QuantumMechanics', '#TheoreticalPhysics', '#ScienceExperiment'],
    'biology': ['#HumanBody', '#BrainHacks', '#PsychologyFacts', '#BiologyFacts', '#Neuroscience', '#HumanAnatomy'],
    'nature': ['#DeepSea', '#OceanMysteries', '#CatastrophicEarth', '#EarthFacts', '#PlanetEarth', '#WildNature'],
    'history': ['#AncientHistory', '#Archaeology', '#LostCivilizations', '#AncientEngineering', '#HistoricalMysteries'],
    'global_viral': ['#Shorts', '#YouTubeShorts', '#Viral', '#Trending', '#CuriousByte', '#DidYouKnow', '#MindBlowing', '#FYP']
}

def build_ultimate_viral_hashtags(title: str, script: str, topic: str = "", pillar: str = "", ai_hashtags: list = None, max_tags: int = 38) -> list[str]:
    seen = set()
    result = []
    for tag in NICHE_VIRAL_HASHTAGS['global_viral']:
        k = tag.replace('#', '').lower()
        if k not in seen:
            seen.add(k)
            result.append(tag)
    if ai_hashtags:
        for tag in ai_hashtags:
            t = tag.strip() if tag.strip().startswith('#') else f'#{tag.strip()}'
            k = t.replace('#', '').lower()
            if k not in seen and len(k) >= 3:
                seen.add(k)
                result.append(t)
    combined_ctx = f'{topic} {pillar} {title}'.lower()
    for niche_key, niche_tags in NICHE_VIRAL_HASHTAGS.items():
        if niche_key in combined_ctx or (niche_key == 'nature' and any(k in combined_ctx for k in ['sea', 'ocean', 'trench', 'abyss', 'crater', 'fire'])):
            for tag in niche_tags:
                k = tag.replace('#', '').lower()
                if k not in seen:
                    seen.add(k)
                    result.append(tag)
    clean = re.sub(r'https?://\S+|@\S+|#\S+', ' ', f'{title} {script}')
    clean = re.sub(r'[^a-zA-Z\s]', ' ', clean)
    for w in clean.split():
        wl = w.lower()
        if len(wl) >= 3 and wl not in HASHTAG_STOP_WORDS and wl not in seen:
            seen.add(wl)
            result.append(f'#{wl}')
            if len(result) >= max_tags:
                break
    return result[:max_tags]

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
    Discovers, scores, fact-checks, and structures a complete 10-scene Short guided by the AI Executive Producer.
    """
    client = get_gemini_client()
    if not client:
        raise RuntimeError("GEMINI_API_KEY is not configured in config/.env!")

    # Ingest persistent memory & strategic plans
    strategy = load_json_safe(STRATEGY_PLAN_FILE, {})
    brain = load_json_safe(CHANNEL_BRAIN_FILE, {})
    audience = load_json_safe(AUDIENCE_INSIGHTS_FILE, {})
    competitors = load_json_safe(COMPETITOR_FILE, {})
    candidates = load_json_safe(CANDIDATE_TOPICS_FILE, {}).get("candidates", [])
    history = load_json_safe(HISTORY_TOPICS_FILE, [])

    recent_topics = [h.get("topic", "") for h in history[-35:]]
    recent_topics_str = ", ".join(f'"{t}"' for t in recent_topics if t)

    # Dynamic pillar selection
    if not pillar:
        pillar = select_intelligent_pillar(brain, strategy)

    # Ingest AI Executive Plan directives
    exec_summary = strategy.get("ai_executive_summary", brain.get("ai_strategic_directive", "Maximize curious retention."))
    loop_directive = strategy.get("infinite_loop_directive", "Ensure the final sentence seamlessly flows into the first hook.")
    debate_directive = strategy.get("debate_bait_strategy", "Pose a polarising open question in the pinned comment.")
    
    # Ingest topic inspirations
    rec_topics = strategy.get("recommended_topics_to_produce", [])
    comp_hits = [c.get("proven_title") for c in competitors.get("curated_intercept_pool", [])[:4]]
    candidate_sample = [c.get("topic") for c in candidates[:4] if c.get("topic")]

    inspiration_block = []
    if rec_topics:
        inspiration_block.append(f"AI Executive Recommended Topics for Today: {rec_topics}")
    if comp_hits:
        inspiration_block.append(f"Breakout Competitor Hit Signals (>15M views): {comp_hits}")
    if candidate_sample:
        inspiration_block.append(f"Live Emerging Scientific Discoveries: {candidate_sample}")

    directive_block = f"""=== AI EXECUTIVE PRODUCER STRATEGIC MANDATE ===
• Strategic Directive: {exec_summary}
• Infinite Loop Mandate: {loop_directive}
• Debate Bait Mandate: {debate_directive}
• Target Inpirations: {'; '.join(inspiration_block)}"""

    system_prompt = SYSTEM_PROMPT_TEMPLATE.replace("{AI_DIRECTIVE_BLOCK}", directive_block)

    user_prompt = f"""Discover a viral Short concept for pillar: '{pillar}'.
Avoid recently covered topics: [{recent_topics_str}].
Ensure the Viral Potential Score is >= {min_score}/100.
Enforce all 6 Hook Archetypes, the 5-Beat Micro-Story Structure across 10 scenes, Infinite Loop transition, and pinned debate comment."""

    candidate_models = ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-3.8-flash"]

    for attempt in range(1, max_attempts + 1):
        print(f"\n[ViralIntelligence] Attempt {attempt}/{max_attempts}: Querying Gemini on '{pillar[:45]}...'")
        response = None
        for model_name in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=f"{system_prompt}\n\nUSER REQUEST: {user_prompt}"
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
        print(f"  • Topic Discovered: \"{concept_data.get('topic')}\" | Viral Score: {score}/100")

        if score < min_score:
            print(f"  • Score {score} below threshold {min_score}. Requesting fresh topic...")
            continue

        verification = concept_data.get("fact_verification", {})
        if not verification.get("is_verified", False):
            print(f"  • Claim failed verification check. Requesting verified topic...")
            continue

        beats = concept_data.get("story_beats", [])
        if len(beats) < 8:
            print(f"  • Only {len(beats)} beats returned. Need at least 8. Retrying...")
            continue

        # Programmatic Guarantee: Enforce Scene 10 Branded CTA Outro & voiceover
        cta_outro = "Hit subscribe to Curious Byte right now so you don't miss tomorrow's mystery, and drop a like if your mind was blown!"
        if beats:
            last_beat = beats[-1]
            last_text = last_beat.get("narration", "").strip()
            if not any(k in last_text.lower() for k in ["subscribe", "sub"]):
                last_beat["narration"] = f"{last_text.rstrip('.')}! {cta_outro}".strip()
            concept_data["full_voiceover_script"] = " ".join(b.get("narration", "") for b in beats)

        date_str = datetime.now().strftime("%Y-%m-%d")
        fact_id = f"ai_{random.randint(10000, 99999)}"
        concept_data["id"] = fact_id
        concept_data["date_created"] = date_str
        concept_data["learned_intelligence_applied"] = {
            "ai_executive_plan_active": bool(strategy),
            "top_pillar_selected": pillar,
            "winning_hook_archetype": concept_data.get("hooks", {}).get("winning_archetype", "Shock Hook"),
            "tested_title_variations": concept_data.get("title_variations", []),
            "infinite_loop_enabled": True
        }

        # Save topic to avoid repeats
        save_topic_history(concept_data.get("topic", "Unknown"), fact_id)

        # Build SEO description with trending viral hashtags + word-by-word hashtags
        debate_q = concept_data.get("pinned_debate_comment") or concept_data.get("debate_question", "What is your theory on this?")
        ai_hashtags = concept_data.get("trending_viral_hashtags", [])
        topic = concept_data.get("topic", "")

        all_hashtags = build_ultimate_viral_hashtags(
            title=concept_data.get("title", ""),
            script=concept_data.get("full_voiceover_script", ""),
            topic=topic,
            pillar=pillar,
            ai_hashtags=ai_hashtags,
            max_tags=38
        )
        hashtag_line = " ".join(all_hashtags)

        # Video tags array
        raw_tags = ["Shorts", "Curious Byte", "Facts"] + [h.replace("#", "") for h in all_hashtags]
        final_tags = []
        cur_len = 0
        for t in raw_tags:
            if t.lower() not in [x.lower() for x in final_tags]:
                if cur_len + len(t) + 1 < 480:
                    final_tags.append(t)
                    cur_len += len(t) + 1
        concept_data["tags"] = final_tags

        seo_description = (
            f"💬 PINNED COMMENT / TOP DEBATE:\n{debate_q}\n"
            f"👇 Drop your answer below! We reply to the top comments!\n\n"
            f"{concept_data.get('full_voiceover_script', '')}\n\n"
            f"🔴 HIT SUBSCRIBE to Curious Byte for daily mind-blowing facts:\n"
            f"https://www.youtube.com/@CuriousByteShort?sub_confirmation=1\n\n"
            f"{hashtag_line}"
        )
        concept_data["description"] = seo_description

        # Save metadata JSON
        meta_path = os.path.join("output", "metadata", f"{date_str}_{fact_id}.json")
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(concept_data, f, indent=2)

        print(f"  ✅ Concept Verified & Locked: \"{concept_data.get('title')}\"")
        print(f"  🎯 Winning Hook ({concept_data.get('hooks', {}).get('winning_archetype')}): \"{concept_data.get('hooks', {}).get('selected_hook')}\"")
        print(f"  💬 Pinned Debate Bait: \"{debate_q[:60]}...\"")
        return concept_data

    raise RuntimeError("Failed to generate a high-scoring, verified concept after multiple attempts.")

if __name__ == "__main__":
    concept = generate_viral_short_concept()
    print("\n--- GENERATED CONCEPT SUMMARY ---")
    print("ID:", concept["id"])
    print("Topic:", concept["topic"])
    print("Title:", concept["title"])
    print("Title Variations:", concept.get("title_variations", []))
    print("Pinned Debate:", concept.get("pinned_debate_comment"))
    print("Winning Hook Archetype:", concept.get("hooks", {}).get("winning_archetype"))
    print("Winning Hook:", concept.get("hooks", {}).get("selected_hook"))
    print("Beats Count:", len(concept["story_beats"]))
