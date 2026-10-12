"""Settings, read from environment variables (or a .env file)."""

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass

ROOT = Path(__file__).resolve().parent.parent

# Order matters: it is the numbered language menu shown to users.
LANGUAGES = {
    "ha": "Hausa",
    "ig": "Igbo",
    "yo": "Yoruba",
    "en": "English",
}


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


@dataclass
class Settings:
    # "mock" runs everything with canned outputs so the team can work without a GPU.
    mock: bool = field(default_factory=lambda: _env("MOCK", "0") == "1")
    hf_token: str = field(default_factory=lambda: _env("HF_TOKEN"))

    # Language model. "vllm" talks to `vllm serve NCAIR1/N-ATLaS` (recommended);
    # "transformers" loads the model inside this process instead.
    llm_backend: str = field(default_factory=lambda: _env("LLM_BACKEND", "vllm"))
    llm_model: str = field(default_factory=lambda: _env("LLM_MODEL", "NCAIR1/N-ATLaS"))
    vllm_url: str = field(default_factory=lambda: _env("VLLM_URL", "http://localhost:8000/v1"))
    load_in_4bit: bool = field(default_factory=lambda: _env("LOAD_IN_4BIT", "0") == "1")

    # NCAIR speech-recognition models, one per language.
    asr_models: dict = field(
        default_factory=lambda: {
            "ha": _env("ASR_MODEL_HA", "NCAIR1/Hausa-ASR"),
            "ig": _env("ASR_MODEL_IG", "NCAIR1/Igbo-ASR"),
            "yo": _env("ASR_MODEL_YO", "NCAIR1/Yoruba-ASR"),
            "en": _env("ASR_MODEL_EN", "NCAIR1/NigerianAccentedEnglish"),
        }
    )

    # Optional spoken replies (NCAIR has no text-to-speech model yet).
    tts_enabled: bool = field(default_factory=lambda: _env("TTS_ENABLED", "0") == "1")
    tts_models: dict = field(
        default_factory=lambda: {
            "ha": _env("TTS_MODEL_HA", "facebook/mms-tts-hau"),
            "ig": _env("TTS_MODEL_IG", ""),  # Meta MMS has no Igbo voice: Igbo replies are text only
            "yo": _env("TTS_MODEL_YO", "facebook/mms-tts-yor"),
            "en": _env("TTS_MODEL_EN", "facebook/mms-tts-eng"),
        }
    )

    # Retrieval. Set to "" to use keyword search only.
    embedding_model: str = field(
        default_factory=lambda: _env("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    )
    top_k: int = field(default_factory=lambda: int(_env("TOP_K", "4")))
    domains_dir: Path = field(default_factory=lambda: Path(_env("DOMAINS_DIR", str(ROOT / "domains"))))

    # Channels
    telegram_token: str = field(default_factory=lambda: _env("TELEGRAM_BOT_TOKEN"))
    twilio_sid: str = field(default_factory=lambda: _env("TWILIO_ACCOUNT_SID"))
    twilio_token: str = field(default_factory=lambda: _env("TWILIO_AUTH_TOKEN"))
    twilio_whatsapp_from: str = field(
        default_factory=lambda: _env("TWILIO_WHATSAPP_FROM", "whatsapp:+17372324091")
    )
    # Public https address of this server (defaults to https://NGROK_DOMAIN). Needed for
    # Twilio request signature checks and for sending voice replies on WhatsApp.
    public_base_url: str = field(
        default_factory=lambda: (_env("PUBLIC_BASE_URL")
                                 or (f"https://{_env('NGROK_DOMAIN')}" if _env("NGROK_DOMAIN") else "")).rstrip("/")
    )

    # NAFDAC product check: the food database is downloaded by scripts/update_nafdac.py;
    # the Greenbook (drugs) is searched live. Set NAFDAC_LIVE=0 to skip the live search.
    nafdac_food_db: Path = field(
        default_factory=lambda: Path(_env("NAFDAC_FOOD_DB", str(ROOT / "data" / "nafdac_food.sqlite")))
    )
    nafdac_live: bool = field(default_factory=lambda: _env("NAFDAC_LIVE", "1") == "1")

    # Web pages on other addresses allowed to call the API (the GitHub Pages copies).
    cors_origins: list = field(default_factory=lambda: [
        o.strip().rstrip("/") for o in _env("CORS_ORIGINS", "https://wazobiaassist.github.io,https://marshalwahlexyz1.github.io").split(",") if o.strip()
    ])

    db_path: Path = field(default_factory=lambda: Path(_env("DB_PATH", str(ROOT / "data" / "interactions.db"))))
    media_dir: Path = field(default_factory=lambda: Path(_env("MEDIA_DIR", str(ROOT / "data" / "media"))))
    # Users are stored only as a salted hash of their channel id.
    id_salt: str = field(default_factory=lambda: _env("ID_SALT", "change-me"))
