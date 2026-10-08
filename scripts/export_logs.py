"""Export the interaction log to CSV and print the summary for the submission.

    python -m scripts.export_logs
"""

import csv
import sqlite3

from app.config import Settings


def main() -> None:
    settings = Settings()
    if not settings.db_path.exists():
        raise SystemExit(f"No log found at {settings.db_path}. Run the server first.")
    db = sqlite3.connect(settings.db_path)
    db.row_factory = sqlite3.Row
    rows = db.execute("SELECT * FROM interactions ORDER BY id").fetchall()

    out = settings.db_path.with_suffix(".csv")
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if rows:
            writer.writerow(rows[0].keys())
            writer.writerows(tuple(r) for r in rows)
    print(f"Wrote {len(rows)} interactions to {out}\n")

    def show(title: str, sql: str) -> None:
        print(title)
        for row in db.execute(sql):
            print("   " + " | ".join(str(v) for v in row))
        print()

    show("Interactions | unique users | failed:",
         "SELECT COUNT(*), COUNT(DISTINCT user_hash), COALESCE(SUM(error IS NOT NULL), 0) FROM interactions")
    for col in ("language", "domain", "channel", "input_type"):
        show(f"By {col}:", f"SELECT COALESCE({col}, '-'), COUNT(*) FROM interactions GROUP BY 1 ORDER BY 2 DESC")
    show("Ratings (up | down | not rated):",
         "SELECT SUM(rating = 'up'), SUM(rating = 'down'), SUM(rating IS NULL) FROM interactions")
    show("Satisfaction (% of rated answers that were helpful):",
         "SELECT ROUND(100.0 * SUM(rating = 'up') / NULLIF(SUM(rating IS NOT NULL), 0), 1) FROM interactions")
    show("Median response time (ms):",
         "SELECT latency_ms FROM interactions WHERE latency_ms IS NOT NULL ORDER BY latency_ms "
         "LIMIT 1 OFFSET (SELECT COUNT(*) / 2 FROM interactions WHERE latency_ms IS NOT NULL)")


if __name__ == "__main__":
    main()
