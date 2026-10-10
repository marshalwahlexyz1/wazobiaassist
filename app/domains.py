"""Domain plug-in folders and retrieval over their documents.

Each folder in domains/ is one domain:

    domains/<name>/domain.json      {"title", "description", "keywords": [...]}
    domains/<name>/instructions.md  how to answer + safety rules for this domain
    domains/<name>/docs/*.md|*.txt  curated source documents; first line may be
                                    "Source: NIMC (https://nimc.gov.ng)"

Adding a domain means adding a folder. No code changes. Files starting with
"_" (drafts, notes) and files still containing {{VERIFY}} are ignored.
"""

import json
import logging
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger(__name__)

CHUNK_CHARS = 700
UNVERIFIED = "{{VERIFY}}"  # documents with this marker are never used
_WORD = re.compile(r"[a-z0-9]+")


def words(text: str) -> list[str]:
    return _WORD.findall(text.lower())


@dataclass
class Chunk:
    text: str
    source: str


@dataclass
class Domain:
    name: str
    title: str
    description: str
    keywords: list[str]
    instructions: str
    chunks: list[Chunk] = field(default_factory=list)
    tool: str = ""  # e.g. "nafdac": answered by a database lookup instead of documents


def _read_doc(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8").strip()
    first, _, rest = text.partition("\n")
    if first.lower().startswith("source:"):
        return first.split(":", 1)[1].strip(), rest.strip()
    return path.stem, text


def _chunk(text: str, source: str) -> list[Chunk]:
    """Splits on blank lines and packs paragraphs into ~CHUNK_CHARS pieces."""
    chunks, current = [], ""
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        if current and len(current) + len(para) > CHUNK_CHARS:
            chunks.append(Chunk(current, source))
            current = ""
        current = f"{current}\n\n{para}".strip()
    if current:
        chunks.append(Chunk(current, source))
    return chunks


def load_domains(root: Path) -> dict[str, Domain]:
    domains = {}
    for folder in sorted(p for p in root.iterdir() if (p / "domain.json").exists()):
        meta = json.loads((folder / "domain.json").read_text(encoding="utf-8"))
        instructions = folder / "instructions.md"
        domain = Domain(
            name=folder.name,
            title=meta["title"],
            description=meta["description"],
            keywords=[k.lower() for k in meta.get("keywords", [])],
            instructions=instructions.read_text(encoding="utf-8") if instructions.exists() else "",
            tool=meta.get("tool", ""),
        )
        for doc in sorted((folder / "docs").glob("*")):
            if doc.suffix in (".md", ".txt") and not doc.name.startswith("_"):
                source, text = _read_doc(doc)
                if UNVERIFIED in text:
                    log.warning("Skipping %s: it still contains %s markers", doc, UNVERIFIED)
                    continue
                domain.chunks += _chunk(text, source)
        log.info("Domain %s: %d chunks", domain.name, len(domain.chunks))
        domains[domain.name] = domain
    return domains


def keyword_scores(question: str, domains: dict[str, Domain]) -> dict[str, int]:
    """Counts domain keywords in the (English) question. Multi-word keywords
    match as phrases."""
    q = " " + " ".join(words(question)) + " "
    return {
        name: sum(1 for k in d.keywords if f" {' '.join(words(k))} " in q)
        for name, d in domains.items()
    }


class Retriever:
    """Embedding search when a model is configured, keyword (BM25) search otherwise."""

    def __init__(self, domains: dict[str, Domain], embedding_model: str = ""):
        self.domains = domains
        self.encoder = None
        self.vectors = {}
        if embedding_model:
            try:
                from sentence_transformers import SentenceTransformer

                self.encoder = SentenceTransformer(embedding_model)
                for name, d in domains.items():
                    if d.chunks:
                        # e5 models expect "passage: " / "query: " prefixes
                        self.vectors[name] = self.encoder.encode(
                            [f"passage: {c.text}" for c in d.chunks], normalize_embeddings=True
                        )
            except Exception:
                log.exception("Embedding model unavailable; using keyword search")
                self.encoder = None

    def search(self, domain: str, question: str, k: int = 4) -> list[Chunk]:
        chunks = self.domains[domain].chunks
        if not chunks:
            return []
        if self.encoder is not None and domain in self.vectors:
            q = self.encoder.encode([f"query: {question}"], normalize_embeddings=True)[0]
            scores = self.vectors[domain] @ q
            order = sorted(range(len(chunks)), key=lambda i: -scores[i])
            return [chunks[i] for i in order[:k]]
        return self._bm25(chunks, question, k)

    @staticmethod
    def _bm25(chunks: list[Chunk], question: str, k: int) -> list[Chunk]:
        docs = [words(c.text) for c in chunks]
        avg = sum(map(len, docs)) / len(docs)
        df = Counter(w for d in docs for w in set(d))
        n = len(docs)
        q = set(words(question))

        def score(d: list[str]) -> float:
            tf = Counter(d)
            return sum(
                math.log(1 + (n - df[w] + 0.5) / (df[w] + 0.5))
                * tf[w] * 2.2 / (tf[w] + 1.2 * (0.25 + 0.75 * len(d) / avg))
                for w in q if w in tf
            )

        ranked = sorted(range(n), key=lambda i: -score(docs[i]))
        return [chunks[i] for i in ranked[:k] if score(docs[i]) > 0] or [chunks[i] for i in ranked[:k]]
