"""Download NAFDAC's Food Products Database into data/nafdac_food.sqlite.

    python -m scripts.update_nafdac

The public table on https://nafdac.gov.ng/food-products-database/ loads its rows
from the site in chunks of 3,000; this fetches them one at a time, politely, and
replaces the local copy only when the download is complete. setup.sh runs it
and installs a daily refresh.
"""

import html
import re
import sqlite3
import sys
import time

import httpx

from app.config import Settings
from app.products import norm_no

PAGE = "https://nafdac.gov.ng/food-products-database/"
HEADERS = {"User-Agent": "WazobiaAssist (NAIC 2026; daily refresh)"}


def data_url(client: httpx.Client) -> str:
    html = client.get(PAGE).text
    m = re.search(r'https:[^"]*admin-ajax\.php\?action=wp_ajax_ninja_tables_public_action[^"]*', html)
    if not m:
        raise SystemExit("Could not find the data link on the NAFDAC page; the page layout may have changed.")
    url = m.group(0).replace("\\/", "/").replace("\\u0026", "&")
    return re.sub(r"&chunk_number=\d+", "", url)


def main() -> None:
    target = Settings().nafdac_food_db
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    db = sqlite3.connect(tmp)
    db.execute("""CREATE TABLE food (number TEXT, number_norm TEXT, name TEXT, category TEXT,
                  subcategory TEXT, packsize TEXT, presentation TEXT, applicant TEXT,
                  manufacturer TEXT, country TEXT, issued TEXT, expiry TEXT)""")
    total = 0
    with httpx.Client(headers=HEADERS, timeout=90, follow_redirects=True) as client:
        base = data_url(client)
        for chunk in range(100):
            rows = client.get(f"{base}&chunk_number={chunk}").json()
            if not rows:
                break
            values = []
            for row in rows:
                v = {k: html.unescape(x) if isinstance(x, str) else x for k, x in row.get("value", row).items()}
                values.append((v.get("nafdacnumber", ""), norm_no(v.get("nafdacnumber", "")),
                               v.get("productname", ""), v.get("category", ""), v.get("subcategory", ""),
                               v.get("packsize", ""), v.get("presentation", ""), v.get("applicantname", ""),
                               v.get("manufacturer", ""), v.get("country", ""), v.get("issuedate", ""),
                               v.get("expirydate", "")))
            db.executemany("INSERT INTO food VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", values)
            total += len(values)
            print(f"chunk {chunk}: {len(values)} products", flush=True)
            time.sleep(1)  # be gentle with NAFDAC's server
    if total == 0:
        sys.exit("No products downloaded; keeping the old copy.")
    db.execute("CREATE INDEX idx_number ON food(number_norm)")
    db.commit()
    db.close()
    tmp.replace(target)
    print(f"Saved {total} food products to {target}")


if __name__ == "__main__":
    main()
