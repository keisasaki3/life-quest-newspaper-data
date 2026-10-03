#!/usr/bin/env python3
"""Check a NEWSPAPER issue before it is published.

Usage: python3 scripts/validate_issue.py YYYY-MM-DD

Checks newspaper/YYYY-MM-DD.json against the schema and STYLE.md,
the registry entries for that date (and that they don't repeat
earlier days), and newspaper/latest.json. Exits 1 on any error.
Standard library only.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKET_GROUPS = ("fx", "stocks", "rates", "commodities", "crypto")
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️]")

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def text(obj, key, where):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        err(f"{where}: {key} が空")
        return ""
    return value


def check_sources(sources, where, required=True):
    if not isinstance(sources, list) or not sources:
        if required:
            err(f"{where}: sources が無い")
        return
    for i, s in enumerate(sources):
        if not isinstance(s, dict):
            err(f"{where}: sources[{i}] の形式が不正")
            continue
        text(s, "name", f"{where}.sources[{i}]")
        url = s.get("url", "")
        if not isinstance(url, str) or not url.startswith("https://"):
            err(f"{where}: sources[{i}].url が https でない")


def check_news(news):
    if not isinstance(news, list):
        err("news が配列でない")
        return
    if not 4 <= len(news) <= 7:
        err(f"news は5本前後（4〜7本）: {len(news)}本")
    ids = set()
    for n, a in enumerate(news, 1):
        where = f"news[{n}]"
        if not isinstance(a, dict):
            err(f"{where}: 形式が不正")
            continue
        aid = a.get("id", "")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", aid or ""):
            err(f"{where}: id は英小文字とハイフン: {aid!r}")
        if aid in ids:
            err(f"{where}: id が重複: {aid}")
        ids.add(aid)
        region = a.get("region", "")
        if not re.fullmatch(r"[a-z]+", region or ""):
            err(f"{where}: region は小文字の英語: {region!r}")
        if "comment" in a:
            err(f"{where}: comment フィールドは使わない")

        en = text(a, "headline_en", where)
        ja = text(a, "headline", where)
        if en:
            if len(en.split()) > 12:
                warn(f"{where}: 英語見出しが長い（{len(en.split())}語）: {en}")
            if not en.endswith((".", "?", "!")):
                err(f"{where}: 英語見出しは文で終える: {en}")
        if ja:
            if len(ja) > 30:
                warn(f"{where}: 日本語見出しが長い（{len(ja)}字）: {ja}")
            if "　" in ja:
                err(f"{where}: 見出しに全角スペース（新聞見出し調）: {ja}")
            if not ja.endswith(("。", "？", "！")):
                err(f"{where}: 日本語見出しは句点で終える: {ja}")

        summary = a.get("summary")
        if not isinstance(summary, list) or not 2 <= len(summary) <= 3:
            err(f"{where}: summary は2〜3組")
        else:
            for i, pair in enumerate(summary):
                if not isinstance(pair, dict):
                    err(f"{where}.summary[{i}]: 形式が不正")
                    continue
                text(pair, "en", f"{where}.summary[{i}]")
                text(pair, "ja", f"{where}.summary[{i}]")

        for field in ("headline_en", "headline", "background", "why_it_matters"):
            if isinstance(a.get(field), str) and EMOJI.search(a[field]):
                err(f"{where}: {field} に絵文字")
        for pair in summary if isinstance(summary, list) else []:
            if isinstance(pair, dict) and any(EMOJI.search(str(v)) for v in pair.values()):
                err(f"{where}: summary に絵文字")
        check_sources(a.get("sources"), where)


def check_markets(m):
    if not isinstance(m, dict):
        err("markets がオブジェクトでない")
        return
    text(m, "as_of", "markets")
    for group in MARKET_GROUPS:
        items = m.get(group)
        if not isinstance(items, list) or not items:
            err(f"markets.{group} が空")
            continue
        for i, item in enumerate(items):
            where = f"markets.{group}[{i}]"
            text(item, "symbol", where)
            if not isinstance(item.get("value"), (int, float)):
                err(f"{where}: value が数値でない")
            has_pct = isinstance(item.get("change_pct"), (int, float))
            has_bp = isinstance(item.get("change_bp"), (int, float))
            if not (has_pct or has_bp):
                err(f"{where}: change_pct か change_bp が必要")
            text(item, "source", where)
            if not str(item.get("source_url", "")).startswith("https://"):
                err(f"{where}: source_url が https でない")
    moves = m.get("market_moves")
    if not isinstance(moves, list) or not moves:
        err("markets.market_moves が空")
    else:
        for i, mv in enumerate(moves):
            for key in ("symbol", "move", "explanation"):
                text(mv, key, f"markets.market_moves[{i}]")


def check_culture(c):
    if not isinstance(c, dict):
        err("daily_culture がオブジェクトでない")
        return
    text(c, "title", "daily_culture")
    body = text(c, "body", "daily_culture")
    if body and len(body) < 500:
        warn(f"daily_culture.body が短い（{len(body)}字）")
    if not isinstance(c.get("explore"), list) or not c["explore"]:
        err("daily_culture.explore が空")
    check_sources(c.get("sources"), "daily_culture")


def check_quiz(q):
    if not isinstance(q, dict):
        err("daily_quiz がオブジェクトでない")
        return
    for key in ("genre", "question", "answer", "explanation"):
        text(q, key, "daily_quiz")
    check_sources(q.get("sources"), "daily_quiz")


def check_registry(name, date, issue_part, keys, unique_keys):
    path = ROOT / "registry" / f"{name}.json"
    reg = json.loads(path.read_text(encoding="utf-8"))
    items = reg.get("items", [])
    today = [x for x in items if x.get("date") == date]
    if len(today) != 1:
        err(f"registry/{name}.json: {date} の項目が {len(today)} 件（1件であること）")
        return
    entry = today[0]
    for key in keys:
        if not entry.get(key):
            err(f"registry/{name}.json: {date} の {key} が空")
    for key in unique_keys:
        past = {x.get(key) for x in items if x.get("date") != date}
        if entry.get(key) in past:
            err(f"registry/{name}.json: {key}={entry.get(key)!r} が過去と重複")
    title_key = "title" if name == "culture" else "question"
    if entry.get(title_key) != issue_part.get(title_key):
        err(f"registry/{name}.json: {title_key} が紙面と一致しない")


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", sys.argv[1]):
        sys.exit("usage: validate_issue.py YYYY-MM-DD")
    date = sys.argv[1]
    issue_path = ROOT / "newspaper" / f"{date}.json"
    issue = json.loads(issue_path.read_text(encoding="utf-8"))

    if issue.get("schemaVersion") != 1:
        err("schemaVersion は 1")
    if issue.get("date") != date:
        err(f"date がファイル名と一致しない: {issue.get('date')}")
    if issue.get("timezone") != "Asia/Tokyo":
        err("timezone は Asia/Tokyo")
    try:
        gen = datetime.fromisoformat(issue.get("generated_at", ""))
        if gen.utcoffset() is None or gen.utcoffset().total_seconds() != 9 * 3600:
            err("generated_at は +09:00 付き")
    except ValueError:
        err("generated_at が ISO 8601 でない")

    check_news(issue.get("news"))
    check_markets(issue.get("markets"))
    # DAILY CULTURE / DAILY QUIZ は 2026-10-03 から生成停止中。入っている号だけ検証する。
    if "daily_culture" in issue:
        check_culture(issue.get("daily_culture"))
        check_registry(
            "culture", date, issue.get("daily_culture") or {},
            ("title", "topic_key", "angle_key", "entities", "knowledge_claims"),
            ("topic_key",),
        )
    if "daily_quiz" in issue:
        check_quiz(issue.get("daily_quiz"))
        check_registry(
            "quiz", date, issue.get("daily_quiz") or {},
            ("genre", "question", "answer", "fact_key", "answer_key", "entities"),
            ("fact_key",),
        )

    latest = json.loads((ROOT / "newspaper" / "latest.json").read_text(encoding="utf-8"))
    if latest.get("date") != date or latest.get("path") != f"newspaper/{date}.json":
        err("latest.json がこの号を指していない")
    if latest.get("schemaVersion") != 1 or not latest.get("published_at"):
        err("latest.json の schemaVersion / published_at")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        sys.exit(1)
    print(f"OK {date}: news {len(issue['news'])}本, warnings {len(warnings)}")


if __name__ == "__main__":
    main()
