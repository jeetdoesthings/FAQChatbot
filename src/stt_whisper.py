"""
Whisper Speech-to-Text (STT) Module (Unit U3)
Transcribes user voice input into clean text using OpenAI Whisper.
"""
import os
import tempfile
import numpy as np
import scipy.io.wavfile as wavfile
from typing import Union, Tuple, Optional
import whisper

class WhisperSTT:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WhisperSTT, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_size: str = "base"):
        if self._initialized:
            return

        self.model_size = model_size
        print(f"[WhisperSTT] Loading Whisper model: '{self.model_size}'...")
        # Device auto-selection (mps/cuda/cpu)
        self.model = whisper.load_model(self.model_size)
        self._initialized = True
        print(f"[WhisperSTT] Model '{self.model_size}' loaded successfully.")

    def transcribe(self, audio_input: Union[str, Tuple[int, np.ndarray], None]) -> str:
        """
        Transcribes speech to text.
        audio_input can be:
          - str: Path to an audio file (.wav, .mp3, etc.)
          - tuple: (sample_rate, numpy_array) from Gradio microphone
          - None: returns empty string
        """
        if audio_input is None:
            return ""

        temp_path = None
        try:
            # Handle Gradio tuple format (sample_rate, audio_data)
            if isinstance(audio_input, tuple):
                sr, data = audio_input
                # Convert to mono if stereo
                if len(data.shape) > 1:
                    data = data.mean(axis=1)

                # Normalize to int16 if float
                if data.dtype == np.float32 or data.dtype == np.float64:
                    data = np.clip(data * 32767, -32768, 32767).astype(np.int16)

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    temp_path = f.name
                    wavfile.write(temp_path, sr, data)
                audio_file = temp_path
            else:
                audio_file = str(audio_input)

            if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
                return ""

            result = self.model.transcribe(audio_file, fp16=False, language="en")
            transcription = result.get("text", "").strip()
            return transcription

        except Exception as e:
            print(f"[WhisperSTT Error] Failed to transcribe: {e}")
            return ""
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

if __name__ == "__main__":
    stt = WhisperSTT(model_size="tiny")
    print("Whisper STT ready for voice recognition.")
