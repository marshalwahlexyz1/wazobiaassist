# Health sources: review notes

Date accessed for all sources: 2026-10-08

## Important: network limits during collection

This session could not reach who.int, iris.who.int, apps.who.int, unicef.org, nphcda.gov.ng, health.gov.ng, ncdc.gov.ng, ncbi.nlm.nih.gov, build.fhir.org or web.archive.org (the egress proxy refused them, so WebFetch failed too). The only official health source that could be fetched in full was WHO's own GitHub organisation (github.com/WorldHealthOrganization), which publishes the spreadsheets of the WHO Digital Adaptation Kit (DAK) for antenatal care. Both files below come from those spreadsheets, downloaded from the public WHO repository (branch master, commit 2ed771d, dated 2025-10-27). Web search summaries were seen for other topics but were NOT used, because the rules require fetched pages.

## Files written

### pregnancy-danger-signs.md
- URL: https://github.com/WorldHealthOrganization/smart-anc/blob/master/input/l2/WHO-SRH-21.2-eng.xlsx
- The workbook's COVER sheet titles it "Digital adaptation kit for antenatal care: operational requirements for implementing WHO recommendations in digital systems / Web Annex B: Decision support logic" (WHO, 2021, CC BY-NC-SA 3.0 IGO). The file name says WHO-SRH-21.2, but the cover says Web Annex B; a reviewer may want to confirm the official document number.
- Sheets used: ANC.DT.01 Danger signs (health-worker quick check, citing WHO IMPAC 2015); ANC.S.03 Counselling schedule rows "Counsel to immediately go to the hospital if severe danger signs are present" and "Counselling on seeking care for danger signs" (citing WHO recommendations on health promotion interventions, 2015); "Counselling on birth preparedness and complications readiness"; ANC.DT.34 Birth preparedness counselling (risk factors for facility birth).
- To double-check:
  - The DAK is written for health workers. The two lay lists (severe signs = go to hospital immediately; other signs = seek care) are paraphrased in plain English. Please confirm wording such as "belly" for abdomen and "fits" for convulsions suits the audience.
  - The paragraph telling the woman to go to the nearest health facility/PHC now was required by the WazobiaAssist rules. Its referral wording ("not wait at home", "primary health centre") is not quoted from WHO.
  - The list of women advised to give birth in a facility (age 17 or under, first pregnancy, 6 or more previous births, etc.) is taken from WHO IMPAC via the DAK. Check it against Nigerian FMoH policy, which may advise facility birth for all women.
  - Danger signs AFTER delivery (mother) and in NEWBORNS are NOT covered. No fetched source had them.

### antenatal-care-visits.md
- URLs: https://github.com/WorldHealthOrganization/smart-anc/blob/master/input/l2/WHO-SRH-21.2-eng.xlsx ; https://github.com/WorldHealthOrganization/smart-anc/blob/master/input/l2/WHO-SRH-21.3-eng.xlsx (Web Annex C: Indicators table)
- Sheets used: ANC.S.01 Contact schedule (8 contacts at 12, 20, 26, 30, 34, 36, 38, 40 weeks; first contact recommended before 20 weeks; must come in at 41 weeks, not counted as a contact; interval rules 8/6/4/2 weeks; Rule 7 for late starters); ANC.S.02 Lab and tests schedule; ANC.S.03 Counselling schedule (8-contact counselling, breastfeeding, malaria prevention with insecticide-treated bed net); Web Annex C indicators ANC.IND.1 (first contact before 12 weeks), ANC.IND.7 and ANC.IND.9 (blood pressure, fetal heartbeat).
- To double-check:
  - This is the WHO 2016 model with 8 contacts. I could not fetch the Nigerian Federal Ministry of Health's national ANC guideline. Confirm whether Nigeria's current policy matches 8 contacts and these weeks before the assistant presents it as advice for Nigeria.
  - There is a small tension in the WHO material: the schedule says the first contact is "recommended when the woman is less than 20 weeks" and is due at 12 weeks, while the indicator measures first contact "before 12 weeks". The file states both.
  - HIV, hepatitis and TB testing in the DAK depend on how common those diseases are locally. The file says "tests such as HIV and syphilis tests" and does not say who must be tested. Please check this wording.
  - Malaria-prevention medicine in pregnancy (IPTp) is in the source but was left out on purpose (no drug names or doses). A health professional may want to add an approved, dose-free line on IPTp from an FMoH or NMEP source.

## Topics NOT covered (no fetchable authoritative source)

- Nigeria routine immunisation schedule (NPHCDA): NOT WRITTEN. nphcda.gov.ng, who.int and unicef.org were all blocked. The only Nigeria-specific schedule reachable was a community FHIR draft (Nigeria-FHIR-Community/NPHCDA-ImmunizationIG), which says it is "not an authorized publication", so it was not used. WHO's immunisation DAK repo has no Nigeria-specific schedule. A health professional should supply the current official NPHCDA schedule (birth, 6, 10, 14 weeks, 9 months, 15 months, HPV), ideally from a printed NPHCDA card or the NPHCDA website. Do not fill it in from memory.
- Danger signs after delivery (mother) and danger signs in newborns: not written.
- Fever in children and malaria (testing before treatment, bed nets for children): not written. The only malaria content is the bed-net advice for pregnant women in antenatal-care-visits.md.
- Diarrhoea in children (ORS and zinc, dehydration danger signs): not written.
- Cough or fast breathing in children (pneumonia danger signs): not written. The WHO EmCare repository (smart-emcare) was checked. It contains only coded data elements for health workers and no plain-language text, so it was not used.

Suggested next step: collect these from WHO fact sheets (who.int/news-room/fact-sheets), the UNICEF Nigeria pages, and NPHCDA on a network that can reach those sites, then add them here using the same format.
