#!/usr/bin/env python3
"""
make_website.py — generate the BSides Roanoke website (single self-contained file).

A neon-noir night scene: a perspective grid over rolling hills scrolls toward
the viewer, a twinkling starfield fills the sky with an occasional shooting
star, and the BSides Roanoke sign floats in front, giving a gentle pothole
bounce every four beats.

The terrain geometry, palette, and sign are mirrored from bsides_engine.py so
the live scene matches the static logos and the looping video exactly.

Output (into ../assets/website/):
  index.html   (inline CSS + JS + SVG, no external dependencies)

Deterministic. Run:  python3 make_website.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bsides_engine as E

ASSETS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "assets"))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BSides Roanoke</title>
<style>
  html, body { margin: 0; height: 100%; background: @@VOID@@; overflow: hidden; }
  #scene { position: fixed; inset: 0; z-index: 1; display: block; }
  #signwrap { position: fixed; inset: 0; z-index: 2; display: flex;
              align-items: center; justify-content: center; pointer-events: none; }
  #bounce { will-change: transform; }
  #sign { width: min(92vw, 1150px); height: auto; display: block; }
  #scan { position: fixed; inset: 0; z-index: 3; pointer-events: none;
          background: repeating-linear-gradient(to bottom,
              rgba(0,0,0,0.30) 0px, rgba(0,0,0,0.30) 1.6px,
              transparent 1.6px, transparent 6px); }
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div id="signwrap"><div id="bounce">@@SIGN@@</div></div>
<div id="scan"></div>
<script>
(function () {
  "use strict";
  var VOID = "@@VOID@@";
  var FILL_N = "@@RIDGE_FILL_NEAR@@";
  var FILL_F = "@@RIDGE_FILL_FAR@@";
  var LINE_BRIGHT = "@@LINE_BRIGHT@@";
  var LINE_DIM = "@@LINE_DIM@@";

  var BEAT = 60 / 91;            /* 0.6593 s */
  var BAR = 4 * BEAT;            /* 2.6374 s */
  var SHOOT_AT = 64 * BEAT;     /* 42.20 s  */
  var BASE_SPEED = 140;          /* world units / s at 1x */
  var SPEED_MULT = 0.70;         /* fixed cruise speed */
  var TAU = Math.PI * 2;

  var canvas = document.getElementById("scene");
  var ctx = canvas.getContext("2d");
  var bounceEl = document.getElementById("bounce");

  var W = 0, H = 0, HZ = 0;
  var offCanvas = document.createElement("canvas");
  var offCtx = offCanvas.getContext("2d");
  function resize() {
    var dpr = Math.min(2, window.devicePixelRatio || 1);
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    canvas.style.width = W + "px";
    canvas.style.height = H + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    offCanvas.width = Math.round(W * dpr);
    offCanvas.height = Math.round(H * dpr);
    offCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
    HZ = 0.37 * H;
  }
  window.addEventListener("resize", resize);
  resize();

  /* deterministic PRNG (mulberry32) */
  function mulberry32(seed) {
    var a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function hexRGB(h) {
    return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16),
            parseInt(h.slice(5, 7), 16)];
  }
  var FILL_NRGB = hexRGB(FILL_N), FILL_FRGB = hexRGB(FILL_F);
  function lerpColor(a, b, t) {
    return "rgb(" + Math.round(a[0] + (b[0] - a[0]) * t) + "," +
      Math.round(a[1] + (b[1] - a[1]) * t) + "," +
      Math.round(a[2] + (b[2] - a[2]) * t) + ")";
  }

  /* ---- terrain: camera drives forward through a fixed world ---- */
  var F = 900, CAM_H = 90, Z_NEAR = 156, Z_FAR = 2600, H0 = 620;
  var U_FLAT = 0.045, U_MAX = 0.55;
  var RISE_SPAN = 0.45 * (Z_FAR - 1.9 * Z_NEAR);
  var FADE_SPAN = 0.25 * (Z_FAR - 1.9 * Z_NEAR);
  var F1Z = @@F1Z@@, F2Z = @@F2Z@@;   /* mirrored from the shared engine */
  function tri(t) { return 2 * Math.abs(t - Math.floor(t + 0.5)) - 1; }
  function elev(x, zv, off) {
    var u = x / zv, au = Math.abs(u);
    /* V-envelope: flat center valley (the road), ridges swell to the edges */
    var thr = U_FLAT + 0.02 * (zv / Z_FAR);
    var env = (au - thr) / (U_MAX - thr);
    env = Math.min(1, Math.max(0, env));
    env = Math.pow(env, 1.25);
    /* flat valley near the camera */
    var rise = (zv - 1.9 * Z_NEAR) / RISE_SPAN;
    rise = Math.pow(Math.min(1, Math.max(0, rise)), 1.2);
    /* fade to zero at the far clip: mountains EMERGE from the horizon */
    var fade = (Z_FAR - zv) / FADE_SPAN;
    fade = Math.min(1, Math.max(0, fade));
    /* the wave is fixed in the world: zw = view depth + camera travel */
    var zw = zv + off;
    var roll = 0.80 * tri(0.00110 * x + F1Z * zw) +
               0.30 * tri(0.00240 * x - F2Z * zw + 0.31);
    /* sharpen crests: power curve emphasizes peaks, flattens valleys */
    var p = 0.80 + 0.45 * roll;
    p = 0.25 + 0.75 * Math.pow(Math.max(0, p), 1.4);
    /* continuous far baseline: lifts distant terrain so the ridgeline meets
       the horizon with no notch behind the star */
    var bf = (zv - 900) / 700;
    bf = Math.min(1, Math.max(0, bf));
    bf = bf * bf * (3 - 2 * bf);
    var e = H0 * fade * env * p * rise + CAM_H * bf;
    return Math.max(0, e);
  }
  function projX(x, z) { return W / 2 + F * x / z; }
  function projY(y, z) { return HZ - F * (y - CAM_H) / z; }

  function drawTerrain(off) {
    var G = 130;
    var nMin = Math.ceil((Z_NEAR + off) / G);
    var rows = [], ns = [];
    for (var n = nMin; n * G - off <= Z_FAR; n++) { rows.push(n * G - off); ns.push(n); }
    var nr = rows.length;
    var xMax = (W * 0.62) * Z_FAR / F;
    var xs = [];
    for (var x = -xMax; x <= xMax + 1e-6; x += 44) xs.push(x);
    var nc = xs.length, ci;
    var P = new Array(nr);
    for (var ri = 0; ri < nr; ri++) {
      var zv = rows[ri];
      var row = new Array(nc);
      for (ci = 0; ci < nc; ci++) {
        row[ci] = [projX(xs[ci], zv), projY(elev(xs[ci], zv, off), zv)];
      }
      P[ri] = row;
    }
    offCtx.clearRect(0, 0, W, H);
    for (var s = nr - 2; s >= 0; s--) {
      var d = rows[s] / Z_FAR;          /* 0 near .. 1 far */
      var far = P[s + 1], near = P[s];
      offCtx.globalCompositeOperation = "source-over";
      offCtx.globalAlpha = 1;
      offCtx.beginPath();
      offCtx.moveTo(far[0][0], far[0][1]);
      for (ci = 1; ci < nc; ci++) offCtx.lineTo(far[ci][0], far[ci][1]);
      offCtx.lineTo(far[nc - 1][0], H);
      offCtx.lineTo(far[0][0], H);
      offCtx.closePath();
      offCtx.fillStyle = lerpColor(FILL_NRGB, FILL_FRGB, d);
      offCtx.fill();
      offCtx.globalCompositeOperation = "source-atop";
      offCtx.globalAlpha = 0.30 + 0.45 * d;
      offCtx.lineWidth = 1.2;
      offCtx.beginPath();
      offCtx.moveTo(far[0][0], far[0][1]);
      for (ci = 1; ci < nc; ci++) offCtx.lineTo(far[ci][0], far[ci][1]);
      offCtx.strokeStyle = (ns[s + 1] % 4 === 0) ? LINE_BRIGHT : LINE_DIM;
      offCtx.stroke();
      for (var pass = 0; pass < 2; pass++) {
        offCtx.beginPath();
        for (ci = 0; ci < nc; ci++) {
          if ((ci % 4 === 0) !== (pass === 0)) continue;
          offCtx.moveTo(far[ci][0], far[ci][1]);
          offCtx.lineTo(near[ci][0], near[ci][1]);
          if (s === 0) {
            var dy = near[ci][1] - HZ;
            if (dy > 1) {
              var ex = W / 2 + (near[ci][0] - W / 2) * (H - HZ) / dy;
              offCtx.lineTo(ex, H);
            }
          }
        }
        offCtx.strokeStyle = (pass === 0) ? LINE_BRIGHT : LINE_DIM;
        offCtx.stroke();
      }
    }
    if (nr >= 1) {
      var d0 = rows[0] / Z_FAR;
      offCtx.globalCompositeOperation = "source-atop";
      offCtx.globalAlpha = 0.30 + 0.45 * d0;
      offCtx.lineWidth = 1.2;
      offCtx.beginPath();
      offCtx.moveTo(P[0][0][0], P[0][0][1]);
      for (ci = 1; ci < nc; ci++) offCtx.lineTo(P[0][ci][0], P[0][ci][1]);
      offCtx.strokeStyle = (ns[0] % 4 === 0) ? LINE_BRIGHT : LINE_DIM;
      offCtx.stroke();
    }
    offCtx.globalAlpha = 1;
    offCtx.globalCompositeOperation = "source-over";
    ctx.drawImage(offCanvas, 0, 0, W, H);
  }

  /* ---- sky ---- */
  function drawSky() {
    ctx.fillStyle = VOID;
    ctx.fillRect(0, 0, W, H);
    var g = ctx.createLinearGradient(0, HZ - 120, 0, HZ);
    g.addColorStop(0, "rgba(122,43,255,0)");
    g.addColorStop(1, "rgba(122,43,255,0.10)");
    ctx.fillStyle = g;
    ctx.fillRect(0, HZ - 120, W, 120);
  }

  /* ---- starfield: seeded positions + beat-quantized sparse twinkle ---- */
  var starRng = mulberry32(1337);
  var twinkleRng = mulberry32(4242);
  var shotRng = mulberry32(90210);
  var stars = [];
  for (var si = 0; si < 50; si++) {
    stars.push({
      x: starRng(), y: 0.04 + starRng() * 0.88,
      base: 0.22 + 0.45 * starRng(),
      ph: starRng() * TAU,
      sp: 0.07 + 0.16 * starRng(),
      r: 0.6 + 1.2 * starRng(),
      pulse: -1
    });
  }
  var lastBeat = -1;
  function tickBeats(t) {
    var b = Math.floor(t / BEAT);
    while (lastBeat < b) {
      lastBeat++;
      if (twinkleRng() < 0.25) {
        var idx = Math.floor(twinkleRng() * stars.length);
        stars[idx].pulse = lastBeat;
      }
    }
  }
  function drawStars(t) {
    for (var i = 0; i < stars.length; i++) {
      var s = stars[i];
      var b = s.base + 0.12 * Math.sin(TAU * s.sp * t + s.ph);
      if (s.pulse >= 0) {
        var db = t / BEAT - s.pulse;
        if (db >= 0.1) {
          var a = Math.exp(-(db - 0.1) / 0.9);
          b += 0.9 * a;
          if (a < 0.01) s.pulse = -1;
        } else if (db >= 0) {
          b += 0.9 * (db / 0.1);
        }
      }
      if (b <= 0.02) continue;
      ctx.globalAlpha = Math.min(1, b);
      ctx.fillStyle = "#f2f7ff";
      ctx.beginPath();
      ctx.arc(s.x * W, s.y * HZ, s.r, 0, TAU);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  /* ---- shooting star: first at beat 64, then every 20-60 s ---- */
  var shot = null;
  var nextShot = SHOOT_AT;
  function drawShooting(t) {
    if (!shot && t >= nextShot) {
      shot = {
        x0: 0.12 + shotRng() * 0.35,
        y0: 0.06 + shotRng() * 0.22,
        ang: (14 + shotRng() * 12) * Math.PI / 180,
        len: 0.38 + shotRng() * 0.12,
        t0: t, dur: 1.0
      };
      nextShot = t + 20 + shotRng() * 40;
    }
    if (!shot) return;
    var p = (t - shot.t0) / shot.dur;
    if (p > 1) { shot = null; return; }
    var L = shot.len * W;
    var hx = shot.x0 * W + Math.cos(shot.ang) * L * p;
    var hy = shot.y0 * HZ + Math.sin(shot.ang) * L * p;
    var tail = 0.28 * W;
    var tx = hx - Math.cos(shot.ang) * tail;
    var ty = hy - Math.sin(shot.ang) * tail;
    ctx.globalAlpha = Math.sin(Math.PI * p);
    var g = ctx.createLinearGradient(tx, ty, hx, hy);
    g.addColorStop(0, "rgba(242,247,255,0)");
    g.addColorStop(1, "rgba(242,247,255,0.85)");
    ctx.strokeStyle = g;
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(hx, hy); ctx.stroke();
    ctx.fillStyle = "#ffffff";
    ctx.beginPath(); ctx.arc(hx, hy, 2.2, 0, TAU); ctx.fill();
    ctx.globalAlpha = 1;
  }

  /* ---- pothole: gentle drop, slow rise, one soft overshoot ---- */
  var lastBar = -1, hitT = 0;
  function bounceY(t) {
    var bar = Math.floor(t / BAR);
    if (bar > lastBar) { lastBar = bar; hitT = bar * BAR; }
    var tau = t - hitT;
    var A = 0.005 * H;            /* reduced amplitude: half the original */
    var TD = 0.22;
    if (tau < TD) {
      var q = tau / TD;
      return A * q * q;                        /* accelerating drop (down) */
    }
    var dd = tau - TD;
    return A * Math.exp(-dd / 0.7) *           /* slower, softer decay */
           Math.cos(TAU * dd / 2.2);           /* one gentle overshoot */
  }

  /* ---- main loop ---- */
  var t0 = performance.now();
  var prev = t0, scroll = 0;
  function frame(now) {
    var t = (now - t0) / 1000;
    var dt = Math.min(0.05, (now - prev) / 1000);
    prev = now;
    scroll += BASE_SPEED * SPEED_MULT * dt;
    drawSky();
    tickBeats(t);
    drawStars(t);
    drawShooting(t);
    drawTerrain(scroll);
    bounceEl.style.transform = "translateY(" + bounceY(t).toFixed(2) + "px)";
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
</script>
</body>
</html>
"""


def build_html():
    sign = ('<svg id="sign" xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 1400 820" role="img" '
            'aria-label="BSides Roanoke">' + E.sign_color(700, 439, 409) +
            '</svg>')
    html = HTML
    html = html.replace("@@VOID@@", E.VOID)
    html = html.replace("@@RIDGE_FILL_NEAR@@", E.RIDGE_FILL_NEAR)
    html = html.replace("@@RIDGE_FILL_FAR@@", E.RIDGE_FILL_FAR)
    html = html.replace("@@LINE_BRIGHT@@", E.LINE_BRIGHT)
    html = html.replace("@@LINE_DIM@@", E.LINE_DIM)
    html = html.replace("@@F1Z@@", repr(E.F1Z))
    html = html.replace("@@F2Z@@", repr(E.F2Z))
    html = html.replace("@@SIGN@@", sign)
    return html


def main():
    out_dir = os.path.join(ASSETS, "website")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_html())
    print("wrote website/index.html")


if __name__ == "__main__":
    main()
