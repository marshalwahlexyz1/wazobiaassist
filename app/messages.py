"""Fixed interface text. The Hausa, Igbo and Yoruba strings are DRAFTS: native
speakers on the team must review them before launch (plan, Fri 9 Oct)."""

from .config import LANGUAGES

# English voice notes use NCAIR's Nigerian-accented English speech model.
LANGUAGE_LABELS = {"ha": "Hausa", "ig": "Igbo", "yo": "Yorùbá", "en": "English (Nigerian)"}

LANGUAGE_MENU = (
    "Welcome to WazobiaAssist / Barka da zuwa / Nnọọ / Ẹ kú àbọ̀!\n\n"
    "Ask questions about Nigeria by voice note or text: scams and money, NIN, PVC and other "
    "government services, health, farming, school and exams, NAFDAC products and your rights.\n\n"
    + "\n".join(f"{i}. {LANGUAGE_LABELS[code]}" for i, code in enumerate(LANGUAGES, 1))
    + "\n\nReply with a number / Amsa da lamba / Zaa na nọmba / Fèsì pẹ̀lú nọ́mbà"
)

TEXT = {
    "en": {
        "privacy": (
            "WazobiaAssist answers your questions about Nigeria: scams and money, NIN, PVC, BVN and "
            "other government services, health, farming, school and exams, NAFDAC product checks, and "
            "your legal rights. Answers come from official sources such as NIMC, CBN, WHO, JAMB and "
            "NAFDAC. We save your questions and our answers anonymously (no name or phone number) to "
            "improve the service. Send DELETE at any time to erase your data."
        ),
        "ready": "Ask your question by voice note or text.",
        "listening": "Listening...",
        "heard": "I heard:",
        "rate": "Was this helpful? Reply 👍 or 👎",
        "up": "👍 Helpful",
        "down": "👎 Not helpful",
        "thanks": "Thank you!",
        "deleted": "Your data has been deleted. Send any message to start again.",
        "off_topic": (
            "I answer questions about Nigeria: scams and money, government services (NIN, PVC, BVN, "
            "CAC), health, farming, school and exams, NAFDAC products and your rights. Please ask a "
            "question about one of these."
        ),
        "general_note": "ℹ️ General knowledge, not from an official source. It may be out of date:",
        "error": "Sorry, something went wrong. Please try again.",
        "unsupported": "Please send a voice note or text.",
    },
    "ha": {
        "privacy": (
            "WazobiaAssist yana amsa tambayoyinka game da Najeriya: yaudara da kuɗi, NIN, PVC, BVN da "
            "sauran ayyukan gwamnati, lafiya, noma, makaranta da jarrabawa, binciken kayayyakin NAFDAC, "
            "da haƙƙoƙinka a shari'a. Amsoshin sun fito daga majiyoyin hukuma kamar NIMC, CBN, WHO, "
            "JAMB da NAFDAC. Muna adana tambayoyinka da amsoshinmu ba tare da sunanka ko lambar "
            "wayarka ba, don inganta sabis. Aiko DELETE a kowane lokaci don goge bayananka."
        ),
        "ready": "Yi tambayarka ta saƙon murya ko rubutu.",
        "listening": "Ina sauraro...",
        "heard": "Na ji:",
        "rate": "Shin wannan ya taimaka? Amsa da 👍 ko 👎",
        "up": "👍 Ya taimaka",
        "down": "👎 Bai taimaka ba",
        "thanks": "Na gode!",
        "deleted": "An goge bayananka. Aiko kowane saƙo don sake farawa.",
        "off_topic": (
            "Ina amsa tambayoyi game da Najeriya: yaudara da kuɗi, ayyukan gwamnati (NIN, PVC, BVN, "
            "CAC), lafiya, noma, makaranta da jarrabawa, kayayyakin NAFDAC da haƙƙoƙinka. Don Allah yi "
            "tambaya game da ɗaya daga cikinsu."
        ),
        "general_note": "ℹ️ Ilimi na gaba ɗaya, ba daga majiyar hukuma ba. Yana iya zama ba na yanzu ba:",
        "error": "Yi haƙuri, an sami matsala. Sake gwadawa.",
        "unsupported": "Don Allah aiko saƙon murya ko rubutu.",
    },
    "ig": {
        "privacy": (
            "WazobiaAssist na-aza ajụjụ gị gbasara Naịjirịa: aghụghọ na ego, NIN, PVC, BVN na ọrụ "
            "gọọmentị ndị ọzọ, ahụike, ọrụ ugbo, ụlọ akwụkwọ na ule, nlele ngwaahịa NAFDAC, na ikike gị "
            "n'iwu. Azịza si n'isi iyi gọọmentị dịka NIMC, CBN, WHO, JAMB na NAFDAC. Anyị na-echekwa ajụjụ gị na azịza anyị na-enweghị aha gị ma ọ bụ "
            "nọmba ekwentị gị, iji mee ka ọrụ a ka mma. Ziga DELETE mgbe ọ bụla iji hichapụ data gị."
        ),
        "ready": "Jụọ ajụjụ gị site na ozi olu ma ọ bụ ederede.",
        "listening": "Ana m ege ntị...",
        "heard": "Ihe m nụrụ:",
        "rate": "Nke a ọ nyere aka? Zaa 👍 ma ọ bụ 👎",
        "up": "👍 O nyere aka",
        "down": "👎 O nyeghị aka",
        "thanks": "Daalụ!",
        "deleted": "Ehichapụla data gị. Ziga ozi ọ bụla ka ịmalite ọzọ.",
        "off_topic": (
            "Ana m aza ajụjụ gbasara Naịjirịa: aghụghọ na ego, ọrụ gọọmentị (NIN, PVC, BVN, CAC), "
            "ahụike, ọrụ ugbo, ụlọ akwụkwọ na ule, ngwaahịa NAFDAC na ikike gị. Biko jụọ ajụjụ gbasara "
            "otu n'ime ha."
        ),
        "general_note": "ℹ️ Ihe ọmụma izugbe, ọ bụghị site na isi iyi gọọmentị. O nwere ike ọ bụghị nke ugbu a:",
        "error": "Ndo, nsogbu mere. Biko nwaa ọzọ.",
        "unsupported": "Biko ziga ozi olu ma ọ bụ ederede.",
    },
    "yo": {
        "privacy": (
            "WazobiaAssist ń dáhùn ìbéèrè yín nípa Nàìjíríà: jìbìtì àti owó, NIN, PVC, BVN àti àwọn "
            "iṣẹ́ ìjọba mìíràn, ìlera, iṣẹ́ àgbẹ̀, ilé-ìwé àti ìdánwò, àyẹ̀wò ọjà NAFDAC, àti ẹ̀tọ́ yín "
            "lábẹ́ òfin. Ìdáhùn wá láti orísun ìjọba bíi NIMC, CBN, WHO, JAMB àti NAFDAC. A ń tọ́jú ìbéèrè yín àti ìdáhùn wa láìsí orúkọ tàbí nọ́mbà fóònù yín, láti mú "
            "iṣẹ́ náà dára sí i. Ẹ fi DELETE ránṣẹ́ nígbàkígbà láti pa data yín rẹ́."
        ),
        "ready": "Ẹ béèrè ìbéèrè yín pẹ̀lú ohùn tàbí ọ̀rọ̀ kíkọ.",
        "listening": "Mo ń gbọ́...",
        "heard": "Ohun tí mo gbọ́:",
        "rate": "Ṣé èyí wúlò? Ẹ fèsì pẹ̀lú 👍 tàbí 👎",
        "up": "👍 Ó wúlò",
        "down": "👎 Kò wúlò",
        "thanks": "Ẹ ṣé!",
        "deleted": "A ti pa data yín rẹ́. Ẹ fi ọ̀rọ̀ èyíkéyìí ránṣẹ́ láti bẹ̀rẹ̀ lẹ́ẹ̀kan sí i.",
        "off_topic": (
            "Mo ń dáhùn ìbéèrè nípa Nàìjíríà: jìbìtì àti owó, iṣẹ́ ìjọba (NIN, PVC, BVN, CAC), "
            "ìlera, iṣẹ́ àgbẹ̀, ilé-ìwé àti ìdánwò, ọjà NAFDAC àti ẹ̀tọ́ yín. Ẹ jọ̀ọ́ ẹ béèrè nípa "
            "ọ̀kan nínú wọn."
        ),
        "general_note": "ℹ️ Ìmọ̀ gbogbogbò ni, kì í ṣe láti orísun ìjọba. Ó lè ti yí padà:",
        "error": "Ẹ má bínú, ìṣòro kan ṣẹlẹ̀. Ẹ tún gbìyànjú.",
        "unsupported": "Ẹ jọ̀ọ́, ẹ fi ohùn tàbí ọ̀rọ̀ kíkọ ránṣẹ́.",
    },
}


def t(lang: str | None, key: str) -> str:
    return TEXT.get(lang or "en", TEXT["en"]).get(key, TEXT["en"][key])
