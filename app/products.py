"""NAFDAC product check: is this food, drug or other product registered?

Two official NAFDAC sources:
  - the Greenbook (greenbook.nafdac.gov.ng): drugs, vaccines, medical devices,
    veterinary, herbal products and disinfectants. Searched live, the same way
    NAFDAC's own web page searches it.
  - the Food Products Database (nafdac.gov.ng/food-products-database): downloaded
    once a day into SQLite by scripts/update_nafdac.py.

Answers are built from the database fields with fixed sentences, never written
freely by the model, so a registration number or date can't be invented.
"""

import html
import logging
import re
import sqlite3
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import httpx

log = logging.getLogger(__name__)

GREENBOOK_URL = "https://greenbook.nafdac.gov.ng/"
# NAFDAC's own enquiry and complaint lines, from nafdac.gov.ng (checked 10 Oct 2026).
ENQUIRIES = "0700-1-623322"
COMPLAINTS = "0800-1-623322"

# NAFDAC numbers look like 04-0411, A4-7579 or A8-102316L.
NAFDAC_NO = re.compile(r"\b([A-Z]{0,2}\d{1,2}-\d{3,7}[A-Z]?)\b", re.IGNORECASE)
LETTER_NO = re.compile(r"\b[A-Z]{1,2}\d{1,2}-\d{3,7}[A-Z]?\b", re.IGNORECASE)

_STOP = set("""
a an the is are was this that these those my our your his her it its of for to in on with by from and or
please check tell me know whether if can you i we do does did has have registered registration approved
approval approve nafdac number no reg product products drug drugs medicine food fake real original genuine
counterfeit valid still legit legal sold sell buy bought want ask about brand called named
yes no not none true false
""".split())


def norm_no(number: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", number.upper())


def tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _STOP and len(w) > 1]


def product_words(question: str, model_guess: str = "") -> str:
    """The product name to search for, using only words the user actually said.

    The model is asked to copy the product name out of the question, but it
    sometimes answers instead ("Indomie - Yes, NAFDAC registered"). Words it adds
    are dropped; if nothing is left, the question's own product words are used."""
    asked = re.findall(r"[A-Za-z0-9][A-Za-z0-9'&.-]*", question)
    asked_lower = {w.lower().strip(".'") for w in asked}
    guess = {t for t in tokens(model_guess) if t in asked_lower}
    keep = guess or set(tokens(question))
    words = [w.strip(".'") for w in asked if w.lower().strip(".'") in keep]
    return " ".join(dict.fromkeys(words))  # in the user's order, no repeats


def mentions_nafdac(text: str) -> bool:
    """True when a question is about NAFDAC registration."""
    return bool(re.search(r"\bnafdac\b", text, re.IGNORECASE) or LETTER_NO.search(text))


@dataclass
class Match:
    name: str
    number: str
    holder: str
    detail: str          # e.g. "Tablet, 500 mg" or "Cereals and Cereal Products"
    expiry: date | None
    status: str          # NAFDAC's status text, if any
    source: str          # "NAFDAC Greenbook" or "NAFDAC Food Products Database"
    score: float = 0.0

    def state(self, today: date) -> str:
        if self.status and self.status.lower() not in ("active", ""):
            return f"NAFDAC status: {self.status}"
        if self.expiry and self.expiry < today:
            return f"registration expired on {self.expiry:%d %B %Y}"
        if self.expiry:
            return f"registration valid until {self.expiry:%d %B %Y}"
        return "registered (no expiry date shown)"


def _date(value: str | None) -> date | None:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime((value or "").strip()[:10], fmt).date()
        except ValueError:
            continue
    return None


def _score(query_tokens: list[str], *fields: str) -> float:
    """Share of the query's words found in the product's name and company."""
    if not query_tokens:
        return 0.0
    hay = set(tokens(" ".join(fields)))
    return sum(1 for t in query_tokens if t in hay) / len(query_tokens)


class FoodDatabase:
    """The downloaded NAFDAC Food Products Database (see scripts/update_nafdac.py)."""

    def __init__(self, path: Path):
        self.path = path

    @property
    def available(self) -> bool:
        return self.path.exists()

    def _rows(self, sql: str, params: tuple) -> list[sqlite3.Row]:
        with sqlite3.connect(f"file:{self.path}?mode=ro", uri=True) as db:
            db.row_factory = sqlite3.Row
            return db.execute(sql, params).fetchall()

    @staticmethod
    def _match(row: sqlite3.Row, score: float) -> Match:
        detail = ", ".join(x for x in (row["subcategory"], row["packsize"] and f"pack {row['packsize']}") if x)
        return Match(html.unescape(row["name"]), row["number"], html.unescape(row["applicant"]), detail,
                     _date(row["expiry"]), "", "NAFDAC Food Products Database", score)

    def by_number(self, number: str) -> list[Match]:
        if not self.available:
            return []
        rows = self._rows("SELECT * FROM food WHERE number_norm = ? LIMIT 5", (norm_no(number),))
        return [self._match(r, 1.0) for r in rows]

    def by_name(self, query: str, limit: int = 3) -> list[Match]:
        q = tokens(query)
        if not self.available or not q:
            return []
        longest = sorted(q, key=len, reverse=True)[:3]
        where = " OR ".join("name LIKE ?" for _ in longest)
        rows = self._rows(f"SELECT * FROM food WHERE {where} LIMIT 3000", tuple(f"%{t}%" for t in longest))
        scored = [(_score(q, r["name"], r["applicant"], r["manufacturer"]), r) for r in rows]
        # Need most of the user's words to match, so "milk" alone doesn't list every milk.
        good = [(s, r) for s, r in scored if s >= 0.6]
        good.sort(key=lambda sr: (-sr[0], -(_date(sr[1]["expiry"]) or date.min).toordinal()))
        return [self._match(r, s) for s, r in good[:limit]]


class Greenbook:
    """Live search of NAFDAC's Greenbook, with a small cache."""

    def __init__(self, url: str = GREENBOOK_URL, fetch=None, ttl: int = 6 * 3600):
        self.url = url
        self._fetch = fetch or self._http
        self.ttl = ttl
        self.cache: dict[str, tuple[float, list[dict]]] = {}

    def _http(self, term: str) -> list[dict]:
        params = {
            "draw": "1", "start": "0", "length": "10", "search[value]": term,
            "columns[0][data]": "product_name", "columns[0][name]": "product_name",
            "columns[0][searchable]": "true",
        }
        headers = {"X-Requested-With": "XMLHttpRequest", "Accept": "application/json",
                   "User-Agent": "WazobiaAssist (NAIC 2026)"}
        for attempt in range(2):  # NAFDAC's server sometimes drops a connection; retry once
            try:
                r = httpx.get(self.url, params=params, timeout=15, headers=headers)
                r.raise_for_status()
                return r.json().get("data", [])
            except httpx.TransportError:
                if attempt:
                    raise
                time.sleep(1)
        return []

    def search(self, term: str) -> list[dict]:
        key = term.lower().strip()
        hit = self.cache.get(key)
        if hit and time.time() - hit[0] < self.ttl:
            return hit[1]
        rows = self._fetch(term)
        self.cache[key] = (time.time(), rows)
        return rows

    @staticmethod
    def to_match(row: dict, score: float) -> Match:
        name = html.unescape((row.get("product_name") or "").split("##")[0].strip(" #*"))
        form = (row.get("form") or {}).get("name") or ""
        detail = ", ".join(x for x in (form, row.get("strength") or "") if x)
        return Match(name, row.get("NAFDAC") or "", (row.get("applicant") or {}).get("name") or "",
                     detail, _date(row.get("expiry_date")), row.get("status") or "",
                     "NAFDAC Greenbook", score)

    def lookup(self, query: str, number: str | None, limit: int = 3) -> list[Match]:
        q = tokens(query)
        if not number and not q:
            return []
        rows = self.search(number or " ".join(q))
        if not rows and not number and len(q) > 1:
            rows = self.search(max(q, key=len))  # retry with the most specific word
        if number:
            exact = [r for r in rows if norm_no(r.get("NAFDAC") or "") == norm_no(number)]
            return [self.to_match(r, 1.0) for r in exact[:limit]]
        scored = [(_score(q, r.get("product_name") or "", (r.get("applicant") or {}).get("name") or "",
                          (r.get("ingredient") or {}).get("ingredient_name") or ""), r) for r in rows]
        good = sorted([(s, r) for s, r in scored if s >= 0.6], key=lambda sr: -sr[0])
        return [self.to_match(r, s) for s, r in good[:limit]]


FOOD_PAGE = "https://nafdac.gov.ng/food-products-database/"


def download_food_db(target: Path, say=print) -> int:
    """Downloads NAFDAC's Food Products Database into SQLite at `target`.

    The public table on FOOD_PAGE loads its rows from the site in chunks of 3,000;
    they are fetched one at a time, politely, and the local copy is replaced only
    when the download is complete. Returns the number of products saved."""
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    db = sqlite3.connect(tmp)
    db.execute("""CREATE TABLE food (number TEXT, number_norm TEXT, name TEXT, category TEXT,
                  subcategory TEXT, packsize TEXT, presentation TEXT, applicant TEXT,
                  manufacturer TEXT, country TEXT, issued TEXT, expiry TEXT)""")
    total = 0
    headers = {"User-Agent": "WazobiaAssist (NAIC 2026; daily refresh)"}
    with httpx.Client(headers=headers, timeout=90, follow_redirects=True) as client:
        page = client.get(FOOD_PAGE).text
        m = re.search(r'https:[^"]*admin-ajax\.php\?action=wp_ajax_ninja_tables_public_action[^"]*', page)
        if not m:
            raise RuntimeError("Could not find the data link on the NAFDAC page; its layout may have changed.")
        base = re.sub(r"&chunk_number=\d+", "", m.group(0).replace("\\/", "/").replace("\\u0026", "&"))
        for chunk in range(100):
            rows = client.get(f"{base}&chunk_number={chunk}").json()
            if not rows:
                break
            values = []
            for row in rows:
                v = {k: html.unescape(x) if isinstance(x, str) else x for k, x in row.get("value", row).items()}
                values.append((v.get("nafdacnumber", ""), norm_no(v.get("nafdacnumber", "")),
                               v.get("productname", ""), v.get("category", ""), v.get("subcategory", ""),
                               v.get("packsize", ""), v.get("presentation", ""), v.get("applicantname", ""),
                               v.get("manufacturer", ""), v.get("country", ""), v.get("issuedate", ""),
                               v.get("expirydate", "")))
            db.executemany("INSERT INTO food VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", values)
            total += len(values)
            say(f"chunk {chunk}: {len(values)} products")
            time.sleep(1)  # be gentle with NAFDAC's server
    if total == 0:
        db.close()
        tmp.unlink(missing_ok=True)
        raise RuntimeError("No products downloaded; keeping the old copy.")
    db.execute("CREATE INDEX idx_number ON food(number_norm)")
    db.commit()
    db.close()
    tmp.replace(target)
    return total


class ProductChecker:
    def __init__(self, food: FoodDatabase, greenbook: Greenbook | None):
        self.food = food
        self.greenbook = greenbook

    def check(self, question: str, product: str = "", today: date | None = None) -> tuple[str, list[str]]:
        """Answers in English. `product` is the product name the model pulled out of
        the question; the NAFDAC number, if any, is read from the question itself."""
        today = today or date.today()
        found = NAFDAC_NO.search(question)
        number = found.group(1).upper() if found else None
        query = product_words(question, product)
        matches: list[Match] = []
        notes: list[str] = []
        food_missing = False

        if self.greenbook:
            try:
                matches += self.greenbook.lookup(query, number)
            except Exception as exc:
                log.warning("Greenbook lookup failed: %r", exc)
                notes.append("NAFDAC's drug database (Greenbook) could not be reached just now, "
                              "so only the food database was checked.")
        if self.food.available:
            matches += self.food.by_number(number) if number else self.food.by_name(query)
        else:
            food_missing = True

        matches.sort(key=lambda m: -m.score)
        if matches:  # show only the best-matching products, not weaker partial matches
            best = matches[0].score
            matches = [m for m in matches if m.score >= best - 0.01]
        sources = sorted({m.source for m in matches}) or ["NAFDAC Greenbook", "NAFDAC Food Products Database"]
        checked = f"checked {today:%d %B %Y}"
        what = f"NAFDAC number {number}" if number else f"«{query}»"

        if not matches:
            lines = [
                f"I could not find {what} in NAFDAC's registered product lists for drugs and food.",
                "This does not prove the product is fake: the name may be written differently.",
                "Send me the NAFDAC number printed on the pack, or ask NAFDAC directly on "
                f"{ENQUIRIES} (enquiries) or report a suspicious product on {COMPLAINTS} (complaints).",
            ]
        else:
            lines = [f"NAFDAC lists {'this' if len(matches[:3]) == 1 else 'these'} for {what}:"]
            for i, m in enumerate(matches[:3], 1):
                detail = f" ({m.detail})" if m.detail else ""
                holder = f", registered to {m.holder}" if m.holder else ""
                lines.append(f"{i}. «{m.name}»{detail}, NAFDAC number {m.number}{holder}: {m.state(today)}.")
            lines.append("Check that the NAFDAC number on your pack is exactly the same and the company name matches. "
                         "Fake products often copy real numbers. If anything looks different, report it to NAFDAC "
                         f"on {COMPLAINTS}.")
        if food_missing:
            # Put this first, in short sentences, so it survives translation.
            lines.insert(0, "Important: I checked only NAFDAC's list of drugs. "
                            "The list of food products is not ready on this server. Food was not checked.")
        lines += notes
        lines.append(f"(Source: {' and '.join(sources)}, {checked})")
        return "\n".join(lines), sources
