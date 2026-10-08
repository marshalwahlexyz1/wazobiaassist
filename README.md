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

### On Google Cloud (live bot)

One `g2-standard-8` VM with an NVIDIA L4 (24 GB) runs everything: about $0.85/hour, so roughly
$80 from Friday to Monday, paid from Google Cloud's $300 new-account credit.

**1. Accounts (start now: GPU quota approval can take a day or two)**
1. Sign up at https://cloud.google.com/free ($300 credit for 90 days; a card is needed for verification).
2. Upgrade the billing account (**Billing → Overview → Activate full account**). Free-trial accounts
   cannot use GPUs. The credit still applies, and you are only charged after it runs out.
3. In **IAM & Admin → Quotas & system limits**, request `GPUs (all regions)` = 1 and
   `NVIDIA L4 GPUs` = 1 in `us-central1` (also `europe-west4` as a backup).
4. Accept the terms on Hugging Face for N-ATLaS **and** each NCAIR ASR model.
5. Create a free ngrok account (dashboard.ngrok.com): copy the authtoken and claim the free static
   domain. This gives WhatsApp a fixed address.

**2. Create the VM** in Cloud Shell (the `>_` button in the console):
```bash
git clone https://github.com/marshalwahlexyz1/wazobiaassist && cd wazobiaassist
gcloud config set project <your-project-id>
bash scripts/gcp/create_vm.sh            # tries several zones until an L4 is free
```

**3. Install and start the bot** on the VM:
```bash
gcloud compute ssh wazobia --zone <zone>
git clone https://github.com/marshalwahlexyz1/wazobiaassist && cd wazobiaassist
cp .env.example .env    # HF_TOKEN, TELEGRAM_BOT_TOKEN, TWILIO_*, NGROK_AUTHTOKEN, NGROK_DOMAIN,
                        # PUBLIC_BASE_URL=https://<NGROK_DOMAIN>   (ID_SALT is generated if empty)
bash scripts/gcp/setup.sh               # one time, ~30 min; installs and starts the service
.venv/bin/python -m scripts.ask --lang ha --text "Ta yaya zan sami NIN?"   # test one question
curl https://<NGROK_DOMAIN>/health      # reachable from the internet?
```

The bot runs as the `wazobia` systemd service (`scripts/run_all.sh`: vLLM, then the app, then
ngrok). It starts on boot and restarts everything if any part crashes. Telegram uses polling and
WhatsApp comes in through ngrok's fixed address, so no firewall changes are needed and the Twilio
URL never changes.

```bash
sudo systemctl status wazobia      # running?
journalctl -u wazobia -f           # service log; vLLM/app/ngrok logs are in data/logs/
sudo systemctl restart wazobia     # after git pull, or changing .env or the domain documents
gcloud compute instances stop wazobia --zone <zone>    # stop paying for the GPU (from Cloud Shell)
```

vLLM settings are in `.env`: `GPU_MEM=0.80` and `MAX_MODEL_LEN=4096` fit the L4 alongside the ASR,
embedding and TTS models (use 0.60 and 8192 on a 40 GB+ card). If `data/logs/vllm.log` shows an
out-of-memory error, set `VLLM_EXTRA_ARGS=--quantization fp8` and restart.

**If L4 quota is refused:** rent a GPU by the hour from RunPod or Lambda (no quota needed). On a
Lambda VM, `bash scripts/gcp/setup.sh` works as is. On RunPod (a container without systemd),
follow the steps below and run `bash scripts/run_all.sh` inside `tmux`.

### Any other GPU machine, by hand

```bash
sudo apt install -y ffmpeg
python -m venv .venv-vllm && .venv-vllm/bin/pip install vllm
python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env                    # fill in HF_TOKEN, ID_SALT, channel keys, NGROK_*
bash scripts/run_all.sh                 # vLLM + app + ngrok; run it inside tmux
```

If vLLM won't install, set `LLM_BACKEND=transformers` to load N-ATLaS inside the app instead
(slower), and start only the app: `.venv/bin/uvicorn app.server:app --port 8080`.
`GET /health` shows status and document counts per domain.

### Public URL (needed for WhatsApp and the web microphone)

`scripts/run_all.sh` starts ngrok on your free static domain, so the address never changes. Put
`https://<NGROK_DOMAIN>` in `PUBLIC_BASE_URL`. Browsers only allow the microphone on https pages.

### Channels

- **Telegram:** message @BotFather, `/newbot`, put the token in `TELEGRAM_BOT_TOKEN`. The bot starts with the server.
- **WhatsApp (Twilio sandbox):** in the Twilio console, open Messaging → Try it out → WhatsApp sandbox. Put the account SID and auth token in `.env`. Set "When a message comes in" to `https://<NGROK_DOMAIN>/whatsapp` (POST). Each tester must first send the sandbox's `join <code>` message to the sandbox number.
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

```bash
python -m scripts.eval_router
```

This measures how often questions reach the right domain, using `eval/router_cases.jsonl`. Native
speakers: add Hausa, Igbo and Yoruba questions to it.

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
scripts/eval_router.py routing accuracy on eval/router_cases.jsonl
scripts/serve_llm.sh   N-ATLaS on vLLM
scripts/run_all.sh     vLLM + app + ngrok together (used by the systemd service)
scripts/gcp/           create_vm.sh (L4 VM on Google Cloud), setup.sh (one-time install + service)
tests/                 pytest, runs without a GPU
```
