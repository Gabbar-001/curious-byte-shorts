"""
AI Script Generator powered by Google Gemini API.
Enables:
1. Dynamic, on-the-fly script creation when the database needs fresh topics.
2. Batch-generation of 10 to 60 viral facts with precise AI visual prompts
   that automatically append into facts_library.py.
"""

import os
import json
import random
import argparse
from dotenv import load_dotenv

# Load environment variables
ENV_FILE = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
load_dotenv(ENV_FILE)

CATEGORIES = [
    # Weirdest History & Bizarre Dark Secrets
    "Weirdest Bizarre Historical Events & Mass Hysterias",
    "Ancient Civilizations & Forbidden Archaeological Secrets",
    "Unsolved Historical Disappearances & Lost Relics",
    "Bizarre Medieval Legends, Cults & Royal Scandals",
    
    # Mad Science & Inventions
    "Mad Science, Secret Experiments & Bizarre Inventions",
    "Nikola Tesla & Suppressed Scientific Technology",
    "Cold War Bizarre Military Projects & Classified Secrets",
    "Impossible Synthetic Materials & Futuristic Physics",
    
    # Brain, Psychology & Medical Curiosities
    "Creepy Psychological Syndromes & Terrifying Brain Glitches",
    "Bizarre Medical Curiosities & The Human Subconscious",
    "Optical Illusions & Reality Perception Anomalies",
    "The Mandela Effect & Glitches in the Matrix",
    
    # Creepy Biology & Genetic Superpowers
    "Mind-Controlling Parasites & Zombie Animals",
    "Organisms With Impossible Biological Superpowers",
    "Deep Earth Extremophiles & Bizarre Mutated Life",
    
    # Extreme Earth & Geological Wonders
    "Bizarre Geological Anomalies & Extreme Earth Secrets",
    "Unexplored Deep Ocean & Abyssal Creature Mysteries",
    "Catastrophic Natural Wonders & Exploding Volcanoes",
    
    # Quantum Physics & Reality Paradoxes
    "Mind-Bending Quantum Physics & Reality Paradoxes",
    "The Simulation Hypothesis & Multiverse Theories",
    "Deep Space Anomalies, Black Holes & Cosmic Horrors"
]

PROMPT_TEMPLATE = """You are a viral YouTube Shorts scriptwriter for the channel "Curious Byte".
Write a high-retention 40-second YouTube Short about: {topic}.

Requirements:
1. Hook A (Curiosity Question): Shocking, question-based opening sentence (under 15 words, e.g. "Did you know that...?").
2. Hook B (Revelation Claim): Urgent, shocking claim opening sentence (under 15 words, e.g. "Scientists were stunned when...!").
3. Facts: Exactly 3 punchy, scientifically verified, mind-blowing facts (1 to 2 sentences each).
4. Loop Outro: 1 sentence that seamlessly loops back to the start or leaves the viewer in awe.
5. Debate Question: 1 polarizing engagement question for the pinned comments section to spark furious viewer discussion (e.g. "Would you volunteer for a one-way trip to Mars? Yes or No?").
6. Scene Prompts: 4 specific cinematic visual prompts for 9:16 vertical AI image generation:
   - "hook": Cinematic visual for the hook.
   - "fact_1": Visual for fact 1.
   - "fact_2": Visual for fact 2.
   - "fact_3": Visual for fact 3.
7. Title: Catchy YouTube title with emoji and #Shorts (under 80 chars).
8. Tags: 8 relevant viral tags.

Return ONLY valid JSON matching this schema with NO extra commentary or markdown backticks:
{{
  "id": "{fact_id}",
  "category": "{category}",
  "hook_a": "...",
  "hook_b": "...",
  "hook": "...",
  "debate_question": "...",
  "facts": ["Fact 1...", "Fact 2...", "Fact 3..."],
  "loop_outro": "...",
  "scene_prompts": {{
    "hook": "cinematic prompt...",
    "fact_1": "cinematic prompt...",
    "fact_2": "cinematic prompt...",
    "fact_3": "cinematic prompt..."
  }},
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "title": "... #Shorts",
  "description": "Engaging description with #CuriousByte #Shorts",
  "tags": ["tag1", "tag2", "tag3"]
}}
"""

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[AIGenerator] Error initializing Gemini client: {e}")
        return None

def generate_ai_short(category: str = None) -> dict:
    """
    Generate a complete Short topic using Google Gemini.
    """
    client = get_gemini_client()
    if not client:
        print("[AIGenerator] GEMINI_API_KEY not found in config/.env. Please add it to enable dynamic AI generation.")
        return None

    if not category:
        category = random.choice(CATEGORIES)

    fact_id = f"ai_{random.randint(1000, 9999)}"
    prompt = PROMPT_TEMPLATE.format(topic=category, fact_id=fact_id, category=category)

    try:
        print(f"[AIGenerator] Requesting fresh viral Short from Gemini on: '{category}'...")
        # Priority models working with this API key
        candidate_models = ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
        response = None
        for m in candidate_models:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=prompt,
                )
                if response and response.text:
                    break
            except Exception as me:
                continue

        if not response or not response.text:
            raise RuntimeError("All Gemini model endpoints busy. Using curated fallback.")

        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        data = json.loads(text.strip())
        return data
    except Exception as e:
        print(f"[AIGenerator Error] Gemini generation failed: {e}")
        return None

def batch_generate_and_save(count: int = 5):
    """
    Batch generate new facts using Gemini and append them to facts_library.py.
    """
    client = get_gemini_client()
    if not client:
        print("\n" + "="*60)
        print("  GEMINI API KEY REQUIRED FOR BATCH GENERATION")
        print("="*60)
        print("To enable unlimited AI generation:")
        print("1. Get a free Gemini API key at: https://aistudio.google.com/app/apikey")
        print("2. Add it to d:\\Youtube Shorts\\config\\.env like this:")
        print("   GEMINI_API_KEY=your_key_here")
        print("="*60 + "\n")
        return

    print(f"\n[AIGenerator] Batch generating {count} new viral Shorts with Gemini...")
    new_facts = []
    for i in range(count):
        cat = random.choice(CATEGORIES)
        short = generate_ai_short(cat)
        if short:
            new_facts.append(short)
            print(f"  [{i+1}/{count}] Generated: {short['title']}")

    if not new_facts:
        print("[AIGenerator] No facts could be generated.")
        return

    # Append to FACTS_DATABASE in facts_library.py
    library_path = os.path.join(os.path.dirname(__file__), "facts_library.py")
    with open(library_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the closing bracket of FACTS_DATABASE
    close_idx = content.rfind("]")
    if close_idx != -1:
        formatted_items = ""
        for nf in new_facts:
            item_json = json.dumps(nf, indent=8)
            formatted_items += f"    {item_json},\n"
        
        updated_content = content[:close_idx] + formatted_items + content[close_idx:]
        with open(library_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print(f"\n[AIGenerator] 🎉 Successfully appended {len(new_facts)} new Shorts to facts_library.py!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Script Generator for Curious Byte")
    parser.add_argument("--batch", type=int, default=1, help="Number of fresh Shorts to batch generate and append to facts_library.py")
    parser.add_argument("--topic", type=str, default=None, help="Specific topic to generate")
    args = parser.parse_args()

    if args.batch > 1:
        batch_generate_and_save(count=args.batch)
    else:
        result = generate_ai_short(category=args.topic)
        if result:
            print(json.dumps(result, indent=2))
