#!/usr/bin/env python3
"""Fetch the MARKETS numbers for today's issue.

Usage: python3 scripts/fetch_markets.py > /tmp/markets.json

Prints the `markets` object (without `as_of` and `market_moves`, which
the writer adds) with the same symbols as past issues. Each value comes
from one source page and the change is against the previous close on
that same source. Anything that can't be fetched is left out and listed
under "missing" so the writer can say so in `as_of`.
Standard library only; uses curl so the environment's proxy applies.
"""
import csv
import datetime
import html
import io
import json
import re
import subprocess
import sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"

YAHOO = [
    ("fx", "USD/JPY", "JPY=X", None, 3),
    ("fx", "EUR/JPY", "EURJPY=X", None, 2),
    ("fx", "EUR/USD", "EURUSD=X", None, 4),
    ("stocks", "NIKKEI225", "^N225", None, 2),
    ("stocks", "S&P500", "^GSPC", None, 2),
    ("stocks", "NASDAQ", "^IXIC", None, 2),
    ("stocks", "DOW", "^DJI", None, 2),
    ("commodities", "GOLD", "GC=F", "USD/oz", 1),
    ("commodities", "WTI", "CL=F", "USD/bbl", 2),
    ("crypto", "BITCOIN", "BTC-USD", "USD", 2),
]
ORDER = {
    "fx": ["USD/JPY", "EUR/JPY", "EUR/USD"],
    "stocks": ["NIKKEI225", "TOPIX", "S&P500", "NASDAQ", "DOW"],
    "rates": ["JP10Y", "US2Y", "US10Y"],
    "commodities": ["GOLD", "WTI"],
    "crypto": ["BITCOIN"],
}


def get(url):
    return subprocess.run(
        ["curl", "-sS", "-L", "-m", "30", "-A", UA, url],
        check=True, capture_output=True,
    ).stdout


def pct(now, prev):
    return round((now - prev) / prev * 100, 2)


def yahoo(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=10d&interval=1d"
    r = json.loads(get(url))["chart"]["result"][0]
    closes = [(t, c) for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c is not None]
    (_, prev), (_, now) = closes[-2], closes[-1]
    return now, prev


def topix():
    page = get("https://kabutan.jp/stock/?code=0010").decode("utf-8", "replace")
    page = re.sub(r"<script.*?</script>", "", page, flags=re.S)
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", page)))
    prev = re.search(r"前日終値 ([\d,]+\.\d+)", text)
    now = re.search(r"終値 ([\d,]+\.\d+) \( 15:30 \)", text)
    return float(now.group(1).replace(",", "")), float(prev.group(1).replace(",", ""))


def us_treasury():
    rows = []
    year = datetime.date.today().year
    for y in (year, year - 1):  # early January has only one row this year
        url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
               f"daily-treasury-rates.csv/{y}/all?type=daily_treasury_yield_curve&field_tdr_date_value={y}&_format=csv")
        rows += list(csv.DictReader(io.StringIO(get(url).decode())))
        if len(rows) >= 2:
            break
    return rows[0], rows[1]  # newest first


def jgb10_rows(url):
    text = get(url).decode("shift_jis", "replace")
    head = next(r for r in csv.reader(io.StringIO(text)) if r and r[0] == "基準日")
    i = head.index("10年")
    return [(r[0], float(r[i])) for r in csv.reader(io.StringIO(text))
            if r and re.match(r"[A-Z]\d+\.\d+\.\d+", r[0]) and re.match(r"-?\d", r[i])]


def jgb10():
    rows = jgb10_rows("https://www.mof.go.jp/jgbs/reference/interest_rate/jgbcm.csv")
    if len(rows) < 2:
        # jgbcm.csv holds only the current month; on its first business day
        # the previous close is in the full-history file (oldest first).
        rows = [r for r in jgb10_rows("https://www.mof.go.jp/jgbs/reference/interest_rate/data/jgbcm_all.csv")
                if r[0] not in dict(rows)] + rows
    return rows[-1][0], rows[-1][1], rows[-2][1]


def main():
    out = {k: [] for k in ORDER}
    missing = []

    for group, sym, ysym, unit, nd in YAHOO:
        try:
            now, prev = yahoo(ysym)
            item = {"symbol": sym, "value": round(now, nd), "change_pct": pct(now, prev),
                    "change": round(now - prev, nd)}
            if unit:
                item["unit"] = unit
            item["source"] = "Yahoo Finance"
            item["source_url"] = f"https://finance.yahoo.com/quote/{ysym.replace('^', '%5E')}/"
            out[group].append(item)
        except Exception as e:  # noqa: BLE001
            missing.append(f"{sym}: {e}")

    try:
        now, prev = topix()
        out["stocks"].append({"symbol": "TOPIX", "value": now, "change_pct": pct(now, prev),
                              "change": round(now - prev, 2),
                              "change": round(now - prev, 2),
                              "source": "株探", "source_url": "https://kabutan.jp/stock/?code=0010"})
    except Exception as e:  # noqa: BLE001
        missing.append(f"TOPIX: {e}")

    try:
        date, now, prev = jgb10()
        out["rates"].append({"symbol": "JP10Y", "value": now, "unit": "%",
                             "change_bp": round((now - prev) * 100, 1),
                             "source": f"財務省 国債金利情報 ({date})",
                             "source_url": "https://www.mof.go.jp/jgbs/reference/interest_rate/index.htm"})
    except Exception as e:  # noqa: BLE001
        missing.append(f"JP10Y: {e}")

    try:
        latest, before = us_treasury()
        for sym, col in (("US2Y", "2 Yr"), ("US10Y", "10 Yr")):
            now, prev = float(latest[col]), float(before[col])
            out["rates"].append({"symbol": sym, "value": now, "unit": "%",
                                 "change_bp": round((now - prev) * 100),
                                 "source": f"U.S. Treasury ({latest['Date']})",
                                 "source_url": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve"})
    except Exception as e:  # noqa: BLE001
        missing.append(f"US2Y/US10Y: {e}")

    for group, names in ORDER.items():
        out[group].sort(key=lambda x: names.index(x["symbol"]))
    json.dump({"markets": out, "missing": missing}, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
