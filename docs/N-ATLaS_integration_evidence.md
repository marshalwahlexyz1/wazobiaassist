# N-ATLaS integration evidence

WazobiaAssist uses **N-ATLaS** as its only language model. Every question a user asks, by voice or text, in Hausa, Igbo, Yorùbá or Nigerian English, passes through N-ATLaS at least three times: to translate the question, to write the answer from official agency information, and to translate the answer back into the user's language. NCAIR's speech recognition models turn voice notes into text first.

## 1. Model in use

| Part | Detail |
|---|---|
| Language model | **N-ATLaS** (`NCAIR1/N-ATLaS`, Llama-3 8B), downloaded from Hugging Face and used as released, with no fine-tuning |
| Serving | vLLM, OpenAI-compatible chat completions API, bfloat16, 4,096-token context, temperature 0 so answers are repeatable |
| Speech recognition | NCAIR models `NCAIR1/Hausa-ASR`, `NCAIR1/Igbo-ASR`, `NCAIR1/Yoruba-ASR`, `NCAIR1/NigerianAccentedEnglish` |
| Hardware | One NVIDIA L40S (48 GB) GPU |
| Code | https://github.com/marshalwahlexyz1/wazobiaassist (`app/llm.py` calls the model, `app/assistant.py` holds every prompt) |

## 2. Where N-ATLaS works in each question

<!-- pipeline -->

| Call | What N-ATLaS does | Code |
|---|---|---|
| Translate in | Hausa, Igbo or Yorùbá question → English | `Assistant.translate` |
| Route | Picks the agency domain when keywords are unclear, or "general" / "other" | `Assistant.route` |
| Product name | Pulls the product name out of a NAFDAC question | `app/products.py` |
| Answer | Writes the answer only from the retrieved agency passages, following the domain's safety rules, and names the agency | `Assistant.answer_en` |
| General | Answers general questions from its own knowledge with a clear label, or refuses on health doses, legal and money questions | `Assistant.answer_general` |
| Translate out | English answer → the user's language | `Assistant.translate` |

After translation out, every number, USSD code, NAFDAC number and link is compared with the English answer. If N-ATLaS dropped or changed one, the English original is attached so the user never receives a wrong code (`app/protect.py`).

## 3. The live system runs N-ATLaS

The live server's status page, `GET /health`, captured on 12 October 2026 at 12:44 PM:

```json
{
  "status": "ok",
  "mock": false,
  "llm": "NCAIR1/N-ATLaS",
  "domains": {"agriculture": 68, "civic": 43, "education": 48, "health": 52,
              "laws": 235, "money": 47, "products": 0},
  "nafdac_food_list": true
}
```

`"llm": "NCAIR1/N-ATLaS"` is the model the server is answering with, and `"mock": false` means no stand-in model is used. The numbers are the official passages loaded per domain. Products have none by design: product questions are answered from NAFDAC's registers, searched at the time of the question.

## 4. Real questions from real users

Six answers from user testing between 10 and 12 October 2026, copied from the anonymous interaction log. Each shows the user's own words, the English that N-ATLaS translated them into, and the start of the answer the user received.

**Hausa, voice note, web page (rated 👍)**
- NCAIR Hausa-ASR heard: *"ta yaya zan kare kaina daga cutar zazzabin sauro?"*
- N-ATLaS translated: "How do I protect myself from malaria?" → health
- Answer in Hausa: *"…Hakanan zaka iya amfani da maganin kwari bayan duhu, coils, masu tururi, da kuma sanya tufafi da ke rufe jikinka… (Source: Hukumar Lafiya ta Duniya)"* ("you can also use insect repellent after dark, coils, vaporisers, and wear clothes that cover your body", from the World Health Organization). 18.0 seconds.

**Yorùbá, voice note, Telegram (rated 👍)**
- NCAIR Yoruba-ASR heard: *"báwo ni mo ṣe lè fi orúkọ sílẹ̀ fún ìdìbò?"*
- N-ATLaS translated: "How can I register for voting?" → civic
- Answer in Yorùbá: *"Lati forukọsilẹ fun idibo ni orilẹ-ede Naijiria, tẹle awọn igbesẹ wọnyi: 1. Ṣabẹwo si ibi ipamọ INEC CVR ni https://cvr.inecnigeria.org… (Orisun: INEC)"*. The link survived translation unchanged. 24.1 seconds.

**Igbo, text, Telegram (rated 👍)**
- User typed: *"Gini bu oru EFCC na-aru imegide nruru aka"*
- N-ATLaS translated: "What is the EFCC's role in combating corruption?" → money
- Answer in Igbo: *"Kọmishọna Economic and Financial Crimes Commission (EFCC) bụ ọrụ maka ịmanye iwu megide mpụ akụ na ụba na ego na Naijiria…"*, from EFCC and CBN guidance. 3.3 seconds.

**Nigerian Pidgin, text, web page**
- User typed: *"Wetin be the rights wey Nigerian Constitution give every citizen?"*
- N-ATLaS routed it to laws and answered from the Constitution: *"…the right to freedom of movement (Constitution, section 41), the right to acquire and own immovable property anywhere in Nigeria (section 43), the right to life (section 33)… you can contact a lawyer or the Legal Aid Council"*. 3.6 seconds.

**Nigerian English, voice note, web page (rated 👍)**
- NCAIR NigerianAccentedEnglish heard: *"someone says cbn is giving grants if i pay a fee. is it true?"*
- Answer: *"This looks like a scam. The Central Bank of Nigeria (CBN) does not ask you to pay a fee to receive any grants or money…"*, from CBN's consumer-protection pages. 11.8 seconds.

**NAFDAC product check, text, web page**
- User typed: *"is emzor paracetamol registered?"*
- N-ATLaS pulled out the product name, the NAFDAC Greenbook was searched live, and the reply listed each registered product: *"Emzor Paracetamol Tablet (Tablet, 500 mg), NAFDAC number 04-0411, registered to Emzor Pharmaceutical Industries Limited: registration valid until 27 March 2028…"*. 3.5 seconds.

## 5. In numbers

From the cleaned interaction log (`interactions.csv`, summarised in the Real-World Validation report):

| Measure | Value |
|---|---|
| Questions answered through N-ATLaS | 170, from 31 users |
| Asked in Hausa, Igbo or Yorùbá and translated by N-ATLaS | 112 |
| Voice notes transcribed by NCAIR speech models | 124 |
| Rated helpful | 97.4% of rated answers (38 👍, 1 👎) |

Every row of the log keeps the user's words (`transcript`), the N-ATLaS English translation (`question_en`), the N-ATLaS answer in English (`answer_en`) and the translated answer the user received (`answer`), so each step can be checked.

## 6. How to check it yourself

- Open https://wazobiaassist.github.io or Telegram **@WazobiaAssist_bot** and ask a question in any of the four languages.
- Open the live server's `/health` page and confirm `"llm": "NCAIR1/N-ATLaS"`.
- Read `app/assistant.py` for every N-ATLaS prompt and `app/llm.py` for the vLLM call. The README's "Run it" section starts the same system on any GPU server with N-ATLaS.
