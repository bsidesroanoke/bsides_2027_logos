#!/usr/bin/env python3
"""
make_favicons.py — generate the BSides Roanoke favicon set.

A bold Mill Mountain star rendered as three concentric neon tubes
(magenta / white / cyan) on a transparent background, so the color rings
stay defined down to 16x16.

Outputs (into ../assets/):
  favicon_16.png  favicon_32.png  favicon_48.png  favicon_96.png  favicon_144.png

Also writes favicon.svg (the vector master) for reuse.

Deterministic. Run:  python3 make_favicons.py
Rasterization requires Inkscape on PATH.
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bsides_engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "assets"))

SIZES = [16, 32, 48, 96, 144]


def favicon_svg():
    W = H = 64
    # three concentric neon star tubes (magenta / white / cyan), matching the
    # billboard sign's tube ratios, so the favicon reads as defined color rings
    # rather than a single washed-out gradient.
    tubes = "".join(
        f'<path d="{E.star_path(32, 33, 28 * s)}" fill="none" stroke="{c}" '
        f'stroke-width="{w}" stroke-linejoin="round"/>'
        for s, c, w in zip(E.TUBE_SCALES,
                          (E.MAGENTA, E.WHITE, E.CYAN),
                          (7.0, 6.0, 5.0))
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" ' \
           f'width="{W}" height="{H}" role="img" aria-label="BSides Roanoke">' \
           + tubes + '</svg>\n'


def main():
    os.makedirs(ASSETS, exist_ok=True)
    svg = favicon_svg()
    master = os.path.join(ASSETS, "favicon.svg")
    with open(master, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print("wrote favicon.svg")
    for s in SIZES:
        out = os.path.join(ASSETS, f"favicon_{s}.png")
        subprocess.run(["inkscape", master, "--export-type=png",
                       f"--export-filename={out}", "-w", str(s), "-h", str(s)],
                       check=True, stdout=subprocess.DEVNULL)
        print("wrote", os.path.basename(out))


if __name__ == "__main__":
    main()
