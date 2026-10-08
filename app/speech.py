"""Speech in (NCAIR ASR models) and optional speech out (Meta MMS-TTS)."""

import logging
import subprocess
import threading
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
        # Questions from different users run in parallel threads; one lock per
        # language keeps each model to one call at a time.
        self.locks = {lang: threading.Lock() for lang in settings.asr_models}

    def _load(self, lang: str):
        if lang not in self.pipes:
            import torch
            from transformers import pipeline

            name = self.settings.asr_models[lang]
            log.info("Loading ASR %s", name)
            gpu = _device() == 0
            self.pipes[lang] = pipeline(
                "automatic-speech-recognition", model=name, device=0 if gpu else -1,
                torch_dtype=torch.float16 if gpu else torch.float32,
                token=self.settings.hf_token or None,
            )
        return self.pipes[lang]

    def warm_up(self) -> None:
        """Loads every language's model, so the first voice note isn't slow."""
        for lang in self.settings.asr_models:
            try:
                with self.locks[lang]:
                    self._load(lang)
            except Exception:
                log.exception("Could not preload ASR for %s", lang)

    def transcribe(self, audio_path: str, lang: str) -> str:
        with self.locks[lang]:
            return self._load(lang)(audio_path, chunk_length_s=30)["text"].strip()


class MockASR:
    def warm_up(self) -> None:
        pass

    def transcribe(self, audio_path: str, lang: str) -> str:
        return "Someone sent me a message that CBN is giving grants and I should pay a fee to receive it"


class MmsTTS:
    """Writes an .ogg (Opus) voice note, the format Telegram and WhatsApp play
    as a voice message. Returns None if the language's model is unavailable."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.models = {}
        self.lock = threading.Lock()

    def speak(self, text: str, lang: str, out_path: Path) -> Path | None:
        if not self.settings.tts_models.get(lang):
            return None  # no voice model for this language
        with self.lock:
            return self._speak(text, lang, out_path)

    def _speak(self, text: str, lang: str, out_path: Path) -> Path | None:
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
