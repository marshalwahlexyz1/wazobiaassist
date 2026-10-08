"""Ask one question from the terminal, showing every pipeline step.

    python -m scripts.ask --lang ha --text "Ina so in san yadda zan sami NIN"
    python -m scripts.ask --lang yo --audio question.ogg
"""

import argparse

from app.assistant import Assistant
from app.config import LANGUAGES, Settings
from app.messages import t


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=LANGUAGES, default="en")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text")
    group.add_argument("--audio", help="audio file (ogg, mp3, wav, webm...)")
    args = parser.parse_args()

    r = Assistant(Settings()).ask(args.lang, text=args.text, audio_path=args.audio,
                                  off_topic_reply=t(args.lang, "off_topic"))
    print(f"Heard:        {r.transcript}")
    print(f"In English:   {r.question_en}")
    print(f"Domain:       {r.domain}")
    print(f"Sources:      {', '.join(r.sources) or '-'}")
    print(f"Answer (en):  {r.answer_en or '-'}")
    print(f"Answer:       {r.answer}")
    print(f"Time:         {r.latency_ms} ms")


if __name__ == "__main__":
    main()
