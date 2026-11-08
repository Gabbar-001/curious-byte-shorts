import os
import subprocess

fb = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe')
env = os.environ.copy()
env['FONTCONFIG_FILE'] = os.path.abspath('config/fonts.conf')

# Convert SRT to ASS with explicit PlayResX: 1080 and PlayResY: 1920
ass_header = """[Script Info]
Title: Curious Byte Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,64,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,400,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

events = []
with open('output/audio/2026-11-07_space_001.srt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

i = 0
while i < len(lines):
    if lines[i].isdigit():
        time_line = lines[i+1]
        text_lines = []
        i += 2
        while i < len(lines) and not lines[i].isdigit():
            text_lines.append(lines[i])
            i += 1
        
        # Parse time: 00:00:00,100 --> 00:00:05,554
        start_str, end_str = time_line.split(' --> ')
        # Convert to ASS time: 0:00:00.10
        def to_ass_time(ts):
            h, m, s_ms = ts.split(':')
            s, ms = s_ms.split(',')
            return f"{int(h)}:{m}:{s}.{ms[:2]}"
        
        ass_start = to_ass_time(start_str)
        ass_end = to_ass_time(end_str)
        text = "\\N".join(text_lines)
        events.append(f"Dialogue: 0,{ass_start},{ass_end},Default,,0,0,0,,{text}")

with open('output/test_subs.ass', 'w', encoding='utf-8') as f:
    f.write(ass_header + "\n".join(events))

print(f"Generated test_subs.ass with {len(events)} cues.")

# Now test burning onto a 5s clip and extract frame at 2s
ass_rel = 'output/test_subs.ass'
cmd = [
    fb, '-y',
    '-f', 'lavfi', '-i', 'color=c=0x0a1020:s=1080x1920:d=5',
    '-vf', f"ass={ass_rel}",
    '-c:v', 'libx264', '-t', '5', 'output/test_ass.mp4'
]
res = subprocess.run(cmd, env=env, capture_output=True, text=True)
print("FFmpeg exit code:", res.returncode)
if res.returncode == 0:
    # Extract frame at 2s
    subprocess.run([fb, '-y', '-ss', '00:00:02', '-i', 'output/test_ass.mp4', '-vframes', '1', 'output/test_ass_frame.jpg'])
    print("Extracted output/test_ass_frame.jpg, size:", os.path.getsize('output/test_ass_frame.jpg'))
else:
    print("Error:", res.stderr[-400:])
