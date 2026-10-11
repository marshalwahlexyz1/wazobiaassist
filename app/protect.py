"""Numbers, USSD codes, URLs and product names that must survive translation
unchanged. protected_parts() lists them so the translation can be checked.

protect()/restore() swap them for placeholders. The pipeline no longer uses them:
in a test on 10 Oct, N-ATLaS scrambled placeholders in 7 of 9 translations (codes
became "0", step numbers became 0, 1, 2), but copied the real codes correctly in
9 of 9 when asked to keep them unchanged."""

import re

_PROTECTED = re.compile(
    r"«[^»\n]{1,120}»"           # product names marked «like this»
    r"|https?://\S+"             # URLs
    r"|www\.\S+"
    r"|\*[\d*]+#"                # USSD codes like *565*0#
    r"|\d[\d,.:/-]*\d|\d"        # numbers, amounts, dates, times
)


def protected_parts(text: str) -> list[str]:
    return [m.group(0) for m in _PROTECTED.finditer(text)]


def protect(text: str) -> tuple[str, list[str]]:
    kept: list[str] = []

    def swap(match: re.Match) -> str:
        kept.append(match.group(0))
        return f"[[{len(kept) - 1}]]"

    return _PROTECTED.sub(swap, text), kept


def restore(text: str, kept: list[str]) -> str:
    def swap(match: re.Match) -> str:
        i = int(match.group(1))
        return kept[i] if i < len(kept) else match.group(0)

    # Models sometimes add spaces inside the brackets; accept that too.
    return re.sub(r"\[\[\s*(\d+)\s*\]\]", swap, text)
