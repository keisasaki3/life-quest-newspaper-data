#!/usr/bin/env python3
"""Print the readable text of a page or the items of an RSS feed.

Usage:
  python3 scripts/fetch_text.py URL            # article text
  python3 scripts/fetch_text.py --rss URL      # feed items: date | title | link

For checking facts when writing an issue. Standard library only; uses
curl with a browser user agent so the environment's proxy applies.
"""
import html
import signal
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"


def get(url):
    r = subprocess.run(["curl", "-sS", "-L", "-m", "30", "-A", UA, "-w", "\n%{http_code}", url],
                       capture_output=True)
    body, _, code = r.stdout.rpartition(b"\n")
    if code.strip() != b"200":
        sys.exit(f"HTTP {code.decode().strip() or r.stderr.decode().strip()} {url}")
    return body


def rss(url):
    root = ET.fromstring(get(url))
    for item in root.iter("item"):
        date = (item.findtext("pubDate") or item.findtext("{http://purl.org/dc/elements/1.1/}date") or "").strip()
        print(f"{date} | {(item.findtext('title') or '').strip()} | {(item.findtext('link') or '').strip()}")


def article(url):
    page = get(url).decode("utf-8", "replace")
    page = re.sub(r"<(script|style|noscript|svg|nav|footer|header)\b.*?</\1>", "", page, flags=re.S | re.I)
    title = re.search(r"<title[^>]*>(.*?)</title>", page, re.S | re.I)
    if title:
        print("TITLE:", html.unescape(title.group(1)).strip())
    for m in re.finditer(r'<meta[^>]+(?:property|name)="(article:published_time|og:description|description)"[^>]+content="([^"]*)"', page):
        print(f"{m.group(1).upper()}: {html.unescape(m.group(2))}")
    paras = re.findall(r"<(?:p|h1|h2|li)\b[^>]*>(.*?)</(?:p|h1|h2|li)>", page, re.S | re.I)
    for p in paras:
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", p))).strip()
        if len(text) > 40:
            print(text)


if __name__ == "__main__":
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    if len(sys.argv) == 3 and sys.argv[1] == "--rss":
        rss(sys.argv[2])
    elif len(sys.argv) == 2:
        article(sys.argv[1])
    else:
        sys.exit(__doc__)
