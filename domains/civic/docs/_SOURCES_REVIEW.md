# Civic sources review (attempt of 2026-10-08)

## Status: NO topic files written

No page could be fetched from this network on 2026-10-08. Every fetch failed:

- WebFetch returned `getaddrinfo ENOTFOUND` for every host tried, including nimc.gov.ng, www.nimc.gov.ng,
  nibss-plc.com.ng, inecnigeria.org, immigration.gov.ng, www.cac.gov.ng, icrp.cac.gov.ng, ncc.gov.ng,
  nairametrics.com, www.premiumtimesng.com, www.thecable.ng, techcabal.com, kuda.com, the Nigerian
  consulate in Atlanta and even en.wikipedia.org. punchng.com was refused outright.
- curl through the session proxy returned `CONNECT tunnel failed, response 403` for all of the same hosts
  (the environment's network policy does not allow them).

Only WebSearch worked. It returns titles, URLs and a model-written summary, not the page text. The rules
say every file must come from pages that were actually fetched, and codes and fees must be copied
exactly. So nothing was written from search results. A human, or a run with network access, needs to
fetch the pages below and write the files.

## Candidate URLs found by search (NOT fetched, NOT verified)

| Planned file | Candidate URL(s) |
|---|---|
| nin-enrolment.md / nin-retrieval.md | nimc.gov.ng (main site, no specific page found); https://nairametrics.com/2020/12/16/how-to-retrieve-your-national-identification-number-nimc/ ; https://www.withinnigeria.com/news/2022/12/14/nin-free-mandatory-to-access-all-govt-services-nimc/ |
| bvn.md | https://nibss-plc.com.ng/ussd-validation-services/ (official NIBSS *565 page) |
| voter-registration.md | https://inecnigeria.org/wp-content/uploads/2022/11/2021-CVR-Guidelines-Final.pdf ; https://cvr.inecnigeria.org ; https://www.thecable.ng/?p=724779 (INEC extends CVR to July 31) |
| passport.md | https://immigration.gov.ng ; https://passport.immigration.gov.ng ; https://www.nigeriaconsulateatlanta.org/immigration-rolls-out-enhanced-epassport-for-nigerians-in-us/ |
| cac-business-name.md | https://www.cac.gov.ng/?p=3443 (Registration steps for Business Names) ; https://icrp.cac.gov.ng/support/faq/ ; https://icrp.cac.gov.ng/assets/docs/crp-user-guide.pdf |
| nin-sim-linkage.md | https://ncc.gov.ng/sim-nin-linkage-faq (NCC FAQ) |

## Things to double-check when these pages are fetched

Search summaries were not fetched pages. They pointed to these disagreements, which need checking on the official page:

- **NIN retrieval USSD (*346#):** many guides name this code, but none of them could be fetched.
  Guides give different fees (some say N20, some give no amount). Confirm the code and fee on nimc.gov.ng.
- **BVN check:** the search summary says the NIBSS page lists `*565*0#` and a N20 fee. Several blogs
  give `5650#` instead. These conflict, so use neither until the NIBSS page is fetched.
- **Passport fees:** search results gave very different figures from 2024 and 2026 (fee changes are
  reported after September 2025). Include no fee unless it is taken from immigration.gov.ng.
- **Passport portal address:** immigration.gov.ng and passport.immigration.gov.ng are both named. Confirm which one is current.
- **CVR (voter registration) dates:** 2026 sources disagree (a two-week extension, 26 July 2026, 31 July, 30 August 2026).
  The 2026 window may have closed. Do not give dates without a current INEC notice.
- **CAC:** the portal moved from the CRP (pre.cac.gov.ng) to the iCRP (icrp.cac.gov.ng). Blogs give a N500 name
  reservation fee and about N10,000 for filing. These are not official, so leave them out unless the CAC fee schedule confirms them.
- **NIN-SIM linkage:** the NCC FAQ is from 2020-2021. It names network codes (*785#, *121*1#, SMS to 109, *996#).
  Check that they are still current before use.

## To unblock

Allow these hosts in the cloud environment's network settings, then run the task again:
nimc.gov.ng, nibss-plc.com.ng, cbn.gov.ng, inecnigeria.org, cvr.inecnigeria.org, immigration.gov.ng,
passport.immigration.gov.ng, cac.gov.ng, icrp.cac.gov.ng, ncc.gov.ng, and the news sites
(premiumtimesng.com, punchng.com, thecable.ng, nairametrics.com).
