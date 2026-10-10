"""Keeps numbers, USSD codes and URLs unchanged through translation by swapping
them for placeholders before the model sees the text and restoring them after."""

import re

_PROTECTED = re.compile(
    r"«[^»\n]{1,120}»"           # product names marked «like this»
    r"|https?://\S+"             # URLs
    r"|www\.\S+"
    r"|\*[\d*]+#"                # USSD codes like *565*0#
    r"|\d[\d,.:/-]*\d|\d"        # numbers, amounts, dates, times
)


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
