# BSides Roanoke — Brand Export

A regenerable package of BSides Roanoke brand media. Every asset is generated
programmatically from shared geometry — no hand-drawn files, no raster-only
dead ends. Copy this folder out as a standalone repo and regenerate everything
from source.

## The look

**Neon-noir. A midnight highway at the edge of the Blue Ridge.** A five-point
Mill Mountain star burns in hot neon above the BSides lockup, and below it a
synthwave grid races toward a vanishing point on the horizon while wireframe
hills roll in from the flanks. A flat center valley keeps the sign clear, the
way a dark stretch of road runs between the mountains. The whole thing hums
like a sign you'd pass at 2 a.m. — glowing tubes, a faint scanline shimmer,
stars twinkling overhead, the occasional shooting star.

The lockup is one object: the star, the BSides core (wordmark + infinity +
two dots), and **ROANOKE** set tight against the star's lower-right edge.

## Color palette

| Token | Hex | Role |
|---|---|---|
| Void | `#05050f` | Night sky, sign plate, deep background |
| Magenta | `#ff2d95` | Star outer tube, accent grid rays, aura core |
| Cyan | `#22e6ff` | Star inner tube, sign edge glow, bright horizon rows |
| Violet | `#7a2bff` | Aura mid-tone, horizon haze |
| Grid | `#5c17c9` | Base grid line purple |
| Hot white | `#f2f7ff` | Sign body, starfield, ROANOKE |
| Ridge near | `#0e1e46` | Foreground hill fill (deep blue) |
| Ridge far | `#4a6fc0` | Distant hill fill (pale haze) |
| Line bright | `#5cc8ff` | Every 4th grid line |
| Line dim | `#3f83e0` | Base grid line blue |

The star's neon gradient runs magenta → hot white → cyan (top-left to
bottom-right). The sign body uses a vertical sheen: white → hot white →
`#bcd4ff`.

## Assets

| File | What it is |
|---|---|
| `assets/logo_grid_color.svg` | Full lockup over grid + rolling hills, full neon, void bg |
| `assets/logo_nogrid_color.svg` | Full lockup, full neon, transparent background |
| `assets/logo_grid_mono_white.svg` | Grid + lockup, single white ink, transparent, no glow |
| `assets/logo_grid_mono_black.svg` | Grid + lockup, single black ink, transparent, no glow |
| `assets/logo_nogrid_mono_white.svg` | Lockup only, white ink, transparent |
| `assets/logo_nogrid_mono_black.svg` | Lockup only, black ink, transparent |
| `assets/favicon_{16,32,48,96,144}.png` | Gradient star, transparent bg |
| `assets/favicon.svg` | Favicon vector master |
| `assets/banner_1600x400.svg` / `.png` | 4:1 banner, lockup centered over hills |
| `assets/loop_1080p.mp4` | 1920×1080 seamless loop, ~60s, gentle roll |
| `assets/website/index.html` | Self-contained animated site |

Mono guidance: white mono for dark surfaces, black mono for light surfaces.
Mono carries no glow by design — it's a flat single-ink mark.

## Toolchain

- **Python 3** + **Pillow** (frame rasterization)
- **Inkscape 1.4+** (SVG → PNG; favicons, banner, baked sign glow)
- **uv** with `imageio-ffmpeg` (bundled static ffmpeg for the MP4)
- Hermetic fontconfig at `../fonts/fonts.conf` (vendored Montserrat)

## Regenerating

Run from `scripts/`:

```sh
python3 make_logos.py        # 6 logo SVGs
python3 make_favicons.py     # 5 favicon PNGs + favicon.svg
python3 make_banner.py       # banner SVG + PNG
python3 make_website.py      # website/index.html

# video (needs uv for the bundled ffmpeg + Pillow):
uv run --with pillow --with imageio-ffmpeg python3 make_video.py

# scrub guard (must pass before shipping):
python3 check_scrub.py
```

All generators are deterministic — no timestamps, no unseeded randomness —
so re-running reproduces byte-identical SVGs and identical video frames.

## Layout

```
export/
├── scripts/     one generator per asset type + shared bsides_engine.py
├── assets/      generated deliverables
├── library/     build inputs (core paths, star geometry, ROANOKE type, license)
└── README.md    this file
```

See `library/README.md` for the provenance of each build input.
