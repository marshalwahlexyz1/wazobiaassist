# Money and scams: sources review

Date accessed for every URL below: 2026-10-08.

All five files were rebuilt from pages that were actually downloaded and read (curl / httpx, PDFs read with pypdf). Every `{{VERIFY}}` value from the old drafts was either confirmed on an opened page or deleted. The old `_draft-*` and `_fetched-*` files have been removed.

Access notes:
- cbn.gov.ng: HTML pages and the 2018 Consumer Protection FAQ PDF opened. Several other CBN PDFs returned a Cloudflare "Just a moment..." 403 page and could NOT be read: How_Lodge_Complaints.pdf, the 2019 Consumer Protection Regulations, the 2018 Regulation on Instant (Inter-Bank) EFT, the 2020 e-payment channels guidelines, and the 2025 APP-fraud exposure draft. Nothing from those PDFs is used.
- efcc.gov.ng and nccc.npf.gov.ng are JavaScript apps. Their text was read from the site's own code and its public data feeds (efcc.gov.ng/backend/..., nccc.npf.gov.ng/api/news/...), not from a rendered browser page. A human should open these pages in a browser and confirm the text is visible.
- ndic.gov.ng has been redesigned. Old URLs redirect: /frequently-asked-questions/ -> /faq; the MFB/PMI "facts" page -> /publications (no content), so it is not used.

## cbn-bank-complaints-and-fraud-warnings.md
- https://www.cbn.gov.ng/FinInc/FinLit/LodgeComplaint.html
- https://www.cbn.gov.ng/OUT/2018/CPD/CONSUMER%20PROTECTION%20FAQs.PDF
- https://www.cbn.gov.ng/supervision/cpdfraudandscam.html
- https://www.cbn.gov.ng/AboutCBN/Reforms.html
- https://nairametrics.com/2025/05/12/cbn-warns-nigerians-against-fake-contracts-grants-loans/
- https://www.vanguardngr.com/2026/04/cbn-warns-of-rising-fraud-targeting-bank-accounts/

Double-check:
- Timelines (2 weeks; 30 days for excess charges and loans, from a circular dated 30 June 2014; ATM dispense errors 72 hours) come from older CBN guidance (the FAQ PDF is from about 2018). The CBN Consumer Protection Regulations 2019 may set different timelines; that PDF was blocked. The file says the rules may have changed.
- Address "Central Business District, Abuja" and cpd@cbn.gov.ng are on the LodgeComplaint page (the email is hidden behind Cloudflare email protection and was decoded; it matches the FAQ PDF).
- The "no fee" statement is from FAQ Q28.
- The CBN iProtect complaint portal was not found on an opened page, so it is not mentioned.
- May 2025 warning: Nairametrics article dated 12 May 2025 says the statement was released "on Monday" (12 May 2025), signed by Mrs Hakama Sidi-Ali. April 2026 warning: Vanguard article dated 23 April 2026 says the statement was issued "yesterday". The file just says "May 2025" and "April 2026". Find the CBN press releases if you want exact dates.
- Instant-transfer opt-out paragraph: from the CBN Reforms page summary of a circular dated 12 March 2026 (effective 1 July 2026). The circular PDF itself was not opened.
- The CBN fraud page also lists the FBI's Internet Fraud Complaint Centre; left out as not relevant to Nigerian users.

## sec-unregistered-investment-schemes.md
- https://sec.gov.ng/for-investors/keep-track-of-circulars/public-notice-unregistered-online-investment-schemes/
- https://sec.gov.ng/for-investors/find-a-registered-operator/
- https://sec.gov.ng/enforcements/keep-track-of-enforcement-updates/
- https://sec.gov.ng/enforcements/keep-track-of-enforcement-updates/illegal-operator-value-growth-platform/
- https://sec.gov.ng/enforcements/keep-track-of-enforcement-updates/illegal-operator-alert-cbex-crypto-bridge-exchange-super-technology-st-technologies-international-ltd/

Double-check:
- Notice date: the SEC page shows "Published: May 14, 2026". The file uses 14 May 2026 (the 8 May date from news reports is not used).
- www.sec.gov.ng/cmos redirects to the "Find a Registered Operator" page; the page says you can verify credentials, view scope of services and confirm registration status.
- The file names one SEC-declared illegal platform (CBEX), as a factual example taken from the SEC alert published 11 June 2025. Decide whether you want named platforms in the assistant's answers.
- The SEC circulars list was checked up to 29 September 2026; no newer notice on unregistered investment schemes was found after 14 May 2026.

## fccpc-loan-app-rules.md (highest risk file)
- https://fccpc.gov.ng/digital-lending-fccpc-tackles-abuses-issues-landmark-regulations/
- https://fccpc.gov.ng/wp-content/uploads/2025/11/Digital-Electronic-Online-or-Non-Traditional-Consumer-Lending-Regulations-2025.pdf
- https://fccpc.gov.ng/about-us/faqs/
- https://fccpc.gov.ng/digital-lending-rule-fccpc-goes-after-violators/
- https://fccpc.gov.ng/status-update-investigation-into-possible-violations-of-privacy-and-other-rights-in-the-online-money-lending-industry-by-the-joint-task-force-fccpc-nitda-and-icpc/
- https://www.vanguardngr.com/2026/07/fccpc-resumes-digital-lending-regulation-as-court-vacates-restraining-order/
- https://www.naijanews.com/2026/07/22/appeal-court-void-fccpcs-deon-lending-regulations/

Double-check:
- LEGAL STATUS: interim order April 2026 (Vanguard; Naija News says WASPAN's originating summons was filed 14 April 2026); suit FHC/L/CS/760/2026 dismissed 20 July 2026 by Justice A.L. Allagoa (Vanguard, published 20 July 2026); notice of appeal dated 21 July 2026 (Naija News). BusinessDay (not used as a source) reported WASPAN also asked for enforcement to be suspended pending appeal. No Court of Appeal decision or stay was found as of 8 October 2026. Re-check before every release and update the "checked" date in the file.
- Effective date 21 July 2025 and announcement date 3 September 2025 are both from the FCCPC release.
- 24 hours / 48 hours complaint rule: regulation 22(d) of the regulation PDF. Report email lenderstaskforce@fccpc.gov.ng: regulation 26(2) and the FCCPC release.
- The ban on access to call logs, contacts and photos is only in the lender application form (Schedule 1, item 15), where lenders must confirm their apps will not have that access. The regulation text itself has no list of banned recovery practices (threats, name-calling, public shaming were NOT found in the PDF and were removed).
- The 5 January 2026 deadline was not on any opened FCCPC page and was removed; the file uses the FCCPC release of 21 January 2026 instead. The same release set an April 2026 deadline for provisionally eligible operators; no follow-up was found.
- Phone numbers: FCCPC FAQ lists 08056002020 and 08056003030 as hotlines for tips; the FCCPC website footer lists them as "Phone: 0805 600 2020, 0805 600 3030" with contact@fccpc.gov.ng.
- Fines (up to N100,000,000 or 1% of turnover) were verified but left out to keep the file focused on consumers.

## ndic-deposit-insurance.md
- https://ndic.gov.ng/faq
- https://ndic.gov.ng/about
- https://ndic.gov.ng/our-mandate?section=deposit-guarantee
- https://ndic.gov.ng/our-mandate?section=failure-resolution&topic=claims-settlement
- https://ndic.gov.ng/your-claims
- https://ndic.gov.ng/article?slug=update-on-the-revocation-of-the-operating-licenses-of-46-microfinance-banks-by-the-central-bank-of-nigeria
- https://www.cbn.gov.ng/OUT/2018/CPD/CONSUMER%20PROTECTION%20FAQs.PDF
- https://nairametrics.com/2024/05/02/ndic-raises-deposit-insurance-coverage-for-bank-customers-in-nigeria-to-n5-million/

Double-check:
- Limits: NDIC About page says N5,000,000 for DMBs and mobile money subscribers, N2,000,000 for MFBs, PMBs and PSBs. Nairametrics (2 May 2024) gives the same new limits and the old ones. The PMB figure (N2,000,000) is consistent across these sources.
- "Per depositor in each insured bank" wording is from the CBN FAQ (which still shows the old N500,000 / N200,000 amounts). No opened NDIC page explains how several accounts in one bank are added together, so that was removed.
- The exclusion list (insider deposits, interbank placements, borrowings) is only confirmed for the non-interest bank scheme. The draft's MFB/PMI exclusion list was removed because its page now redirects.
- 46 MFBs: NDIC article dated 1 July 2026. The link it gives to a "pre-verification claims form" now returns 404, so the file points to the "Your Claims" page instead. The four enquiry phone numbers were for that exercise.
- "Wonder banks" sentence is from CBN FAQ Q36.

## reporting-fraud-efcc-police.md
- https://www.cbn.gov.ng/supervision/cpdfraudandscam.html
- https://www.efcc.gov.ng/Contactus
- https://www.efcc.gov.ng/SubmitPetition
- https://www.efcc.gov.ng/
- https://www.efcc.gov.ng/news/efcc-sets-up-public-complaints-unit
- https://www.efcc.gov.ng/news/public-alert-about-impersonators-fake-efcc-sting-operations
- https://www.efcc.gov.ng/news/efcc-disclaims-lagos-roadblocks-online-invitations
- https://www.efcc.gov.ng/news/akure-now-hub-of-fake-efcc-operations-kingpin-in-efcc-net
- https://nccc.npf.gov.ng/news/npf-launches-enhanced-platform

Double-check (open each in a browser; see access note above):
- EFCC phone numbers: the Contact page shows +234 99 044 000 (main line) and +234 809 332 2644 (secondary line), and info@efcc.gov.ng. The site footer also shows +234 (9) 9044751 (not used).
- The "How to report a crime" page is at /SubmitPetition. Its "Report Cyber Crimes (EC2R2 Center)" option says "Coming Soon", so it is not mentioned.
- Reporting app: the EFCC home page promotes the "EFCC Eagle App" (Google Play id com.efcc.eagleapp; Apple App Store id6566193857). The draft's "EagleEye" website eagleeye.efcc.gov.ng was not found on any EFCC page and was removed.
- The old news URLs in the draft (/efcc/news-and-information/news-release/10454-... and /1026-...) no longer work; the same releases are now at /news/<slug>. The Public Complaints Desk release is dated 16 October 2024.
- Impersonation alert dated 21 April 2026 (Head, Media & Publicity, Dele Oyewale). The Channels TV article from the draft was not used.
- Invitation-letter advice is from 2014 and the "no online invitations / no Gmail" advice from 2019. Both are dated in the file. Old contacts in those releases (info@efccnigeria.org, DIA@EFCCNIGERIA.ORG, 09-9044758) were deliberately left out.
- Police: the statement dated 30 May 2024 gives https://nccc.npf.gov.ng/ereport/signin. The current site's code links its "File a Report" button to /signup and /portal/reports/new, so /ereport/signin may now just open the home page. Check which address works and update the file if needed.

## pos-wrong-transfer-and-fake-alerts.md: NOT written
- No official CBN page that could be opened covers sending money to the wrong account or fake credit alerts. The relevant CBN documents (2018 Regulation on Instant (Inter-Bank) EFT Services, https://www.cbn.gov.ng/out/2018/bpsd/regulation%20on%20instant%20payment.pdf; 2019 Consumer Protection Regulations; 2025 APP-fraud exposure draft) all returned Cloudflare 403 pages. Open them in a normal browser, save the PDFs, and write the file from them.
- The only related official content opened (CBN Reforms page: instant-transfer opt-out and N20,000 new-device limit, March 2026 circular) was added to cbn-bank-complaints-and-fraud-warnings.md.

## Topics not covered
- Wrong transfers / reversals and fake credit alerts (see above).
- Real scam messages from team and testers (from _TODO.md): not part of this task.
