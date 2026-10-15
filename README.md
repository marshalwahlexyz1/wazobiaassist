<p align="center"><img src="docs/logo.svg" alt="WazobiaAssist" width="360"></p>

# WazobiaAssist

**Government answers in one place, in your language.**

**Our goal: anyone in Nigeria can find out anything about their government by asking in their own language, and get an answer that is correct.**

WazobiaAssist is a front desk for the whole of government. You do not need to know which agency handles your problem, find its website or read English. Ask by **voice note or text in Hausa, Igbo, Yorùbá or Nigerian English**, on the **web or Telegram**, and WazobiaAssist answers in your language from the government's own information, and tells you which agency the answer came from. It is built on **N-ATLaS**, Nigeria's multilingual language model, and NCAIR's speech recognition models.

National AI Innovation Challenge (NAIC) 2026, Problem Statement 02: Voice-First Access, Track B (Innovation & Enterprise).

## Why it matters

Government information in Nigeria is spread across dozens of agencies, each with its own website, PDFs, USSD codes and helplines, almost all in English. To get a NIN, register to vote, apply for a student loan, check that a loan app is legal or know your rights when the police stop you, you first have to know which agency handles it, then find its page, then read it in a language many people do not read comfortably.

So most people ask a friend, a WhatsApp group or an agent instead, and the answers they get are often wrong. People pay "registration fees" for services that are free, send money for CBN "grants" that do not exist, borrow from loan apps that regulators have removed from their lists, and do not know what the law allows the police to do. **A wrong answer about government costs people money, missed deadlines and their rights.**

WazobiaAssist makes two promises:

1. **Anything about government, in one place.** People should not need to know which agency to ask.
2. **The answer must be correct.** It comes from the agency's own information, names its source, and when the official information does not answer the question, WazobiaAssist says so instead of guessing.

## Try it

| Channel | How |
|---|---|
| Web | **https://wazobiaassist.github.io**: pick a language, then type or tap the microphone |
| Telegram | **@WazobiaAssist_bot**: send any message, pick a language, then send a voice note or text |

## What it does: explain, verify, direct

Every question is handled in one of three ways. None of them is tied to one agency: each works the same way for any agency that is added.

| | What WazobiaAssist does | Working today | Next |
|---|---|---|---|
| **Explain** | Explains a government procedure, requirement, right or rule from the agency's own published information or the text of the law, with the exact steps, codes and fees. *"How do I retrieve my NIN?" "Can the police arrest me for my brother's debt?" "How do I apply for a student loan?"* | 20+ agencies and bodies (NIMC, NIBSS, NCC, INEC, Immigration, CAC, CBN, SEC, FCCPC, NDIC, EFCC, JAMB, WAEC, NECO, UBEC, NELFUND, NPHCDA, NiMet, Legal Aid Council and others), the Constitution and the main federal laws | Every federal agency, then state and local government services |
| **Verify** | Many agencies publish their records online. WazobiaAssist searches those databases at the moment the question is asked, so the answer matches today's official record, not an old copy. *"Is this drug registered?" "Is this loan app approved?"* | NAFDAC's product registers (drugs, vaccines, medical devices, herbal products and foods) | FCCPC's register of approved digital lenders and the lenders removed from it; CAC business search; SEC's registered operators; CBN's licensed banks and microfinance banks |
| **Direct** | When the official information does not answer the question, it says so and points the user to the right agency and its official helpline or website. It does not guess. | All topics | Agency complaint and appointment links |

**Examples from the pilot:**
- **Rights, with the exact law.** "Can the police arrest me for my brother's debt?" is answered from the Constitution, the Police Act 2020 and the Administration of Criminal Justice Act 2015, naming the section and pointing to free help from the Legal Aid Council. The 270 passages quoted from Nigerian laws were checked against the source texts.
- **Procedures, with codes checked against the official pages.** Retrieving a NIN (`*346#`, NIMC), checking a BVN (`*565*0#`, NIBSS), registering to vote and collecting a PVC (INEC), applying for a passport, registering a business name (CAC), creating a JAMB profile.
- **A live record check.** "Is Emzor paracetamol registered?", or a NAFDAC number read from the pack, is checked against NAFDAC's live register. The reply gives the product, registration number, company and whether the registration is valid or expired, for example "registration expired on 19 December 2024".
- **Money safety.** "Someone says CBN is giving grants if I pay a fee" is recognised as a scam from CBN guidance. The pilot covers 20 common scam patterns, and how to report fraud to the EFCC and the police.
- **Everyday public services.** The NPHCDA immunisation schedule, danger signs in pregnancy and in newborns, JAMB, WAEC and NECO, and farming guidance with NiMet's 2026 rainy-season forecast.
- **General questions** about Nigeria that no agency document covers ("What is the capital?") are answered from N-ATLaS's own knowledge, clearly labelled *"General knowledge, not from an official source. It may be out of date"*.

**Coverage in the pilot:**

| Ask about | Answers come from |
|---|---|
| Identity and registration: NIN, BVN, NIN-SIM linking, voter registration and PVC, passport, business names | NIMC, NIBSS, NCC, INEC, Nigeria Immigration Service, CAC |
| Your rights: arrest, bail, detention, data privacy, consumer rights | Constitution, Police Act 2020, ACJA 2015, NDPA 2023, FCCPA 2018, Cybercrimes Act, Legal Aid Council |
| Money and scams: loan apps, "grants" that ask for a fee, Ponzi schemes, reporting fraud | CBN, SEC, FCCPC, NDIC, EFCC |
| Registered products (live check) | NAFDAC's registers |
| Exams and schooling: JAMB, WAEC, NECO, free basic education, student loans | JAMB, WAEC, NECO, UBEC, NELFUND |
| Health: immunisation, pregnancy and newborn danger signs, malaria | NPHCDA, WHO |
| Farming: planting times, pests, storage, the 2026 rainy season | IITA, FAO, NAERLS, NiMet |

## How we keep answers correct

Correctness is built into every step, not left to the language model:

| Safeguard | How it works |
|---|---|
| **Official sources only** | Every document was written from the agency's own page or the law's official text, and starts with its source links and the date it was checked. Drafts, and any file still marked `{{VERIFY}}`, are never loaded. |
| **Answers grounded in the source** | N-ATLaS writes each official answer only from the passages retrieved for that question. If those passages do not contain the answer, it says it does not know and gives the agency to contact. |
| **Live records, copied not generated** | When an agency's database is searched, the answer is built from the record's own fields (name, registration number, holder, expiry date), so a number or date is never invented and an expired record is reported as expired. A record that is not found is never called fake; the user is sent to the agency to confirm. |
| **Every answer names its source** | Official answers end with the agency they came from. Any source named in an answer that was not in the retrieved passages is removed. |
| **Codes survive translation** | After N-ATLaS translates an answer, every number, USSD code, registration number and link is compared with the English. If one was lost or changed, the English original is attached, so a user never gets a wrong code. |
| **Safety rules per topic** | Health danger signs always mean "go to a health facility now", with no doses and no diagnosis. Legal answers cite the law and section and say they are information, not legal advice. Money answers warn against paying fees for "grants". |
| **Memory is labelled or refused** | General knowledge from N-ATLaS's memory is always labelled. N-ATLaS will not answer health, legal or money questions from memory. |
| **People check the content** | The domain content lead checks each document against its source. Each domain's `docs/_SOURCES_REVIEW.md` lists what still needs a second check before launch. |
| **Real users check the answers** | Every answer can be rated 👍 or 👎. In testing, 97.4% of rated answers were rated helpful. Every 👎 and every unanswered question is reviewed, and the content is fixed. |

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
| Record lookup | Pulls the name or number to look up out of the question (for example a product name for NAFDAC's register) | `app/products.py` |
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

## Live checks against agency databases

Some answers must come from an official record, not from a document: whether a product is registered, whether a lender is approved, whether a business exists. For these, WazobiaAssist searches the agency's own online database when the question is asked, and builds the reply from the record's fields. Each database is a connector: it recognises the questions it can check, searches the database, and returns the record. N-ATLaS only pulls out the name or number to look up and translates the reply, so it never writes a registration number or date itself.

| Database | Status |
|---|---|
| NAFDAC Greenbook and Food Products Database | Working (`app/products.py`) |
| FCCPC register of approved digital lenders, and lenders removed from it | Next: "Is this loan app approved?" |
| CAC public search | Planned: "Is this business registered?" |
| SEC registered capital market operators; CBN licensed banks and microfinance banks | Planned: "Is this investment company or bank licensed?" |

### The first connector: NAFDAC

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

## Privacy and safety

- Users are stored only as a salted hash of their channel id. Phone, account and ID numbers and emails are masked before saving. Voice notes are deleted after transcription.
- The privacy notice is shown before the first question, and `DELETE` erases everything.
- Answers come only from curated documents. Each domain has safety rules (for example, health danger signs mean "go to a health facility now").
- If translation drops a number, USSD code or link, the English original is attached so the user never gets a wrong code.
- General-knowledge answers are labelled as such, and N-ATLaS refuses to answer health doses, legal or money questions from memory.

## Further improvements and integrations

The goal stays the same as we grow: every question about government, answered correctly, on every phone, in the user's language. All new channels use the same backend (`POST /api/ask`), so every answer goes through the same sources, safety rules and translation checks described in [How we keep answers correct](#how-we-keep-answers-correct).

### Android and iOS apps

A WazobiaAssist app for Android phones and iPhones, built from one shared codebase (Flutter):

- **Android first.** Most phones in Nigeria run Android, many of them low-cost models, so the app targets Android 8 and newer, a download under 20 MB, and a low-data mode that sends text answers by default and voice replies only on request. It will be on Google Play, and the install file will also be shared directly for phones without the Play Store.
- **iPhone** from the same code, on the App Store.
- **Hold to talk.** The main screen is one large microphone button, and the app remembers the user's language. Typing is always available.
- **Saved answers work offline.** Users can save an answer, such as the NIN steps or a PVC checklist, and open it later without data.
- **Opt-in reminders** for government deadlines people often miss: voter registration, JAMB registration, immunisation days and tax dates.
- **Scan instead of typing.** Point the camera at a registration number, such as the NAFDAC number on a pack or a CAC number on a receipt, and get the official record.
- **Share an answer** with its source to WhatsApp, as text or a voice note, so correct information spreads through the same groups where rumours do.
- **Same privacy as today.** No account and no phone number are needed. `DELETE` in settings erases everything.

### Other channels and integrations

- **WhatsApp.** The WhatsApp channel is built and tested up to the provider's limit: Twilio delivers users' messages to the bot and the bot writes its answers, but a Twilio trial account may only send Twilio's own template messages (error 21654), so replies are not delivered yet. Next step: an upgraded Twilio account, then a WhatsApp Business number approved by Meta so users don't need a sandbox join phrase. Code: `app/channels/whatsapp.py`, endpoint `POST /whatsapp`. Setup: in the Twilio Console, open Messaging → Try it out → Send a WhatsApp message. Note the sandbox number and join phrase shown there (ours: +1 415 523 8886, `join examine-so`) and set `TWILIO_WHATSAPP_FROM=whatsapp:<that number>` (replies go out from whichever number the user wrote to). Put the account SID and auth token in `.env`. In the Sandbox settings tab, set "When a message comes in" to `https://<NGROK_DOMAIN>/whatsapp` (POST). Each tester must send the join phrase first. **A Twilio trial account cannot send the bot's own replies** (only Twilio's templates, error 21654), so WhatsApp needs an upgraded account.
- **Feature phones.** A USSD menu and a phone line (IVR) using the same pipeline, for people without smartphones or data.

### Covering all of government, and keeping it correct

- **More agencies, then states.** Next are birth certificates (NPC), driver's licences and plate numbers (FRSC), tax (the Nigeria Revenue Service, formerly FIRS), pensions (PenCom) and health insurance (NHIA). After that come state and local government services, starting with the states where our users are. Each new agency gets the same source checks before it goes live.
- **More live database checks.** Connect every agency database the public can already search: FCCPC's register of approved digital lenders first, then CAC, SEC and CBN. Each one turns a question people are often lied to about into a check against the official record.
- **Live lookup on official sites.** When the curated documents have no answer, search only an approved list of official sites (nimc.gov.ng, inecnigeria.org, cbn.gov.ng, jamb.gov.ng, nafdac.gov.ng and others), pull the relevant paragraphs, and answer from them with a label such as "From nimc.gov.ng, checked today". The NAFDAC Greenbook check already works this way. Health and money answers from a live page add "please confirm with the agency".
- **Never out of date.** A nightly job re-downloads every source page and flags any change for review, so a fee, code or deadline that changes on the agency's site is updated in WazobiaAssist too.
- **Agency partnerships.** Agencies can review and confirm their own content, and receive an anonymous monthly report of what citizens ask them about and where their information is unclear.

### Languages and voice

- **Igbo voice replies.** No open Igbo text-to-speech voice exists yet, so Igbo answers are text only for now.
- **Nigerian Pidgin, and more Nigerian languages** as N-ATLaS and NCAIR's speech models add them.
- **Native-speaker review** of the interface text and a sample of translated answers in each language.

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
domains/               the seven topic domains
scripts/ask.py         ask one question from the terminal
scripts/export_logs.py evidence CSV and summary
scripts/fetch_sources.py download source pages as drafts for review
scripts/routing_test.py check routing per language (tests/routing_questions.csv)
scripts/update_nafdac.py download NAFDAC's food product database
app/products.py        NAFDAC product check (Greenbook live search + food database)
scripts/gcp/            Google Cloud VM creation, setup and always-on services
tests/                 routing questions per language (routing_questions.csv)
```

## Team profile

| # | Name | Role | Affiliation |
|---|---|---|---|
| 1 | Olawale Amos Akanji | Team lead and AI engineer | Boston University |
| 2 | Umar Mamman Toro | Language and translation lead | Miva Open University; Digital Encode |
| 3 | Joseph Abah | Domain content lead | NNPC Limited |
| 4 | Nwaikwu Ekenedilichukwu Sebastian | User testing and outreach lead | Inspirive Technologies |

### 1. Olawale Amos Akanji: Team lead and AI engineer
- **Affiliation:** Boston University, Department of Electrical and Computer Engineering (PhD candidate, Computer Engineering: Security and Privacy)
- **Location:** Boston, Massachusetts
- **Responsibilities:** leads the project; built the N-ATLaS pipeline, speech recognition, retrieval, web page and Telegram bot; runs the GPU server and deployment.
- **Relevant experience:** builds Transformer-based models that detect financial scams in conversations and run on the phone. Led an LLM-assisted review of 434 consumer-lending apps that led to the removal of 93 apps with more than 300 million users (ACM AsiaCCS 2026). Eleven years as a cybersecurity specialist in the Nigerian Air Force, and founder of a Nigerian non-profit that teaches young people to avoid fraud. BSc Cybersecurity, Air Force Institute of Technology, Kaduna (overall best graduating student).
- **Languages:** Yorùbá, English

### 2. Umar Mamman Toro: Language and translation lead
- **Affiliation:** Miva Open University (Master of Information Technology); Information Security Consultant, Digital Encode
- **Location:** Surulere, Lagos
- **Responsibilities:** reviews Hausa, Igbo and Yorùbá questions and answers as a native speaker; checks that N-ATLaS translations keep the meaning, names and codes right; writes the test questions in each language.
- **Relevant experience:** Master of Information Technology with a specialisation in Artificial Intelligence; works as an information security consultant.
- **Languages:** Hausa, Yorùbá, English

### 3. Joseph Abah: Domain content lead
- **Affiliation:** NNPC Limited
- **Location:** Abuja, FCT
- **Responsibilities:** collects and checks the official sources for every domain: identity, voting, money and scams (NIMC, INEC, CBN, EFCC), health, farming and education (NPHCDA, WHO, IITA, JAMB); owns the safety rules (no doses, no diagnosis, danger signs go to a health facility).
- **Relevant experience:** Three years in IT security.
- **Languages:** Idoma, English

### 4. Nwaikwu Ekenedilichukwu Sebastian: User testing and outreach lead
- **Affiliation:** Inspirive Technologies, IT Support Engineer
- **Location:** Ikoyi, Lagos
- **Responsibilities:** recruits testers through WhatsApp groups and communities, collects feedback and testing evidence, produces the demo video, and leads the plan to reach 1,000 users.
- **Relevant experience:** Manages user accounts, access controls, identity management, and enterprise IT resources. 
- **Languages:** Igbo, Pidgin, English
