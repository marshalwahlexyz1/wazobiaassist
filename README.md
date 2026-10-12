<p align="center"><img src="docs/logo.svg" alt="WazobiaAssist" width="360"></p>

# WazobiaAssist

**Government answers in one place, in your language.**

To get a NIN, check a BVN, register to vote, check whether a drug is NAFDAC-registered, or know your rights when the police stop you, a Nigerian today has to find the right agency (NIMC, NIBSS, INEC, NAFDAC, CBN, JAMB, the Police Act…), find its website, and read it in English. Millions of people never get past the first step.

WazobiaAssist puts those answers in one place. Ask by **voice note or text in Hausa, Igbo, Yorùbá or Nigerian English**, on the **web or Telegram**, and it answers in the same language from the agencies' own published information or official registers, and names the agency it came from. It is built on **N-ATLaS**, Nigeria's multilingual language model, and NCAIR's speech recognition models.

National AI Innovation Challenge (NAIC) 2026, Problem Statement 02: Voice-First Access, Track B (Innovation & Enterprise).

## Try it

| Channel | How |
|---|---|
| Web | **https://wazobiaassist.github.io**: pick a language, then type or tap the microphone |
| Telegram | **@WazobiaAssist_bot**: send any message, pick a language, then send a voice note or text |

## What it does

One assistant, many agencies:

| Ask about | Answers come from |
|---|---|
| Identity and registration: NIN, BVN, NIN-SIM linking, voter registration and PVC, passport, business names | NIMC, NIBSS, NCC, INEC, Nigeria Immigration Service, CAC |
| Is this product registered? | NAFDAC Greenbook (live search) and NAFDAC Food Products Database |
| Your rights: arrest, bail, detention, data privacy, consumer rights | Constitution, Police Act 2020, ACJA 2015, NDPA 2023, FCCPA 2018, Legal Aid Council |
| Money and scams: loan apps, "grants" that ask for a fee, Ponzi schemes, reporting fraud | CBN, SEC, FCCPC, NDIC, EFCC |
| Exams and schooling: JAMB, WAEC, NECO, free basic education, student loans | JAMB, WAEC, NECO, UBEC, NELFUND |
| Health: immunisation, pregnancy and newborn danger signs, malaria | NPHCDA, WHO |
| Farming: planting times, pests, storage, the 2026 rainy season | IITA, FAO, NAERLS, NiMet |


**1. Checks a product against NAFDAC's registers.** Ask "Is Emzor paracetamol registered?" or read out the NAFDAC number on the pack. The assistant searches NAFDAC's Greenbook (about 8,900 drugs, vaccines, medical devices and herbal products, searched live) and NAFDAC's Food Products Database (28,481 foods, refreshed daily) and replies with the product name, NAFDAC number, company and whether the registration is valid or expired. Example: NAFDAC number A8-102316L comes back as "registration expired on 19 December 2024". It never calls a product fake just because it isn't found.

**2. Explains your legal rights with the exact law.** "Can the police arrest me for my brother's debt?" or "Can a company share my data?" is answered from the Constitution's fundamental rights, the Police Act 2020, the Administration of Criminal Justice Act 2015, the Nigeria Data Protection Act 2023, the Cybercrimes Act, the EFCC Act, the Advance Fee Fraud Act and the consumer rights in the FCCPA 2018. Answers name the law and section and point to free help from the Legal Aid Council. The 270 passages quoted from these laws were checked against the source texts.

**3. Walks you through government procedures with codes checked against the official pages.** Getting or retrieving a NIN (`*346#`, NIMC), checking a BVN (`*565*0#`, NIBSS), registering to vote and collecting a PVC (INEC), applying for a passport (Nigeria Immigration Service), registering a business name (CAC), and creating a JAMB profile (SMS to 55019 or 66019).

**It also answers everyday questions** on health (the NPHCDA immunisation schedule and WHO danger signs for pregnancy, newborns, fever, diarrhoea and pneumonia), farming (IITA, FAO, NAERLS and ICRISAT guides, NiMet's 2026 forecast), education (JAMB, WAEC, NECO, UBE, NELFUND) and money safety (CBN, SEC, FCCPC, NDIC and EFCC guidance plus 20 common scam patterns).

**General questions** about Nigeria that no agency document covers ("Who is the president?", "What is the capital?") are answered from N-ATLaS's own knowledge, clearly labelled *"General knowledge, not from an official source. It may be out of date"*. For health doses, legal and money questions, it refuses to answer from memory and points to the right agency instead.

**Why the answers can be trusted:**
- Official answers come only from curated agency documents or live registers, and say "I don't know" otherwise.
- Every official answer names the agency. Sources that were not in the retrieved passages are removed from the answer.
- Numbers, USSD codes, NAFDAC numbers and links are checked after translation; if one is lost, the English original is attached.
- Health answers send danger signs to a health facility; legal answers say they are information, not legal advice.

## How it works

| Step | Component | Code |
|---|---|---|
| 1. Receive | Web page (FastAPI API) and Telegram bot | `app/server.py`, `app/channels/` |
| 2. Transcribe | NCAIR ASR model for the user's language (Hausa, Igbo, Yoruba, Nigerian-accented English) | `app/speech.py` |
| 3. Translate in | N-ATLaS translates the question to English. A typed question is translated from the language it is written in, even if the user picked another one | `Assistant.translate`, `app/langdetect.py` |
| 4. Route | Domain keywords; N-ATLaS decides when keywords are unclear, including "general" (answered from memory, labelled) | `Assistant.route` |
| 5. Retrieve | Top 4 passages from that domain's curated documents (multilingual-e5 embeddings, keyword fallback) | `app/domains.py` |
| 6. Answer | N-ATLaS answers in English using only those passages and the domain's safety rules | `Assistant.answer_en` |
| 7. Translate out | N-ATLaS translates the answer; numbers, USSD codes and URLs are checked and the English is attached if one is lost | `app/protect.py` |
| 8. Speak (optional) | Meta MMS-TTS voice note | `app/speech.py` |
| 9. Log | Anonymous SQLite log + 👍/👎 rating | `app/store.py` |

```
voice note ─► NCAIR ASR ─► N-ATLaS: translate to English ─► route to domain
          ─► retrieve passages ─► N-ATLaS: answer ─► N-ATLaS: translate back ─► reply (+ voice)
```

## N-ATLaS integration

N-ATLaS (`NCAIR1/N-ATLaS`, Llama-3 8B) is used as released, with no fine-tuning, served by vLLM (OpenAI-compatible API, bfloat16, 4,096-token context). It does the language work in every answer:

| Call | What N-ATLaS does | Code |
|---|---|---|
| Translate in | Hausa, Igbo or Yorùbá question → English | `Assistant.translate` |
| Route | Picks the agency domain when keywords are unclear, or "general" / "other" | `Assistant.route` |
| Product name | Pulls the product name out of a NAFDAC question | `app/products.py` |
| Answer | Writes the answer from the retrieved agency passages, following the domain's safety rules | `Assistant.answer_en` |
| General | Answers general questions from memory with a label, or refuses on sensitive topics | `Assistant.answer_general` |
| Translate out | English answer → the user's language | `Assistant.translate` |

Speech uses NCAIR's ASR models (`NCAIR1/Hausa-ASR`, `Igbo-ASR`, `Yoruba-ASR`, `NigerianAccentedEnglish`). `GET /health` on the live server reports the model in use (`"llm": "NCAIR1/N-ATLaS"`, `"mock": false`) and the number of passages per domain.

Two real answers from user testing:

> **Yorùbá, text:** *Báwo ni mo ṣe lè forúkọ sílẹ̀ fún káàdì ìdìbò (PVC)?*
> N-ATLaS translation: "How can I register for a Permanent Voter Card (PVC)?" → civic domain → answer in Yorùbá with the steps on `https://cvr.inecnigeria.org`, ending *(Orisun: INEC)*. 3.9 seconds.

> **Nigerian English, voice note:** "how i feel protect myself from malaria" (NCAIR NigerianAccentedEnglish transcript)
> → health domain → "Sleep under a mosquito net… use mosquito repellent after dark, coils and vaporisers… (Source: World Health Organization)".

## Technology stack

| Layer | Tools |
|---|---|
| Language model | **N-ATLaS** (`NCAIR1/N-ATLaS`, Llama-3 8B), used as released, served by **vLLM** (OpenAI-compatible API, bfloat16) |
| Speech recognition | **NCAIR ASR** models: Hausa-ASR, Igbo-ASR, Yoruba-ASR, NigerianAccentedEnglish (Whisper-based) |
| Retrieval | `intfloat/multilingual-e5-small` embeddings over curated agency documents, with a keyword fallback |
| Model runtime | PyTorch, Hugging Face Transformers, Sentence-Transformers, FFmpeg |
| Backend | Python 3.12, FastAPI, Uvicorn, SQLite (anonymous log and NAFDAC food database) |
| Channels | Web app (HTML, CSS, JavaScript with in-browser recording) on GitHub Pages; Telegram Bot API (`python-telegram-bot`); Twilio WhatsApp API (built, next phase) |
| Infrastructure | One NVIDIA L40S (48 GB) GPU; ngrok for a fixed HTTPS address; Google Cloud (NVIDIA L4) setup scripts as an alternative |
| Engineering | GitHub, GitHub Actions |
| Official data | NAFDAC Greenbook (live) and Food Products Database; NIMC, NIBSS, NCC, INEC, NIS, CAC, CBN, SEC, FCCPC, NDIC, EFCC, JAMB, WAEC, NECO, UBEC, NELFUND, NPHCDA, WHO, IITA, FAO, NAERLS, NiMet; the Constitution and federal laws |

## Domains are plug-in folders

```
domains/<name>/domain.json       title, description, routing keywords
domains/<name>/instructions.md   answering and safety rules for this domain
domains/<name>/docs/*.md         curated official sources (first line: "Source: NIMC")
```

Adding a domain means adding a folder, with no code changes. Files starting with `_` (drafts, notes) are ignored, and so is any file that still contains `{{VERIFY}}`.

### Content status

Every live document was written from official pages opened on 8 Oct 2026, and every file starts with its source links.

| Domain | Live documents | Main sources | Not covered yet |
|---|---|---|---|
| money | 20 scam patterns; CBN complaints and fraud warnings; SEC unregistered schemes; FCCPC loan-app rules; NDIC deposit insurance; reporting fraud to EFCC/police | CBN, SEC, FCCPC, NDIC, EFCC, NPF-NCCC | wrong-transfer / fake-alert rules (CBN documents blocked automated download) |
| civic | NIN enrolment; NIN retrieval; BVN; NIN-SIM linkage; voter registration and PVC; passport; CAC business name | NIMC, NIBSS, NCC, INEC, NIS, CAC | birth certificate, driver's licence |
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

### On a GPU server

The live deployment runs on a single **NVIDIA L40S (48 GB)** GPU: vLLM serves N-ATLaS on the GPU, and the app (speech recognition, embeddings, Telegram bot, web API) runs beside it on the CPU. An ngrok tunnel gives it a fixed public https address, which the web page and Twilio call. No training is needed: N-ATLaS is used as released.

Any NVIDIA GPU with 24 GB or more works. The scripts below set it up on Google Cloud (one NVIDIA L4, 24 GB). Before you start:

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

`PUBLIC_BASE_URL` defaults to `https://<NGROK_DOMAIN>`. It is needed for the web page's microphone (browsers only allow it on https). On ngrok's free plan, visitors to the web page see a one-time ngrok warning page first; WhatsApp and Telegram are not affected.

### Channels

- **Telegram:** message @BotFather, `/newbot`, put the token in `TELEGRAM_BOT_TOKEN`. The bot starts with the server.
- **Web:** `https://<NGROK_DOMAIN>` serves the page directly. The public copy at **https://wazobiaassist.github.io** (repo `Wazobiaassist/wazobiaassist.github.io`, a copy of `app/static` with the API address filled in) calls the same server; its address must be in `CORS_ORIGINS` (both GitHub Pages addresses are allowed by default).

## Users' commands

- First message: what WazobiaAssist answers, the language menu (1 Hausa, 2 Igbo, 3 Yorùbá, 4 English (Nigerian)), then the privacy notice
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

This writes `data/interactions.csv` and prints counts by language, domain, channel and input type, the satisfaction rate and the median response time. Every question asked on the web page or Telegram is logged automatically and anonymously; our own test questions were removed from the log. The team also collects screenshots and photos of testing sessions as visual evidence.

## Team profile

| # | Name | Role | Affiliation |
|---|---|---|---|
| 1 | Olawale Amos Akanji | Team lead and AI engineer | Boston University |
| 2 | [Name] | Language and translation lead | [University or company] |
| 3 | [Name] | Domain content lead | [University or company] |
| 4 | [Name] | User testing and outreach lead | [University or company] |

### 1. Olawale Amos Akanji: Team lead and AI engineer
- **Affiliation:** Boston University, Department of Electrical and Computer Engineering (PhD candidate, Computer Engineering: Security and Privacy)
- **Location:** Boston, Massachusetts
- **Responsibilities:** leads the project; built the N-ATLaS pipeline, speech recognition, retrieval, web page and Telegram bot; runs the GPU server and deployment.
- **Relevant experience:** builds Transformer-based models that detect financial scams in conversations and run on the phone. Led an LLM-assisted review of 434 consumer-lending apps that led to the removal of 93 apps with more than 300 million users (ACM AsiaCCS 2026). Eleven years as a cybersecurity specialist in the Nigerian Air Force, and founder of a Nigerian non-profit that teaches young people to avoid fraud. BSc Cybersecurity, Air Force Institute of Technology, Kaduna (overall best graduating student).
- **Languages:** Yorùbá, English

### 2. [Name]: Language and translation lead
- **Affiliation:** [University or company, department]
- **Location:** [City, state]
- **Responsibilities:** reviews Hausa, Igbo and Yorùbá questions and answers as a native speaker; checks that N-ATLaS translations keep the meaning, names and codes right; writes the test questions in each language.
- **Relevant experience:** [1 to 3 lines]
- **Languages:** [e.g. Hausa, English]

### 3. [Name]: Domain content lead
- **Affiliation:** [University or company, department]
- **Location:** [City, state]
- **Responsibilities:** collects and checks the official sources for every domain: identity, voting, money and scams (NIMC, INEC, CBN, EFCC), health, farming and education (NPHCDA, WHO, IITA, JAMB); owns the safety rules (no doses, no diagnosis, danger signs go to a health facility).
- **Relevant experience:** [1 to 3 lines]
- **Languages:** [e.g. Igbo, English]

### 4. [Name]: User testing and outreach lead
- **Affiliation:** [University or company, department]
- **Location:** [City, state]
- **Responsibilities:** recruits testers through WhatsApp groups and communities, collects feedback and testing evidence, produces the demo video, and leads the plan to reach 1,000 users.
- **Relevant experience:** [1 to 3 lines]
- **Languages:** [e.g. Yorùbá, Pidgin, English]

## Privacy and safety

- Users are stored only as a salted hash of their channel id. Phone, account and ID numbers and emails are masked before saving. Voice notes are deleted after transcription.
- The privacy notice is shown before the first question, and `DELETE` erases everything.
- Answers come only from curated documents. Each domain has safety rules (for example, health danger signs mean "go to a health facility now").
- If translation drops a number, USSD code or link, the English original is attached so the user never gets a wrong code.
- General-knowledge answers are labelled as such, and N-ATLaS refuses to answer health doses, legal or money questions from memory.

## Further improvements and integrations

- **WhatsApp.** The WhatsApp channel is built and tested up to the provider's limit: Twilio delivers users' messages to the bot and the bot writes its answers, but a Twilio trial account may only send Twilio's own template messages (error 21654), so replies are not delivered yet. Next step: an upgraded Twilio account, then a WhatsApp Business number approved by Meta so users don't need a sandbox join phrase. Code: `app/channels/whatsapp.py`, endpoint `POST /whatsapp`. Setup: in the Twilio Console, open Messaging → Try it out → Send a WhatsApp message. Note the sandbox number and join phrase shown there (ours: +1 415 523 8886, `join examine-so`) and set `TWILIO_WHATSAPP_FROM=whatsapp:<that number>` (replies go out from whichever number the user wrote to). Put the account SID and auth token in `.env`. In the Sandbox settings tab, set "When a message comes in" to `https://<NGROK_DOMAIN>/whatsapp` (POST). Each tester must send the join phrase first. **A Twilio trial account cannot send the bot's own replies** (only Twilio's templates, error 21654), so WhatsApp needs an upgraded account.
- **Live lookup on official sites.** When the curated documents have no answer, search only an approved list of official sites (nimc.gov.ng, inecnigeria.org, cbn.gov.ng, jamb.gov.ng, nafdac.gov.ng and others), pull the relevant paragraphs, and answer from them with a label such as "From nimc.gov.ng, checked today". The NAFDAC Greenbook check already works this way. Health and money answers from a live page add "please confirm with the agency". A nightly job also re-downloads every source page and flags changes for review, so curated documents never go out of date.
- **Feature phones.** A USSD menu and a phone line (IVR) using the same pipeline, for users without smartphones or data.
- **Igbo voice replies.** No open Igbo text-to-speech voice exists yet; Igbo answers are text only.
- **More agencies.** Birth certificates (NPC), driver's licences (FRSC), tax (FIRS), pensions (PenCom), and state-level services.
- **Native-speaker review** of interface text and a sample of translated answers in each language, and Nigerian Pidgin once the models support it.

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
app/static/index.html  web page (also published at https://wazobiaassist.github.io)
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
