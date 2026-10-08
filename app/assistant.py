"""The answering pipeline: transcribe -> translate in -> route -> retrieve ->
answer -> translate out -> (speak)."""

import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from .config import LANGUAGES, Settings
from .domains import Chunk, Retriever, keyword_scores, load_domains
from .llm import make_llm
from .protect import protect, restore
from .speech import make_asr, make_tts

TRANSLATE_PROMPT = """TASK: translate
Translate the user's text from {src} to {dst}.
Keep every placeholder like [[0]] or [[1]] exactly as it is.
Output only the translation, nothing else."""

ROUTE_PROMPT = """TASK: route
Decide which topic the user's question belongs to.
{topics}
- other: greetings, thanks, or anything not covered above
Reply with only the topic name, one word."""

ANSWER_PROMPT = """TASK: answer
You are WazobiaAssist, a trustworthy assistant for ordinary Nigerians.
Topic: {title}

{instructions}

GENERAL RULES:
- Use ONLY the passages below. If they do not contain the answer, say you do not know and name the official body the person should ask.
- Never invent phone numbers, prices, dates, websites or USSD codes.
- Keep the answer under 120 words, in simple English.
- Use numbered steps for procedures.
- End with the source in brackets, for example (Source: NIMC).

PASSAGES:
{passages}"""


@dataclass
class Result:
    transcript: str
    question_en: str
    domain: str
    answer_en: str
    answer: str
    sources: list[str] = field(default_factory=list)
    latency_ms: int = 0
    audio_path: Path | None = None


class Assistant:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.domains = load_domains(settings.domains_dir)
        embed = "" if settings.mock else settings.embedding_model
        self.retriever = Retriever(self.domains, embed)
        self.llm = make_llm(settings)
        self.asr = make_asr(settings)
        self.tts = make_tts(settings)

    # --- steps -----------------------------------------------------------

    def translate(self, text: str, src: str, dst: str) -> str:
        if src == dst:
            return text
        masked, kept = protect(text)
        out = self.llm.chat([
            {"role": "system", "content": TRANSLATE_PROMPT.format(src=LANGUAGES[src], dst=LANGUAGES[dst])},
            {"role": "user", "content": masked},
        ])
        restored = restore(out, kept)
        missing = [k for k in kept if k not in restored]
        if missing and dst != "en":
            # A number, code or link was lost in translation: keep the English
            # original too, so the user never gets a wrong or missing code.
            restored += f"\n\n(English: {text})"
        return restored

    def route(self, question_en: str) -> str:
        scores = keyword_scores(question_en, self.domains)
        ranked = sorted(scores.items(), key=lambda kv: -kv[1])
        if ranked and ranked[0][1] >= 2 and (len(ranked) == 1 or ranked[0][1] > ranked[1][1]):
            return ranked[0][0]  # clear keyword winner: skip the model call
        topics = "\n".join(f"- {n}: {d.description}" for n, d in self.domains.items())
        out = self.llm.chat([
            {"role": "system", "content": ROUTE_PROMPT.format(topics=topics)},
            {"role": "user", "content": question_en},
        ], max_tokens=5)
        for word in re.findall(r"[a-z]+", out.lower()):
            if word in self.domains or word == "other":
                return word
        return ranked[0][0] if ranked and ranked[0][1] > 0 else "other"

    def answer_en(self, domain: str, question_en: str) -> tuple[str, list[Chunk]]:
        d = self.domains[domain]
        chunks = self.retriever.search(domain, question_en, self.settings.top_k)
        passages = "\n\n".join(f"[{i}] (Source: {c.source})\n{c.text}" for i, c in enumerate(chunks, 1))
        answer = self.llm.chat([
            {"role": "system", "content": ANSWER_PROMPT.format(
                title=d.title, instructions=d.instructions.strip(),
                passages=passages or "(no documents yet)")},
            {"role": "user", "content": question_en},
        ])
        return answer, chunks

    # --- full pipeline ---------------------------------------------------

    def ask(self, lang: str, text: str | None = None, audio_path: str | None = None,
            off_topic_reply: str = "", speak_to: Path | None = None) -> Result:
        start = time.monotonic()
        transcript = self.asr.transcribe(audio_path, lang) if audio_path else (text or "").strip()
        if not transcript:
            raise ValueError("empty question")
        question_en = self.translate(transcript, lang, "en")
        domain = self.route(question_en)
        if domain == "other":
            answer_en, chunks, answer = "", [], off_topic_reply
        else:
            answer_en, chunks = self.answer_en(domain, question_en)
            answer = self.translate(answer_en, "en", lang)
        audio = None
        if self.tts and speak_to and answer:
            audio = self.tts.speak(answer, lang, speak_to)
        return Result(
            transcript=transcript,
            question_en=question_en,
            domain=domain,
            answer_en=answer_en,
            answer=answer,
            sources=sorted({c.source for c in chunks}),
            latency_ms=int((time.monotonic() - start) * 1000),
            audio_path=audio,
        )
