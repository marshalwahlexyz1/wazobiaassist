"""WhatsApp through the Twilio sandbox.

Twilio calls POST /whatsapp for each incoming message. We reply to Twilio at
once (it gives up after 15 seconds) and send the answer afterwards through the
Twilio REST API.
"""

import base64
import hashlib
import hmac
import logging
import tempfile
from pathlib import Path

import httpx

from ..config import Settings
from ..conversation import Conversation
from ..i18n import t

log = logging.getLogger(__name__)
CHANNEL = "whatsapp"
MAX_BODY = 1600  # Twilio's limit for one WhatsApp message


def split_message(body: str, limit: int = MAX_BODY) -> list[str]:
    """Splits a long answer into WhatsApp-sized parts, at paragraph or line breaks
    where possible, so nothing is cut off."""
    parts = []
    while len(body) > limit:
        cut = max(body.rfind("\n\n", 0, limit), body.rfind("\n", 0, limit), body.rfind(" ", 0, limit))
        if cut <= 0:
            cut = limit
        parts.append(body[:cut].rstrip())
        body = body[cut:].lstrip()
    return parts + [body] if body else parts


def valid_signature(auth_token: str, url: str, params: dict, signature: str) -> bool:
    """Twilio's X-Twilio-Signature check (HMAC-SHA1 of URL + sorted params)."""
    payload = url + "".join(f"{k}{params[k]}" for k in sorted(params))
    digest = hmac.new(auth_token.encode(), payload.encode(), hashlib.sha1).digest()
    return hmac.compare_digest(base64.b64encode(digest).decode(), signature or "")


class WhatsApp:
    def __init__(self, settings: Settings, conversation: Conversation):
        self.s = settings
        self.conversation = conversation
        self.auth = (settings.twilio_sid, settings.twilio_token)

    @property
    def enabled(self) -> bool:
        return bool(self.s.twilio_sid and self.s.twilio_token)

    def send(self, to: str, body: str, media_url: str | None = None) -> None:
        parts = split_message(body) or [""]
        for i, part in enumerate(parts):
            data = {"From": self.s.twilio_whatsapp_from, "To": to, "Body": part}
            if media_url and i == len(parts) - 1:
                data["MediaUrl"] = media_url
            r = httpx.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{self.s.twilio_sid}/Messages.json",
                data=data, auth=self.auth, timeout=30,
            )
            if r.status_code >= 300:
                log.error("Twilio send failed: %s %s", r.status_code, r.text[:300])

    def process(self, form: dict) -> None:
        """Runs in the background after Twilio's webhook call has returned."""
        sender = form.get("From", "")
        text = form.get("Body", "")
        media_type = form.get("MediaContentType0", "")
        with tempfile.TemporaryDirectory() as tmp:
            audio_path = None
            if int(form.get("NumMedia", "0") or 0) > 0 and media_type.startswith("audio"):
                r = httpx.get(form["MediaUrl0"], auth=self.auth, follow_redirects=True, timeout=60)
                r.raise_for_status()
                audio_path = str(Path(tmp) / "voice.audio")
                Path(audio_path).write_bytes(r.content)
            elif int(form.get("NumMedia", "0") or 0) > 0 and not text:
                text = ""  # an image or document: handled as "unsupported"
            replies = self.conversation.handle(CHANNEL, sender, text=text, audio_path=audio_path)

        store = self.conversation.store
        user = store.get_user(store.user_hash(CHANNEL, sender))
        lang = user["language"] if user else None
        for reply in replies:
            body = reply.text
            if reply.interaction_id:
                body += "\n\n" + t(lang, "rate")
            media_url = None
            if reply.audio_path and self.s.public_base_url:
                media_url = f"{self.s.public_base_url}/media/{Path(reply.audio_path).name}"
            self.send(sender, body, media_url)
