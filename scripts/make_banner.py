#!/usr/bin/env python3
"""
make_banner.py — generate the BSides Roanoke banner (4:1, 1600x400).

Full lockup (Mill Mountain star + BSides core + ROANOKE) scaled to fit,
centered over the perspective grid and rolling hills. The star is vertically
centered; the hills are observable on the flanks through the flat center
valley. No sky stars.

Outputs (into ../assets/):
  banner_1600x400.svg
  banner_1600x400.png   (requires Inkscape on PATH)

Deterministic. Run:  python3 make_banner.py
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bsides_engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "assets"))

W, H = 1600, 400
HZ = 262.0
SCX, SCY, R = 800.0, 196.0, 176.0


def banner_svg():
    b = [E.defs_neon(),
         f'<rect x="0" y="0" width="{W}" height="{H}" fill="{E.VOID}"/>',
         f'<rect x="0" y="{HZ - 110}" width="{W}" height="110" '
         f'fill="{E.VIOLET}" opacity="0.10"/>']
    b.append(E.terrain_svg(W, H, HZ, 0.0))
    b.append(E.sign_color(SCX, SCY, R))
    b.append(E.scanlines(W, H, 0.35))
    return E.svg_wrap(W, H, "".join(b), "BSides Roanoke — banner")


def main():
    os.makedirs(ASSETS, exist_ok=True)
    svg_path = os.path.join(ASSETS, "banner_1600x400.svg")
    with open(svg_path, "w", encoding="utf-8") as fh:
        fh.write(banner_svg())
    print("wrote banner_1600x400.svg")
    subprocess.run(["inkscape", svg_path, "--export-type=png",
                   "--export-filename=" + os.path.join(ASSETS, "banner_1600x400.png")],
                  check=True, stdout=subprocess.DEVNULL)
    print("wrote banner_1600x400.png")


if __name__ == "__main__":
    main()
