"""Telegram bot (long polling, started by the FastAPI server)."""

import asyncio
import logging
import tempfile
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from ..conversation import Conversation, Reply
from ..messages import LANGUAGE_LABELS, t

log = logging.getLogger(__name__)
CHANNEL = "telegram"


def _language_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(label, callback_data=f"lang:{code}")] for code, label in LANGUAGE_LABELS.items()]
    )


def _rating_buttons(lang: str, iid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t(lang, "up"), callback_data=f"rate:{iid}:up"),
        InlineKeyboardButton(t(lang, "down"), callback_data=f"rate:{iid}:down"),
    ]])


def build_telegram(token: str, conversation: Conversation) -> Application:
    store = conversation.store

    def language_of(user_id: int) -> str | None:
        user = store.get_user(store.user_hash(CHANNEL, str(user_id)))
        return user["language"] if user else None

    async def send(message, replies: list[Reply], user_id: int) -> None:
        lang = language_of(user_id)
        for r in replies:
            markup = None
            if r.language_menu:
                markup = _language_buttons()
            elif r.interaction_id:
                markup = _rating_buttons(lang, r.interaction_id)
            await message.reply_text(r.text, reply_markup=markup)
            if r.audio_path:
                with open(r.audio_path, "rb") as f:
                    await message.reply_voice(f)

    async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.effective_message
        user_id = update.effective_user.id
        voice = message.voice or message.audio
        text = message.text or message.caption

        if voice and language_of(user_id):
            await message.reply_text(t(language_of(user_id), "listening"))
        with tempfile.TemporaryDirectory() as tmp:
            audio_path = None
            if voice:
                audio_path = str(Path(tmp) / "voice.ogg")
                await (await voice.get_file()).download_to_drive(audio_path)
            replies = await asyncio.to_thread(
                conversation.handle, CHANNEL, str(user_id), text=text, audio_path=audio_path,
                audio_seconds=voice.duration if voice else None,
            )
        await send(message, replies, user_id)

    async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = query.from_user.id
        data = query.data or ""
        await query.edit_message_reply_markup(reply_markup=None)
        if data.startswith("rate:"):
            _, iid, rating = data.split(":")
            store.rate(store.user_hash(CHANNEL, str(user_id)), rating, int(iid))
            await query.answer(t(language_of(user_id), "thanks"))
            return
        await query.answer()
        replies = await asyncio.to_thread(conversation.handle, CHANNEL, str(user_id), text=data)
        await send(query.message, replies, user_id)

    app = Application.builder().token(token).concurrent_updates(True).build()
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.ALL, on_message))
    return app
