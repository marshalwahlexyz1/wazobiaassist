"""Speech in (NCAIR ASR models) and optional speech out (Meta MMS-TTS)."""

import logging
import subprocess
from pathlib import Path

from .config import Settings

log = logging.getLogger(__name__)


def _device():
    import torch

    return 0 if torch.cuda.is_available() else -1


class NcairASR:
    """One NCAIR speech-recognition model per language, loaded on first use.
    ffmpeg must be installed: it decodes .ogg/.webm/.amr voice notes."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.pipes = {}

    def transcribe(self, audio_path: str, lang: str) -> str:
        if lang not in self.pipes:
            from transformers import pipeline

            name = self.settings.asr_models[lang]
            log.info("Loading ASR %s", name)
            self.pipes[lang] = pipeline(
                "automatic-speech-recognition", model=name, device=_device(),
                token=self.settings.hf_token or None,
            )
        return self.pipes[lang](audio_path, chunk_length_s=30)["text"].strip()


class MockASR:
    def transcribe(self, audio_path: str, lang: str) -> str:
        return "Someone sent me a message that CBN is giving grants and I should pay a fee to receive it"


class MmsTTS:
    """Writes an .ogg (Opus) voice note, the format Telegram and WhatsApp play
    as a voice message. Returns None if the language's model is unavailable."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.models = {}

    def speak(self, text: str, lang: str, out_path: Path) -> Path | None:
        if lang in self.models and self.models[lang] is None:
            return None  # this language's model failed to load before
        try:
            if lang not in self.models:
                from transformers import pipeline

                self.models[lang] = pipeline(
                    "text-to-speech", model=self.settings.tts_models[lang], device=_device()
                )
            result = self.models[lang](text)
            import numpy as np
            import scipy.io.wavfile

            wav = out_path.with_suffix(".wav")
            audio = np.asarray(result["audio"]).squeeze()
            scipy.io.wavfile.write(wav, result["sampling_rate"], audio)
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libopus", str(out_path)],
                check=True,
            )
            wav.unlink(missing_ok=True)
            return out_path
        except Exception:
            log.exception("TTS failed for %s; sending text only", lang)
            self.models.setdefault(lang, None)
            return None


def make_asr(settings: Settings):
    return MockASR() if settings.mock else NcairASR(settings)


def make_tts(settings: Settings):
    if settings.mock or not settings.tts_enabled:
        return None
    return MmsTTS(settings)
