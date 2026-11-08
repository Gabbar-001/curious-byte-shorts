"""
Voice Synthesizer using Edge TTS.
Generates high-definition neural voiceovers with word-level subtitle timings (VTT/SRT).
No API keys required, 100% free, natural documentary voices.
"""

import os
import asyncio
import edge_tts

DEFAULT_VOICE = "en-US-ChristopherNeural"  # Professional, deep, engaging documentary narrator

async def generate_speech(text: str, output_audio_path: str, output_vtt_path: str = None, voice: str = DEFAULT_VOICE, rate: str = "+4%", pitch: str = "+0Hz"):
    """
    Generate audio and subtitles for the given script.
    """
    os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
    
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    
    if output_vtt_path:
        os.makedirs(os.path.dirname(output_vtt_path), exist_ok=True)
        submaker = edge_tts.SubMaker()
        with open(output_audio_path, "wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                    submaker.feed(chunk)
                    
        with open(output_vtt_path, "w", encoding="utf-8") as vtt_file:
            vtt_file.write(submaker.get_srt())
    else:
        await communicate.save(output_audio_path)
        
    return output_audio_path

def synthesize_short(short_data: dict, voice: str = DEFAULT_VOICE, rate: str = "+4%"):
    """
    Synchronous wrapper to synthesize audio and subtitles for a short.
    """
    audio_filename = f"{short_data['date_created']}_{short_data['id']}.mp3"
    sub_filename = f"{short_data['date_created']}_{short_data['id']}.srt"
    
    audio_path = os.path.join("output", "audio", audio_filename)
    sub_path = os.path.join("output", "audio", sub_filename)
    
    asyncio.run(generate_speech(
        text=short_data["voiceover_text"],
        output_audio_path=audio_path,
        output_vtt_path=sub_path,
        voice=voice,
        rate=rate
    ))
    
    return {
        "audio_path": os.path.abspath(audio_path),
        "sub_path": os.path.abspath(sub_path)
    }

if __name__ == "__main__":
    test_text = "Did you know that space is not completely empty? In fact, NASA recorded the eerie sound of a black hole."
    print("Testing Voice Synthesizer...")
    result = asyncio.run(generate_speech(test_text, "output/audio/test.mp3", "output/audio/test.srt"))
    print(f"Generated test audio at {result}")
