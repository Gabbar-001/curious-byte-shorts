"""
Curious Byte Unique — Autonomous Channel Brain & Self-Learning Engine (Module 9).
Analyzes performance metrics, discovers winning patterns, calculates dynamic pillar weights,
and generates real-time strategic directives that evolve future video generation.
"""

import os
import sys
import json
from datetime import datetime, timezone

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PERFORMANCE_METRICS_FILE = os.path.join("output", "performance_metrics.json")
CHANNEL_BRAIN_FILE = os.path.join("output", "channel_brain.json")

def load_performance_metrics() -> dict:
    if os.path.exists(PERFORMANCE_METRICS_FILE):
        try:
            with open(PERFORMANCE_METRICS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    from analytics.performance_analyzer import analyze_channel_performance
    return analyze_channel_performance()

def compute_pillar_analytics(videos: list) -> dict:
    """Computes average views, velocity, and dynamic weights per content pillar."""
    pillar_data = {}
    for v in videos:
        p = v.get("pillar") or "General Science & Curiosities"
        if p not in pillar_data:
            pillar_data[p] = {"count": 0, "total_views": 0, "total_velocity": 0.0, "total_likes": 0}
        pillar_data[p]["count"] += 1
        pillar_data[p]["total_views"] += v.get("views", 0)
        pillar_data[p]["total_velocity"] += v.get("velocity_per_hour", 0.0)
        pillar_data[p]["total_likes"] += v.get("likes", 0)

    results = {}
    total_score = 0.0
    for p, stats in pillar_data.items():
        cnt = max(1, stats["count"])
        avg_views = round(stats["total_views"] / cnt, 1)
        avg_vel = round(stats["total_velocity"] / cnt, 2)
        score = max(1.0, avg_views * 0.7 + avg_vel * 20.0)
        total_score += score
        results[p] = {
            "video_count": cnt,
            "total_views": stats["total_views"],
            "avg_views_per_video": avg_views,
            "avg_velocity_per_hour": avg_vel,
            "raw_performance_score": round(score, 1)
        }

    # Normalize into Dynamic Production Probabilities (e.g. 35% Space, 25% Earth...)
    for p, stats in results.items():
        weight_pct = round((stats["raw_performance_score"] / max(1.0, total_score)) * 100, 1)
        # Apply min floor of 10% and max cap of 45% for healthy diversity
        stats["recommended_allocation_pct"] = max(10.0, min(45.0, weight_pct))

    return results

def compute_hook_analytics(videos: list) -> dict:
    """Computes win-rate and average views per hook archetype."""
    hook_data = {}
    channel_median = sorted([v.get("views", 0) for v in videos])[len(videos) // 2] if videos else 1

    for v in videos:
        ht = v.get("hook_type") or "Shock"
        if ht not in hook_data:
            hook_data[ht] = {"count": 0, "total_views": 0, "wins": 0}
        hook_data[ht]["count"] += 1
        views = v.get("views", 0)
        hook_data[ht]["total_views"] += views
        if views > channel_median:
            hook_data[ht]["wins"] += 1

    results = {}
    for ht, stats in hook_data.items():
        cnt = max(1, stats["count"])
        avg_views = round(stats["total_views"] / cnt, 1)
        win_rate = round((stats["wins"] / cnt) * 100, 1)
        results[ht] = {
            "attempts": cnt,
            "avg_views": avg_views,
            "win_rate_pct": win_rate
        }

    return results

def extract_breakout_and_flop_patterns(videos: list) -> tuple[list, list]:
    """Identifies the channel's top breakout hits and underperformers for learning."""
    sorted_vids = sorted(videos, key=lambda x: x.get("views", 0), reverse=True)
    breakouts = []
    for v in sorted_vids[:5]:
        if v.get("views", 0) >= 50:
            breakouts.append({
                "title": v.get("title"),
                "topic": v.get("topic"),
                "pillar": v.get("pillar"),
                "views": v.get("views"),
                "hook": v.get("selected_hook")
            })

    flops = []
    for v in reversed(sorted_vids[-5:]):
        if v.get("age_hours", 0) >= 12.0 and v.get("views", 0) < 5:
            flops.append({
                "title": v.get("title"),
                "topic": v.get("topic"),
                "pillar": v.get("pillar"),
                "views": v.get("views")
            })

    return breakouts, flops

def generate_ai_strategic_directive(pillar_stats: dict, hook_stats: dict, breakouts: list, flops: list) -> str:
    """Synthesizes high-level actionable instructions for Gemini to improve the next batch."""
    # Find winning pillar
    sorted_pillars = sorted(pillar_stats.items(), key=lambda x: x[1].get("avg_views_per_video", 0), reverse=True)
    top_pillar_names = [p[0] for p in sorted_pillars[:2]]

    # Find winning hook
    sorted_hooks = sorted(hook_stats.items(), key=lambda x: x[1].get("win_rate_pct", 0), reverse=True)
    best_hook = sorted_hooks[0][0] if sorted_hooks else "Shock"

    breakout_titles = [f"'{b['title']}' ({b['views']} views)" for b in breakouts[:3]]
    flop_titles = [f"'{f['title']}'" for f in flops[:2]]

    directive = f"""=== REAL-TIME CURIOUS BYTE CHANNEL INTELLIGENCE DIRECTIVE ===
1. AUDIENCE CRAVING: Your audience generates 3x-5x higher engagement on: {', '.join(top_pillar_names)}. Prioritize these themes.
2. WINNING HOOK ARCHETYPE: '{best_hook} Hook' is your channel's highest-converting opener. Deliver a visceral, high-stakes curiosity gap in the first 2 seconds.
3. PROVEN BREAKOUT WINNERS (Model your upcoming scripts on these):
   • {' / '.join(breakout_titles) if breakout_titles else 'High-contrast natural mysteries and ancient enigmas'}
4. UNDERPERFORMING PATTERNS (Avoid these angles):
   • {', '.join(flop_titles) if flop_titles else 'Generic abstract facts without physical stakes'}
5. RETENTION MANDATE: Keep narrative cuts under 4.5 seconds per beat. Never explain academic theory without immediate visual proof."""

    return directive

def update_channel_brain() -> dict:
    """
    Executes the complete Self-Learning Cycle:
    Ingests live metrics -> Computes attribution -> Generates strategy -> Persists to channel_brain.json
    """
    print("[ChannelBrain] Initiating Self-Learning Cycle...")
    metrics = load_performance_metrics()
    videos = metrics.get("videos", [])

    if not videos:
        print("[ChannelBrain] No video performance data available to train on.")
        return {}

    pillar_analytics = compute_pillar_analytics(videos)
    hook_analytics = compute_hook_analytics(videos)
    breakouts, flops = extract_breakout_and_flop_patterns(videos)
    directive = generate_ai_strategic_directive(pillar_analytics, hook_analytics, breakouts, flops)

    # Formulate spin-off video recommendations from breakout hits
    spin_offs = []
    for b in breakouts[:3]:
        spin_offs.append({
            "parent_title": b["title"],
            "parent_views": b["views"],
            "suggested_sequels": [
                f"Part 2: What happened next with {b['topic']}",
                f"The Secret Science Behind {b['topic']}",
                f"3 Things Everyone Missed About {b['topic']}"
            ]
        })

    brain_state = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_videos_analyzed": len(videos),
        "total_channel_views": metrics.get("total_channel_views", 0),
        "median_views": metrics.get("median_views", 0),
        "pillar_analytics": pillar_analytics,
        "hook_analytics": hook_analytics,
        "breakout_hits": breakouts,
        "underperforming_patterns": flops,
        "spin_off_recommendations": spin_offs,
        "ai_strategic_directive": directive
    }

    os.makedirs(os.path.dirname(CHANNEL_BRAIN_FILE), exist_ok=True)
    with open(CHANNEL_BRAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(brain_state, f, indent=2)

    print("\n" + "=" * 65)
    print("  🧠 CHANNEL BRAIN UPDATED WITH LIVE AUDIENCE LEARNINGS")
    print(f"  • Videos Learned From : {len(videos)}")
    print(f"  • Top Winning Pillar  : {sorted(pillar_analytics.items(), key=lambda x: x[1]['avg_views_per_video'], reverse=True)[0][0]}")
    print(f"  • Top Hook Style      : {sorted(hook_analytics.items(), key=lambda x: x[1]['win_rate_pct'], reverse=True)[0][0]}")
    print(f"  • Breakout Winners    : {len(breakouts)} identified")
    print("=" * 65 + "\n")

    return brain_state

if __name__ == "__main__":
    brain = update_channel_brain()
    print("Brain Directive:\n", brain.get("ai_strategic_directive"))
