"""Channel-independent conversation logic: language menu, privacy notice,
DELETE, ratings and questions. Telegram, WhatsApp and the web page all call
Conversation.handle()."""

import logging
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path

from .assistant import Assistant
from .config import LANGUAGES
from .messages import LANGUAGE_MENU, t
from .store import Store

log = logging.getLogger(__name__)

_LANGUAGE_WORDS = {
    "hausa": "ha", "igbo": "ig", "yoruba": "yo", "yorùbá": "yo", "english": "en",
}


def parse_language(text: str) -> str | None:
    text = text.strip().lower()
    codes = list(LANGUAGES)
    if text.isdigit() and 1 <= int(text) <= len(codes):
        return codes[int(text) - 1]
    if text.startswith("lang:") and text[5:] in LANGUAGES:
        return text[5:]
    return _LANGUAGE_WORDS.get(text)


def parse_rating(text: str) -> str | None:
    text = text.strip()
    if text.startswith("👍"):
        return "up"
    if text.startswith("👎"):
        return "down"
    return None


@dataclass
class Reply:
    text: str
    audio_path: Path | None = None
    interaction_id: int | None = None  # set on answers: channels show rating buttons
    language_menu: bool = False        # channels with buttons show the language choices


class Conversation:
    def __init__(self, assistant: Assistant, store: Store, media_dir: Path):
        self.assistant = assistant
        self.store = store
        self.media_dir = media_dir
        media_dir.mkdir(parents=True, exist_ok=True)
        self.model_lock = threading.Lock()  # one question on the GPU at a time

    def handle(self, channel: str, channel_user_id: str, text: str | None = None,
               audio_path: str | None = None, audio_seconds: float | None = None) -> list[Reply]:
        store = self.store
        uh = store.user_hash(channel, str(channel_user_id))
        user = store.get_user(uh)
        msg = (text or "").strip()

        if msg.upper().lstrip("/") == "DELETE":
            lang = user["language"] if user else None
            store.delete_user(uh)
            return [Reply(t(lang, "deleted"))]

        if user is None:
            store.create_user(uh, channel)
            return [Reply(LANGUAGE_MENU, language_menu=True)]

        if msg.lower().lstrip("/") in ("start", "language", "menu"):
            store.set_language(uh, None)
            return [Reply(LANGUAGE_MENU, language_menu=True)]

        lang = user["language"]
        if not lang or msg.startswith("lang:"):  # "lang:xx" comes from language buttons
            choice = parse_language(msg)
            if choice is None:
                return [Reply(LANGUAGE_MENU, language_menu=True)]
            store.set_language(uh, choice)
            return [Reply(t(choice, "privacy")), Reply(t(choice, "ready"))]

        if not audio_path:
            rating = parse_rating(msg)
            if rating:
                store.rate(uh, rating)
                return [Reply(t(lang, "thanks"))]
            if not msg:
                return [Reply(t(lang, "unsupported"))]

        record = {
            "channel": channel,
            "language": lang,
            "input_type": "voice" if audio_path else "text",
            "audio_seconds": audio_seconds,
        }
        try:
            with self.model_lock:
                result = self.assistant.ask(
                    lang, text=msg, audio_path=audio_path,
                    off_topic_reply=t(lang, "off_topic"),
                    speak_to=self.media_dir / f"{uuid.uuid4().hex}.ogg",
                )
        except Exception as exc:  # failures are logged too: they are part of the evidence
            log.exception("question failed")
            store.log(uh, **record, error=repr(exc)[:500])
            return [Reply(t(lang, "error"))]

        iid = store.log(
            uh, **record,
            transcript=result.transcript,
            question_en=result.question_en,
            domain=result.domain,
            answer_en=result.answer_en,
            answer=result.answer,
            sources="; ".join(result.sources),
            latency_ms=result.latency_ms,
        )
        body = result.answer
        if audio_path:
            body = f"{t(lang, 'heard')} \"{result.transcript}\"\n\n{body}"
        return [Reply(body[:3900], audio_path=result.audio_path, interaction_id=iid)]
