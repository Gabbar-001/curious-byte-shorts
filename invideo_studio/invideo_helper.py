"""
Invideo AI CLI Studio integration.
Allows creating projects, generating scenes, and exporting videos using the Invideo CLI.
"""

import subprocess
import shutil
import json
import os

class InvideoStudio:
    def __init__(self):
        self.cli_name = "invideo"
        self._check_installed()

    def _check_installed(self):
        """Check if invideo CLI is in PATH."""
        return shutil.which(self.cli_name) is not None

    def check_auth(self):
        """Check if user is logged into Invideo."""
        if not self._check_installed():
            return False, "Invideo CLI is not installed. Run 'npm install -g invideo'."
        try:
            result = subprocess.run(
                ["invideo", "auth", "status"],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip() or result.stdout.strip()
        except Exception as e:
            return False, str(e)

    def print_login_guide(self):
        """Print instructions on how to sign in to Invideo CLI."""
        print("\n=======================================================")
        print("  INVIDEO AI AUTHENTICATION REQUIRED")
        print("=======================================================")
        print("To connect your Invideo account, run:")
        print("    invideo auth login")
        print("\nThis will open your web browser to authenticate.")
        print("Once logged in, your daily shorts can be rendered via Invideo.")
        print("=======================================================\n")

    def create_project(self, title: str):
        """Create a new project in Invideo."""
        is_logged_in, status_msg = self.check_auth()
        if not is_logged_in:
            self.print_login_guide()
            return None

        cmd = ["invideo", "project", "new", "--title", title, "--json"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if res.returncode == 0:
                data = json.loads(res.stdout)
                return data
            else:
                print(f"[Invideo Error] {res.stderr}")
                return None
        except Exception as e:
            print(f"[Invideo Error] {e}")
            return None

    def generate_short_brief(self, short_data: dict, output_prompt_file: str):
        """
        Saves a ready-to-use structured prompt file that can be pasted into
        Invideo AI Studio (AI Shorts Generator) or fed via CLI.
        """
        prompt = f"""Create a 45-second vertical 9:16 YouTube Short about: {short_data['category']}.

Voiceover Script:
"{short_data['voiceover_text']}"

Style & Visual Direction:
- Tone: Mysterious, engaging, high energy, crisp documentary style
- Visuals: Cinematic B-roll matching: {', '.join(short_data['keywords'])}
- Subtitles: Bold, center-middle animated captions with highlighted keywords
- Background Music: Subtle, atmospheric, suspenseful ambient beat (low volume)
- Aspect Ratio: 9:16 (1080x1920) for YouTube Shorts
"""
        os.makedirs(os.path.dirname(output_prompt_file), exist_ok=True)
        with open(output_prompt_file, "w", encoding="utf-8") as f:
            f.write(prompt)
        return output_prompt_file
