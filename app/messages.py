"""Fixed interface text. The Hausa, Igbo and Yoruba strings are DRAFTS: native
speakers on the team must review them before launch (plan, Fri 9 Oct)."""

from .config import LANGUAGES

LANGUAGE_LABELS = {"ha": "Hausa", "ig": "Igbo", "yo": "Yorùbá", "en": "English"}

LANGUAGE_MENU = (
    "Welcome to WazobiaAssist / Barka da zuwa / Nnọọ / Ẹ kú àbọ̀!\n\n"
    + "\n".join(f"{i}. {LANGUAGE_LABELS[code]}" for i, code in enumerate(LANGUAGES, 1))
    + "\n\nReply with a number / Amsa da lamba / Zaa na nọmba / Fèsì pẹ̀lú nọ́mbà"
)

TEXT = {
    "en": {
        "privacy": (
            "WazobiaAssist answers questions about farming, health, school, government services, "
            "and money and scams. We save your questions and our answers anonymously (no name or "
            "phone number) to improve the service. Send DELETE at any time to erase your data."
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
            "I can help with farming, health, school and exams, government services (NIN, PVC, BVN), "
            "and money and scams. Please ask a question about one of these."
        ),
        "general_note": "ℹ️ General knowledge, not from an official source. It may be out of date:",
        "error": "Sorry, something went wrong. Please try again.",
        "unsupported": "Please send a voice note or text.",
    },
    "ha": {
        "privacy": (
            "WazobiaAssist yana amsa tambayoyi game da noma, lafiya, makaranta, ayyukan gwamnati, "
            "da kuɗi da yaudara. Muna adana tambayoyinka da amsoshinmu ba tare da sunanka ko lambar "
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
            "Zan iya taimaka maka game da noma, lafiya, makaranta da jarrabawa, ayyukan gwamnati "
            "(NIN, PVC, BVN), da kuɗi da yaudara. Don Allah yi tambaya game da ɗaya daga cikinsu."
        ),
        "general_note": "ℹ️ Ilimi na gaba ɗaya, ba daga majiyar hukuma ba. Yana iya zama ba na yanzu ba:",
        "error": "Yi haƙuri, an sami matsala. Sake gwadawa.",
        "unsupported": "Don Allah aiko saƙon murya ko rubutu.",
    },
    "ig": {
        "privacy": (
            "WazobiaAssist na-aza ajụjụ gbasara ọrụ ugbo, ahụike, ụlọ akwụkwọ, ọrụ gọọmentị, "
            "na ego na aghụghọ. Anyị na-echekwa ajụjụ gị na azịza anyị na-enweghị aha gị ma ọ bụ "
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
            "Enwere m ike inyere gị aka gbasara ọrụ ugbo, ahụike, ụlọ akwụkwọ na ule, ọrụ gọọmentị "
            "(NIN, PVC, BVN), na ego na aghụghọ. Biko jụọ ajụjụ gbasara otu n'ime ha."
        ),
        "general_note": "ℹ️ Ihe ọmụma izugbe, ọ bụghị site na isi iyi gọọmentị. O nwere ike ọ bụghị nke ugbu a:",
        "error": "Ndo, nsogbu mere. Biko nwaa ọzọ.",
        "unsupported": "Biko ziga ozi olu ma ọ bụ ederede.",
    },
    "yo": {
        "privacy": (
            "WazobiaAssist ń dáhùn ìbéèrè nípa iṣẹ́ àgbẹ̀, ìlera, ilé-ìwé, iṣẹ́ ìjọba, àti owó àti "
            "jìbìtì. A ń tọ́jú ìbéèrè yín àti ìdáhùn wa láìsí orúkọ tàbí nọ́mbà fóònù yín, láti mú "
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
            "Mo lè ràn yín lọ́wọ́ nípa iṣẹ́ àgbẹ̀, ìlera, ilé-ìwé àti ìdánwò, iṣẹ́ ìjọba "
            "(NIN, PVC, BVN), àti owó àti jìbìtì. Ẹ jọ̀ọ́ ẹ béèrè nípa ọ̀kan nínú wọn."
        ),
        "general_note": "ℹ️ Ìmọ̀ gbogbogbò ni, kì í ṣe láti orísun ìjọba. Ó lè ti yí padà:",
        "error": "Ẹ má bínú, ìṣòro kan ṣẹlẹ̀. Ẹ tún gbìyànjú.",
        "unsupported": "Ẹ jọ̀ọ́, ẹ fi ohùn tàbí ọ̀rọ̀ kíkọ ránṣẹ́.",
    },
}


def t(lang: str | None, key: str) -> str:
    return TEXT.get(lang or "en", TEXT["en"]).get(key, TEXT["en"][key])
