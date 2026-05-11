#!/usr/bin/env python3
"""Sync index.html into chispa_notebook_v2.ipynb Cell 7 (html_b64)."""
import base64
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
HTML = ROOT / "index.html"
NB = ROOT / "chispa_notebook_v2.ipynb"


def sync():
    if not HTML.exists():
        print(f"sync_notebook: {HTML} not found, skipping", file=sys.stderr)
        return
    if not NB.exists():
        print(f"sync_notebook: {NB} not found, skipping", file=sys.stderr)
        return

    b64 = base64.b64encode(HTML.read_bytes()).decode("ascii")

    nb = json.loads(NB.read_text(encoding="utf-8"))

    replaced = False
    for cell in nb["cells"]:
        src = "".join(cell["source"])
        new_src = re.sub(r'html_b64 = "[A-Za-z0-9+/=]+"', f'html_b64 = "{b64}"', src)
        if new_src != src:
            cell["source"] = [new_src]
            replaced = True
            break

    if not replaced:
        print("sync_notebook: html_b64 assignment not found in notebook", file=sys.stderr)
        sys.exit(1)

    NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"sync_notebook: updated {NB.name} ({len(b64)} b64 chars)")


if __name__ == "__main__":
    sync()
