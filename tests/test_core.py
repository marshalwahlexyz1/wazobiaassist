import re
from pathlib import Path

import pytest

from app.assistant import Assistant
from app.channels.whatsapp import valid_signature
from app.config import LANGUAGES, ROOT, Settings
from app.conversation import Conversation, parse_language, parse_rating
from app.domains import Retriever, keyword_scores, load_domains
from app.i18n import TEXT
from app.protect import protect, restore
from app.store import Store, redact


@pytest.fixture
def settings(tmp_path, monkeypatch):
    monkeypatch.setenv("MOCK", "1")
    monkeypatch.setenv("DB_PATH", str(tmp_path / "db.sqlite"))
    monkeypatch.setenv("MEDIA_DIR", str(tmp_path / "media"))
    return Settings()


@pytest.fixture
def convo(settings):
    return Conversation(Assistant(settings), Store(settings.db_path, "salt"), settings.media_dir)


# --- protect / restore -------------------------------------------------------

def test_protect_keeps_codes_numbers_and_urls():
    text = "Dial *346# or visit https://nimc.gov.ng/ by 12/10/2026. Fee: 1,500 naira."
    masked, kept = protect(text)
    assert "*346#" not in masked and "nimc" not in masked and "1,500" not in masked
    assert restore(masked, kept) == text


def test_restore_tolerates_spaces_inside_placeholders():
    masked, kept = protect("Dial *346#")
    assert restore(masked.replace("[[0]]", "[[ 0 ]]"), kept) == "Dial *346#"


def test_lost_placeholder_appends_english(settings):
    a = Assistant(settings)
    a.llm.chat = lambda messages, max_tokens=400: "Kira lambar."  # model dropped [[0]]
    out = a.translate("Dial *346# to check.", "en", "ha")
    assert "*346#" in out and out.startswith("Kira lambar.")


# --- domains, routing, retrieval ------------------------------------------------

def test_all_domains_load():
    domains = load_domains(ROOT / "domains")
    assert set(domains) == {"agriculture", "health", "education", "civic", "money"}
    assert domains["money"].chunks, "money domain should ship with scam patterns"
    for d in domains.values():
        assert d.instructions and d.keywords and d.description
        assert all(not c.source.startswith("_") for c in d.chunks)  # _TODO files ignored


def test_keyword_routing(settings):
    a = Assistant(settings)
    assert a.route("How do I control fall armyworm on my maize farm?") == "agriculture"
    assert a.route("How do I get my NIN slip from NIMC?") == "civic"
    assert a.route("Someone says CBN grant, pay a fee to receive it. Is it a scam?") == "money"
    assert a.route("How do I register for JAMB UTME?") == "education"
    assert a.route("My pregnant wife has fever and bleeding") == "health"
    assert a.route("My wife is pregnant and has severe headache with blurred vision") == "health"
    a.llm.chat = lambda messages, max_tokens=400: "education"  # ties go to the model
    assert a.route("Can I use my BVN to register for JAMB?") == "education"


def test_keyword_scores_match_phrases():
    domains = load_domains(ROOT / "domains")
    assert keyword_scores("someone sent a credit alert", domains)["money"] >= 2


def test_bm25_finds_relevant_scam_pattern():
    domains = load_domains(ROOT / "domains")
    hits = Retriever(domains).search("money", "they said they sent money by mistake, send it back", 2)
    assert any("Wrong transfer" in c.text for c in hits)


# --- conversation flow -------------------------------------------------------------

def test_full_flow(convo):
    first = convo.handle("whatsapp", "+234800", text="hello")
    assert first[0].language_menu
    chosen = convo.handle("whatsapp", "+234800", text="1")  # 1 = Hausa
    assert chosen[0].text == TEXT["ha"]["privacy"]
    answer = convo.handle("whatsapp", "+234800", audio_path="voice.ogg", audio_seconds=4)
    assert answer[0].interaction_id and answer[0].text.startswith(TEXT["ha"]["heard"])
    thanks = convo.handle("whatsapp", "+234800", text="👍🏾")
    assert thanks[0].text == TEXT["ha"]["thanks"]
    row = convo.store.db.execute("SELECT * FROM interactions").fetchone()
    assert (row["channel"], row["language"], row["domain"], row["rating"]) == ("whatsapp", "ha", "money", "up")


def test_language_button_switches_language(convo):
    convo.handle("telegram", "7", text="/start")
    convo.handle("telegram", "7", text="lang:yo")
    out = convo.handle("telegram", "7", text="lang:ig")  # switching later works too
    assert out[0].text == TEXT["ig"]["privacy"]


def test_delete_erases_everything(convo):
    convo.handle("web", "abcdefgh", text="hi")
    convo.handle("web", "abcdefgh", text="english")
    convo.handle("web", "abcdefgh", text="Is this CBN grant real?")
    out = convo.handle("web", "abcdefgh", text="DELETE")
    assert out[0].text == TEXT["en"]["deleted"]
    assert convo.store.db.execute("SELECT COUNT(*) FROM interactions").fetchone()[0] == 0
    assert convo.store.db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0


def test_failures_are_logged(convo):
    convo.handle("web", "abcdefgh", text="hi")
    convo.handle("web", "abcdefgh", text="4")

    def boom(*a, **k):
        raise RuntimeError("GPU down")

    convo.assistant.ask = boom
    out = convo.handle("web", "abcdefgh", text="question")
    assert out[0].text == TEXT["en"]["error"]
    assert "GPU down" in convo.store.db.execute("SELECT error FROM interactions").fetchone()[0]


def test_parsers():
    assert [parse_language(x) for x in ("1", "2", "3", "4", "Yoruba", "lang:ig", "5", "hi")] == \
        ["ha", "ig", "yo", "en", "yo", "ig", None, None]
    assert parse_rating("👍") == "up" and parse_rating("👎🏽") == "down" and parse_rating("ok") is None


# --- store, i18n, twilio -----------------------------------------------------------

def test_redact():
    out = redact("Call 08012345678 or +234 801 234 5678, a.b@x.com, send N50,000")
    assert "08012345678" not in out and "801 234" not in out and "a.b@x.com" not in out
    assert "N50,000" in out


def test_only_owner_can_rate(tmp_path):
    s = Store(tmp_path / "db", "salt")
    a, b = s.user_hash("web", "a"), s.user_hash("web", "b")
    s.create_user(a, "web")
    iid = s.log(a, channel="web", language="en", input_type="text")
    assert not s.rate(b, "up", iid)
    assert s.rate(a, "up", iid)


def test_every_language_has_every_string():
    assert set(TEXT) == set(LANGUAGES)
    for lang in TEXT:
        assert set(TEXT[lang]) == set(TEXT["en"]), lang


def test_twilio_signature():
    # Expected value computed with the official twilio library (RequestValidator).
    url = "https://mycompany.com/myapp.php?foo=1&bar=2"
    params = {"CallSid": "CA1234567890ABCDE", "Caller": "+12349013030", "Digits": "1234",
              "From": "+12349013030", "To": "+18005551212"}
    assert valid_signature("12345", url, params, "0/KCTR6DLpKmkAf8muzZqo1nDgQ=")
    assert not valid_signature("12345", url, params, "wrong")


# --- source collection script ---------------------------------------------------

def test_html_to_text_keeps_content_and_drops_menus():
    from scripts.fetch_sources import html_to_text

    html = """<html><head><style>p{}</style><script>var x=1;</script></head><body>
    <nav><a>Home</a> <a>About us and everything else in this long menu</a></nav>
    <h1>Getting your NIN</h1>
    <p>Visit any NIMC enrolment centre with a document that proves who you are and where you live.</p>
    <ul><li>Birth certificate</li><li>Old ID</li></ul>
    <footer>Copyright notice that is long enough to pass the length filter easily</footer></body></html>"""
    text = html_to_text(html)
    assert "Visit any NIMC enrolment centre" in text
    assert "- Birth certificate" in text
    assert "var x" not in text and "About us" not in text and "Copyright" not in text


def test_every_sources_file_parses():
    from scripts.fetch_sources import read_sources

    for path in (ROOT / "domains").glob("*/sources.txt"):
        for name, items in read_sources(path).items():
            assert re.fullmatch(r"[a-z0-9-]+", name), name
            assert all(url.startswith("https://") for _, url in items)


def test_documents_with_verify_markers_are_skipped(tmp_path):
    d = tmp_path / "x"
    (d / "docs").mkdir(parents=True)
    (d / "domain.json").write_text('{"title": "X", "description": "x", "keywords": []}')
    (d / "docs" / "ok.md").write_text("Source: A\n\nChecked text.")
    (d / "docs" / "bad.md").write_text("Source: B\n\nFee is 20 naira {{VERIFY}}.")
    (d / "docs" / "_draft-c.md").write_text("Source: C\n\nDraft.")
    chunks = load_domains(tmp_path)["x"].chunks
    assert [c.source for c in chunks] == ["A"]
