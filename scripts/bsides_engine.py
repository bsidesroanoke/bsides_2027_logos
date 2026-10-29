#!/usr/bin/env python3
"""
bsides_engine.py — shared geometry, palette, and renderers for the BSides
Roanoke export package.

Everything the generators need lives here so the look is identical across the
static SVG logos, the banner, the looping video, and the website:

  * palette constants
  * the canonical BSides core silhouette (verbatim path data)
  * the Mill Mountain star ({5/2} pentagram, golden tube ratios)
  * the pre-outlined ROANOKE wordmark (from ../library/type_data.json)
  * the billboard sign builder (color + mono)
  * a perspective heightfield terrain engine (scrolling neon grid over
    rolling hills with a flat center valley), emitted as SVG or PIL raster

Deterministic: no timestamps, no unseeded randomness.
"""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.normpath(os.path.join(HERE, "..", "library"))

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
VOID = "#05050f"          # deep night sky / sign plate black
MAGENTA = "#ff2d95"       # hot neon pink (star outer tube, grid accent rays)
CYAN = "#22e6ff"          # electric blue (star inner tube, sign edge, horizon)
VIOLET = "#7a2bff"        # aura mid-tone / horizon haze
GRID = "#5c17c9"          # base grid line purple
WHITE = "#f2f7ff"         # hot white (sign body, stars)
# Terrain depth shading: near hills deep blue, far hills pale haze
RIDGE_FILL_NEAR = "#0e1e46"
RIDGE_FILL_FAR = "#4a6fc0"
LINE_BRIGHT = "#5cc8ff"   # every 4th grid line, bright
LINE_DIM = "#3f83e0"      # base grid line blue

# ---------------------------------------------------------------------------
# Canonical BSides core (Prishtina) — verbatim. viewBox 0 0 409.5 144.3
# ---------------------------------------------------------------------------
CORE_W = 409.5
CORE_H = 144.3

CORE_WORDMARK = ('M180.18,70.09H199.9l-11.77,70.8H168.41Zm32,0h27.31c25.29,0,37.53,14.56,34.14,35l0,.21c-3.4,20.43-20.79,35.6-46.27,35.6H200.4Zm18.74,53.4c11.73,0,20.59-6.47,22.49-17.9l0-.2c1.88-11.33-4.81-17.9-16.55-17.9h-8l-6,36Zm56-53.4h56.94l-2.77,16.69H303.6L301.81,97.5h34L333.22,113h-34l-1.87,11.23h38l-2.77,16.69H275.18Zm52.38,60.28,13.09-13.05a31.16,31.16,0,0,0,21.55,8.5c5.26,0,8.39-1.82,8.9-4.86l0-.2c.49-2.93-1.57-4.55-10.81-6.78-14.5-3.44-25.42-7.68-23-22.25l0-.2c2.19-13.15,14.19-22.65,31.18-22.65,12,0,20.91,3.23,27.57,9.4L395.75,92.14a30.47,30.47,0,0,0-18.66-7c-4.76,0-7.42,2-7.84,4.55l0,.2c-.54,3.24,1.65,4.65,11.09,6.88,15.7,3.54,24.94,8.8,22.74,22l0,.2c-2.4,14.46-15.26,23.06-32.46,23.06C358,142.1,346.73,138.16,339.33,130.37ZM35.83,76.08a27.47,27.47,0,0,1,19.69-8.76h1c.86,0,1.72.09,2.57.18A19.64,19.64,0,0,0,64,57.34l0-.19c1.54-9.24-2.94-13.91-10.74-16.63,6.46-2.62,11.71-7.29,13-15.16l0-.2c.77-4.66-.28-8.26-2.55-11-3.32-4-9-6.13-17.55-6.13H11.31L0,76.1H35.09ZM27.17,23.22H39.41c5.64,0,8.2,2.14,7.59,5.83l0,.2c-.67,4-4.2,5.93-9.93,5.93H25.18ZM23,48.4H37.36c6.32,0,8.84,2.43,8.22,6.12l0,.2c-.66,4-4.34,6.22-10.07,6.22H20.89ZM142.46,96.79c-9.44-2.23-11.63-3.64-11.09-6.88l0-.2c.42-2.53,3.09-4.55,7.84-4.55a28.85,28.85,0,0,1,13.46,3.57,49,49,0,0,0,11.36-14.82c-5.77-3.31-12.85-5-21.61-5l-.72,0A27.62,27.62,0,0,1,117,79.38a24.88,24.88,0,0,0-5.67,12.15l0,.2c-2.42,14.57,8.51,18.81,23,22.25,9.23,2.23,11.29,3.85,10.8,6.78l0,.2c-.5,3-3.64,4.86-8.9,4.86-10.24,0-19.36-4.8-25.43-10.06A58.37,58.37,0,0,1,102.13,131c7.4,7.36,18.39,11.1,30.58,11.1,17.19,0,30-8.6,32.45-23.06l0-.2C167.4,105.59,158.16,100.33,142.46,96.79Z')
CORE_INFINITY = ('M160.83,24.31A49.34,49.34,0,0,0,79,79.48,27.72,27.72,0,1,1,30,85.68H7.6A49.33,49.33,0,1,0,96.94,67.39a27.72,27.72,0,1,1,49.5-7.47,49.64,49.64,0,0,1,20.92,5.42A49.2,49.2,0,0,0,160.83,24.31Z')
DOT_TOP = 'M114.72,44.18a9.3,9.3,0,1,0,12.92,2.51A9.31,9.31,0,0,0,114.72,44.18Z'
DOT_BOTTOM = 'M61.23,102.69a9.3,9.3,0,0,0-5-17h-.33a9.3,9.3,0,1,0,5.37,17Z'

# Letter-band geometry (core units). ROANOKE fills the band above the SIDES
# row / right of the B. Tuned so the wordmark sits tight against the star's
# lower-right tube (see make_logos review).
ROANOKE_X0 = 176.0
ROANOKE_X1 = 407.7
ROANOKE_MID = 36.0

# Lockup: shrink ROANOKE a touch (keeping its center) so it pulls away from
# the infinity symbol, and clear a rounded radius around the wordmark so no
# star tube passes behind the letters. Applied to every sign variant (mono,
# color, banner, website, video) for a consistent lockup.
ROANOKE_SCALE = 0.86
ROANOKE_CLEAR_RADIUS = 20.0

# ---------------------------------------------------------------------------
# Mill Mountain Star — regular {5/2} pentagram, point-up.
# Golden tube ratios 1 : 0.7794 : 0.5627 (library/golden_geometry.json)
# ---------------------------------------------------------------------------
TUBE_SCALES = (1.0, 0.7794, 0.5627)
INNER_RATIO = math.cos(math.radians(72)) / math.cos(math.radians(36))


def star_path(cx, cy, R):
    pts = []
    for k in range(5):
        ta = math.radians(90.0 - 72.0 * k)
        ia = math.radians(54.0 - 72.0 * k)
        pts.append((cx + R * math.cos(ta), cy - R * math.sin(ta)))
        pts.append((cx + R * INNER_RATIO * math.cos(ia),
                   cy - R * INNER_RATIO * math.sin(ia)))
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"


def star_neon(cx, cy, R, colors, widths, glow):
    out = [f'<g filter="{glow}">']
    for s, c, w in zip(TUBE_SCALES, colors, widths):
        out.append(
            f'<path d="{star_path(cx, cy, R * s)}" fill="none" stroke="{c}" '
            f'stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>'
        )
    out.append('</g>')
    return "".join(out)


# ---------------------------------------------------------------------------
# Outlined type (Montserrat Bold, pre-outlined with Inkscape)
# ---------------------------------------------------------------------------
with open(os.path.join(LIB, "type_data.json"), "r", encoding="utf-8") as fh:
    TYPE = json.load(fh)


def text_group(label, cx, cy, target_w, fill, glow=None, stretch_y=1.0,
              stroke=None, stroke_w=0.0):
    t = TYPE[label]
    s = target_w / t["w"]
    h = t["h"] * s * stretch_y
    x0 = cx - target_w / 2.0
    y0 = cy - h / 2.0
    fglow = f' filter="{glow}"' if glow else ''
    stk = f' stroke="{stroke}" stroke-width="{stroke_w}"' if stroke else ''
    return (f'<g transform="translate({x0:.2f},{y0:.2f}) scale({s:.5f},{s * stretch_y:.5f})"{fglow}>'
            f'<path d="{t["d"]}" transform="translate({t["dx"]},{t["dy"]})" '
            f'fill="{fill}"{stk}/></g>')


def roanoke_xform(tx, ty, scale, width_scale=1.0):
    """Transform string + path d placing ROANOKE for the sign at (tx, ty, scale).

    width_scale shrinks the wordmark about its center (used by the mono lockup
    to pull ROANOKE away from the infinity symbol)."""
    w_core = (ROANOKE_X1 - ROANOKE_X0) * width_scale
    t = TYPE["ROANOKE"]
    target_w = w_core * scale
    s = target_w / t["w"]
    h = t["h"] * s
    cx = tx + ((ROANOKE_X0 + ROANOKE_X1) / 2.0) * scale
    cy = ty + ROANOKE_MID * scale
    x0 = cx - target_w / 2.0
    y0 = cy - h / 2.0
    xf = (f'translate({x0:.2f},{y0:.2f}) scale({s:.5f},{s:.5f}) '
          f'translate({t["dx"]},{t["dy"]})')
    return xf, t["d"]


def roanoke_clear_rect(fill, pad=None):
    """Rounded-rect path string (core coords) clearing the star around ROANOKE.

    Caller supplies the core transform. `fill` is the mask ink (black for the
    mono mask) or VOID for the color sign plate."""
    pad = ROANOKE_CLEAR_RADIUS if pad is None else pad
    rt = TYPE["ROANOKE"]
    w_core = (ROANOKE_X1 - ROANOKE_X0) * ROANOKE_SCALE
    h_core = rt["h"] * (w_core / rt["w"])
    cx = (ROANOKE_X0 + ROANOKE_X1) / 2.0
    cy = ROANOKE_MID
    return (f'<rect x="{cx - w_core / 2.0 - pad:.2f}" '
            f'y="{cy - h_core / 2.0 - pad:.2f}" '
            f'width="{w_core + 2.0 * pad:.2f}" height="{h_core + 2.0 * pad:.2f}" '
            f'rx="{pad:.2f}" fill="{fill}"/>')


# ---------------------------------------------------------------------------
# Shared SVG defs (glow filters, gradients, scanline pattern)
# ---------------------------------------------------------------------------
def defs_neon():
    return f'''<defs>
<filter id="glowSoft" x="-60%" y="-60%" width="220%" height="220%">
<feGaussianBlur stdDeviation="4" result="b1"/>
<feMerge><feMergeNode in="b1"/><feMergeNode in="b1"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="glowMed" x="-60%" y="-60%" width="220%" height="220%">
<feGaussianBlur stdDeviation="7" result="b1"/>
<feGaussianBlur in="SourceGraphic" stdDeviation="16" result="b2"/>
<feMerge><feMergeNode in="b2"/><feMergeNode in="b1"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="glowBig" x="-80%" y="-80%" width="260%" height="260%">
<feGaussianBlur stdDeviation="10" result="b1"/>
<feGaussianBlur in="SourceGraphic" stdDeviation="26" result="b2"/>
<feMerge><feMergeNode in="b2"/><feMergeNode in="b1"/><feMergeNode in="b1"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<radialGradient id="starAura" cx="50%" cy="50%" r="50%">
<stop offset="0%" stop-color="{MAGENTA}" stop-opacity="0.30"/>
<stop offset="45%" stop-color="{VIOLET}" stop-opacity="0.14"/>
<stop offset="100%" stop-color="{VOID}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="coreSheen" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#ffffff"/>
<stop offset="55%" stop-color="{WHITE}"/>
<stop offset="100%" stop-color="#bcd4ff"/>
</linearGradient>
<pattern id="scan" width="6" height="6" patternUnits="userSpaceOnUse">
<rect x="0" y="0" width="6" height="1.6" fill="#000000" opacity="0.30"/>
</pattern>
</defs>'''


def scanlines(w, h, opacity=1.0):
    return f'<rect x="0" y="0" width="{w}" height="{h}" fill="url(#scan)" opacity="{opacity}"/>'


# ---------------------------------------------------------------------------
# Billboard sign.
#
# The sign is placed by its star: center (scx, scy), outer radius R.
# The BSides core occupies the star's lower third; ROANOKE fills the band
# above the SIDES row.
# ---------------------------------------------------------------------------
CORE_BOTTOM_OFF = 0.6626   # core bottom sits this * R below the star center
CORE_H_FRAC = 0.603        # core height as a fraction of R


def sign_placement(scx, scy, R):
    scale = CORE_H_FRAC * R / CORE_H
    core_bottom = scy + CORE_BOTTOM_OFF * R
    tx = scx - (CORE_W * scale) / 2.0
    ty = core_bottom - CORE_H * scale
    return scale, tx, ty


def sign_color(scx, scy, R):
    """Full neon sign: aura, star tubes, opaque plate, bright core, ROANOKE."""
    scale, tx, ty = sign_placement(scx, scy, R)
    t = f'translate({tx:.2f},{ty:.2f}) scale({scale:.5f})'
    parts = [f'<circle cx="{scx:.1f}" cy="{scy:.1f}" r="{R * 1.15:.1f}" fill="url(#starAura)"/>']
    parts.append(star_neon(scx, scy, R, [MAGENTA, WHITE, CYAN], [11, 8.5, 7],
                          "url(#glowBig)"))
    # opaque sign plate punches the star out behind the letters
    parts.append(f'<g transform="{t}">'
                 f'<path d="{CORE_WORDMARK} {CORE_INFINITY} {DOT_TOP} {DOT_BOTTOM}" '
                 f'fill="{VOID}" stroke="{VOID}" stroke-width="20" stroke-linejoin="round"/>'
                 f'<g filter="url(#glowMed)">'
                 f'<path d="{CORE_WORDMARK} {CORE_INFINITY} {DOT_TOP} {DOT_BOTTOM}" '
                 f'fill="none" stroke="{CYAN}" stroke-width="1.6"/></g></g>')
    ro_xf, ro_d = roanoke_xform(tx, ty, scale, ROANOKE_SCALE)
    # rounded plate clears the star behind/around ROANOKE (matches the mono mask)
    parts.append(f'<g transform="{t}">{roanoke_clear_rect(VOID)}</g>')
    parts.append(f'<g transform="{ro_xf}" filter="url(#glowMed)">'
                 f'<path d="{ro_d}" fill="{VOID}" stroke="{VOID}" '
                 f'stroke-width="{26.0 / scale:.2f}" stroke-linejoin="round"/></g>')
    # bright body on top
    parts.append(f'<g transform="{t}">'
                 f'<path d="{CORE_WORDMARK} {CORE_INFINITY}" fill="url(#coreSheen)"/>'
                 f'<path d="{DOT_TOP} {DOT_BOTTOM}" fill="{WHITE}"/></g>')
    parts.append(f'<g transform="{ro_xf}" filter="url(#glowSoft)">'
                 f'<path d="{ro_d}" fill="{WHITE}"/></g>')
    return "".join(parts)


def sign_mono(scx, scy, R, ink):
    """Flat single-ink sign: star outline + solid core + solid ROANOKE, no glow.

    The star is masked out around the wordmark: a rounded radius clears the
    whole ROANOKE band, and the core + ROANOKE letter shapes (generously
    stroked to cover counters and inter-letter gaps) clear the rest. No star
    tube passes behind the letters."""
    scale, tx, ty = sign_placement(scx, scy, R)
    t = f'translate({tx:.2f},{ty:.2f}) scale({scale:.5f})'
    ro_xf, ro_d = roanoke_xform(tx, ty, scale, ROANOKE_SCALE)
    clear = f'<g transform="{t}">{roanoke_clear_rect("#000000")}</g>'
    mask_id = f"signmask_{ink[1:]}"
    parts = [f'<mask id="{mask_id}" x="-2000" y="-2000" width="10000" height="10000">'
             f'<rect x="-2000" y="-2000" width="10000" height="10000" fill="#ffffff"/>'
             f'{clear}'
             f'<path d="{CORE_WORDMARK} {CORE_INFINITY} {DOT_TOP} {DOT_BOTTOM}" '
             f'transform="{t}" fill="#000000" stroke="#000000" '
             f'stroke-width="30" stroke-linejoin="round"/>'
             f'<path d="{ro_d}" transform="{ro_xf}" fill="#000000" '
             f'stroke="#000000" stroke-width="{36.0 / scale:.2f}" '
             f'stroke-linejoin="round"/></mask>']
    parts.append(f'<g mask="url(#{mask_id})">')
    for s in TUBE_SCALES:
        parts.append(f'<path d="{star_path(scx, scy, R * s)}" fill="none" '
                     f'stroke="{ink}" stroke-width="9" stroke-linejoin="round"/>')
    parts.append('</g>')
    parts.append(f'<g transform="{t}">'
                 f'<path d="{CORE_WORDMARK} {CORE_INFINITY} {DOT_TOP} {DOT_BOTTOM}" '
                 f'fill="{ink}"/></g>')
    parts.append(f'<g transform="{ro_xf}"><path d="{ro_d}" fill="{ink}"/></g>')
    return "".join(parts)


# ---------------------------------------------------------------------------
# Perspective heightfield terrain.
#
# Camera at height CAM_H looking down +z; horizon / vanishing point at
# (W/2, HZ). A heightfield (flat center valley, rolling hills on the flanks)
# is draped in a grid: constant-z lines (horizontal, compressed toward the
# horizon) and constant-x lines (rays converging to the vanishing point).
#
# The wave is fixed in the world; the camera travels by `off`. For a seamless
# loop, choose the loop distance D as an integer multiple of the grid cell G
# and snap the wave's z-frequencies to integer multiples of 1/D.
# ---------------------------------------------------------------------------
F = 900.0
CAM_H = 90.0
Z_NEAR = 156.0
Z_FAR = 2600.0
H0 = 620.0
U_FLAT = 0.045
U_MAX = 0.55
G = 130.0
RISE_SPAN = 0.45 * (Z_FAR - 1.9 * Z_NEAR)
FADE_SPAN = 0.25 * (Z_FAR - 1.9 * Z_NEAR)
X_STEP = 44.0

# loop-by-construction constants (see design.md D2).
# LOOP_K must be a multiple of 4 so the every-4th bright row pattern also
# wraps at the loop distance (17 would shift the striping by one -> seam).
LOOP_K = 16
LOOP_D = G * LOOP_K            # 2080 world units per loop
F1Z = 2.0 / LOOP_D            # ~9.62e-4  (2 wave cycles per loop)
F2Z = 1.0 / LOOP_D            # ~4.81e-4  (1 wave cycle per loop)


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _tri(t):
    return 2.0 * abs(t - math.floor(t + 0.5)) - 1.0


def elev(x, zv, off, f1z=F1Z, f2z=F2Z):
    """World elevation at lateral x, view depth zv, camera travel off."""
    u = x / zv
    au = abs(u)
    thr = U_FLAT + 0.02 * (zv / Z_FAR)
    env = _clamp((au - thr) / (U_MAX - thr), 0.0, 1.0) ** 1.25
    rise = _clamp((zv - 1.9 * Z_NEAR) / RISE_SPAN, 0.0, 1.0) ** 1.2
    fade = _clamp((Z_FAR - zv) / FADE_SPAN, 0.0, 1.0)
    zw = zv + off
    roll = (0.80 * _tri(0.00110 * x + f1z * zw)
            + 0.30 * _tri(0.00240 * x - f2z * zw + 0.31))
    p = 0.80 + 0.45 * roll
    p = 0.25 + 0.75 * max(0.0, p) ** 1.4
    bf = _clamp((zv - 900.0) / 700.0, 0.0, 1.0)
    bf = bf * bf * (3.0 - 2.0 * bf)
    return max(0.0, H0 * fade * env * p * rise + CAM_H * bf)


def proj_x(x, z, W):
    return W / 2.0 + F * x / z


def proj_y(y, z, hz):
    return hz - F * (y - CAM_H) / z


def terrain_points(W, hz, off, f1z=F1Z, f2z=F2Z):
    """Projected grid: rows (view depths), xs (lateral), P[ri][ci] = (sx, sy)."""
    n_min = math.ceil((Z_NEAR + off) / G)
    rows, ns = [], []
    n = n_min
    while n * G - off <= Z_FAR:
        rows.append(n * G - off)
        ns.append(n)
        n += 1
    x_max = (W * 0.62) * Z_FAR / F
    xs = []
    x = -x_max
    while x <= x_max + 1e-6:
        xs.append(x)
        x += X_STEP
    P = []
    for zv in rows:
        P.append([(proj_x(x, zv, W), proj_y(elev(x, zv, off, f1z, f2z), zv, hz))
                 for x in xs])
    return rows, ns, xs, P


def _hexrgb(h):
    if isinstance(h, tuple):
        return h
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


def blend(c1, c2, t):
    a, b = _hexrgb(c1), _hexrgb(c2)
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def _rgb(c):
    return f"rgb({c[0]},{c[1]},{c[2]})"


def _fill_polyd(far, H):
    pts = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in far)
    return f"M{pts} L{far[-1][0]:.1f},{H} L{far[0][0]:.1f},{H} Z"


def terrain_svg(W, H, hz, off, f1z=F1Z, f2z=F2Z, mono=None):
    """Painter's-algorithm terrain as SVG, mirroring the website's renderer.

    Each strip lays an opaque fill, then its wireframe is drawn CLIPPED to the
    union of that strip's fill and all farther fills (the SVG equivalent of the
    canvas `source-atop` the site uses). This keeps wireframe from floating over
    the sky above the silhouette, while nearer fills (drawn later) still cover
    farther strokes that fall behind them.

    color: depth-shaded opaque fills + bright/dim wireframe.
    mono (ink): wireframe only in one ink, depth via opacity (fills still used
    as the clip region so lines stay on the ground).
    """
    rows, ns, xs, P = terrain_points(W, hz, off, f1z, f2z)
    nr = len(rows)
    nc = len(xs)
    filld = [_fill_polyd(P[s + 1], H) for s in range(nr - 1)]

    defs = ['<defs>']
    for s in range(nr - 1):
        defs.append(f'<path id="tf{s}" d="{filld[s]}"/>')
    for s in range(nr - 1):
        uses = "".join(f'<use href="#tf{k}"/>' for k in range(s, nr - 1))
        defs.append(f'<clipPath id="tc{s}" clipPathUnits="userSpaceOnUse">{uses}</clipPath>')
    defs.append('</defs>')

    out = []
    for s in range(nr - 2, -1, -1):
        d = rows[s] / Z_FAR
        far = P[s + 1]
        near = P[s]
        if mono is None:
            fill = _rgb(blend(RIDGE_FILL_NEAR, RIDGE_FILL_FAR, d))
            out.append(f'<use href="#tf{s}" fill="{fill}"/>')
        op = 0.30 + 0.45 * d
        row_col = mono if mono else (LINE_BRIGHT if ns[s + 1] % 4 == 0 else LINE_DIM)
        strokes = [f'<g clip-path="url(#tc{s})">']
        pts = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in far)
        strokes.append(f'<polyline points="{pts}" fill="none" stroke="{row_col}" '
                      f'stroke-width="1.2" opacity="{op:.2f}"/>')
        for ci in range(nc):
            col = mono if mono else (LINE_BRIGHT if ci % 4 == 0 else LINE_DIM)
            x1, y1 = far[ci]
            x2, y2 = near[ci]
            if s == 0:
                dy = y2 - hz
                if dy > 1:
                    x2 = W / 2.0 + (x2 - W / 2.0) * (H - hz) / dy
                    y2 = H
            strokes.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                          f'stroke="{col}" stroke-width="1.2" opacity="{op:.2f}"/>')
        strokes.append('</g>')
        out.append("".join(strokes))
    if nr >= 1:
        d0 = rows[0] / Z_FAR
        pts = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in P[0])
        out.append(f'<g clip-path="url(#tc0)"><polyline points="{pts}" fill="none" '
                  f'stroke="{mono if mono else (LINE_BRIGHT if ns[0] % 4 == 0 else LINE_DIM)}" '
                  f'stroke-width="1.2" opacity="{0.30 + 0.45 * d0:.2f}"/></g>')
    return "".join(defs) + "".join(out)


def terrain_pil(img, W, H, hz, off, f1z=F1Z, f2z=F2Z):
    """Painter's-algorithm terrain drawn onto a PIL RGB image, mirroring the
    website: per strip, opaque fill then wireframe composited with source-atop
    against the accumulated ground mask (so no line floats over the sky)."""
    from PIL import Image, ImageDraw, ImageChops
    d = ImageDraw.Draw(img)
    rows, ns, xs, P = terrain_points(W, hz, off, f1z, f2z)
    nr = len(rows)
    nc = len(xs)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    for s in range(nr - 2, -1, -1):
        dep = rows[s] / Z_FAR
        far = P[s + 1]
        near = P[s]
        fill = blend(RIDGE_FILL_NEAR, RIDGE_FILL_FAR, dep)
        poly = [(p[0], p[1]) for p in far]
        poly.append((far[-1][0], H))
        poly.append((far[0][0], H))
        d.polygon(poly, fill=fill)
        md.polygon(poly, fill=255)
        alpha = int(255 * (0.30 + 0.45 * dep))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        rb = _hexrgb(LINE_BRIGHT)
        rd = _hexrgb(LINE_DIM)
        rc = rb if ns[s + 1] % 4 == 0 else rd
        ld.line([(p[0], p[1]) for p in far], fill=rc + (alpha,), width=1)
        for ci in range(nc):
            x1, y1 = far[ci]
            x2, y2 = near[ci]
            if s == 0:
                dy = y2 - hz
                if dy > 1:
                    x2 = W / 2.0 + (x2 - W / 2.0) * (H - hz) / dy
                    y2 = H
            c = rb if ci % 4 == 0 else rd
            ld.line([(x1, y1), (x2, y2)], fill=c + (alpha,), width=1)
        sa = ImageChops.multiply(layer.split()[3], mask)
        img.paste(layer, (0, 0), sa)
    if nr >= 1:
        d0 = rows[0] / Z_FAR
        alpha = int(255 * (0.30 + 0.45 * d0))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        c = _hexrgb(LINE_BRIGHT) if ns[0] % 4 == 0 else _hexrgb(LINE_DIM)
        ld.line([(p[0], p[1]) for p in P[0]], fill=c + (alpha,), width=1)
        sa = ImageChops.multiply(layer.split()[3], mask)
        img.paste(layer, (0, 0), sa)


def svg_wrap(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img" aria-label="{label}">'
            + body + '</svg>\n')
