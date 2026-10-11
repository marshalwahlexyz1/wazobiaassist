"""FastAPI server: web demo page, WhatsApp webhook, health check, and the
Telegram bot running alongside.

    uvicorn app.server:app --host 0.0.0.0 --port 8080
"""

import asyncio
import logging
import re
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, Response

from .assistant import Assistant
from .products import download_food_db
from .config import LANGUAGES, Settings
from .conversation import Conversation
from .channels.whatsapp import WhatsApp, valid_signature
from .store import Store

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("wazobia")

settings = Settings()
if not settings.mock and settings.id_salt in ("", "change-me"):
    # An empty salt makes user hashes reversible (anyone can hash every phone number).
    raise SystemExit("Set ID_SALT in .env to a long random string, e.g. the output of: openssl rand -hex 32")
store = Store(settings.db_path, settings.id_salt)
assistant = Assistant(settings)
conversation = Conversation(assistant, store, settings.media_dir)
whatsapp = WhatsApp(settings, conversation)
STATIC = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the four ASR models in the background, so the first voice note in each
    # language isn't slow.
    asyncio.get_running_loop().run_in_executor(None, assistant.asr.warm_up)
    # The NAFDAC food list is normally downloaded by setup.sh; fetch it now if it is missing.
    if not settings.mock and not settings.nafdac_food_db.exists():
        asyncio.get_running_loop().run_in_executor(None, _download_food_list)
    telegram = None
    if settings.telegram_token:
        from .channels.telegram import build_telegram

        telegram = build_telegram(settings.telegram_token, conversation)
        await telegram.initialize()
        await telegram.start()
        await telegram.updater.start_polling()
        log.info("Telegram bot started")
    log.info("WhatsApp %s", "enabled" if whatsapp.enabled else "disabled (no Twilio credentials)")
    yield
    if telegram:
        await telegram.updater.stop()
        await telegram.stop()
        await telegram.shutdown()


def _download_food_list() -> None:
    try:
        total = download_food_db(settings.nafdac_food_db, say=log.info)
        log.info("NAFDAC food list ready: %d products", total)
    except Exception:
        log.exception("NAFDAC food list download failed; food products can't be checked yet")


app = FastAPI(title="WazobiaAssist", lifespan=lifespan)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mock": settings.mock,
        "llm": settings.llm_model,
        "domains": {name: len(d.chunks) for name, d in assistant.domains.items()},
        "nafdac_food_list": settings.nafdac_food_db.exists(),
    }


# --- web demo page -----------------------------------------------------------

@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.post("/api/ask")
async def api_ask(
    session_id: str = Form(...),
    lang: str = Form(...),
    text: str = Form(""),
    audio: UploadFile | None = File(None),
):
    if lang not in LANGUAGES or not re.fullmatch(r"[\w-]{8,64}", session_id):
        raise HTTPException(400, "bad request")
    # The web page has its own language picker, so set the language directly.
    uh = store.user_hash("web", session_id)
    store.create_user(uh, "web")
    store.set_language(uh, lang)
    with tempfile.TemporaryDirectory() as tmp:
        audio_path = None
        if audio is not None:
            audio_path = str(Path(tmp) / "voice.webm")
            Path(audio_path).write_bytes(await audio.read())
        replies = await asyncio.to_thread(
            conversation.handle, "web", session_id, text=text, audio_path=audio_path
        )
    r = replies[-1]
    return {
        "answer": r.text,
        "interaction_id": r.interaction_id,
        "audio_url": f"/media/{Path(r.audio_path).name}" if r.audio_path else None,
    }


@app.post("/api/rate")
def api_rate(session_id: str = Form(...), interaction_id: int = Form(...), rating: str = Form(...)):
    if rating not in ("up", "down"):
        raise HTTPException(400, "bad rating")
    ok = store.rate(store.user_hash("web", session_id), rating, interaction_id)
    return {"ok": ok}


@app.get("/media/{name}")
def media(name: str):
    if not re.fullmatch(r"[0-9a-f]{32}\.ogg", name):
        raise HTTPException(404)
    path = settings.media_dir / name
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path, media_type="audio/ogg")


# --- WhatsApp (Twilio) ---------------------------------------------------------

def _process_whatsapp(form: dict) -> None:
    try:
        whatsapp.process(form)
    except Exception:
        log.exception("WhatsApp message failed")


@app.post("/whatsapp")
async def whatsapp_webhook(request: Request, background: BackgroundTasks):
    if not whatsapp.enabled:
        raise HTTPException(503, "WhatsApp not configured")
    form = dict(await request.form())
    if settings.public_base_url:
        url = settings.public_base_url + "/whatsapp"
        if not valid_signature(settings.twilio_token, url, form, request.headers.get("X-Twilio-Signature")):
            raise HTTPException(403, "bad signature")
    background.add_task(_process_whatsapp, form)
    return Response('<?xml version="1.0" encoding="UTF-8"?><Response></Response>', media_type="application/xml")
