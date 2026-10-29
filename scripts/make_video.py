#!/usr/bin/env python3
"""
make_video.py — render the BSides Roanoke looping video (1920x1080, ~60s).

A seamless loop: the perspective grid and rolling hills drift toward the
viewer at a gentle cruise, the sign floats static (no bounce), the starfield
twinkles, and exactly one shooting star crosses the sky per loop.

Loop-by-construction (see design.md D2):
    G  = 130   grid cell
    D  = 130 * 16 = 2080   loop distance (16 cells)
    f1 = 2/D, f2 = 1/D      wave completes 2 and 1 cycles per loop
    off(frame) = (frame / N) * D   (never accumulated -> no float drift)
    frame 0 == frame N  ->  seamless

Run under uv so the bundled static ffmpeg and Pillow are available:

    uv run --with pillow --with imageio-ffmpeg python3 make_video.py

Preview a single frame without encoding:

    uv run --with pillow --with imageio-ffmpeg python3 make_video.py --preview 300

Deterministic.
"""

import math
import os
import random
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bsides_engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "assets"))

W, H = 1920, 1080
HZ = 0.37 * H            # 399.6
FPS = 30
T = 60.0                 # loop duration (seconds)
N_FRAMES = int(round(FPS * T))   # 1800
D = E.LOOP_D             # 2210
F1Z, F2Z = E.F1Z, E.F2Z

# sign placement (static, centered)
SIGN_VB = (140, -80, 1120, 1040)
SIGN_EXPORT_W = 1080

# shooting star: one per loop, fully inside
SHOT_T0 = 30.0
SHOT_DUR = 1.2


def render_sign_png():
    """Bake the neon sign (with glow) into one transparent PNG via Inkscape."""
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" '
           f'viewBox="{SIGN_VB[0]} {SIGN_VB[1]} {SIGN_VB[2]} {SIGN_VB[3]}">'
           + E.defs_neon() + E.sign_color(700, 439, 409) + '</svg>')
    tmp = tempfile.NamedTemporaryFile(suffix=".svg", delete=False, mode="w")
    tmp.write(svg)
    tmp.close()
    out = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
    subprocess.run(["inkscape", tmp.name, "--export-type=png",
                   f"--export-filename={out}", "-w", str(SIGN_EXPORT_W)],
                  check=True, stdout=subprocess.DEVNULL)
    os.unlink(tmp.name)
    return out


def make_stars():
    rng = random.Random(1337)
    stars = []
    for _ in range(70):
        stars.append({
            "x": rng.uniform(0, W),
            "y": rng.uniform(0.04 * HZ, 0.96 * HZ),
            "base": rng.uniform(0.22, 0.62),
            "amp": rng.uniform(0.12, 0.30),
            "n": rng.randint(3, 12),          # loop-safe integer period divisor
            "ph": rng.uniform(0, 2 * math.pi),
            "r": rng.uniform(0.8, 2.0),
        })
    return stars


def draw_sky(img, stars, t):
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=E.VOID)
    # violet horizon haze
    for i in range(120):
        a = 0.10 * (i / 120.0)
        c = E.blend(E.VOID, E.VIOLET, a)
        y = int(HZ - 120 + i)
        d.line([(0, y), (W, y)], fill=c)
    for s in stars:
        b = s["base"] + s["amp"] * math.sin(2 * math.pi * s["n"] * t / T + s["ph"])
        a = max(0.0, min(1.0, b))
        if a < 0.03:
            continue
        col = E.blend(E.VOID, E.WHITE, a)
        r = s["r"]
        d.ellipse([s["x"] - r, s["y"] - r, s["x"] + r, s["y"] + r], fill=col)


def draw_shooting_star(img, t):
    from PIL import ImageDraw
    p = (t - SHOT_T0) / SHOT_DUR
    if p < 0 or p > 1:
        return
    d = ImageDraw.Draw(img)
    ang = 20 * math.pi / 180
    L = 0.42 * W
    hx = 0.16 * W + math.cos(ang) * L * p
    hy = 0.14 * HZ + math.sin(ang) * L * p
    tail = 0.26 * W
    tx = hx - math.cos(ang) * tail
    ty = hy - math.sin(ang) * tail
    alpha = math.sin(math.pi * p)
    steps = 48
    for i in range(steps):
        f0, f1 = i / steps, (i + 1) / steps
        x0 = tx + (hx - tx) * f0
        y0 = ty + (hy - ty) * f0
        x1 = tx + (hx - tx) * f1
        y1 = ty + (hy - ty) * f1
        a = alpha * f1
        col = E.blend(E.VOID, "#ffffff", a)
        d.line([(x0, y0), (x1, y1)], fill=col, width=2)
    d.ellipse([hx - 2.5, hy - 2.5, hx + 2.5, hy + 2.5], fill="#ffffff")


def render_frame(sign_img, stars, i):
    from PIL import Image
    off = (i / N_FRAMES) * D
    img = Image.new("RGB", (W, H))
    t = i / FPS
    draw_sky(img, stars, t)
    draw_shooting_star(img, t)
    E.terrain_pil(img, W, H, HZ, off, F1Z, F2Z)
    sw, sh = sign_img.size
    img.paste(sign_img, ((W - sw) // 2, (H - sh) // 2), sign_img)
    return img


def main():
    preview = None
    if "--preview" in sys.argv:
        preview = int(sys.argv[sys.argv.index("--preview") + 1])
    sign_path = render_sign_png()
    from PIL import Image
    sign_img = Image.open(sign_path).convert("RGBA")
    stars = make_stars()

    if preview is not None:
        img = render_frame(sign_img, stars, preview)
        out = os.path.join(ASSETS, f"video_preview_{preview}.png")
        img.save(out)
        print("wrote", out)
        os.unlink(sign_path)
        return

    import imageio_ffmpeg
    os.makedirs(ASSETS, exist_ok=True)
    out_path = os.path.join(ASSETS, "loop_1080p.mp4")
    writer = imageio_ffmpeg.write_frames(
        out_path, (W, H), fps=FPS, codec="libx264", macro_block_size=1,
        output_params=["-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium"])
    writer.send(None)
    for i in range(N_FRAMES):
        img = render_frame(sign_img, stars, i)
        writer.send(img.tobytes())
        if i % 180 == 0:
            print(f"frame {i}/{N_FRAMES}")
    writer.close()
    os.unlink(sign_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
