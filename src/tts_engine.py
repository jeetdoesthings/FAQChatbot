"""
Text-to-Speech (TTS) Engine (Unit U4)
Converts chatbot responses into fluent spoken voice audio.
"""
import os
import re
import hashlib
import subprocess
from pathlib import Path
from typing import Optional
from gtts import gTTS

from src.config import AUDIO_DIR

class TTSEngine:
    def __init__(self, output_dir: Path = AUDIO_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def clean_text_for_speech(self, text: str) -> str:
        """Removes markdown syntax, URLs, bullet formatting, and hashes so voice sounds natural."""
        # Remove URLs
        cleaned = re.sub(r'http\S+|www\.\S+', 'link', text)
        # Remove markdown headers and formatting
        cleaned = re.sub(r'[#*_`~>\[\]\(\)]', ' ', cleaned)
        # Remove list markers
        cleaned = re.sub(r'^\s*[-*•\d\.]+\s+', '', cleaned, flags=re.MULTILINE)
        # Collapse multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def synthesize(self, text: str, voice_accent: str = "co.in") -> Optional[str]:
        """
        Synthesizes speech from text and returns the path to the output audio file (.mp3).
        Falls back to macOS native `say` utility if offline.
        """
        clean_text = self.clean_text_for_speech(text)
        if not clean_text:
            return None

        # Truncate text if excessively long for speech (up to 80 words)
        words = clean_text.split()
        if len(words) > 80:
            clean_text = " ".join(words[:80]) + "... For the complete details, please read the displayed text response."

        text_hash = hashlib.md5(clean_text.encode("utf-8")).hexdigest()[:12]
        output_file = self.output_dir / f"response_{text_hash}.mp3"

        if output_file.exists() and output_file.stat().st_size > 0:
            return str(output_file)

        # Primary: gTTS
        try:
            tts = gTTS(text=clean_text, lang="en", tld=voice_accent, slow=False)
            tts.save(str(output_file))
            return str(output_file)
        except Exception as e:
            print(f"[TTSEngine Warning] gTTS failed ({e}), attempting offline fallback...")

        # Fallback 1: macOS native `say` command (if on macOS)
        try:
            aiff_file = self.output_dir / f"response_{text_hash}.aiff"
            subprocess.run(["say", "-v", "Samantha", "-o", str(aiff_file), clean_text], check=True, timeout=10)
            return str(aiff_file)
        except Exception:
            pass

        # Fallback 2: Linux `espeak` command (if installed)
        try:
            wav_file = self.output_dir / f"response_{text_hash}.wav"
            subprocess.run(["espeak", "-w", str(wav_file), clean_text], check=True, timeout=10)
            return str(wav_file)
        except Exception:
            pass

        return None

if __name__ == "__main__":
    engine = TTSEngine()
    audio_path = engine.synthesize("Welcome to the Department of Artificial Intelligence FAQ portal.")
    print(f"Generated speech audio at: {audio_path}")
