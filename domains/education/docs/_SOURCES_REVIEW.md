# Education sources review

Date of attempt: 2026-10-08

## Status: NO topic files written

No source files were written in this pass. The network blocked every page
fetch, so no page could be read in full. The collection rules say that every
file, short code, fee and date must come from a page that was actually fetched.
Writing files from search-engine summaries would break those rules. Because
the assistant answers only from these files, it is better to leave them out
than to add facts nobody has checked.

What failed (2026-10-08):
- WebFetch returned "getaddrinfo ENOTFOUND" for every host tried, including
  jamb.gov.ng, waecnigeria.org, neco.gov.ng, ubec.gov.ng, nelf.gov.ng,
  premiumtimesng.com, thecable.ng, vanguardngr.com, guardian.ng,
  channelstv.com, en.wikipedia.org and even example.com.
- curl through the agent proxy returned "CONNECT tunnel failed, response 403"
  for all of the above and for punchng.com, dailytrust.com, techcabal.com,
  legit.ng, nairametrics.com and others.
- To fix this, a person must allow these hosts under Network access in the
  cloud environment settings (Edit environment > Allowed domains), or run the
  collection from a machine with normal internet access.

## Topics still to collect (none covered)

1. jamb-profile-and-utme-registration.md: profile code by SMS with NIN,
   UTME registration, accredited CBT centres, result checking
2. jamb-caps-admission-status.md: CAPS check, accept or reject
3. waec-wassce-private-candidates-and-results.md
4. neco-registration-and-results.md
5. ube-free-compulsory-basic-education.md (UBEC / UBE Act 2004)
6. nelfund-student-loan.md: eligibility and how to apply
7. exam-scams-fake-officials-score-upgrade.md

## Leads found by web search (NOT fetched, NOT verified)

These URLs showed up in search results only. Nobody has opened or read them.
Fetch each one and check it before using it.

JAMB fraud and "score upgrade" warnings (news that quotes JAMB):
- https://www.channelstv.com/2026/03/27/jamb-re-arrests-fraudster-warns-against-score-manipulation/
  (March 2026; search snippet says JAMB re-arrested a man posing as
  "Official Frederick" who offered score inflation on WhatsApp)
- https://guardian.ng/?p=1141790 ("Don't fall for score upgrade fraudsters,
  JAMB advises UTME candidates")
- https://dubawa.org/fraud-alert-this-website-is-fraudulent-you-cant-upgrade-your-jamb-score-by-paying-any-amount/

JAMB profile code and UTME registration (mostly blogs; better to use
jamb.gov.ng or a major newspaper):
- https://technext24.com/explainer/guide-to-registering-for-utme-de-2026/
- https://www.legit.ng/education/1686971-2026-utme-easy-step-by-step-instructions-how-successfully-register/
- https://techcabal.com/2024/01/04/how-to-create-jamb-profile-for-2025-utme/

JAMB CAPS (university helpdesk pages; FUNAAB ones date from 2017-2018):
- https://www.helpdesk.funaab.edu.ng/knowledgebase.php?article=32
- https://www.helpdesk.funaab.edu.ng/knowledgebase.php?article=33

## Claims to double-check before anyone writes them into a file

Search snippets made the claims below. Confirm each one on an official page
first:
- Profile code: send "NIN <11-digit NIN>" by SMS to 55019 or 66019, and the
  SMS costs N50. Snippets disagreed on whether 66019 is only for Direct Entry
  candidates and on the USSD format, so check against jamb.gov.ng.
- "RESEND" to 55019/66019 to get a lost profile code back.
- 2026 e-PIN prices of N7,200 (UTME) and N5,700 (DE) come from a December 2025
  blog, not from JAMB. Confirm them on jamb.gov.ng.
- 2026 UTME registration dates (31 Jan to 8 Mar 2026) come from a blog and are
  now out of date. The 2027 cycle dates have not been checked.
- Accepting or rejecting CAPS admission by SMS ("ACCEPT"/"REJECT"): this came
  from one blog only and is not confirmed by JAMB.
- No WAEC, NECO, UBEC or NELFUND information was collected at all.

Official sites to use first, once network access works: jamb.gov.ng,
waecnigeria.org, neco.gov.ng, ubec.gov.ng, nelf.gov.ng.
