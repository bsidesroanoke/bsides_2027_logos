#!/usr/bin/env python3
"""
make_logos.py — generate the six BSides Roanoke logo SVGs.

  grid    = billboard sign over the perspective grid + rolling hills
  nogrid  = billboard sign over the void
  color   = full neon treatment on the deep-void background
  mono    = single flat ink on transparent, no glow (white and black)

Outputs (into ../assets/):
  logo_grid_color.svg        logo_nogrid_color.svg
  logo_grid_mono_white.svg   logo_nogrid_mono_white.svg
  logo_grid_mono_black.svg   logo_nogrid_mono_black.svg

Deterministic. Run:  python3 make_logos.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bsides_engine as E

ASSETS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "assets"))

W, H = 1400, 820
HZ = 303.0
SCX, SCY, R = 700.0, 439.0, 409.0


def grid_color():
    b = [E.defs_neon(),
         f'<rect x="0" y="0" width="{W}" height="{H}" fill="{E.VOID}"/>',
         f'<rect x="0" y="{HZ - 120}" width="{W}" height="120" '
         f'fill="{E.VIOLET}" opacity="0.10"/>']
    b.append(E.terrain_svg(W, H, HZ, 0.0))
    b.append(E.sign_color(SCX, SCY, R))
    b.append(E.scanlines(W, H, 0.45))
    return E.svg_wrap(W, H, "".join(b), "BSides Roanoke — grid (color)")


def nogrid_color():
    # transparent background: the sign's aura + neon glow composite over alpha,
    # no void rect and no full-canvas scanlines (they would tint the empty space)
    b = [E.defs_neon(),
         E.sign_color(SCX, SCY, R)]
    return E.svg_wrap(W, H, "".join(b), "BSides Roanoke — nogrid (color)")


def mono(with_grid, ink):
    b = []
    if with_grid:
        b.append(E.terrain_svg(W, H, HZ, 0.0, mono=ink))
    b.append(E.sign_mono(SCX, SCY, R, ink))
    tag = "white" if ink == E.WHITE else "black"
    return E.svg_wrap(W, H, "".join(b), f"BSides Roanoke — mono {tag}")


def main():
    os.makedirs(ASSETS, exist_ok=True)
    out = {
        "logo_grid_color.svg": grid_color(),
        "logo_nogrid_color.svg": nogrid_color(),
        "logo_grid_mono_white.svg": mono(True, E.WHITE),
        "logo_grid_mono_black.svg": mono(True, "#000000"),
        "logo_nogrid_mono_white.svg": mono(False, E.WHITE),
        "logo_nogrid_mono_black.svg": mono(False, "#000000"),
    }
    for name, content in out.items():
        with open(os.path.join(ASSETS, name), "w", encoding="utf-8") as fh:
            fh.write(content)
        print("wrote", name)


if __name__ == "__main__":
    main()
