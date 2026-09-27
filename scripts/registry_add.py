#!/usr/bin/env python3
"""Add (or replace) one day's entry in a registry file, keeping its layout.

Usage: python3 scripts/registry_add.py culture|quiz ENTRY.json

ENTRY.json holds one item with a "date". An existing item with the same
date is replaced; otherwise the item is appended. The file keeps the
existing style: 2-space indent, one key per line, lists of strings on
one line. Standard library only.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def dump(value, indent=0):
    pad = "  " * indent
    if isinstance(value, dict):
        lines = [f'{pad}  {json.dumps(k, ensure_ascii=False)}: {dump(v, indent + 1).lstrip()}' for k, v in value.items()]
        return pad + "{\n" + ",\n".join(lines) + "\n" + pad + "}"
    if isinstance(value, list) and any(isinstance(v, (dict, list)) for v in value):
        return pad + "[\n" + ",\n".join(dump(v, indent + 1) for v in value) + "\n" + pad + "]"
    return pad + json.dumps(value, ensure_ascii=False)


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("culture", "quiz"):
        sys.exit(__doc__)
    path = ROOT / "registry" / f"{sys.argv[1]}.json"
    reg = json.loads(path.read_text(encoding="utf-8"))
    entry = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    items = [x for x in reg["items"] if x.get("date") != entry["date"]]
    items.append(entry)
    items.sort(key=lambda x: x["date"])
    reg["items"] = items
    path.write_text(dump(reg) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
