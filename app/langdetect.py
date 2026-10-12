"""Which language a typed question is written in.

People often pick one language in the menu and then type in another (a user who
chose English asks in Hausa). The question must then be translated from the
language it is written in, or retrieval works on untranslated text and the
answer is poor. Voice notes are not checked: they are transcribed with the
chosen language's speech model.

Letters only one language uses decide first (Hausa ɓ ɗ ƙ ƴ, Yorùbá ẹ ṣ, Igbo
ị ụ ṅ). Otherwise common words decide, written with or without tone marks, and
only when they clearly outnumber English words. Pidgin and English return None.
"""

import re
import unicodedata

_LETTERS = {"ha": "ɓɗƙƴ", "yo": "ẹṣ", "ig": "ịụṅ"}

_WORDS = {
    "ha": """yaya zan kaina menene mene shin wane wace yake nake kake sami samu lambar cutar
        kudin kudi yadda ake ina tana yana sannu daga zazzabin sauro kare rajista gwamnati
        nawa ina ne wannan kuma amma saboda yanzu lafiya magani makaranta jarrabawa noma
        katin zabe biya wutar lantarki""",
    "yo": """bawo kini oruko mo se le fun nibo melo awon eyi naijiria jowo omo ise idibo kaadi
        ijoba owo ile iwe nipa ti ni wa ki je yi bi lati sugbon nitori iba oogun oko
        dokita akoole banki""",
    "ig": """kedu gini olee ebee biko nwere enwere ndi ihe nke ahu ulo oru ochichi otu aga
        emere ego ogwu oria akwukwo ule ugbo ana m ka m ga ime nweta naijiria""",
}
_WORDS = {lang: set(words.split()) for lang, words in _WORDS.items()}

_ENGLISH = set("""the is are was how what who where when why which can could do does did i my me
    you your to a an of for and in on with about get have has be from it this that please""".split())


def _plain(text: str) -> str:
    """Lower case without tone marks or dots below, so 'Báwo' and 'bawo' match."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def written_language(text: str) -> str | None:
    """'ha', 'ig' or 'yo' when the text is clearly written in that language, else None."""
    lower = unicodedata.normalize("NFC", text.lower())
    by_letter = [lang for lang, letters in _LETTERS.items() if any(ch in lower for ch in letters)]
    if len(by_letter) == 1:
        return by_letter[0]

    words = re.findall(r"[a-z]+", _plain(text))
    if not words:
        return None
    english = sum(w in _ENGLISH for w in words)
    scores = {lang: sum(w in vocab for w in words) for lang, vocab in _WORDS.items()}
    best = max(scores, key=scores.get)
    runner_up = max(v for lang, v in scores.items() if lang != best)
    if scores[best] >= 2 and scores[best] > runner_up and scores[best] > english:
        return best
    return None
