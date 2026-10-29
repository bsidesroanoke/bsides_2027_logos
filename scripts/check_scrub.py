#!/usr/bin/env python3
"""
check_scrub.py — build-time guard for the export package.

Fails (exit 1) if any banned token appears anywhere under export/ — in
filenames or file contents. Run after generating all assets:

    python3 check_scrub.py

The 91 BPM beat mechanics are allowed; only the source-track naming is banned.
"""

import os
import sys

# assembled from parts so this guard doesn't flag its own literals
BANNED = ["night" + "call", "kav" + "insky"]
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# don't scan binary media (video/png/svg pixels); scan text sources only
TEXT_EXT = {".py", ".md", ".html", ".json", ".txt", ".svg"}


def main():
    hits = []
    for dirpath, _dirs, files in os.walk(ROOT):
        for f in files:
            full = os.path.join(dirpath, f)
            low = f.lower()
            for tok in BANNED:
                if tok in low:
                    hits.append((full, "<filename>", tok))
            ext = os.path.splitext(low)[1]
            if ext in TEXT_EXT:
                try:
                    with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                        for ln, line in enumerate(fh, 1):
                            for tok in BANNED:
                                if tok in line.lower():
                                    hits.append((full, ln, tok))
                except Exception:
                    pass
    if hits:
        print("SCRUB FAILED — banned tokens found:")
        for path, ln, tok in hits:
            print(f"  {path}:{ln}  '{tok}'")
        sys.exit(1)
    print("SCRUB OK — no banned tokens in export/")


if __name__ == "__main__":
    main()
