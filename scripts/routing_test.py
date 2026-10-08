"""Checks that questions reach the right domain, in every language.

Native speakers add 10 questions per language to tests/routing_questions.csv
(columns: language, question, expected), then run on the GPU server:

    python -m scripts.routing_test
    python -m scripts.routing_test --lang ha

Each question is translated to English by N-ATLaS and routed, exactly as in the
live bot. Wrong routes are listed so keywords or domain descriptions can be fixed.
"""

import argparse
import csv
from collections import Counter

from app.assistant import Assistant
from app.config import ROOT, Settings

QUESTIONS = ROOT / "tests" / "routing_questions.csv"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang")
    args = parser.parse_args()

    assistant = Assistant(Settings())
    rows = list(csv.DictReader(QUESTIONS.open(encoding="utf-8")))
    rows = [r for r in rows if not args.lang or r["language"] == args.lang]
    total, right, misses = Counter(), Counter(), []
    for r in rows:
        english = assistant.translate(r["question"], r["language"], "en")
        got = assistant.route(english)
        key = (r["language"], r["expected"])
        total[key] += 1
        if got == r["expected"]:
            right[key] += 1
        else:
            misses.append((r, english, got))

    print(f"{'language':<9}{'domain':<13}correct")
    for key in sorted(total):
        print(f"{key[0]:<9}{key[1]:<13}{right[key]}/{total[key]}")
    n, ok = sum(total.values()), sum(right.values())
    print(f"\nOverall: {ok}/{n} ({100 * ok / max(n, 1):.0f}%)")
    if misses:
        print("\nWrong routes:")
        for r, english, got in misses:
            print(f"  [{r['language']}] {r['question']}\n      English: {english}\n      expected {r['expected']}, got {got}")


if __name__ == "__main__":
    main()
