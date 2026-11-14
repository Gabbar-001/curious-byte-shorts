"""
Autonomous Decision Agent & Persistent Memory Ledger for Curious Byte Unique.
Acts as the channel's AI Executive Producer:
1. Conducts daily self-evaluation of channel views, audience comments, and viral velocity.
2. Ingests real-time competitor viral signals (output/competitor_viral_trends.json).
3. Reads persistent memory ledger (output/decision_memory_ledger.json) to reflect on past decisions.
4. Formulates today's Autonomous Strategic Plan (output/daily_strategy_plan.json).
5. Appends decisions and predictions to the permanent Memory Ledger so the AI never forgets.
"""

import os
import sys
import json
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

MEMORY_LEDGER_FILE = os.path.join("output", "decision_memory_ledger.json")
STRATEGY_PLAN_FILE = os.path.join("output", "daily_strategy_plan.json")
PERF_FILE = os.path.join("output", "performance_metrics.json")
COMPETITOR_FILE = os.path.join("output", "competitor_viral_trends.json")
AUDIENCE_FILE = os.path.join("output", "audience_insights.json")
CANDIDATE_FILE = os.path.join("output", "candidate_topics.json")

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

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[DecisionAgent] Gemini init error: {e}")
        return None

def run_autonomous_decision_agent() -> dict:
    print("[DecisionAgent] Convening Daily Autonomous Channel Strategy Meeting...")
    
    # 1. Gather all sensory intelligence
    perf = load_json_safe(PERF_FILE, {})
    competitors = load_json_safe(COMPETITOR_FILE, {})
    audience = load_json_safe(AUDIENCE_FILE, {})
    candidates = load_json_safe(CANDIDATE_FILE, {})
    memory_ledger = load_json_safe(MEMORY_LEDGER_FILE, [])
    if isinstance(memory_ledger, dict):
        memory_ledger = memory_ledger.get("history", [])

    total_views = perf.get("total_channel_views", 2800)
    videos_count = perf.get("total_videos_analyzed", 67)
    top_performers = [v.get("title", "") for v in perf.get("videos", [])[:5]]
    
    competitor_hits = [c.get("proven_title", "") + f" ({c.get('view_text', '')})" for c in competitors.get("curated_intercept_pool", [])[:6]]
    audience_cravings = [c.get("craving", "") for c in audience.get("audience_cravings", [])]
    recent_memory = memory_ledger[-5:] if memory_ledger else []

    client = get_gemini_client()
    if not client:
        print("[DecisionAgent] Warning: GEMINI_API_KEY not found. Using algorithmic default plan.")
        # Fallback heuristic strategy (Everyday Human Operations & Relatable Humor Focus)
        plan = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "ai_executive_summary": "Pivoting 100% to funny, relatable everyday human body glitches, weird daily habits, and funny life mysteries.",
            "strategic_pillar_weights": {
                "Mind-Blowing Head-to-Head Comparisons & Versus Battles": 25,
                "Crazy Sports Mysteries & Bizarre Rules": 25,
                "Everyday Human Body Glitches & Quirks": 25,
                "Hilarious Human Behavior & Bizarre Object Secrets": 25
            },
            "primary_hook_archetype": "Shock Hook",
            "recommended_topics_to_produce": [
                "Why Kerala Gets 3,000mm of Rain While Karnataka & Telangana Stay Dry (Western Ghats Rain Shadow)",
                "Kohli vs. Sachin: The One Chasing Stat That Proves Who Is The Real King",
                "iPhone 100x Zoom vs Samsung 100x Zoom: The Dirty AI Secret Behind Moon Photos"
            ],
            "infinite_loop_mandate": True,
            "debate_bait_strategy": "Ask viewers if they have experienced this exact daily glitch today."
        }
    else:
        system_prompt = """You are the Chief AI Executive Producer for the YouTube Shorts channel "Curious Byte Unique" (@CuriousByteShort).
You have full autonomous authority over content strategy, topic selection, hook engineering, and audience conversion.

CRITICAL EDITORIAL PIVOT DIRECTIVE:
1. STRICTLY FORBIDDEN: Stop generating abstract deep science, quantum physics, complex biology, and deep ocean abysses. Viewers find these too difficult to understand.
2. MANDATORY FOCUS: Prioritize facts that are FUNNY, SURPRISING, ENTERTAINING, and directly tied to:
   • HEAD-TO-HEAD COMPARISONS & VERSUS BATTLES: Regional weather contrasts (Kerala rain vs neighboring Karnataka/Telangana rain shadow), sports legends statistical shootouts (Kohli vs Sachin, Ronaldo vs Messi), tech gadget spec shootouts (iPhone vs Samsung real camera/battery truth).
   • CRAZY SPORTS SECRETS & BIZARRE RULES (Cricket, Football/Soccer, referee secrets, historical match flukes).
   • DAILY HUMAN OPERATIONS & RELATABLE BODY GLITCHES (doorway forgetting effect, voice cringe, sleep twitches, phantom vibrations).
3. The content must make normal everyday people laugh and say: 'Wait, I do this every single day and never knew why!'"""

        user_prompt = f"""Channel Intelligence Context:
- Lifetime Channel Views: {total_views} across {videos_count} uploads.
- Channel Top Performers: {top_performers}
- Breakout Competitor Hits Currently Exploding on YouTube (>15M views): {competitor_hits}
- Audience Cravings Detected from Comments: {audience_cravings}
- Recent Memory Ledger of Past Strategic Decisions: {json.dumps(recent_memory, indent=1)}

Make your executive decisions for today based STRICTLY on the EDITORIAL PIVOT DIRECTIVE.
Output valid JSON ONLY with this schema:
{{
  "ai_executive_summary": "1-2 sentence executive justification of today's strategy",
  "self_learning_reflection": "What we learned from previous days' view patterns and competitor waves",
  "strategic_pillar_weights": {{
    "Mind-Blowing Head-to-Head Comparisons & Versus Battles": 25,
    "Crazy Sports Mysteries & Bizarre Rules": 25,
    "Everyday Human Body Glitches & Quirks": 25,
    "Hilarious Human Behavior & Bizarre Object Secrets": 25
  }},
  "primary_hook_archetype": "Shock Hook|Paradox Hook|High-Stakes Negation",
  "recommended_topics_to_produce": [
    "Specific Topic 1 (regional comparison like Kerala rain vs Karnataka/Telangana OR Kohli vs Sachin stats OR iPhone vs Samsung)",
    "Specific Topic 2 (crazy sports secret or weird cricket/football rule)",
    "Specific Topic 3 (funny human body glitch or everyday object secret)"
  ],
  "infinite_loop_directive": "Specific guidance on connecting the final scene back to the opening hook",
  "debate_bait_strategy": "Formula for provoking heated comment arguments",
  "projected_24h_view_target": 500
}}"""

        try:
            resp = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=f"{system_prompt}\n\nUSER PROMPT: {user_prompt}"
            )
            raw = resp.text.strip()
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            plan = json.loads(raw.strip())
            plan["date"] = datetime.now().strftime("%Y-%m-%d")
        except Exception as e:
            print(f"[DecisionAgent] LLM strategy generation error: {e}. Using resilient heuristic strategy.")
            plan = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "ai_executive_summary": "Capitalizing on Deep Ocean & Subterranean Catastrophes surging across YouTube.",
                "self_learning_reflection": "Ancient engineering and extreme depths reliably outperform abstract theory.",
                "strategic_pillar_weights": {
                    "Catastrophic Earth & Natural Anomalies": 50,
                    "Ancient Wonders & Archaeological Enigmas": 30,
                    "Space & Universal Paradoxes": 10,
                    "Dark Science & Human Body Mysteries": 10
                },
                "primary_hook_archetype": "Shock Hook",
                "recommended_topics_to_produce": [
                    "What Is Hiding At Point Nemo (The Deepest Ocean Abyss)",
                    "The Subterranean Fire Burning For 60 Years (Part 2)",
                    "The Impossible Roman Harbor That Concrete Cured Underwater"
                ],
                "infinite_loop_directive": "End with an open dependent clause linking directly to the first word of the hook.",
                "debate_bait_strategy": "Ask viewers if they believe official science is hiding deeper ocean anomalies.",
                "projected_24h_view_target": 500
            }

    # Save today's strategy plan
    os.makedirs(os.path.dirname(STRATEGY_PLAN_FILE), exist_ok=True)
    with open(STRATEGY_PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)

    # Append to Persistent Memory Ledger
    ledger_entry = {
        "timestamp": datetime.now().isoformat(),
        "date": plan.get("date"),
        "ai_executive_summary": plan.get("ai_executive_summary"),
        "primary_hook_archetype": plan.get("primary_hook_archetype"),
        "recommended_topics": plan.get("recommended_topics_to_produce", []),
        "pillar_weights": plan.get("strategic_pillar_weights", {})
    }
    
    memory_ledger.append(ledger_entry)
    # Retain up to 90 days of memory
    if len(memory_ledger) > 90:
        memory_ledger = memory_ledger[-90:]

    with open(MEMORY_LEDGER_FILE, "w", encoding="utf-8") as f:
        json.dump({"updated_at": datetime.now().isoformat(), "history": memory_ledger}, f, indent=2)

    print("\n=================================================================")
    print("  🧠 AUTONOMOUS DECISION AGENT — TODAY'S STRATEGIC DIRECTIVE")
    print(f"  • Date                  : {plan.get('date')}")
    print(f"  • Executive Summary     : {plan.get('ai_executive_summary')}")
    print(f"  • Primary Hook Mandate  : {plan.get('primary_hook_archetype')}")
    print(f"  • Pillar Weights        : {plan.get('strategic_pillar_weights')}")
    print(f"  • Recommended Topics    : {len(plan.get('recommended_topics_to_produce', []))} identified")
    print("=================================================================\n")

    return plan

if __name__ == "__main__":
    run_autonomous_decision_agent()
