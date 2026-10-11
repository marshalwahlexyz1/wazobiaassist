"""Download NAFDAC's Food Products Database into data/nafdac_food.sqlite.

    python -m scripts.update_nafdac

setup.sh runs this and installs a daily refresh. The app also downloads it by
itself at startup if the file is missing.
"""

import sys

from app.config import Settings
from app.products import download_food_db


def main() -> None:
    target = Settings().nafdac_food_db
    try:
        total = download_food_db(target, say=lambda m: print(m, flush=True))
    except Exception as exc:
        sys.exit(f"NAFDAC food download failed: {exc}")
    print(f"Saved {total} food products to {target}")


if __name__ == "__main__":
    main()
