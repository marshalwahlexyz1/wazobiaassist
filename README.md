# WazobiaAssist

A voice-first assistant built on **N-ATLAS**. Nigerians send a voice note in Hausa, Igbo, Yoruba or English and get a short, trustworthy answer in the same language, about agriculture, health, education, government services, or money and scams. Available on WhatsApp, Telegram and a web page.

National AI Innovation Challenge (NAIC) 2026, Problem Statement 02: Voice-First Access, Track B (Innovation & Enterprise).

## How it works

| Step | Component | Code |
|---|---|---|
| 1. Receive | Telegram bot, Twilio WhatsApp webhook, web page (FastAPI) | `app/channels/`, `app/server.py` |
| 2. Transcribe | NCAIR ASR model for the user's language (Hausa, Igbo, Yoruba, Nigerian-accented English) | `app/speech.py` |
| 3. Translate in | N-ATLaS translates the question to English | `Assistant.translate` |
| 4. Route | Domain keywords; N-ATLaS decides when keywords are unclear | `Assistant.route` |
| 5. Retrieve | Top 4 passages from that domain's curated documents (multilingual-e5 embeddings, keyword fallback) | `app/domains.py` |
| 6. Answer | N-ATLaS answers in English using only those passages and the domain's safety rules | `Assistant.answer_en` |
| 7. Translate out | N-ATLaS translates the answer; numbers, USSD codes and URLs are protected | `app/protect.py` |
| 8. Speak (optional) | Meta MMS-TTS voice note | `app/speech.py` |
| 9. Log | Anonymous SQLite log + 👍/👎 rating | `app/store.py` |

```
voice note ─► NCAIR ASR ─► N-ATLaS: translate to English ─► route to domain
          ─► retrieve passages ─► N-ATLaS: answer ─► N-ATLaS: translate back ─► reply (+ voice)
```

## Domains are plug-in folders

```
domains/<name>/domain.json       title, description, routing keywords
domains/<name>/instructions.md   answering and safety rules for this domain
domains/<name>/docs/*.md         curated official sources (first line: "Source: NIMC")
```

Adding a domain means adding a folder, with no code changes. Files starting with `_` (drafts, notes) are ignored, and so is any file that still contains `{{VERIFY}}`.

### Content status (8 Oct)

| Domain | Live documents | Waiting for review | Still to collect |
|---|---|---|---|
| money | 20 scam patterns | 5 drafts (CBN complaints, SEC schemes, FCCPC loan apps, NDIC, reporting fraud) with `{{VERIFY}}` marks | POS / wrong-transfer guidance |
| health | WHO pregnancy danger signs, WHO antenatal visits | - | NPHCDA immunisation schedule, newborn and after-delivery danger signs, malaria/fever, diarrhoea, pneumonia |
| agriculture | - | - | all (sources listed) |
| education | - | - | all (sources listed) |
| civic | - | - | all (sources listed) |

Each `docs/_SOURCES_REVIEW.md` lists the candidate sources and the facts to double-check (USSD codes, fees, dates). Until a domain has documents, the assistant says it does not know.

### Collecting and approving sources (content owners)

The build environment could not open Nigerian government sites, so source pages are fetched from the GPU server, which has normal internet:

```bash
python -m scripts.fetch_sources            # or: python -m scripts.fetch_sources health civic
```

This reads `domains/*/sources.txt` and saves each page as `docs/_fetched-<name>.md`. For each file:

1. Open the official page and check the text against it.
2. Delete menus, adverts and anything off-topic. Keep the first `Source:` line. Long manuals: keep only the relevant sections.
3. Check every number, USSD code, fee and date. Remove anything you cannot confirm.
4. Rename the file to `<name>.md`. Run `curl localhost:8080/health` after restarting to see the new document count.

To add a source, add a line `<file-name> | <Organisation> | <URL>` to the domain's `sources.txt`, or write the file by hand with a `Source:` first line.

## Run it

### Without a GPU (mock mode)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env               # set MOCK=1
uvicorn app.server:app --port 8080 # open http://localhost:8080
pytest
```

### On the GPU server

Requirements: ffmpeg, Python 3.10+, about 24 GB of GPU memory. Accept the terms on Hugging Face for N-ATLaS **and** each NCAIR ASR model, and check their exact names at https://huggingface.co/NCAIR1.

```bash
sudo apt install -y ffmpeg

# 1. Serve N-ATLaS with vLLM (in its own environment, because vLLM pins its own torch)
python -m venv .venv-vllm && .venv-vllm/bin/pip install vllm
HF_TOKEN=hf_xxx .venv-vllm/bin/vllm serve NCAIR1/N-ATLaS \
    --dtype bfloat16 --max-model-len 8192 --gpu-memory-utilization 0.75 --port 8000

# 2. Run the app (second terminal)
python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in HF_TOKEN, ID_SALT, channel keys
.venv/bin/python -m scripts.ask --lang ha --text "Ta yaya zan sami NIN?"   # test one question
.venv/bin/uvicorn app.server:app --host 0.0.0.0 --port 8080
```

`--gpu-memory-utilization 0.75` leaves room on a 24 GB card for the ASR, embedding and TTS models. On a 40 GB+ card you can raise it.

If vLLM won't install, set `LLM_BACKEND=transformers` to load N-ATLaS inside the app instead (slower).

Run both processes in `tmux` so they survive disconnects. `GET /health` shows status and document counts per domain.

### Public URL (needed for WhatsApp and the web microphone)

```bash
cloudflared tunnel --url http://localhost:8080
```

Put the `https://….trycloudflare.com` address in `PUBLIC_BASE_URL` and restart the app. Browsers only allow the microphone on https pages.

### Channels

- **Telegram:** message @BotFather, `/newbot`, put the token in `TELEGRAM_BOT_TOKEN`. The bot starts with the server.
- **WhatsApp (Twilio sandbox):** in the Twilio console, open Messaging → Try it out → WhatsApp sandbox. Put the account SID and auth token in `.env`. Set "When a message comes in" to `https://<public url>/whatsapp` (POST). Each tester must first send the sandbox's `join <code>` message to the sandbox number.
- **Web:** open the public URL.

## Users' commands

- First message: language menu (1 Hausa, 2 Igbo, 3 Yoruba, 4 English), then the privacy notice
- `👍` / `👎` after an answer: rate it (Telegram and web have buttons)
- `LANGUAGE`: change language
- `DELETE`: erase all of the user's data

## Validation evidence

```bash
python -m scripts.export_logs
```

This writes `data/interactions.csv` and prints counts by language, domain, channel and input type, the satisfaction rate and the median response time.

## Privacy and safety

- Users are stored only as a salted hash of their channel id. Phone, account and ID numbers and emails are masked before saving. Voice notes are deleted after transcription.
- The privacy notice is shown before the first question, and `DELETE` erases everything.
- Answers come only from curated documents. Each domain has safety rules (for example, health danger signs mean "go to a health facility now").
- If translation drops a number, USSD code or link, the English original is attached so the user never gets a wrong code.

## Known limitations

- N-ATLaS is weakest in Yoruba, so we answer in English first, then translate.
- Nigerian Pidgin is not supported by the model.
- NCAIR has no text-to-speech model, so spoken replies use Meta MMS-TTS and are optional. MMS may not cover every language.
- The Hausa, Igbo and Yoruba interface text in `app/i18n.py` is a draft for native-speaker review.

## Project layout

```
app/server.py          FastAPI: web page, /api/ask, /whatsapp, /health, Telegram startup
app/conversation.py    language menu, privacy, DELETE, ratings, questions (all channels)
app/assistant.py       the 9-step pipeline
app/domains.py         domain folders, routing keywords, retrieval
app/llm.py             N-ATLaS via vLLM / transformers / mock
app/speech.py          NCAIR ASR, MMS-TTS
app/protect.py         keeps numbers, USSD codes and URLs intact through translation
app/store.py           anonymous SQLite log
app/i18n.py            interface text in 4 languages
app/channels/          telegram.py, whatsapp.py
app/static/index.html  web demo page
domains/               the five domains
scripts/ask.py         ask one question from the terminal
scripts/export_logs.py evidence CSV and summary
scripts/fetch_sources.py download source pages as drafts for review
tests/                 pytest, runs without a GPU
```
