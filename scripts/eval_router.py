"""Measure how often questions are routed to the right domain.

    python -m scripts.eval_router            (uses eval/router_cases.jsonl)

Runs the real translate + route steps, so start vLLM first (with MOCK=1 only the
keyword routing is meaningful). Native speakers: add Hausa, Igbo and Yoruba cases.
"""

import json
from collections import defaultdict

from app.assistant import Assistant
from app.config import ROOT, Settings


def main() -> None:
    assistant = Assistant(Settings())
    lines = (ROOT / "eval" / "router_cases.jsonl").read_text(encoding="utf-8").splitlines()
    cases = [json.loads(line) for line in lines if line.strip()]
    per_lang = defaultdict(lambda: [0, 0])
    misses = []
    for case in cases:
        question_en = assistant.translate(case["text"], case["lang"], "en")
        got = assistant.route(question_en)
        ok = got == case["domain"]
        per_lang[case["lang"]][0] += ok
        per_lang[case["lang"]][1] += 1
        if not ok:
            misses.append((case, got, question_en))
    total = sum(correct for correct, _ in per_lang.values())
    print(f"Routing accuracy: {total}/{len(cases)} = {100 * total / len(cases):.0f}%")
    for lang, (correct, n) in sorted(per_lang.items()):
        print(f"  {lang}: {correct}/{n}")
    for case, got, question_en in misses:
        print(f"  MISS [{case['lang']}] expected {case['domain']}, got {got}: {case['text']!r} -> {question_en!r}")


if __name__ == "__main__":
    main()
