"""Anonymous SQLite log of users and interactions: the validation evidence."""

import hashlib
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_hash TEXT PRIMARY KEY,
    channel TEXT NOT NULL,
    language TEXT,
    first_seen TEXT NOT NULL,
    last_interaction_id INTEGER
);
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    user_hash TEXT NOT NULL,
    channel TEXT NOT NULL,          -- telegram / whatsapp / web
    language TEXT NOT NULL,
    input_type TEXT NOT NULL,       -- voice / text
    audio_seconds REAL,
    transcript TEXT,                -- what we heard (or the typed text)
    question_en TEXT,
    domain TEXT,
    answer_en TEXT,
    answer TEXT,                    -- answer in the user's language
    sources TEXT,
    latency_ms INTEGER,
    error TEXT,
    rating TEXT                     -- up / down / NULL
);
"""

# Phone, account and ID numbers and email addresses are masked before saving.
_DIGITS_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s-]{8,}\d)(?!\d)")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def redact(text: str | None) -> str | None:
    if not text:
        return text
    return _DIGITS_RE.sub("[number]", _EMAIL_RE.sub("[email]", text))


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, path: Path, salt: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.salt = salt
        self.lock = threading.Lock()

    def user_hash(self, channel: str, channel_user_id: str) -> str:
        return hashlib.sha256(f"{self.salt}:{channel}:{channel_user_id}".encode()).hexdigest()[:16]

    def _write(self, sql: str, params: tuple) -> sqlite3.Cursor:
        with self.lock:
            cur = self.db.execute(sql, params)
            self.db.commit()
            return cur

    def get_user(self, user_hash: str) -> sqlite3.Row | None:
        with self.lock:
            return self.db.execute("SELECT * FROM users WHERE user_hash = ?", (user_hash,)).fetchone()

    def create_user(self, user_hash: str, channel: str) -> None:
        self._write("INSERT OR IGNORE INTO users (user_hash, channel, first_seen) VALUES (?, ?, ?)",
                    (user_hash, channel, now()))

    def set_language(self, user_hash: str, lang: str | None) -> None:
        self._write("UPDATE users SET language = ? WHERE user_hash = ?", (lang, user_hash))

    def log(self, user_hash: str, **fields) -> int:
        for key in ("transcript", "question_en", "answer_en", "answer"):
            fields[key] = redact(fields.get(key))
        fields.update(created_at=now(), user_hash=user_hash)
        cols = ", ".join(fields)
        marks = ", ".join("?" for _ in fields)
        iid = self._write(f"INSERT INTO interactions ({cols}) VALUES ({marks})", tuple(fields.values())).lastrowid
        self._write("UPDATE users SET last_interaction_id = ? WHERE user_hash = ?", (iid, user_hash))
        return iid

    def rate(self, user_hash: str, rating: str, interaction_id: int | None = None) -> bool:
        """Rates the given interaction, or the user's latest one. Only the person
        who asked can rate an answer."""
        if interaction_id is None:
            user = self.get_user(user_hash)
            interaction_id = user["last_interaction_id"] if user else None
        if interaction_id is None:
            return False
        cur = self._write("UPDATE interactions SET rating = ? WHERE id = ? AND user_hash = ?",
                          (rating, interaction_id, user_hash))
        return cur.rowcount > 0

    def delete_user(self, user_hash: str) -> None:
        self._write("DELETE FROM interactions WHERE user_hash = ?", (user_hash,))
        self._write("DELETE FROM users WHERE user_hash = ?", (user_hash,))
