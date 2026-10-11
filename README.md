# WazobiaAssist

A voice-first assistant built on **N-ATLAS**. Nigerians send a voice note in Hausa, Igbo, Yoruba or English and get a short, trustworthy answer in the same language, about agriculture, health, education, government services, or money and scams. Available on WhatsApp, Telegram and a web page.

National AI Innovation Challenge (NAIC) 2026, Problem Statement 02: Voice-First Access, Track B (Innovation & Enterprise).

**Flagship domains: scam checking and government services**, which no other N-ATLAS project covers. Farming, health and education show that the platform scales.

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

### Content status (8 Oct, evening)

Every live document was written from official pages opened on 8 Oct 2026, and every file starts with its source links.

| Domain | Live documents | Main sources | Not covered yet |
|---|---|---|---|
| money (flagship) | 20 scam patterns; CBN complaints and fraud warnings; SEC unregistered schemes; FCCPC loan-app rules; NDIC deposit insurance; reporting fraud to EFCC/police | CBN, SEC, FCCPC, NDIC, EFCC, NPF-NCCC | wrong-transfer / fake-alert rules (CBN documents blocked automated download) |
| civic (flagship) | NIN enrolment; NIN retrieval; BVN; NIN-SIM linkage; voter registration and PVC; passport; CAC business name | NIMC, NIBSS, NCC, INEC, NIS, CAC | birth certificate, driver's licence |
| health | immunisation schedule; pregnancy danger signs; antenatal visits; newborn danger signs; mother after delivery; malaria and fever; diarrhoea; pneumonia | NPHCDA card (via UNICEF Nigeria), WHO | Federal Ministry of Health / NCDC material |
| education | JAMB profile and UTME; JAMB CAPS; WAEC; NECO; free basic education (UBE); NELFUND; exam scams | JAMB, WAEC, NECO, UBEC, NELFUND | JAMB result SMS, WAEC/NECO 2026 fraud warnings |
| agriculture | maize; fall armyworm; cowpea storage; cassava; rice; sorghum; grain storage and aflatoxin; NiMet 2026 seasonal prediction | IITA, FAO, Purdue (PICS), NAERLS, ICRISAT, NiMet | yam, millet, groundnut, soybean, livestock |
| laws | Constitution fundamental rights (ss.33–46); Police Act 2020 (arrest, bail, detention, complaints); ACJA 2015 (arrest rights); Nigeria Data Protection Act 2023; Cybercrimes Act 2015 with 2024 amendment; EFCC Act 2004; Advance Fee Fraud Act 2006; FCCPA 2018 consumer rights; Legal Aid Council (who qualifies, offices) | PLAC, FAOLEX, NDPC, NFIU, FCCPC, Legal Aid Council | lawyer review: quotes typed from scanned PDFs (Police Act, Legal Aid Act, Cybercrimes 2024 amendment), later amendments |
| products | none by design: answers come from NAFDAC's Greenbook (live) and Food Products Database (downloaded daily) | NAFDAC | cosmetics are not in either database |

**Before launch, a person must read each domain's `docs/_SOURCES_REVIEW.md`.** It lists what to double-check, for example: conflicting NIMC fees (left out), the HPV dose count, pesticides that must still be registered in Nigeria, the FCCPC court case, and dates that came only from news reports quoting an agency.

### Collecting and approving sources (content owners)

To add or refresh sources:

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

### On the GPU server (Google Cloud, NVIDIA L4)

The bot runs on one always-on Google Cloud server with an NVIDIA L4 (24 GB). No training is needed: N-ATLaS is used as released. Before you start:

- **Google Cloud:** sign up for the $300 credit at https://cloud.google.com/free, upgrade the billing account (free-trial accounts cannot use GPUs; the credit still applies), and request quota for 1 NVIDIA L4 GPU in `us-central1`. Approval can take a day.
- **Hugging Face:** with the account whose token you will use, accept the terms on all five gated models: [N-ATLaS](https://huggingface.co/NCAIR1/N-ATLaS), [Hausa-ASR](https://huggingface.co/NCAIR1/Hausa-ASR), [Igbo-ASR](https://huggingface.co/NCAIR1/Igbo-ASR), [Yoruba-ASR](https://huggingface.co/NCAIR1/Yoruba-ASR) and [NigerianAccentedEnglish](https://huggingface.co/NCAIR1/NigerianAccentedEnglish) (names checked 8 Oct). Then create a read token.
- **ngrok:** create an account at https://dashboard.ngrok.com, copy your authtoken, and claim your free fixed domain.

```bash
# 1. In Google Cloud Shell: create the server (g2-standard-8 with one L4, Deep Learning VM image)
git clone https://github.com/marshalwahlexyz1/wazobiaassist && cd wazobiaassist
bash scripts/gcp/create_vm.sh

# 2. On the server
gcloud compute ssh wazobia --zone us-central1-a
git clone https://github.com/marshalwahlexyz1/wazobiaassist && cd wazobiaassist
bash scripts/gcp/setup.sh      # first run creates .env and asks for HF_TOKEN, NGROK_AUTHTOKEN, NGROK_DOMAIN
nano .env                      # fill them in (plus Telegram/Twilio keys when ready)
bash scripts/gcp/setup.sh      # second run installs and starts everything
```

`setup.sh` installs three services that start on boot and restart themselves if they crash:

| Service | What it runs |
|---|---|
| `wazobia-vllm` | N-ATLaS on vLLM, `localhost:8000` (`--max-model-len 4096 --gpu-memory-utilization 0.8`, leaving room for the speech and embedding models) |
| `wazobia-app` | the bot, WhatsApp webhook and web page, `localhost:8080`; waits for vLLM to be ready |
| `wazobia-ngrok` | your fixed public address `https://<NGROK_DOMAIN>` → `localhost:8080` |

Day-to-day commands on the server:

```bash
journalctl -u wazobia-vllm -u wazobia-app -f                # live logs
curl -s localhost:8080/health                               # status and documents per domain
.venv/bin/python -m scripts.ask --lang ha --text "Ta yaya zan sami NIN?"   # one question, every step shown
git pull && sudo systemctl restart wazobia-app              # after a code, document or .env change
```

If vLLM runs out of GPU memory, put `VLLM_EXTRA_ARGS=--quantization fp8` in `.env` and run `sudo systemctl restart wazobia-vllm`. If vLLM won't install at all, set `LLM_BACKEND=transformers` to load N-ATLaS inside the app (slower).

Stop the server when nobody is testing, to save credit: `gcloud compute instances stop wazobia --zone us-central1-a` (start it again with `start`; the services come back by themselves).

Without Google Cloud (e.g. a rented RunPod or Lambda GPU), follow the same steps from `setup.sh` by hand.

### Public address

`PUBLIC_BASE_URL` defaults to `https://<NGROK_DOMAIN>`. It is needed for WhatsApp, for voice replies on WhatsApp, and for the web page's microphone (browsers only allow it on https). On ngrok's free plan, visitors to the web page see a one-time ngrok warning page first; WhatsApp and Telegram are not affected.

### Channels

- **Telegram:** message @BotFather, `/newbot`, put the token in `TELEGRAM_BOT_TOKEN`. The bot starts with the server.
- **WhatsApp (Twilio sandbox):** in the Twilio console, open Messaging → Try it out → WhatsApp sandbox. Put the account SID and auth token in `.env`. Set "When a message comes in" to `https://<NGROK_DOMAIN>/whatsapp` (POST). Each tester must first send the sandbox's `join <code>` message to the sandbox number.
- **Web:** open `https://<NGROK_DOMAIN>`.

## Users' commands

- First message: language menu (1 Hausa, 2 Igbo, 3 Yoruba, 4 English), then the privacy notice
- `👍` / `👎` after an answer: rate it (Telegram and web have buttons)
- `LANGUAGE`: change language
- `DELETE`: erase all of the user's data

## NAFDAC product check

Users can ask whether a product is registered with NAFDAC, by name or by NAFDAC number ("Is Emzor paracetamol registered?", "Check A8-0121"). Any question that mentions NAFDAC or contains a NAFDAC number goes to the `products` domain, which looks the product up instead of reading documents:

- **NAFDAC Greenbook** (drugs, vaccines, medical devices, veterinary, herbal products, disinfectants; about 8,900 products): searched live, the same way NAFDAC's own page searches it, with a 6-hour cache.
- **NAFDAC Food Products Database** (about 28,000 products): downloaded by `python -m scripts.update_nafdac` into `data/nafdac_food.sqlite`. `setup.sh` runs it and refreshes it daily at 03:15.

N-ATLaS pulls the product name out of the question; the answer itself is built from NAFDAC's fields (name, NAFDAC number, company, expiry date), so a number or date is never invented. Expired registrations are reported as expired. A product that isn't found is never called fake: the bot asks for the NAFDAC number on the pack and gives NAFDAC's lines (0700-1-623322 enquiries, 0800-1-623322 complaints). A product that is found comes with a reminder that fakes copy real numbers. Cosmetics are not in either database.

## Routing test

Native speakers add 10 questions per language to `tests/routing_questions.csv` (`language,question,expected`), then on the server:

```bash
.venv/bin/python -m scripts.routing_test          # or --lang ha
```

It translates and routes each question exactly like the live bot and lists the wrong routes. Fix them by adding keywords to `domains/<name>/domain.json` or sharpening its description.

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
- NCAIR has no text-to-speech model, so spoken replies use Meta MMS-TTS and are optional. MMS has Hausa, Yoruba and English voices but **no Igbo voice**, so Igbo replies are text only.
- The Hausa, Igbo and Yoruba interface text in `app/messages.py` is a draft for native-speaker review.

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
app/messages.py        interface text in 4 languages
app/channels/          telegram.py, whatsapp.py
app/static/index.html  web demo page
domains/               the five domains
scripts/ask.py         ask one question from the terminal
scripts/export_logs.py evidence CSV and summary
scripts/fetch_sources.py download source pages as drafts for review
scripts/routing_test.py check routing per language (tests/routing_questions.csv)
scripts/update_nafdac.py download NAFDAC's food product database
app/products.py        NAFDAC product check (Greenbook live search + food database)
scripts/gcp/            Google Cloud VM creation, setup and always-on services
tests/                 pytest, runs without a GPU
```
