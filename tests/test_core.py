import re
from pathlib import Path

import pytest

from app.assistant import Assistant
from app.channels.whatsapp import valid_signature
from app.config import LANGUAGES, ROOT, Settings
from app.conversation import Conversation, parse_language, parse_rating
from app.domains import Retriever, keyword_scores, load_domains
from app.messages import TEXT
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
    assert set(domains) == {"agriculture", "health", "education", "civic", "money", "products", "laws"}
    assert domains["products"].tool == "nafdac"
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


def test_unclear_voice_note_asks_again_and_is_not_logged(convo):
    convo.handle("telegram", "u1", text="hi")
    convo.handle("telegram", "u1", text="1")
    convo.assistant.asr.transcribe = lambda path, lang: "ƙara ƙara ƙara ƙara ƙara ƙara ƙara"
    assert convo.handle("telegram", "u1", audio_path="voice.ogg")[0].text == TEXT["ha"]["unclear"]

    def no_audio(path, lang):
        raise ValueError("Soundfile is either not in the correct format or is malformed")
    convo.assistant.asr.transcribe = no_audio
    assert convo.handle("telegram", "u1", audio_path="voice.ogg")[0].text == TEXT["ha"]["unclear"]
    assert convo.store.db.execute("SELECT COUNT(*) FROM interactions").fetchone()[0] == 0


def test_is_unclear_keeps_real_questions():
    from app.assistant import is_unclear
    assert not is_unclear("menene aikin hukumar efcc wajen yaƙi da cin hanci?")
    assert not is_unclear("báwo ni mo ṣe lè forúkọsílẹ̀ fún káàdì ìdìbò?")
    assert is_unclear("mafiyar ƙasa ƙasa ƙasa ƙasa ƙasa ƙasa ƙasa ƙasa")
    assert is_unclear("")



def test_question_written_in_another_language_is_translated_from_it(convo, monkeypatch):
    from app.langdetect import written_language

    assert written_language("Ta yaya zan kare kaina daga cutar zazzabin cizon sauro?") == "ha"
    assert written_language("Báwo ni mo ṣe lè forúkọ sílẹ̀ fún káàdì ìdìbò?") == "yo"
    assert written_language("Kedu ka m ga esi nweta NIN?") == "ig"
    for english in ("How i fit protect myself from malaria?", "Is Indomie NAFDAC registered?",
                    "I'm looking for my NIN, can you help me get it?"):
        assert written_language(english) is None

    seen = []
    real_ask = convo.assistant.ask
    monkeypatch.setattr(convo.assistant, "ask", lambda lang, **kw: seen.append(lang) or real_ask(lang, **kw))
    convo.handle("web", "u1", text="hello")
    convo.handle("web", "u1", text="4")  # 4 = English
    convo.handle("web", "u1", text="Ta yaya zan kare kaina daga cutar zazzabin cizon sauro?")
    convo.handle("web", "u1", text="How do I check my NIN?")
    assert seen == ["ha", "en"]
    rows = convo.store.db.execute("SELECT language FROM interactions ORDER BY id").fetchall()
    assert [r["language"] for r in rows] == ["ha", "en"]


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


# --- store, messages, twilio -----------------------------------------------------------

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


def test_english_routing_questions_route_correctly(settings):
    """The English rows of the routing test must pass on keywords alone."""
    import csv

    a = Assistant(settings)
    a.llm.chat = lambda messages, max_tokens=400: "other"  # model only decides when keywords can't
    rows = csv.DictReader((ROOT / "tests" / "routing_questions.csv").open(encoding="utf-8"))
    wrong = [(r["question"], a.route(r["question"])) for r in rows
             if r["language"] == "en" and a.route(r["question"]) != r["expected"]]
    assert not wrong, wrong


def test_no_tts_model_means_text_only(settings, tmp_path):
    from app.speech import MmsTTS

    settings.tts_models["ig"] = ""
    assert MmsTTS(settings).speak("Ndewo", "ig", tmp_path / "x.ogg") is None


# --- WhatsApp message splitting ------------------------------------------------

def test_split_message_keeps_all_text_within_limit():
    from app.channels.whatsapp import split_message

    body = "\n\n".join(f"{i}. " + "word " * 80 for i in range(1, 8))  # ~2,900 characters
    parts = split_message(body, 1600)
    assert len(parts) == 2 and all(len(p) <= 1600 for p in parts)
    assert " ".join(parts).split() == body.split()
    assert split_message("short") == ["short"]


def test_whatsapp_replies_from_the_number_the_user_wrote_to(settings, convo, monkeypatch):
    from app.channels.whatsapp import WhatsApp

    sent = []
    monkeypatch.setattr("app.channels.whatsapp.httpx.post", lambda url, data, **kw: sent.append(data)
                        or type("R", (), {"status_code": 201, "text": ""})())
    wa = WhatsApp(settings, convo)
    wa.process({"From": "whatsapp:+234800", "To": "whatsapp:+14155238886", "Body": "hi"})
    assert sent and all(d["From"] == "whatsapp:+14155238886" and d["To"] == "whatsapp:+234800" for d in sent)


# --- concurrency -----------------------------------------------------------------

def test_different_users_are_answered_in_parallel(convo, monkeypatch):
    import threading
    import time

    real_ask = convo.assistant.ask
    inside, both_inside = [0], threading.Event()
    guard = threading.Lock()

    def slow_ask(*args, **kwargs):
        with guard:
            inside[0] += 1
            if inside[0] == 2:
                both_inside.set()
        both_inside.wait(timeout=2)  # only returns early if the other user is also inside
        return real_ask(*args, **kwargs)

    monkeypatch.setattr(convo.assistant, "ask", slow_ask)
    for user in ("a", "b"):
        convo.handle("telegram", user, text="hi")
        convo.handle("telegram", user, text="4")
    start = time.monotonic()
    threads = [threading.Thread(target=convo.handle, args=("telegram", u), kwargs={"text": "CBN grant fee"})
               for u in ("a", "b")]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    assert both_inside.is_set() and time.monotonic() - start < 1.5


def test_server_refuses_empty_salt_outside_mock(monkeypatch, tmp_path):
    import importlib
    import sys

    monkeypatch.setenv("MOCK", "0")
    monkeypatch.setenv("ID_SALT", "")
    monkeypatch.setenv("DB_PATH", str(tmp_path / "db.sqlite"))
    sys.modules.pop("app.server", None)
    with pytest.raises(SystemExit):
        importlib.import_module("app.server")
    sys.modules.pop("app.server", None)


# --- NAFDAC product check ------------------------------------------------------

def _food_db(path):
    import sqlite3

    db = sqlite3.connect(path)
    db.execute("""CREATE TABLE food (number TEXT, number_norm TEXT, name TEXT, category TEXT,
                  subcategory TEXT, packsize TEXT, presentation TEXT, applicant TEXT,
                  manufacturer TEXT, country TEXT, issued TEXT, expiry TEXT)""")
    rows = [
        ("A8-0121", "A80121", "INDOMIE INSTANT NOODLES RELISH CHICKEN DELIGHT", "Food", "Cereals", "120G", "",
         "DUFIL PRIMA FOODS LTD", "DUFIL", "Nigeria", "31/01/2024", "30/01/2029"),
        ("A8-102316L", "A8102316L", "OZIGEO FOODS SOY MILK POWDER", "Food", "Cereals", "180", "",
         "GEORGE SOFT STIR FOODS LTD", "GEORGE", "Nigeria", "20/12/2022", "19/12/2024"),
        ("01-0241", "010241", "GOLDEN PENNY SEMOVITA", "Food", "Cereals", "1KG", "",
         "FLOUR MILLS OF NIGERIA PLC.", "FMN", "Nigeria", "26/01/2023", "25/01/2028"),
        ("A1-9999", "A19999", "GOLDEN PENNY EASYBAKE FLOUR", "Food", "Cereals", "50KG", "",
         "EAGLE FLOUR", "EAGLE", "Nigeria", "26/01/2023", "25/01/2028"),
    ]
    db.executemany("INSERT INTO food VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    db.commit()
    db.close()


GREENBOOK_ROW = {"product_name": "Emzor Paracetamol Tablet## (check description)", "strength": "500 mg",
                 "NAFDAC": "04-0411", "expiry_date": "2028-03-27", "status": "Active",
                 "ingredient": {"ingredient_name": "Paracetamol"}, "form": {"name": "Tablet"},
                 "applicant": {"name": "Emzor Pharmaceutical Industries Limited"}}


def _checker(tmp_path, greenbook_rows=(), fail=False):
    from app.products import FoodDatabase, Greenbook, ProductChecker

    _food_db(tmp_path / "food.sqlite")
    calls = []

    def fetch(term):
        calls.append(term)
        if fail:
            raise RuntimeError("down")
        return list(greenbook_rows)

    return ProductChecker(FoodDatabase(tmp_path / "food.sqlite"), Greenbook(fetch=fetch)), calls


def test_product_found_in_greenbook(tmp_path):
    from datetime import date

    pc, calls = _checker(tmp_path, [GREENBOOK_ROW])
    text, sources = pc.check("Is Emzor paracetamol registered with NAFDAC?", "Emzor paracetamol",
                             today=date(2026, 10, 10))
    assert "«Emzor Paracetamol Tablet»" in text and "04-0411" in text
    assert "valid until 27 March 2028" in text and "##" not in text
    assert sources == ["NAFDAC Greenbook"] and calls == ["emzor paracetamol"]


def test_expired_food_registration_by_number(tmp_path):
    from datetime import date

    pc, _ = _checker(tmp_path)
    text, _ = pc.check("Check NAFDAC number a8-102316l", "", today=date(2026, 10, 10))
    assert "OZIGEO FOODS SOY MILK POWDER" in text and "expired on 19 December 2024" in text


def test_only_best_matches_are_listed(tmp_path):
    pc, _ = _checker(tmp_path)
    text, _ = pc.check("Is Golden Penny semovita registered?", "Golden Penny semovita")
    assert "SEMOVITA" in text and "EASYBAKE" not in text


def test_not_found_is_not_called_fake_and_greenbook_outage_is_reported(tmp_path):
    pc, _ = _checker(tmp_path, fail=True)
    text, _ = pc.check("Is Super Miracle Bitters registered with NAFDAC?", "Super Miracle Bitters")
    assert "could not find «Super Miracle Bitters»" in text
    assert "does not prove the product is fake" in text and "0700-1-623322" in text
    assert "could not be reached" in text


def test_nafdac_questions_route_to_products(settings):
    a = Assistant(settings)
    assert a.route("Is Indomie NAFDAC approved?") == "products"
    assert a.route("Check reg no A4-7579 for me") == "products"
    assert a.route("I was charged 12-2026 naira") != "products"  # digits alone are not a NAFDAC number


def test_product_names_survive_translation():
    masked, kept = protect("NAFDAC lists «Golden Penny Semovita», NAFDAC number 01-0241.")
    assert "Golden Penny" not in masked
    assert restore(masked, kept) == "NAFDAC lists «Golden Penny Semovita», NAFDAC number 01-0241."


def test_full_pipeline_product_question(settings, tmp_path):
    from app.products import FoodDatabase, ProductChecker

    _food_db(tmp_path / "food.sqlite")
    a = Assistant(settings)
    a.products = ProductChecker(FoodDatabase(tmp_path / "food.sqlite"), None)
    r = a.ask("en", text="Is Indomie chicken noodles NAFDAC approved?")
    assert r.domain == "products" and "A8-0121" in r.answer
    assert r.sources == ["NAFDAC Food Products Database"]


# --- general knowledge, citations, translation guards ----------------------------

def test_general_questions_get_labelled_memory_answers(settings):
    a = Assistant(settings)
    a.route = lambda q: "general"
    r = a.ask("en", text="Who is the president of Nigeria?", general_note="NOTE:", off_topic_reply="MENU")
    assert r.domain == "general" and r.answer.startswith("NOTE:") and r.sources == []


def test_sensitive_general_questions_fall_back_to_the_menu(settings):
    a = Assistant(settings)
    a.route = lambda q: "general"
    a.llm.chat = lambda messages, max_tokens=400: "SAFETY"
    r = a.ask("en", text="Paracetamol dose for a child?", general_note="NOTE:", off_topic_reply="MENU")
    assert r.domain == "other" and r.answer == "MENU"


def test_made_up_citations_are_removed():
    from app.assistant import _clean_citations
    from app.domains import Chunk

    chunks = [Chunk("text", "NIMC (https://nimc.gov.ng)"), Chunk("text", "WazobiaAssist scam patterns (from CBN)")]
    assert _clean_citations("Dial *346#. (Source: NIMC)", chunks) == "Dial *346#. (Source: NIMC)"
    assert _clean_citations("I do not know. [Source: NBS]", chunks) == "I do not know."
    assert _clean_citations("See passage [1] for more. (Source: WazobiaAssist scam patterns)", chunks) \
        == "See passage for more. (Source: WazobiaAssist scam patterns)"


def test_an_answered_question_is_cut_back_to_the_question():
    from app.assistant import _looks_like_an_answer

    q = "Ta yaya zan sami lambar NIN?"
    assert _looks_like_an_answer(q, "To find your NIN, follow these steps:\n\n1. Dial *346#.\n2. Wait.")
    assert not _looks_like_an_answer(q, "How do I get my NIN number?")



def test_translation_keeps_codes_or_attaches_the_english(settings):
    a = Assistant(settings)
    a.llm.chat = lambda messages, max_tokens=400: "Kira *346# don samun NIN."
    assert a.translate("Dial *346# to get your NIN.", "en", "ha") == "Kira *346# don samun NIN."
    a.llm.chat = lambda messages, max_tokens=400: "Kira lambar don samun NIN."
    assert a.translate("Dial *346# to get your NIN.", "en", "ha").endswith("(English: Dial *346# to get your NIN.)")


def test_missing_food_list_is_said_first(tmp_path):
    from app.products import FoodDatabase, Greenbook, ProductChecker

    pc = ProductChecker(FoodDatabase(tmp_path / "missing.sqlite"), Greenbook(fetch=lambda term: []))
    text, _ = pc.check("Check NAFDAC number A8-102316L", "")
    assert text.startswith("Important: I checked only NAFDAC's list of drugs.")
    assert "Food was not checked." in text


def test_product_words_ignore_what_the_model_adds():
    from app.products import product_words

    assert product_words("Is Indomie NAFDAC registered?", "Indomie (Noodles) - Yes, NAFDAC registered") == "Indomie"
    assert product_words("Is Golden Penny semovita registered?", "") == "Golden Penny semovita"
    assert product_words("Is Indomie NAFDAC registered?", "Dangote sugar") == "Indomie"  # nothing usable: fall back


def test_indomie_question_with_a_chatty_model(tmp_path):
    from app.products import FoodDatabase, ProductChecker

    _food_db(tmp_path / "food.sqlite")
    pc = ProductChecker(FoodDatabase(tmp_path / "food.sqlite"), None)
    text, _ = pc.check("Is Indomie NAFDAC registered?", "Indomie (Noodles) - Yes, NAFDAC registered")
    assert "for «Indomie»" in text and "A8-0121" in text and "Yes," not in text


def test_github_pages_origin_may_call_the_api(monkeypatch, tmp_path):
    import importlib
    import sys

    from fastapi.testclient import TestClient

    monkeypatch.setenv("MOCK", "1")
    monkeypatch.setenv("DB_PATH", str(tmp_path / "db.sqlite"))
    sys.modules.pop("app.server", None)
    server = importlib.import_module("app.server")
    client = TestClient(server.app)
    for origin in ("https://wazobiaassist.github.io", "https://marshalwahlexyz1.github.io"):
        r = client.options("/api/ask", headers={
            "Origin": origin, "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "ngrok-skip-browser-warning",
            "Access-Control-Request-Private-Network": "true"})
        assert r.status_code == 200 and r.headers.get("access-control-allow-origin") == origin
    r = client.options("/api/ask", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    assert r.headers.get("access-control-allow-origin") is None
    sys.modules.pop("app.server", None)


def test_web_page_and_logos_are_served(monkeypatch, tmp_path):
    import importlib
    import sys

    from fastapi.testclient import TestClient

    monkeypatch.setenv("MOCK", "1")
    monkeypatch.setenv("DB_PATH", str(tmp_path / "db.sqlite"))
    sys.modules.pop("app.server", None)
    client = TestClient(importlib.import_module("app.server").app)
    page = client.get("/").text
    assert "powered by Awarri Technologies" in page
    for logo in ("fmcide", "ncair", "ondi"):
        assert f"logos/{logo}.png" in page
        assert client.get(f"/logos/{logo}.png").headers["content-type"] == "image/png"
    sys.modules.pop("app.server", None)
