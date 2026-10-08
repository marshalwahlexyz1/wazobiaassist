# Civic sources review (2026-10-08)

All seven topic files were written from pages opened on **2026-10-08** (date accessed for every URL below).
nimc.gov.ng, inecnigeria.org and cvr.inecnigeria.org are JavaScript sites, so they were read in a headless
browser (the plain fetch script returns no text for them). www.cac.gov.ng is behind a Cloudflare bot check and
could not be opened, so the CAC file uses only the iCRP portal (icrp.cac.gov.ng).

Every USSD code, fee, phone number, email and web address in the files was checked by script against the saved
page text. Fees and codes that conflicted between official pages were left out (see below).

## nin-enrolment.md

- https://nimc.gov.ng/nin
- https://nimc.gov.ng/storage/Uploads/NIMC_FAQs_2026.docx (linked from https://nimc.gov.ng/faqs)
- https://nimc.gov.ng/fees
- https://nimc.gov.ng/fraud-alert
- https://nimc.gov.ng/press-releases/nimc-restates-commitment-to-zero-tolerance-for-extortion (Dec 20, 2024)
- https://nimc.gov.ng/nin-enrolment-documents

Double-check:
- **Customer care email:** the 2024 extortion press release says `customercare@nimc.gov.ng`; the 2026 FAQ, the fraud-alert page and a 2025 press release say `nimccustomercare@nimc.gov.ng`. The file uses the second one.
- **Toll-free line:** the FAQ gives `08000616462` many times, but once as `0800616462` (ward section). The file uses `08000616462`.
- **Enrolment centre locator:** the FAQ links `https://nimc.gov.ng/nimc-enrolment-centres/`; the live site route is `https://nimc.gov.ng/enrolment-centres` (used in the file). The locator map did not load in the headless browser.
- The official "How to enrol" page (https://nimc.gov.ng/nin/nin-issuance) showed "Something went wrong" on 2026-10-08, so the steps come from the NIMC FAQs 2026 document instead. Recheck that page when it works.
- Documents list: the FAQ gives a short list ("valid government ID and your BVN", and for pre-enrolment "Affidavit, NPC Birth Certificate, Nigerian Passport, Nigerian Driver's License or Other Government issued Document"). Appendix III of the FAQ has a much longer "source documents" list that was not copied.
- Left out: the 2026 Ward-Level Enrolment Project dates (started 16 February 2026, planned for six weeks), as it has probably ended.

## nin-retrieval.md

- https://nimc.gov.ng/sms-services
- https://nimc.gov.ng/storage/Uploads/NIMC_FAQs_2026.docx
- https://nimc.gov.ng/nin/nin-for-sim-tips
- https://nimc.gov.ng/nin/nin-slip-reissuance
- https://nimc.gov.ng/mobile-digital-id
- https://nimc.gov.ng/fraud-alert

Double-check:
- `*346#` and its N20 fee are confirmed by two NIMC sources (SMS services page and FAQs 2026). The NCC FAQ also confirms the code.
- **NIN slip re-issue fee LEFT OUT, because NIMC's own pages disagree:** the slip re-issuance page says N500, the fees page says N600 (loss, damage or theft) and N1000 per field (change of record), and the FAQs 2026 say "NIN Slip Reprint – N1,000". A human should ask NIMC which is current.
- The self-print route (https://myportal.nimc.gov.ng with the NIMC Mobile ID app, and `*346*2*Your NIN#` for UserID/OTP by SMS) is from the live mobile-digital-id page, but that page describes the older MWS Mobile ID app (stats from 2021-2022) and NIMC now promotes NINAuth. Confirm this still works.

## bvn.md

- https://nibss-plc.com.ng/bank-verification-numberbvn/
- https://nibss-plc.com.ng/ussd-validation-services/
- https://nibss-plc.com.ng/nrbvn/
- https://nimc.gov.ng/fraud-alert

Double-check:
- `*565*0#` (check BVN) and `*565*1#` (validate BVN), each with a N20 service fee, are from the official NIBSS page. The page is not dated. The `5650#` code found on blogs was NOT used.
- NIBSS does not say whether BVN enrolment itself is free, so no fee or "free" claim is made. The anti-fraud sentence comes from NIMC's fraud-alert page, not from NIBSS or CBN.
- https://bvn.nibss-plc.com.ng/ returned 502 and no CBN BVN page was found (cbn.gov.ng BVN URL returned 404).

## voter-registration-and-pvc.md

- https://cvr.inecnigeria.org/ ("The Continuous Voter Registration (CVR) exercise has ended")
- https://cvr.inecnigeria.org/Public/getStarted
- https://cvr.inecnigeria.org/vvs
- https://cvr.inecnigeria.org/Home/help
- https://inecnigeria.org/voters/education (including the "Voter FAQs" tab)
- News fallback: https://blueprint.ng/inec-announces-date-for-nationwide-pvc-collection/ ; https://www.legit.ng/politics/1733273-breaking-inec-announces-date-voters-card-collection/ ; https://businessday.ng/news/article/inec-resumes-nationwide-continuous-voters-registration/

Double-check:
- **Nationwide PVC collection from Friday, October 9, 2026** comes only from news reports (Blueprint and Legit.ng, both quoting INEC Chairman Prof. Joash Amupitan). No INEC page with this date was found. Confirm on inecnigeria.org or INEC's X account, and add collection hours and venues when INEC publishes them.
- **CVR third phase 11 May 2026 to 10 July 2026** is from BusinessDay quoting an INEC statement, not an INEC page.
- **No anti-tout sentence** in this file, because no INEC page opened says anything about agents or fees.
- **Election date LEFT OUT:** the INEC home page shows a countdown to "January 16, 2027" for Presidential/House of Assembly elections; verify before adding.
- The 8:30 AM to 2:30 PM polling hours are from INEC's "2023-2027" election procedure text.
- The old CVR guidelines PDF (inecnigeria.org/wp-content/uploads/2022/11/2021-CVR-Guidelines-Final.pdf) is now 404, so registration documents are not listed.

## passport.md

- https://immigration.gov.ng/passports/ (requirement tabs read from the page HTML)
- https://passport.immigration.gov.ng/
- https://immigration.gov.ng/nigeria-immigration-service-announces-upward-review-of-nigerian-standard-passport-fees/
- https://immigration.gov.ng

Double-check:
- **Fees** are from the NIS press release, effective 1st September 2025: N100,000 (32-page, 5-year) and N200,000 (64-page, 10-year) in Nigeria; $150 and $230 abroad. No fee is given for the 64-page 5-year passport. A 2026 search found no newer official fee notice, but one commercial page claimed a new price "from April, 2026" (not verified, not used). Recheck before each release.
- Portal address: passport.immigration.gov.ng is the in-Nigeria portal (it links separately to an "Apply from outside Nigeria" route).
- NIS HQ phone `+234-912-1900-655` and `nis.servicom@nigeriaimmigration.gov.ng` are from the NIS site footer (note the email domain is nigeriaimmigration.gov.ng, not immigration.gov.ng).

## cac-business-name.md

- https://icrp.cac.gov.ng/support/faq/
- https://icrp.cac.gov.ng/assets/docs/crp-user-guide.pdf ("Interim User Guide: CRP 3.0")
- https://icrp.cac.gov.ng/

Double-check:
- **No fees given.** The only official amount seen was "N500 only" for a name availability request, in an old CRP-era section of the iCRP FAQ (it also refers to services.cac.gov.ng). The blog figure of about N10,000 for filing was not found on any CAC page. Get the current fees from the CAC fee schedule on www.cac.gov.ng (blocked by Cloudflare from this environment).
- The www.cac.gov.ng "Registration steps for Business Names" page (https://www.cac.gov.ng/?p=3443) could not be opened (Cloudflare bot check). Compare it with this file.
- "Business Name registrations are now AI-approved and processed instantly" is from the iCRP FAQ; check this is still true.

## nin-sim-linkage.md

- https://nimc.gov.ng/nin/nin-for-sim-tips
- https://ncc.gov.ng/sim-nin-linkage-faq
- https://nimc.gov.ng/sms-services

Double-check:
- `*996#` (all networks) is given by both NIMC and the NCC; `*996*NIN#` only by the NCC FAQ.
- **Left out on purpose:** the network-specific codes in the NCC FAQ (`*785#` MTN, `*121*1#` Airtel, SMS "UPDATENIN" to 109 for Glo) and the 2020-2021 deadlines, because that FAQ dates from the 2020-2021 exercise and the current NIMC page lists only `*996#` and the network websites. Also left out: the temporary waiver of the N20 `*346#` charge mentioned by the NCC FAQ.
- "Linking is free" is from the 2020-2021 NCC FAQ; confirm it still applies.
- Network websites (airtel.com.ng/NIN_information, nin.mtn.ng, gloworld.com/ng/nin, 9mobile.com.ng/nin) are copied from the NIMC page but were not opened; check they still work.
- The NIMC page's "link up to seven (7) mobile numbers with the NIMC Mobile ID app" was not used, as the MWS app may have been replaced by NINAuth.

## Not covered

- Birth certificate, driver's licence and other items in domain.json keywords: no sources were collected for them.
