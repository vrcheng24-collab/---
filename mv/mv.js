'use strict';
// 《远去的列车》— hand-drawn MV rendered from code.
// Every frame is a pure function of time: window.renderFrame(T) draws video-time T (seconds).
// Song time s = T - PRE. Scenes are listed in SCENES (song time).

const W = 1280, H = 720, FPS = 24;
const PRE = 22;                 // cold open before the music starts
const END_S = 272;              // song-time at which the film ends
const TOTAL = PRE + END_S;
const BAR = Math.round((H - W / 2.39) / 2);   // 2.39:1 letterbox
const IW = W, IH = H - 2 * BAR;               // 1280 x 536 image area
const FONT = '"MVSerif", "WenQuanYi Zen Hei", serif';

const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
const bufA = mk(IW, IH), bufB = mk(IW, IH);

// ---------------------------------------------------------------- math
function R(n) { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const smooth = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const ease = (t0, t1, t) => smooth((t - t0) / (t1 - t0));
const easeOut = (t0, t1, t) => { const k = clamp((t - t0) / (t1 - t0)); return 1 - (1 - k) * (1 - k); };
const easeIn = (t0, t1, t) => { const k = clamp((t - t0) / (t1 - t0)); return k * k; };
function hex(c) { const n = parseInt(c.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
function mix(a, b, t) {
  const A = hex(a), B = hex(b);
  return `rgb(${Math.round(lerp(A[0], B[0], t))},${Math.round(lerp(A[1], B[1], t))},${Math.round(lerp(A[2], B[2], t))})`;
}
function rgba(c, a) { const A = hex(c); return `rgba(${A[0]},${A[1]},${A[2]},${a})`; }

let BOIL = 0;   // hand-drawn line "boil": changes 8 times a second

// ---------------------------------------------------------------- palette
const INK = '#26231f';
const PAPER = '#ece5d7';
const TEAL = '#3fb4ab', TEAL_D = '#2a8a84', TEAL_L = '#7fd3cb';
const YEL = '#f1cf2c', YEL_D = '#c4a313';
const SIL = '#c2c6cb', SIL_D = '#868c93', SIL_L = '#e3e5e8';
const EYE = '#74bcff';
const SKIN = '#d9c7b4';

// ---------------------------------------------------------------- point helpers
function ell(cx, cy, rx, ry, n = 28, rot = 0) {
  const p = [];
  for (let i = 0; i < n; i++) {
    const a = i / n * Math.PI * 2;
    const x = Math.cos(a) * rx, y = Math.sin(a) * ry;
    p.push([cx + x * Math.cos(rot) - y * Math.sin(rot), cy + x * Math.sin(rot) + y * Math.cos(rot)]);
  }
  return p;
}
function rect(x, y, w, h) { return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]; }
function subdiv(pts, closed, step = 16) {
  const out = [];
  const n = pts.length, m = closed ? n : n - 1;
  for (let i = 0; i < m; i++) {
    const a = pts[i], b = pts[(i + 1) % n];
    const d = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const k = Math.max(1, Math.round(d / step));
    for (let j = 0; j < k; j++) out.push([lerp(a[0], b[0], j / k), lerp(a[1], b[1], j / k)]);
  }
  if (!closed) out.push(pts[n - 1]);
  return out;
}

// ---------------------------------------------------------------- drawing primitives
// sketch stroke: pencil line that wobbles a little and "boils"
function sk(c, pts, o = {}) {
  const w = o.w ?? 1.3, col = o.col ?? INK, a = o.a ?? 0.85, j = o.j ?? 0.9, seed = o.seed ?? 1;
  const closed = !!o.closed, passes = o.passes ?? 2;
  const P = subdiv(pts, closed, o.step ?? 18);
  c.save();
  const ga = c.globalAlpha;
  c.lineCap = 'round'; c.lineJoin = 'round'; c.strokeStyle = col;
  for (let p = 0; p < passes; p++) {
    c.globalAlpha = ga * a * (p ? 0.45 : 1);
    c.lineWidth = w * (p ? 0.6 : 1);
    c.beginPath();
    const n = P.length;
    for (let i = 0; i <= n - (closed ? 0 : 1); i++) {
      const q = P[i % n];
      const k = seed * 31.7 + i * 7.13 + p * 101.3 + BOIL * 13.1;
      const x = q[0] + (R(k) - 0.5) * 2 * j, y = q[1] + (R(k + 3.3) - 0.5) * 2 * j;
      if (i === 0) c.moveTo(x, y); else c.lineTo(x, y);
    }
    c.stroke();
  }
  c.restore();
}
function ln(c, x1, y1, x2, y2, o = {}) { sk(c, [[x1, y1], [x2, y2]], o); }

// watercolor-ish wash fill
function wash(c, pts, col, a = 0.9, o = {}) {
  const j = o.j ?? 1.6, seed = o.seed ?? 7;
  const P = subdiv(pts, true, o.step ?? 22);
  c.save();
  const ga = c.globalAlpha;
  c.fillStyle = col;
  for (let p = 0; p < 2; p++) {
    c.globalAlpha = ga * a * (p ? 0.5 : 0.75);
    c.beginPath();
    P.forEach((q, i) => {
      const k = seed * 17.3 + i * 3.7 + p * 57.1 + BOIL * 0.0;
      const kb = BOIL * 5.7 + i;
      const x = q[0] + (R(k) - 0.5) * 2 * j + (R(kb) - 0.5) * 0.6;
      const y = q[1] + (R(k + 1.1) - 0.5) * 2 * j + (R(kb + 2) - 0.5) * 0.6;
      if (i === 0) c.moveTo(x, y); else c.lineTo(x, y);
    });
    c.closePath();
    c.fill();
  }
  // darker pigment edge
  c.globalAlpha = ga * a * 0.22;
  c.strokeStyle = col; c.lineWidth = 2.2; c.lineJoin = 'round';
  c.stroke();
  c.restore();
}
function shape(c, pts, fill, o = {}) {
  if (fill) wash(c, pts, fill, o.fa ?? 0.92, { seed: o.seed, j: o.fj });
  if (o.line !== false) sk(c, pts, { closed: true, w: o.w ?? 1.2, a: o.la ?? 0.75, col: o.lc ?? INK, seed: o.seed, j: o.j });
}
function glow(c, x, y, r, col, a = 1) {
  if (a <= 0) return;
  c.save();
  c.globalCompositeOperation = 'screen';
  const g = c.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, rgba(col, a)); g.addColorStop(1, rgba(col, 0));
  c.fillStyle = g; c.fillRect(x - r, y - r, r * 2, r * 2);
  c.restore();
}
function grad(c, x0, y0, x1, y1, stops) {
  const g = c.createLinearGradient(x0, y0, x1, y1);
  stops.forEach(([o, col]) => g.addColorStop(o, col));
  return g;
}
function txt(c, s, x, y, size, col = INK, o = {}) {
  c.save();
  c.font = `${o.weight ?? 400} ${size}px ${FONT}`;
  c.fillStyle = col;
  c.globalAlpha = c.globalAlpha * (o.a ?? 1);
  c.textAlign = o.align ?? 'center';
  c.textBaseline = o.base ?? 'middle';
  if (o.rot) { c.translate(x, y); c.rotate(o.rot); x = 0; y = 0; }
  if (o.blur) c.filter = `blur(${o.blur}px)`;
  if (o.spacing) c.letterSpacing = o.spacing + 'px';
  c.fillText(s, x, y);
  c.restore();
}
function fillAll(c, col) { c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.fillStyle = col; c.fillRect(0, 0, IW, IH); c.restore(); }
function cam(c, x, y, z) { c.setTransform(z, 0, 0, z, IW / 2 - x * z, IH / 2 - y * z); }
function camReset(c) { c.setTransform(1, 0, 0, 1, 0, 0); }
function tint(c, col, a, mode = 'multiply') {
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  c.globalCompositeOperation = mode; c.globalAlpha = a; c.fillStyle = col; c.fillRect(0, 0, IW, IH);
  c.restore();
}
// hatch fill: diagonal pencil hatching inside a rect area (shadows)
function hatch(c, x, y, w, h, o = {}) {
  const gap = o.gap ?? 7, a = o.a ?? 0.25, ang = o.ang ?? 1;
  c.save();
  c.beginPath(); c.rect(x, y, w, h); c.clip();
  for (let i = -h; i < w; i += gap) {
    const k = i * 1.7 + (o.seed ?? 0);
    ln(c, x + i, y + h, x + i + h * ang, y, { w: 0.7, a: a * (0.6 + R(k) * 0.4), j: 0.6, seed: k, passes: 1 });
  }
  c.restore();
}

// ---------------------------------------------------------------- textures (built once)
let PAPER_TEX, GRAIN = [], VIGNETTE;
function buildTextures() {
  PAPER_TEX = mk(W, H);
  const p = PAPER_TEX.getContext('2d');
  p.fillStyle = '#f3eee4'; p.fillRect(0, 0, W, H);
  const id = p.getImageData(0, 0, W, H), d = id.data;
  let seed = 1234567;
  const lcg = () => (seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0) / 4294967296;
  for (let i = 0; i < d.length; i += 4) {
    const v = (lcg() - 0.5) * 22;
    d[i] += v; d[i + 1] += v; d[i + 2] += v * 0.9;
  }
  p.putImageData(id, 0, 0);
  for (let i = 0; i < 60; i++) {
    const x = lcg() * W, y = lcg() * H, r = 60 + lcg() * 220;
    const g = p.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, `rgba(170,150,120,${0.05 + lcg() * 0.06})`); g.addColorStop(1, 'rgba(170,150,120,0)');
    p.fillStyle = g; p.fillRect(x - r, y - r, 2 * r, 2 * r);
  }
  p.strokeStyle = 'rgba(120,100,80,0.10)'; p.lineWidth = 0.6;
  for (let i = 0; i < 700; i++) {
    const x = lcg() * W, y = lcg() * H, a = lcg() * Math.PI, l = 4 + lcg() * 14;
    p.beginPath(); p.moveTo(x, y); p.quadraticCurveTo(x + Math.cos(a) * l * 0.5 + 2, y + Math.sin(a) * l * 0.5, x + Math.cos(a) * l, y + Math.sin(a) * l); p.stroke();
  }
  for (let k = 0; k < 4; k++) {
    const g = mk(W / 2, H / 2), gc = g.getContext('2d');
    const gid = gc.createImageData(W / 2, H / 2), gd = gid.data;
    for (let i = 0; i < gd.length; i += 4) { const v = 128 + (lcg() - 0.5) * 120; gd[i] = gd[i + 1] = gd[i + 2] = v; gd[i + 3] = 255; }
    gc.putImageData(gid, 0, 0);
    GRAIN.push(g);
  }
  VIGNETTE = mk(W, IH);
  const v = VIGNETTE.getContext('2d');
  const g = v.createRadialGradient(W / 2, IH / 2, IH * 0.35, W / 2, IH / 2, W * 0.62);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(20,15,10,0.55)');
  v.fillStyle = g; v.fillRect(0, 0, W, IH);
}

// ================================================================ CHARACTERS
// Human figure, picture-book style, faceless. (x, y) = feet. h = standing height.
function person(c, x, y, h, o = {}) {
  const view = o.view ?? 'front';
  const coat = o.coat ?? '#7d7a76', pants = o.pants ?? '#4a4845', hairC = o.hairC ?? '#3a3633';
  const skin = o.skin ?? SKIN, seed = o.seed ?? 3, la = o.la ?? 0.7;
  const pose = o.pose ?? 'down';
  const sit = pose === 'sit' || o.sit;
  const hunch = o.hunch ?? 0;
  const dir = o.dir ?? 1;
  c.save();
  if (o.alpha !== undefined) c.globalAlpha = o.alpha;
  const r = h * 0.068;
  let hipY = y - h * 0.47;
  let seatY = o.seat ?? (y - h * 0.26);
  if (sit) hipY = seatY;
  const shY = hipY - h * 0.35;
  const headX = x + hunch * h * 0.05 * dir, headY = shY - r * 1.25 + hunch * h * 0.02;
  if (view === 'side') {
    const ph = o.phase ?? 0, sw = o.walk ? 0.42 : 0;
    // legs
    for (let k = 0; k < 2; k++) {
      const ang = Math.sin(ph + k * Math.PI) * sw;
      const kx = x + Math.sin(ang) * h * 0.24, ky = hipY + Math.cos(ang) * h * 0.24;
      const fx = kx + Math.sin(ang * 0.6) * h * 0.22 * (k ? 1 : 0.9), fy = y;
      sk(c, [[x, hipY], [kx, ky], [fx, fy]], { w: h * 0.055, col: pants, a: 0.95, j: 0.4, seed: seed + k, passes: 1 });
      ln(c, fx - 2 * dir, fy, fx + h * 0.06 * dir, fy, { w: h * 0.03, col: INK, a: 0.8, passes: 1 });
    }
    // torso
    const tw = h * 0.085;
    const tor = [[x - tw + dir * hunch * 8, shY], [x + tw + dir * hunch * 8, shY], [x + tw * 1.15, hipY + h * (o.coatLong ? 0.12 : 0.03)], [x - tw * 1.15, hipY + h * (o.coatLong ? 0.12 : 0.03)]];
    shape(c, tor, coat, { seed, la });
    // arm
    for (let k = 0; k < 2; k++) {
      const ang = Math.sin(ph + k * Math.PI + Math.PI) * sw * 0.8;
      const hx = x + Math.sin(ang) * h * 0.3, hy = shY + Math.cos(ang) * h * 0.3;
      if (k === 1) sk(c, [[x, shY + 4], [hx, hy]], { w: h * 0.045, col: coat, a: 0.95, j: 0.4, seed: seed + 9, passes: 1 });
      if (k === 1) wash(c, ell(hx, hy, h * 0.022, h * 0.022, 10), skin, 0.9);
    }
    // head
    wash(c, ell(headX + dir * 2, headY, r, r * 1.08, 18), skin, 0.95, { seed });
    sk(c, ell(headX + dir * 2, headY, r, r * 1.08, 18), { closed: true, w: 1.1, a: la, seed });
    hair(c, headX + dir * 2, headY, r, o.hair ?? 'short', hairC, 'side', dir);
    c.restore();
    return;
  }
  // ---- front / back
  // legs
  const lx = h * 0.045;
  if (sit) {
    const ky = seatY + h * 0.03;
    for (const sgn of [-1, 1]) {
      sk(c, [[x + sgn * lx, hipY], [x + sgn * lx * 1.4, ky], [x + sgn * lx * 1.3, y]], { w: h * 0.06, col: pants, a: 0.95, j: 0.4, seed: seed + sgn, passes: 1 });
      ln(c, x + sgn * lx * 1.3 - 3, y, x + sgn * lx * 1.3 + sgn * 5, y, { w: h * 0.03, a: 0.8, passes: 1 });
    }
  } else {
    const ph = o.phase ?? 0, wk = o.walk ? 1 : 0;
    for (const sgn of [-1, 1]) {
      const off = wk * Math.sin(ph + (sgn > 0 ? Math.PI : 0)) * h * 0.03;
      const lift = wk * Math.max(0, Math.sin(ph + (sgn > 0 ? Math.PI : 0))) * h * 0.02;
      sk(c, [[x + sgn * lx, hipY], [x + sgn * lx * 1.15 + off, y - lift]], { w: h * 0.06, col: pants, a: 0.95, j: 0.4, seed: seed + sgn, passes: 1 });
      ln(c, x + sgn * lx * 1.15 + off - 3, y - lift, x + sgn * lx * 1.15 + off + 3, y - lift, { w: h * 0.035, a: 0.8, passes: 1 });
    }
  }
  // torso
  const sw2 = h * 0.11, ww = h * 0.085, hem = o.coatLong ? h * 0.14 : h * 0.04;
  const tor = [[x - sw2 + hunch * 4 * dir, shY], [x + sw2 + hunch * 4 * dir, shY], [x + ww * 1.2, hipY + hem], [x - ww * 1.2, hipY + hem]];
  shape(c, tor, coat, { seed, la });
  if (o.scarf) wash(c, rect(x - sw2 * 0.6, shY - 2, sw2 * 1.2, h * 0.04), o.scarf, 0.95);
  // arms
  const arms = armPose(pose, x, shY, h, o);
  for (const a of arms) {
    sk(c, a.pts, { w: h * 0.045, col: coat, a: 0.95, j: 0.5, seed: seed + 5, passes: 1 });
    if (a.hand) wash(c, ell(a.hand[0], a.hand[1], h * 0.022, h * 0.022, 10), skin, 0.95);
  }
  // head
  wash(c, ell(headX, headY, r, r * 1.1, 18), skin, 0.95, { seed });
  sk(c, ell(headX, headY, r, r * 1.1, 18), { closed: true, w: 1.1, a: la, seed });
  hair(c, headX, headY, r, o.hair ?? 'short', hairC, view === 'back' ? 'back' : 'front', dir);
  if (o.glasses && view !== 'back') {
    sk(c, ell(headX - r * 0.38, headY + r * 0.05, r * 0.25, r * 0.2, 10), { closed: true, w: 0.9, a: 0.8, passes: 1 });
    sk(c, ell(headX + r * 0.38, headY + r * 0.05, r * 0.25, r * 0.2, 10), { closed: true, w: 0.9, a: 0.8, passes: 1 });
  }
  // props
  if (o.phone && arms.phoneAt) {
    const [px, py] = arms.phoneAt;
    wash(c, rect(px - h * 0.02, py - h * 0.035, h * 0.04, h * 0.07), '#bcd6ee', 0.95);
    glow(c, px, py, h * 0.12, '#a9cdf0', 0.35);
  }
  if (o.card && arms.cardAt) {
    const [px, py] = arms.cardAt;
    wash(c, rect(px - h * 0.05, py - h * 0.035, h * 0.1, h * 0.07), '#f4f1ea', 0.98);
  }
  if (o.sign) {
    const sx = x + (o.signDx ?? 0), sy = shY - h * 0.38;
    ln(c, sx, sy, sx, shY + h * 0.1, { w: 2.2, col: '#5a4a3a', a: 0.9 });
    const sw = o.signW ?? h * 0.42;
    shape(c, rect(sx - sw / 2, sy - h * 0.22, sw, h * 0.22), '#efe9dc', { seed: seed + 2 });
    const lines = o.sign.split('\n');
    lines.forEach((t, i) => txt(c, t, sx, sy - h * 0.22 + h * 0.07 + i * h * 0.075, h * 0.055, '#2a2520', { weight: 600 }));
  }
  c.restore();
}
function armPose(pose, x, shY, h, o) {
  const L = h * 0.14, sx = h * 0.11;
  const res = [];
  const t = o.t ?? 0;
  const mk2 = (sgn, ex, ey, hx, hy) => res.push({ pts: [[x + sgn * sx, shY + 3], [ex, ey], [hx, hy]], hand: [hx, hy] });
  switch (pose) {
    case 'phone': {
      mk2(-1, x - sx * 1.1, shY + L, x - sx * 1.0, shY + L * 2);
      const px = x + sx * 0.4, py = shY - h * 0.02;
      mk2(1, x + sx * 1.3, shY + L * 0.6, px, py + h * 0.03);
      res.phoneAt = [px, py - h * 0.01];
      break;
    }
    case 'phoneHigh': {
      mk2(-1, x - sx * 1.1, shY + L, x - sx * 1.0, shY + L * 2);
      const px = x + sx * 0.5, py = shY - h * 0.16;
      mk2(1, x + sx * 1.4, shY - L * 0.2, px, py + h * 0.03);
      res.phoneAt = [px, py];
      break;
    }
    case 'clap': {
      const k = (Math.sin(t * Math.PI * 2 * 2.2) + 1) / 2;
      const gap = lerp(0.02, 0.12, k) * h;
      mk2(-1, x - sx * 1.2, shY + L * 0.8, x - gap / 2, shY + L * 0.5);
      mk2(1, x + sx * 1.2, shY + L * 0.8, x + gap / 2, shY + L * 0.5);
      break;
    }
    case 'hold': {
      mk2(-1, x - sx * 1.1, shY + L * 0.9, x - sx * 0.35, shY + L * 1.2);
      mk2(1, x + sx * 1.1, shY + L * 0.9, x + sx * 0.35, shY + L * 1.2);
      res.cardAt = [x, shY + L * 1.15];
      break;
    }
    case 'wave': {
      mk2(-1, x - sx * 1.1, shY + L, x - sx * 1.0, shY + L * 2);
      const wv = Math.sin(t * 6) * h * 0.03;
      mk2(1, x + sx * 1.6, shY - L * 0.3, x + sx * 1.5 + wv, shY - L * 1.2);
      break;
    }
    case 'reachUp': {
      mk2(-1, x - sx * 1.1, shY + L, x - sx * 1.0, shY + L * 2);
      mk2(1, x + sx * 1.5, shY - L * 0.6, x + sx * 1.7 + (o.reachDx ?? 0), shY - L * 1.6 + (o.reachDy ?? 0));
      break;
    }
    case 'stopHand': {
      mk2(-1, x - sx * 1.1, shY + L, x - sx * 1.0, shY + L * 2);
      mk2(1, x + sx * 1.8, shY + L * 0.2, x + sx * 2.7, shY - L * 0.3);
      break;
    }
    case 'cable': {
      mk2(-1, x - sx * 1.2, shY + L * 0.9, x - sx * 0.9, shY + L * 1.8);
      mk2(1, x + sx * 1.6, shY + L * 0.8, x + sx * 2.4, shY + L * 1.6);
      break;
    }
    case 'sitHands': {
      mk2(-1, x - sx * 1.15, shY + L, x - sx * 0.4, shY + L * 1.7);
      mk2(1, x + sx * 1.15, shY + L, x + sx * 0.4, shY + L * 1.7);
      break;
    }
    default:
      mk2(-1, x - sx * 1.15, shY + L, x - sx * 1.05, shY + L * 2);
      mk2(1, x + sx * 1.15, shY + L, x + sx * 1.05, shY + L * 2);
  }
  return res;
}
function hair(c, x, y, r, style, col, view, dir) {
  if (style === 'none') return;
  if (style === 'grey') col = '#a9a49c';
  const top = [];
  for (let i = 0; i <= 12; i++) { const a = Math.PI + i / 12 * Math.PI; top.push([x + Math.cos(a) * r * 1.08, y + Math.sin(a) * r * 1.12 + (view === 'front' ? 0 : 0)]); }
  if (view === 'back') { wash(c, ell(x, y, r * 1.06, r * 1.12, 18), col, 0.95); }
  else if (view === 'side') {
    const pts = top.concat([[x - dir * r * 1.0, y + r * 0.5], [x - dir * r * 0.3, y - r * 0.1]]);
    wash(c, pts, col, 0.95);
  } else {
    wash(c, top.concat([[x + r, y - r * 0.1], [x - r, y - r * 0.1]]), col, 0.95);
  }
  if (style === 'bob') {
    wash(c, [[x - r * 1.1, y - r * 0.3], [x - r * 1.2, y + r * 0.8], [x - r * 0.75, y + r * 0.85], [x - r * 0.8, y]], col, 0.95);
    wash(c, [[x + r * 1.1, y - r * 0.3], [x + r * 1.2, y + r * 0.8], [x + r * 0.75, y + r * 0.85], [x + r * 0.8, y]], col, 0.95);
  }
  if (style === 'pony') {
    const px = view === 'side' ? x - dir * r * 1.1 : x + r * 0.9;
    wash(c, [[px, y - r * 0.6], [px + r * 0.5, y + r * 0.2], [px + r * 0.2, y + r * 1.3], [px - r * 0.2, y + r * 0.3]], col, 0.95);
  }
  if (style === 'cap') {
    wash(c, [[x - r * 1.1, y - r * 0.2], [x + r * 1.1, y - r * 0.2], [x + r * 1.0, y - r * 1.0], [x - r * 1.0, y - r * 1.0]], '#555', 0.95);
    wash(c, [[x - r * 0.2, y - r * 0.25], [x + r * 1.7, y - r * 0.15], [x + r * 1.0, y - r * 0.4]], '#444', 0.95);
  }
}

// ---- ALPHA (front view). (x, y) = floor point between feet. S = standing height.
function alpha(c, x, y, S, o = {}) {
  const pose = o.pose ?? 'stand';
  const eye = o.eye ?? 0.8;
  c.save();
  if (o.alpha !== undefined) c.globalAlpha = o.alpha;
  const r = S * 0.082;
  const sit = pose === 'sit';
  const hipY = sit ? (o.seat ?? y - S * 0.27) : y - S * 0.46;
  const shY = hipY - S * 0.30;
  const headX = x + (o.headDx ?? 0) * S, headY = shY - S * 0.105;
  const la = 0.7;
  const ph = o.phase ?? 0, wk = o.walk ? 1 : 0;
  // ---- legs
  for (const sgn of [-1, 1]) {
    const off = wk * Math.sin(ph + (sgn > 0 ? Math.PI : 0)) * S * 0.025;
    let kx, ky, fx;
    if (sit) { kx = x + sgn * S * 0.085; ky = hipY + S * 0.035; fx = x + sgn * S * 0.1; }
    else { kx = x + sgn * S * 0.07 + off * 0.5; ky = y - S * 0.24; fx = x + sgn * S * 0.085 + off; }
    // thigh
    sk(c, [[x + sgn * S * 0.055, hipY + S * 0.01], [kx, ky]], { w: S * 0.075, col: TEAL, a: 0.95, j: 0.4, passes: 1 });
    // shin (flared)
    const shin = [[kx - S * 0.035, ky], [kx + S * 0.035, ky], [fx + S * 0.06 * (sgn > 0 ? 1 : 0.7), y - S * 0.02], [fx - S * 0.06 * (sgn > 0 ? 0.7 : 1), y - S * 0.02]];
    shape(c, shin, TEAL, { la, seed: 40 + sgn });
    sk(c, [[kx + sgn * S * 0.02, ky + S * 0.03], [fx + sgn * S * 0.04, y - S * 0.04]], { w: S * 0.012, col: YEL, a: 0.9, passes: 1 });
    wash(c, rect(fx - S * 0.055, y - S * 0.035, S * 0.11, S * 0.035), YEL, 0.95);
    wash(c, ell(kx, ky, S * 0.035, S * 0.033, 14), YEL, 0.98);
    sk(c, ell(kx, ky, S * 0.035, S * 0.033, 14), { closed: true, w: 1, a: 0.6, passes: 1 });
  }
  // ---- hips + waist
  shape(c, [[x - S * 0.11, hipY - S * 0.03], [x + S * 0.11, hipY - S * 0.03], [x + S * 0.08, hipY + S * 0.05], [x - S * 0.08, hipY + S * 0.05]], TEAL, { la, seed: 51 });
  shape(c, [[x - S * 0.06, shY + S * 0.16], [x + S * 0.06, shY + S * 0.16], [x + S * 0.08, hipY - S * 0.03], [x - S * 0.08, hipY - S * 0.03]], SIL_D, { la, seed: 52 });
  for (let i = 0; i < 3; i++) ln(c, x - S * 0.06, shY + S * (0.19 + i * 0.03), x + S * 0.06, shY + S * (0.19 + i * 0.03), { w: 0.8, a: 0.5, passes: 1 });
  // ---- torso
  shape(c, [[x - S * 0.15, shY], [x + S * 0.15, shY], [x + S * 0.1, shY + S * 0.17], [x - S * 0.1, shY + S * 0.17]], TEAL, { la, seed: 53 });
  if (!o.back) {
    for (const sgn of [-1, 1]) {
      wash(c, ell(x + sgn * S * 0.055, shY + S * 0.085, S * 0.058, S * 0.055, 20), TEAL_L, 0.55);
      sk(c, ell(x + sgn * S * 0.055, shY + S * 0.085, S * 0.058, S * 0.055, 20), { closed: true, w: 1, a: 0.55, passes: 1 });
      sk(c, [[x + sgn * S * 0.005, shY + S * 0.04], [x + sgn * S * 0.06, shY + S * 0.025], [x + sgn * S * 0.11, shY + S * 0.06]], { w: S * 0.014, col: YEL, a: 0.95, passes: 1 });
    }
    shape(c, rect(x - S * 0.012, shY + S * 0.01, S * 0.024, S * 0.15), SIL, { la: 0.5 });
  } else {
    shape(c, rect(x - S * 0.02, shY, S * 0.04, S * 0.17), SIL_D, { la: 0.5 });
  }
  // ---- arms
  const armPts = alphaArms(x, shY, S, o, hipY);
  for (const a of armPts.behind || []) drawAlphaArm(c, a, S);
  if (o.guitar) guitar(c, x + S * 0.0, hipY - S * 0.06, S, o.guitarAng ?? -0.38, o.strum ?? 0, o.core ?? 0);
  for (const a of armPts.front) drawAlphaArm(c, a, S);
  // shoulder caps
  for (const sgn of [-1, 1]) {
    wash(c, ell(x + sgn * S * 0.15, shY + S * 0.01, S * 0.055, S * 0.04, 16), YEL, 0.98);
    sk(c, ell(x + sgn * S * 0.15, shY + S * 0.01, S * 0.055, S * 0.04, 16), { closed: true, w: 1, a: 0.6, passes: 1 });
  }
  // ---- neck
  for (let i = -1; i <= 1; i++) ln(c, headX + i * S * 0.012, headY + r * 0.8, x + i * S * 0.016, shY + 2, { w: 1.4, a: 0.7 });
  wash(c, rect(headX - S * 0.018, headY + r * 0.75, S * 0.036, shY - headY - r * 0.75), SIL_D, 0.6);
  alphaHead(c, headX, headY, r, { eye, back: o.back, tilt: o.tilt ?? 0, look: o.look ?? 0, mouth: o.mouth ?? 0 });
  c.restore();
}
function alphaArms(x, shY, S, o, hipY) {
  const front = [], behind = [];
  const L = S * 0.15;
  if (o.guitar) {
    const st = o.strum ?? 0;
    const strumY = Math.sin(st * Math.PI * 2 * 1.2) * S * 0.02;
    // right hand (image left) strums at the body
    front.push({ s: [x - S * 0.15, shY + S * 0.01], e: [x - S * 0.17, shY + S * 0.15], h: [x - S * 0.04, hipY - S * 0.05 + strumY] });
    // left hand (image right) on the neck
    front.push({ s: [x + S * 0.15, shY + S * 0.01], e: [x + S * 0.24, shY + S * 0.12], h: [x + S * 0.28, hipY - S * 0.18] });
  } else if (o.arms === 'lap') {
    front.push({ s: [x - S * 0.15, shY + S * 0.01], e: [x - S * 0.17, shY + L], h: [x - S * 0.07, hipY + S * 0.01] });
    front.push({ s: [x + S * 0.15, shY + S * 0.01], e: [x + S * 0.17, shY + L], h: [x + S * 0.07, hipY + S * 0.01] });
  } else if (o.arms === 'reach') {
    const k = o.reach ?? 0;
    front.push({ s: [x - S * 0.15, shY + S * 0.01], e: [x - S * 0.17, shY + L], h: [x - S * 0.07, hipY + S * 0.01] });
    front.push({ s: [x + S * 0.15, shY + S * 0.01], e: [x + S * lerp(0.17, 0.27, k), shY + L * lerp(1, 0.7, k)], h: [x + S * lerp(0.08, 0.42, k), lerp(hipY, shY + L * 0.9, k)] });
  } else if (o.arms === 'hold') {
    front.push({ s: [x - S * 0.15, shY + S * 0.01], e: [x - S * 0.15, shY + L], h: [x - S * 0.03, shY + L * 1.2] });
    front.push({ s: [x + S * 0.15, shY + S * 0.01], e: [x + S * 0.15, shY + L], h: [x + S * 0.03, shY + L * 1.2] });
  } else {
    front.push({ s: [x - S * 0.15, shY + S * 0.01], e: [x - S * 0.18, shY + L], h: [x - S * 0.19, shY + L * 1.9] });
    front.push({ s: [x + S * 0.15, shY + S * 0.01], e: [x + S * 0.18, shY + L], h: [x + S * 0.19, shY + L * 1.9] });
  }
  return { front, behind };
}
function drawAlphaArm(c, a, S) {
  sk(c, [a.s, a.e], { w: S * 0.05, col: TEAL, a: 0.97, j: 0.4, passes: 1 });
  sk(c, [a.e, a.h], { w: S * 0.042, col: SIL, a: 0.97, j: 0.4, passes: 1 });
  sk(c, [a.e, [lerp(a.e[0], a.h[0], 0.55), lerp(a.e[1], a.h[1], 0.55)]], { w: S * 0.046, col: TEAL, a: 0.97, j: 0.4, passes: 1 });
  wash(c, ell(a.e[0], a.e[1], S * 0.022, S * 0.022, 10), SIL_D, 0.95);
  wash(c, ell(a.h[0], a.h[1], S * 0.026, S * 0.022, 12), YEL, 0.97);
  sk(c, ell(a.h[0], a.h[1], S * 0.026, S * 0.022, 12), { closed: true, w: 0.9, a: 0.5, passes: 1 });
}
function alphaHead(c, x, y, r, o = {}) {
  const eye = o.eye ?? 0.8;
  c.save();
  c.translate(x, y); c.rotate(o.tilt ?? 0);
  const look = (o.look ?? 0) * r * 0.12;
  // horn fin (right side)
  shape(c, [[r * 0.55, -r * 0.75], [r * 1.55, -r * 1.35], [r * 1.25, -r * 0.65], [r * 0.95, -r * 0.2]], YEL, { la: 0.65, seed: 61 });
  // ear turbines
  for (const sgn of [-1, 1]) {
    wash(c, ell(sgn * r * 1.0, r * 0.18, r * 0.36, r * 0.42, 20), SIL, 0.97);
    wash(c, ell(sgn * r * 1.0, r * 0.18, r * 0.24, r * 0.29, 18), SIL_D, 0.9);
    sk(c, ell(sgn * r * 1.0, r * 0.18, r * 0.36, r * 0.42, 20), { closed: true, w: 1.1, a: 0.65, passes: 1 });
    for (let i = 0; i < 8; i++) {
      const a = i / 8 * Math.PI * 2;
      ln(c, sgn * r * 1.0, r * 0.18, sgn * r * 1.0 + Math.cos(a) * r * 0.22, r * 0.18 + Math.sin(a) * r * 0.27, { w: 0.6, a: 0.4, passes: 1, j: 0.3 });
    }
    sk(c, [[sgn * r * 0.75, r * 0.55], [sgn * r * 1.05, r * 0.62], [sgn * r * 1.3, r * 0.35]], { w: r * 0.1, col: YEL, a: 0.95, passes: 1 });
  }
  // helmet
  const helm = ell(0, -r * 0.08, r * 0.95, r * 1.0, 30);
  shape(c, helm, SIL, { la: 0.7, seed: 62 });
  // teal patches on helmet
  wash(c, [[-r * 0.9, -r * 0.3], [-r * 0.55, -r * 0.85], [-r * 0.35, -r * 0.55], [-r * 0.7, -r * 0.05]], TEAL, 0.9);
  wash(c, [[r * 0.9, -r * 0.3], [r * 0.6, -r * 0.8], [r * 0.4, -r * 0.5], [r * 0.72, -r * 0.05]], TEAL, 0.9);
  if (!o.back) {
    // yellow crest with grille
    shape(c, [[-r * 0.38, -r * 1.0], [r * 0.38, -r * 1.0], [r * 0.28, -r * 0.45], [-r * 0.28, -r * 0.45]], YEL, { la: 0.6, seed: 63 });
    for (let i = -2; i <= 2; i++) ln(c, i * r * 0.1, -r * 0.92, i * r * 0.08, -r * 0.52, { w: 1, a: 0.45, passes: 1, j: 0.3 });
    // face plate
    const face = [[-r * 0.62, -r * 0.3], [r * 0.62, -r * 0.3], [r * 0.6, r * 0.25], [r * 0.32, r * 0.78], [0, r * 0.92], [-r * 0.32, r * 0.78], [-r * 0.6, r * 0.25]];
    shape(c, face, SIL_L, { la: 0.6, seed: 64 });
    // brow V markings (yellow / teal)
    sk(c, [[-r * 0.5, -r * 0.3], [-r * 0.32, -r * 0.42], [-r * 0.12, -r * 0.3]], { w: r * 0.07, col: YEL, a: 0.95, passes: 1 });
    sk(c, [[r * 0.12, -r * 0.3], [r * 0.32, -r * 0.42], [r * 0.5, -r * 0.3]], { w: r * 0.06, col: TEAL, a: 0.95, passes: 1 });
    // seams
    ln(c, 0, -r * 0.3, 0, r * 0.05, { w: 0.8, a: 0.4, passes: 1 });
    ln(c, -r * 0.55, r * 0.25, -r * 0.1, r * 0.4, { w: 0.7, a: 0.35, passes: 1 });
    ln(c, r * 0.55, r * 0.25, r * 0.1, r * 0.4, { w: 0.7, a: 0.35, passes: 1 });
    // eyes
    for (const sgn of [-1, 1]) {
      const ex = sgn * r * 0.3 + look, ey = -r * 0.08;
      wash(c, ell(ex, ey, r * 0.19, r * 0.13, 16), '#3b4048', 0.95);
      if (eye > 0.02) {
        glow(c, ex, ey, r * 0.5, EYE, 0.55 * eye);
        sk(c, ell(ex, ey, r * 0.12, r * 0.1, 14), { closed: true, w: r * 0.035, col: EYE, a: eye, passes: 1, j: 0.2 });
        wash(c, ell(ex, ey, r * 0.05, r * 0.045, 10), '#d8ecff', eye);
      }
      sk(c, [[ex - r * 0.2, ey - r * 0.1], [ex, ey - r * 0.16], [ex + r * 0.2, ey - r * 0.1]], { w: r * 0.035, col: TEAL_D, a: 0.9, passes: 1 });
    }
    // nose
    sk(c, [[0, r * 0.0], [-r * 0.07, r * 0.3], [r * 0.07, r * 0.32]], { w: 0.9, a: 0.5, passes: 1 });
    // lips
    const mo = (o.mouth ?? 0) * r * 0.06;
    wash(c, [[-r * 0.17, r * 0.52], [0, r * 0.47], [r * 0.17, r * 0.52], [0, r * 0.57]], TEAL, 0.95);
    wash(c, [[-r * 0.15, r * 0.55 + mo], [r * 0.15, r * 0.55 + mo], [0, r * 0.66 + mo]], TEAL_D, 0.95);
  } else {
    shape(c, [[-r * 0.3, -r * 1.0], [r * 0.3, -r * 1.0], [r * 0.25, r * 0.6], [-r * 0.25, r * 0.6]], YEL, { la: 0.5, seed: 65 });
  }
  c.restore();
}
// ALPHA head in profile (facing left). For close-ups.
function alphaHeadSide(c, x, y, r, o = {}) {
  const eye = o.eye ?? 0.8;
  c.save(); c.translate(x, y);
  shape(c, [[r * 0.2, -r * 0.8], [r * 1.5, -r * 1.55], [r * 1.25, -r * 0.7], [r * 0.7, -r * 0.2]], YEL, { la: 0.65 });
  shape(c, ell(r * 0.1, -r * 0.05, r * 1.0, r * 1.02, 30), SIL, { la: 0.7 });
  wash(c, [[r * 0.2, -r * 1.0], [r * 0.9, -r * 0.55], [r * 0.95, r * 0.0], [r * 0.4, -r * 0.4]], TEAL, 0.9);
  shape(c, [[-r * 0.85, -r * 0.95], [-r * 0.1, -r * 1.05], [-r * 0.05, -r * 0.6], [-r * 0.75, -r * 0.5]], YEL, { la: 0.55 });
  // face profile
  const face = [[-r * 0.55, -r * 0.45], [-r * 0.9, -r * 0.3], [-r * 0.95, -r * 0.05], [-r * 1.12, r * 0.22], [-r * 0.95, r * 0.3], [-r * 1.0, r * 0.48], [-r * 0.9, r * 0.6], [-r * 0.85, r * 0.8], [-r * 0.45, r * 0.98], [-r * 0.05, r * 0.7], [-r * 0.1, -r * 0.2]];
  shape(c, face, SIL_L, { la: 0.7 });
  wash(c, [[-r * 1.0, r * 0.47], [-r * 0.85, r * 0.45], [-r * 0.88, r * 0.62], [-r * 0.95, r * 0.6]], TEAL, 0.95);
  // ear turbine
  wash(c, ell(r * 0.25, r * 0.15, r * 0.42, r * 0.46, 22), SIL, 0.97);
  wash(c, ell(r * 0.25, r * 0.15, r * 0.3, r * 0.33, 20), SIL_D, 0.9);
  sk(c, ell(r * 0.25, r * 0.15, r * 0.42, r * 0.46, 22), { closed: true, w: 1.2, a: 0.6 });
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; ln(c, r * 0.25, r * 0.15, r * 0.25 + Math.cos(a) * r * 0.28, r * 0.15 + Math.sin(a) * r * 0.31, { w: 0.7, a: 0.4, passes: 1, j: 0.3 }); }
  sk(c, [[r * 0.0, r * 0.62], [r * 0.4, r * 0.7], [r * 0.75, r * 0.4]], { w: r * 0.09, col: YEL, a: 0.95 });
  // eye
  const ex = -r * 0.7, ey = -r * 0.12;
  wash(c, ell(ex, ey, r * 0.13, r * 0.12, 14), '#3b4048', 0.95);
  if (eye > 0.02) {
    glow(c, ex, ey, r * 0.45, EYE, 0.5 * eye);
    sk(c, ell(ex, ey, r * 0.08, r * 0.09, 12), { closed: true, w: r * 0.03, col: EYE, a: eye, passes: 1, j: 0.2 });
  }
  sk(c, [[ex - r * 0.15, ey - r * 0.16], [ex + r * 0.12, ey - r * 0.18]], { w: r * 0.035, col: TEAL_D, a: 0.9 });
  // neck
  for (let i = 0; i < 4; i++) ln(c, -r * 0.3 + i * r * 0.15, r * 0.85, -r * 0.35 + i * r * 0.17, r * 1.6, { w: 1.6, a: 0.7 });
  c.restore();
}
// Yellow angular guitar with the gear core. centred at (x, y), scaled by S (alpha height).
function guitar(c, x, y, S, ang, strum = 0, core = 0) {
  c.save(); c.translate(x, y); c.rotate(ang);
  const u = S * 0.01;
  // neck
  shape(c, rect(u * 6, -u * 1.6, u * 46, u * 3.2), '#2c2f36', { la: 0.6 });
  for (let i = 0; i < 14; i++) ln(c, u * (9 + i * 3.1), -u * 1.6, u * (9 + i * 3.1), u * 1.6, { w: 0.7, col: SIL_L, a: 0.6, passes: 1, j: 0.2 });
  // headstock
  shape(c, [[u * 51, -u * 2.2], [u * 59, -u * 2.6], [u * 59, u * 1.2], [u * 51, u * 2]], SIL, { la: 0.6 });
  // body: angular flying-V-ish shape
  const body = [[-u * 16, -u * 9], [-u * 4, -u * 6], [u * 4, -u * 11], [u * 9, -u * 3], [u * 9, u * 3], [u * 2, u * 7], [-u * 6, u * 11], [-u * 18, u * 6], [-u * 13, 0]];
  shape(c, body, YEL, { la: 0.7, seed: 71 });
  // spikes
  for (let i = 0; i < 3; i++) ln(c, -u * (13 - i * 3), -u * (8 - i), -u * (17 - i * 3), -u * (12 - i), { w: 1.5, col: SIL_D, a: 0.8, passes: 1 });
  // gear core
  wash(c, ell(-u * 3, 0, u * 5.2, u * 5.2, 22), SIL, 0.98);
  sk(c, ell(-u * 3, 0, u * 5.2, u * 5.2, 22), { closed: true, w: 1.2, a: 0.7 });
  wash(c, ell(-u * 3, 0, u * 2.2, u * 2.2, 14), SIL_D, 0.95);
  for (let i = 0; i < 10; i++) {
    const a = i / 10 * Math.PI * 2;
    ln(c, -u * 3 + Math.cos(a) * u * 2.4, Math.sin(a) * u * 2.4, -u * 3 + Math.cos(a) * u * 4.8, Math.sin(a) * u * 4.8, { w: 0.8, a: 0.5, passes: 1, j: 0.2 });
  }
  if (core > 0) glow(c, -u * 3, 0, u * 9, '#ffe9a0', 0.35 * core);
  // strings
  for (let i = -1; i <= 1; i++) {
    const vib = Math.sin(strum * 90 + i) * u * 0.25 * clamp(1 - (strum % 1) * 1.5);
    ln(c, -u * 1, i * u * 0.9 + vib, u * 52, i * u * 0.8, { w: 0.6, col: '#e8e8e8', a: 0.75, passes: 1, j: 0.1 });
  }
  c.restore();
}

// ---- a human hand seen from above (back of the hand). Wrist at (x, y), fingers point along `ang`.
function hand(c, x, y, sc, ang, o = {}) {
  const skin = o.skin ?? SKIN, seed = o.seed ?? 0;
  c.save(); c.translate(x, y); c.rotate(ang); c.scale(sc, sc);
  if (o.sleeve) shape(c, [[-320, -78], [8, -66], [8, 66], [-320, 78]], o.sleeve, { seed: seed + 9 });
  // thumb (tucked along the lower side)
  sk(c, [[30, 48], [78, 80], [118, 88]], { w: 30, col: INK, a: 0.55, passes: 1, j: 0.3 });
  sk(c, [[30, 48], [78, 80], [118, 88]], { w: 26, col: skin, a: 1, passes: 1, j: 0.3 });
  // palm / back of hand
  shape(c, [[0, -54], [60, -62], [118, -58], [130, -10], [126, 44], [96, 62], [20, 58], [0, 50]], skin, { seed: seed + 1 });
  const lifts = o.lifts ?? [0, 0, 0, 0];
  const lens = [74, 86, 80, 62];
  for (let i = 0; i < 4; i++) {
    const ky = -44 + i * 30, len = lens[i] * (1 - (lifts[i] || 0) * 0.3);
    const curl = (o.curl ?? 0) * 18;
    const pts = [[118, ky], [118 + len * 0.55, ky + curl * 0.3], [118 + len, ky + curl]];
    if (lifts[i]) wash(c, ell(118 + len + 10, ky + 14, 16, 8, 10), '#000', 0.18 * lifts[i]);
    sk(c, pts, { w: 27, col: INK, a: 0.5, passes: 1, j: 0.3 });
    sk(c, pts, { w: 23, col: skin, a: 1, passes: 1, j: 0.3 });
    sk(c, [[124, ky - 8], [128, ky], [124, ky + 8]], { w: 1, a: 0.35, passes: 1 });
    sk(c, [[118 + len * 0.55 - 3, ky - 7], [118 + len * 0.55 + 2, ky + 7]], { w: 0.8, a: 0.3, passes: 1 });
  }
  // veins / age lines
  if (o.old) for (let i = 0; i < 4; i++) sk(c, [[20, -30 + i * 22], [70, -36 + i * 24], [112, -40 + i * 28]], { w: 0.9, col: '#8a7466', a: 0.35, passes: 1 });
  if (o.onBack) o.onBack(c);
  c.restore();
}

// ---- train: carriages extending to the right of headX (head faces left). y = rail level.
function train(c, headX, y, n, o = {}) {
  const cw = o.cw ?? 330, ch = o.ch ?? 92, gap = 10;
  const body = o.body ?? '#55635a';
  for (let k = 0; k < n; k++) {
    const x0 = headX + k * (cw + gap);
    if (x0 > IW + 400 || x0 + cw < -400) continue;
    const top = y - ch - 14;
    const pts = k === 0
      ? [[x0 + 30, top], [x0 + cw, top], [x0 + cw, y - 14], [x0, y - 14], [x0, top + 40]]
      : rect(x0, top, cw, ch);
    shape(c, pts, body, { la: 0.8, seed: 80 + k });
    wash(c, rect(x0 + 4, top + ch * 0.62, cw - 8, ch * 0.1), '#e8e2cf', 0.5);   // stripe
    sk(c, [[x0 + 6, top - 6], [x0 + cw - 6, top - 6]], { w: 3, col: '#3b443e', a: 0.9 });
    // windows
    for (let w = 0; w < 7; w++) {
      const wx = x0 + 40 + w * 40;
      if (k === 0 && w < 1) continue;
      const lit = o.lit ?? 0.0;
      shape(c, rect(wx, top + 14, 26, 24), lit > 0 ? mix('#4a5560', '#f3d999', lit) : '#3e4850', { la: 0.6, seed: 90 + w + k * 9 });
      if (o.face && o.face[0] === k && o.face[1] === w) {
        person(c, wx + 13, top + 52, 46, { coat: '#6d6862', hair: 'grey', glasses: true, pose: o.facePose ?? 'down', t: o.t, seed: 5 });
      }
    }
    if (k === 0) {
      wash(c, rect(x0 + 8, top + 52, 16, 10), '#efe7c0', 0.9);
      if (o.headlight) glow(c, x0 + 12, top + 57, 160, '#fff1c8', o.headlight);
    }
    // bogies
    for (const bx of [x0 + 50, x0 + cw - 50]) {
      wash(c, ell(bx - 16, y - 6, 9, 9, 12), '#2f2f2f', 0.95);
      wash(c, ell(bx + 16, y - 6, 9, 9, 12), '#2f2f2f', 0.95);
    }
  }
}

// ================================================================ SCENES
// Each scene: fn(c, u, d, s) — u local time, d duration, s song time.

function sBlack(c) { fillAll(c, '#000'); }

function sTitleCard(c, u, d) {
  fillAll(c, '#0b0b0b');
  const a = ease(0.3, 1.2, u) * (1 - ease(d - 0.9, d - 0.1, u));
  txt(c, '综艺访谈节目《对面》第 47 期', IW / 2, IH / 2 - 18, 30, '#e9e2d2', { a, spacing: 4 });
  txt(c, '录制前二十分钟', IW / 2, IH / 2 + 30, 20, '#a9a294', { a, spacing: 6 });
}

// ---------- the studio (shared by many moments)
// crew walking across the studio; xf = where each one ends up standing once they stop to listen
const WALKERS = [
  { xf: 455, y: 500, h: 215, v: 55, stop: 16.5, coat: '#6f6c68', hair: 'short', seed: 11, pose: 'cable' },
  { xf: 1010, y: 512, h: 228, v: -48, stop: 18.5, coat: '#585654', hair: 'cap', seed: 12, pose: 'down' },
  { xf: 830, y: 492, h: 205, v: 38, stop: 15.5, coat: '#8a8580', hair: 'bob', hairC: '#2c2826', seed: 13, pose: 'hold', card: true },
  { xf: 330, y: 520, h: 240, v: -62, stop: 22.5, coat: '#4f4d4b', hair: 'short', seed: 14, pose: 'down' },
];
WALKERS.forEach(w => { w.x0 = w.xf - w.v * (w.stop + 0.7 + 25); });
function walkerX(w, s) {
  const eff = s < w.stop ? s : w.stop + 0.7 * (1 - Math.exp(-(s - w.stop) / 0.7));
  let x = w.x0 + w.v * (eff + 25);
  const span = IW + 300;
  x = ((x + 150) % span + span) % span - 150;
  const moving = s < w.stop + 1.2;
  return { x, eff, moving };
}
function studioBackdrop(c, s, o = {}) {
  // back wall
  c.fillStyle = grad(c, 0, 0, 0, 340, [[0, '#2f2f31'], [1, '#4b4a4a']]);
  c.fillRect(-200, -100, IW + 400, 440);
  // LED backdrop
  shape(c, rect(380, 70, 520, 230), '#3a3c40', { la: 0.6, seed: 201 });
  txt(c, '对 面', 640, 170, 92, '#5c5f66', { weight: 600, a: 0.8 });
  txt(c, 'FACE TO FACE', 640, 245, 18, '#6d7077', { spacing: 8, a: 0.8 });
  // truss
  for (const ty of [22, 44]) ln(c, -100, ty, IW + 100, ty, { w: 2.2, col: '#1d1d1d', a: 0.9 });
  for (let i = -100; i < IW + 100; i += 44) ln(c, i, 22, i + 22, 44, { w: 1, col: '#1d1d1d', a: 0.7, passes: 1 });
  for (const lx of [180, 360, 520, 640, 760, 920, 1100]) {
    shape(c, [[lx - 12, 46], [lx + 12, 46], [lx + 18, 78], [lx - 18, 78]], '#262626', { la: 0.8, seed: lx });
  }
  // floor
  c.fillStyle = grad(c, 0, 330, 0, 536, [[0, '#605e5b'], [1, '#7c7975']]);
  c.fillRect(-200, 330, IW + 400, 300);
  ln(c, -100, 330, IW + 100, 330, { w: 1.2, a: 0.6 });
  // stage disc
  shape(c, ell(640, 432, 250, 36, 40), '#8e8a84', { la: 0.5, seed: 210 });
  // spot cone
  const spot = o.spot ?? 0.3;
  c.save(); c.globalCompositeOperation = 'screen';
  c.fillStyle = grad(c, 0, 40, 0, 440, [[0, `rgba(255,248,230,${0.18 * spot})`], [1, `rgba(255,248,230,${0.32 * spot})`]]);
  c.beginPath(); c.moveTo(615, 46); c.lineTo(665, 46); c.lineTo(790, 440); c.lineTo(490, 440); c.closePath(); c.fill();
  c.restore();
  glow(c, 640, 425, 210, '#fff4dc', 0.25 * spot);
}
function sStudioWide(c, u, d, s) {
  // camera path by song time
  let cx = 640, cy = 268, z = 1;
  if (s < 0) { cx = 640 + Math.sin(s * 0.2) * 8; z = 1.0; }
  else if (s < 20.8) { z = lerp(1.0, 1.12, ease(0, 20.8, s)); cy = lerp(268, 300, ease(0, 20.8, s)); }
  else if (s < 34) { z = lerp(1.18, 1.5, ease(26.6, 33.6, s)); cy = lerp(300, 330, ease(26.6, 33.6, s)); }
  else if (s < 205) { z = 1.0; }
  else if (s < 241) { z = lerp(1.02, 1.08, ease(231.4, 240.6, s)); cy = 280; }
  fillAll(c, '#3a3a3a');
  cam(c, cx, cy, z);
  const spot = s < 0 ? 0.25 : clamp(0.3 + ease(0, 30, s) * 0.6);
  studioBackdrop(c, s, { spot });

  // ladder + 老杨
  ln(c, 230, 480, 268, 140, { w: 3, col: '#3c3c3c', a: 0.9 });
  ln(c, 300, 480, 300, 140, { w: 3, col: '#3c3c3c', a: 0.9 });
  for (let i = 0; i < 9; i++) { const yy = 460 - i * 38; ln(c, lerp(232, 268, (480 - yy) / 340), yy, 300, yy, { w: 2, col: '#3c3c3c', a: 0.8, passes: 1 }); }
  const yangStop = 21.5;
  const yangPose = s > 233.2 && s < 260 ? 'clap' : (s < yangStop ? 'reachUp' : 'reachUp');
  const fiddle = s < yangStop ? Math.sin(s * 5) * 6 : 0;
  const lowered = s >= yangStop && s < 233 ? ease(yangStop, yangStop + 1.5, s) : 0;
  person(c, 285, 272, 170, {
    coat: '#5b5550', hair: 'grey', pose: yangPose, t: s, seed: 21, reachDx: fiddle, reachDy: lowered * 40,
  });
  // host desk + 林姐 (right)
  const linPose = s > 27.4 && s < 31.5 ? 'stopHand' : (s > 234.2 && s < 240.5 ? 'clap' : 'hold');
  person(c, 975, 452, 200, { pose: linPose, sit: true, seat: 400, coat: '#2f2d2c', hair: 'bob', hairC: '#1f1b19', card: linPose === 'hold', t: s + 0.3, seed: 22 });
  shape(c, [[860, 390], [1080, 390], [1070, 452], [870, 452]], '#4a4743', { la: 0.7, seed: 220 });
  // producer: walks toward stage at 26.5 then stops
  const prodX = s < 26.5 ? 1180 : lerp(1180, 1110, ease(26.5, 27.6, s));
  person(c, prodX, 506, 230, { coat: '#3e3c3a', hair: 'short', pose: s > 235 && s < 241 ? 'clap' : 'down', walk: s > 26.5 && s < 27.6, phase: s * 8, t: s + 0.6, seed: 23 });

  // ALPHA on the stool
  ln(c, 625, 378, 610, 432, { w: 2, col: '#333', a: 0.9 }); ln(c, 655, 378, 670, 432, { w: 2, col: '#333', a: 0.9 });
  const hasGuitar = s > -1.2;
  const singing = s > 14 && s < 231.5;
  alpha(c, 640, 432, 250, {
    pose: 'sit', seat: 378, guitar: hasGuitar, arms: hasGuitar ? undefined : 'lap',
    strum: hasGuitar && s < 232 ? s : 0, eye: s < 0 ? 0.5 : 0.9, core: hasGuitar ? 0.3 + 0.4 * ease(0, 40, s) : 0,
    mouth: singing ? (Math.sin(s * 7.3) * 0.5 + 0.5) * 0.8 : 0,
  });
  if (!hasGuitar) {
    // guitar on its display stand with a tag
    ln(c, 735, 432, 725, 360, { w: 2, col: '#333' }); ln(c, 735, 432, 748, 360, { w: 2, col: '#333' });
    guitar(c, 736, 330, 250, -Math.PI / 2 + 0.05, 0, 0);
    shape(c, rect(752, 380, 62, 22), '#f2eee4', { la: 0.5 });
    txt(c, '展品·请勿触碰', 783, 391, 9.5, '#333');
  }
  // camera crew foreground (left) — big silhouette
  const camLean = s > 25 && s < 240 ? ease(25, 26.5, s) : 0;
  shape(c, [[60, 300], [200, 290], [205, 360], [70, 372]], '#1e1e1f', { la: 0.9, seed: 230 });
  shape(c, ell(210, 325, 22, 30, 14), '#2a2a2b', { la: 0.8 });
  ln(c, 130, 370, 70, 560, { w: 4, col: '#1a1a1a' }); ln(c, 130, 370, 140, 560, { w: 4, col: '#1a1a1a' }); ln(c, 130, 370, 200, 560, { w: 4, col: '#1a1a1a' });
  person(c, 40 - camLean * 25, 640, 380, { coat: '#232323', pants: '#1a1a1a', hair: 'short', hairC: '#151515', skin: '#6a625a', pose: 'down', seed: 24, la: 0.9 });
  // monitor (right foreground)
  shape(c, rect(1090, 250, 175, 110), '#151618', { la: 0.9, seed: 240 });
  c.save(); c.globalAlpha = 0.95;
  c.fillStyle = '#2a3442'; c.fillRect(1098, 258, 159, 94); c.restore();
  if (s < 30) {
    txt(c, '播放量破十亿', 1177, 278, 13, '#cfd8e3');
    txt(c, 'AI，该不该被限制？', 1177, 303, 15, '#ffffff', { weight: 600 });
    // tiny protest image
    for (let i = 0; i < 6; i++) { const px = 1110 + i * 24; ln(c, px, 345, px, 325, { w: 1, col: '#9aa7b6', a: 0.8, passes: 1 }); wash(c, rect(px - 8, 318, 16, 9), '#cdd5df', 0.9); }
  } else {
    txt(c, '● LIVE', 1177, 300, 18, '#e8b0a8', { weight: 600 });
  }
  ln(c, 1177, 360, 1177, 536, { w: 3, col: '#1a1a1a' });

  // walking crew
  for (const w of WALKERS) {
    const P = walkerX(w, s);
    let pose = w.pose;
    if (s > 234.6 && s < 241) pose = 'clap';
    person(c, P.x, w.y, w.h, { view: P.moving ? 'side' : 'front', dir: Math.sign(w.v), walk: P.moving, phase: P.eff * 7, coat: w.coat, hair: w.hair, hairC: w.hairC, pose, card: w.card, t: s + w.seed, seed: w.seed });
  }
  camReset(c);
}
// 老杨 on the ladder, from below: his hand stops on the light
function sLadder(c, u, d, s) {
  fillAll(c, '#2c2c2e');
  cam(c, 640, 268, 1 + u * 0.01);
  // truss + big light fixture
  c.fillStyle = grad(c, 0, 0, 0, 536, [[0, '#262628'], [1, '#3d3c3b']]); c.fillRect(-50, -50, IW + 100, 640);
  for (const ty of [40, 90]) ln(c, -100, ty, IW + 100, ty, { w: 4, col: '#151515' });
  for (let i = -100; i < IW + 100; i += 70) ln(c, i, 40, i + 35, 90, { w: 2, col: '#151515', passes: 1 });
  shape(c, [[520, 95], [640, 95], [665, 190], [495, 190]], '#1f1f1f', { seed: 301 });
  glow(c, 580, 200, 260, '#fff4d8', 0.35);
  // ladder rails rising into frame
  ln(c, 360, 560, 470, 150, { w: 8, col: '#3a3a3a' }); ln(c, 520, 560, 560, 150, { w: 8, col: '#3a3a3a' });
  for (let i = 0; i < 6; i++) { const yy = 520 - i * 70; ln(c, lerp(370, 470, (560 - yy) / 410), yy, lerp(520, 560, (560 - yy) / 410), yy, { w: 5, col: '#3a3a3a', passes: 1 }); }
  // man (large, from below)
  const stop = 21.5;
  const turn = ease(stop + 0.3, stop + 2.0, s);
  const fid = s < stop ? Math.sin(s * 5) * 10 : 0;
  person(c, 520, 700, 620, { coat: '#5b5550', hair: 'grey', pose: 'reachUp', reachDx: fid - turn * 30, reachDy: 80 + turn * 60, seed: 21, view: 'front' });
  // stage light spill from below right (the singing)
  glow(c, 1100, 520, 520, '#fff0d0', 0.18 + 0.1 * Math.sin(s * 0.7));
  camReset(c);
}
function sStudioMed(c, u, d, s) {
  fillAll(c, '#3a3a3a');
  cam(c, 640, 268, 1 + u * 0.006);
  c.fillStyle = grad(c, 0, 0, 0, 536, [[0, '#2e2e30'], [0.62, '#454444'], [0.63, '#66635f'], [1, '#77746f']]);
  c.fillRect(-50, -50, IW + 100, 640);
  shape(c, rect(250, 30, 780, 270), '#38393d', { la: 0.4 });
  txt(c, '对 面', 640, 150, 140, '#4f5258', { weight: 600 });
  glow(c, 600, 260, 420, '#fff4dc', 0.18);
  // stand + guitar (right)
  ln(c, 905, 536, 888, 380, { w: 3, col: '#333' }); ln(c, 905, 536, 930, 380, { w: 3, col: '#333' });
  guitar(c, 905, 300, 560, -Math.PI / 2 + 0.05, 0, 0);
  shape(c, rect(950, 415, 120, 40), '#f2eee4', { la: 0.5, seed: 311 });
  txt(c, '展品 · 请勿触碰', 1010, 435, 16, '#333');
  // ALPHA seated, larger, looking toward the guitar
  const look = ease(-4.6, -3.2, s);
  const reach = ease(-2.2, -1.3, s);
  alpha(c, 560, 720, 560, { pose: 'sit', seat: 560, arms: reach > 0 ? 'reach' : 'lap', reach, eye: 0.55, look: look * 1.2, tilt: look * 0.05, headDx: look * 0.01 });
  // 小鹿 crouching at left
  person(c, 230, 560, 400, { sit: true, seat: 500, coat: '#6a7078', hair: 'pony', hairC: '#2a2420', pose: 'sitHands', seed: 31 });
  camReset(c);
}
function sPluck(c, u, d, s) {
  fillAll(c, '#2a2a2a');
  // strings close-up over the yellow body
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#1f1f20'], [1, '#2f2f30']]); c.fillRect(0, 0, IW, IH);
  cam(c, 640, 268, 1 + u * 0.02);
  shape(c, [[-60, 330], [520, 300], [700, 430], [640, 620], [-60, 620]], YEL, { seed: 321 });
  wash(c, ell(330, 430, 120, 120, 30), SIL, 0.95); sk(c, ell(330, 430, 120, 120, 30), { closed: true, w: 2 });
  for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2; ln(c, 330 + Math.cos(a) * 50, 430 + Math.sin(a) * 50, 330 + Math.cos(a) * 112, 430 + Math.sin(a) * 112, { w: 1.2, a: 0.5 }); }
  shape(c, rect(560, 200, 760, 70), '#2c2f36', { seed: 322 });
  const pl = s + 0.75;  // pluck at s=-0.75
  for (let i = 0; i < 6; i++) {
    const yy = 214 + i * 9 + (i > 2 ? 60 : 0) * 0;
    const vib = i === 2 && pl > 0 ? Math.sin(pl * 160) * 5 * Math.exp(-pl * 2.4) : 0;
    const pts = [];
    for (let k = 0; k <= 20; k++) { const xx = -40 + k * 70; pts.push([xx, yy + 90 + Math.sin(k / 20 * Math.PI) * vib]); }
    sk(c, pts, { w: 1.4, col: '#ececec', a: 0.85, passes: 1, j: 0.15 });
  }
  // metal fingers
  const fx = lerp(900, 640, ease(-1.2, -0.85, s)), fy = lerp(150, 225, ease(-1.2, -0.8, s)) - (pl > 0 ? easeOut(0, 0.25, pl) * 50 : 0);
  for (let i = 0; i < 4; i++) {
    const ox = fx + i * 46, oy = fy - i * 10;
    sk(c, [[ox + 80, oy - 230], [ox + 30, oy - 90], [ox, oy]], { w: 30, col: SIL, a: 0.98, passes: 1 });
    wash(c, ell(ox, oy, 17, 14, 12), YEL, 0.98);
    wash(c, ell(ox + 30, oy - 90, 13, 13, 12), SIL_D, 0.95);
  }
  shape(c, [[fx + 60, fy - 340], [fx + 330, fy - 360], [fx + 300, fy - 200], [fx + 60, fy - 200]], TEAL, { seed: 323 });
  camReset(c);
}
// cue card close-up: 「你的悲伤是真的吗？」 — the second time a tear falls on it
function sCard(c, u, d, s) {
  const tear = s > 30;
  fillAll(c, '#4a4846');
  cam(c, 640, 268, 1 + u * 0.012);
  c.fillStyle = grad(c, 0, 0, IW, IH, [[0, '#3d3b39'], [1, '#55524f']]); c.fillRect(-50, -50, IW + 100, 640);
  // desk
  shape(c, [[-50, 420], [1330, 380], [1330, 600], [-50, 600]], '#2f2c2a', { seed: 331 });
  // card
  const tremble = tear ? Math.sin(s * 23) * 0.6 : 0;
  c.save(); c.translate(640 + tremble, 280); c.rotate(-0.04);
  shape(c, rect(-260, -150, 520, 300), '#f6f3ec', { seed: 332, la: 0.5 });
  ln(c, -230, -95, 230, -95, { w: 1, col: '#c55', a: 0.4, passes: 1 });
  txt(c, 'Q1', -215, -120, 22, '#888', { align: 'left', weight: 600 });
  txt(c, '你的悲伤是真的吗？', 0, 0, 46, '#1f1d1b', { weight: 600 });
  txt(c, '（追问：被抵制时，你有什么感受）', 0, 70, 20, '#77716a');
  if (tear) {
    const land = 35.7;
    if (s > land) {
      const k = easeOut(land, land + 2.2, s);
      c.save();
      c.beginPath(); c.arc(-60, 4, 16 + k * 44, 0, Math.PI * 2); c.clip();
      c.fillStyle = '#f2efe8'; c.fillRect(-140, -70, 200, 140);
      txt(c, '你的悲伤是真的吗？', 0, 0, 46, '#3e3a37', { weight: 600, blur: 1 + k * 4, a: 0.85 });
      c.restore();
      c.save(); c.globalAlpha = 0.25 * k; c.strokeStyle = '#8a8580'; c.lineWidth = 1.5;
      c.beginPath(); c.arc(-60, 4, 16 + k * 44, 0, Math.PI * 2); c.stroke(); c.restore();
    }
  }
  c.restore();
  // hands holding the card
  for (const sgn of [-1, 1]) {
    const hx = 640 + sgn * 255, hy = 330;
    shape(c, ell(hx, hy, 46, 60, 18, sgn * 0.3), SKIN, { seed: 340 + sgn });
    sk(c, [[hx - sgn * 20, hy - 40], [hx - sgn * 52, hy - 70]], { w: 22, col: SKIN, a: 1, passes: 1 });
    shape(c, [[hx + sgn * 10, hy + 30], [hx + sgn * 120, hy + 120], [hx + sgn * 160, hy + 300], [hx + sgn * 40, hy + 300]], '#2b2826', { seed: 345 + sgn });
  }
  if (tear) {
    const t0 = 35.1, land = 35.7;
    if (s > t0 && s < land) {
      const k = easeIn(t0, land, s);
      const ty = lerp(-30, 284, k);
      wash(c, [[580, ty - 22], [586, ty], [580, ty + 8], [574, ty]], '#cfe0ec', 0.8);
      glow(c, 580, ty, 14, '#ffffff', 0.6);
    }
  }
  camReset(c);
}
function sAlphaClose(c, u, d, s) {
  fillAll(c, '#2f2f30');
  const z = lerp(1.0, 1.25, ease(0, d, u));
  cam(c, 640, 250, z);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#2a2a2c'], [1, '#3e3d3c']]); c.fillRect(-100, -100, IW + 200, 800);
  glow(c, 640, 120, 500, '#fff4dc', 0.2);
  alpha(c, 640, 1400, 1500, { pose: 'sit', seat: 900, eye: 0.95, mouth: (Math.sin(s * 7) * 0.5 + 0.5) * 0.6, look: -0.2 });
  camReset(c);
}

// ---------- MEMORY: the lab (warm sepia)
function labRoom(c, s, o = {}) {
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#3a3128'], [1, '#4a4036']]); c.fillRect(-100, -100, IW + 200, 800);
  // window with the railway outside
  const wx = 120, wy = 70, ww = 380, wh = 220;
  c.fillStyle = grad(c, 0, wy, 0, wy + wh, [[0, '#1d2230'], [1, '#2e3442']]); c.fillRect(wx, wy, ww, wh);
  ln(c, wx, wy + wh * 0.78, wx + ww, wy + wh * 0.78, { w: 1.2, col: '#7a7f88', a: 0.7 });
  ln(c, wx, wy + wh * 0.84, wx + ww, wy + wh * 0.84, { w: 1.2, col: '#7a7f88', a: 0.7 });
  if (o.trainT !== undefined && o.trainT > 0 && o.trainT < 1) {
    c.save(); c.beginPath(); c.rect(wx, wy, ww, wh); c.clip();
    const tx = lerp(wx + ww + 40, wx - 1400, o.trainT);
    for (let k = 0; k < 4; k++) {
      const cx0 = tx + k * 330;
      wash(c, rect(cx0, wy + wh * 0.5, 320, wh * 0.28), '#14171d', 0.95);
      for (let w = 0; w < 7; w++) { wash(c, rect(cx0 + 20 + w * 42, wy + wh * 0.55, 26, 14), '#f5d891', 0.9); }
    }
    c.restore();
    glow(c, wx + ww / 2, wy + wh * 0.6, 260, '#f5d891', 0.12);
  }
  // window frame
  sk(c, rect(wx, wy, ww, wh), { closed: true, w: 5, col: '#2a221b', a: 0.95 });
  ln(c, wx + ww / 2, wy, wx + ww / 2, wy + wh, { w: 4, col: '#2a221b' });
  ln(c, wx, wy + wh / 2, wx + ww, wy + wh / 2, { w: 4, col: '#2a221b' });
  // blueprint turnaround pinned on the wall
  shape(c, rect(610, 60, 260, 150), '#d9d2c2', { seed: 401, la: 0.5 });
  for (let i = 0; i < 3; i++) {
    const bx = 660 + i * 80;
    sk(c, ell(bx, 92, 9, 10, 10), { closed: true, w: 0.9, a: 0.6, passes: 1 });
    sk(c, [[bx - 14, 104], [bx + 14, 104], [bx + 9, 150], [bx - 9, 150]], { closed: true, w: 0.9, a: 0.6, passes: 1 });
    ln(c, bx - 6, 150, bx - 9, 195, { w: 0.9, a: 0.6, passes: 1 }); ln(c, bx + 6, 150, bx + 9, 195, { w: 0.9, a: 0.6, passes: 1 });
  }
  txt(c, 'ALPHA-01', 860, 200, 11, '#6b6255', { align: 'right' });
  // workbench
  shape(c, [[560, 400], [1240, 400], [1240, 430], [560, 430]], '#5a4a3a', { seed: 402 });
  ln(c, 590, 430, 590, 536, { w: 5, col: '#3a2f25' }); ln(c, 1210, 430, 1210, 536, { w: 5, col: '#3a2f25' });
  // lamp
  ln(c, 1120, 400, 1080, 300, { w: 3, col: '#2a221b' }); ln(c, 1080, 300, 1010, 270, { w: 3, col: '#2a221b' });
  shape(c, [[990, 250], [1040, 262], [1030, 300], [980, 290]], '#3a2f25', { seed: 403 });
  glow(c, 960, 360, 420, '#ffd9a0', 0.38);
  // cables
  sk(c, [[700, 400], [760, 470], [880, 450], [980, 500]], { w: 2, col: '#2a2420', a: 0.8 });
}
function sLab(c, u, d, s) {
  fillAll(c, '#3a3128');
  cam(c, 640 + u * 3, 268, 1.02 + u * 0.004);
  labRoom(c, s, { trainT: (s - 41.4) / 4.6 });
  const boot = ease(44.6, 45.6, s);
  alpha(c, 830, 470, 300, { pose: 'sit', seat: 400, arms: 'lap', eye: boot * (0.7 + 0.3 * Math.sin(Math.min(1, (s - 44.6)) * 20) * (1 - boot)) + boot * 0.3, look: 0.3 });
  person(c, 1050, 520, 280, { coat: '#6d6256', hair: 'grey', glasses: true, hunch: 0.8, dir: -1, pose: s > 45.5 ? 'hold' : 'down', seed: 41 });
  camReset(c);
  tint(c, '#f2d7b0', 0.55);
}
function sLesson(c, u, d, s) {
  fillAll(c, '#3a3128');
  cam(c, 640, 268, 1.05 + u * 0.01);
  c.fillStyle = grad(c, 0, 0, IW, 0, [[0, '#2e261f'], [1, '#4a3d30']]); c.fillRect(-50, -50, IW + 100, 640);
  // cassette recorder in the background (soft)
  c.save(); c.filter = 'blur(3px)';
  shape(c, rect(880, 90, 300, 150), '#5b4c3c', { line: false });
  for (const rx of [960, 1100]) {
    wash(c, ell(rx, 165, 34, 34, 16), '#2a221b', 0.9);
    const a = s * 3;
    for (let i = 0; i < 3; i++) ln(c, rx, 165, rx + Math.cos(a + i * 2.1) * 30, 165 + Math.sin(a + i * 2.1) * 30, { w: 3, col: '#8a7a66', passes: 1 });
  }
  c.restore();
  glow(c, 400, 200, 500, '#ffd9a0', 0.3);
  // guitar neck diagonal
  c.save(); c.translate(640, 300); c.rotate(-0.22);
  shape(c, rect(-700, -55, 1400, 110), '#2c2f36', { seed: 411 });
  for (let i = 0; i < 12; i++) ln(c, -650 + i * 120, -55, -650 + i * 120, 55, { w: 3, col: SIL_L, a: 0.7, passes: 1 });
  for (let i = 0; i < 6; i++) ln(c, -700, -45 + i * 18, 700, -45 + i * 18, { w: 1.4, col: '#e5e5e5', a: 0.75, passes: 1, j: 0.2 });
  // metal fingers pressing
  const press = Math.sin(s * 3) * 4;
  for (let i = 0; i < 3; i++) {
    const fx = -120 + i * 120, fy = -10 + i * 14 + press;
    sk(c, [[fx - 40, -260], [fx - 10, -110], [fx, fy]], { w: 40, col: SIL, a: 0.98, passes: 1 });
    wash(c, ell(fx, fy, 22, 18, 12), YEL, 0.98);
    wash(c, ell(fx - 10, -110, 16, 16, 12), SIL_D, 0.95);
  }
  shape(c, [[-260, -420], [220, -420], [180, -240], [-210, -240]], TEAL, { seed: 412 });
  // the old man's hand resting over hers, guiding
  hand(c, -40, -250 + press * 0.5, 1.15, 1.25, { sleeve: '#6d6256', old: true, seed: 413, curl: 0.6 });
  c.restore();
  camReset(c);
  tint(c, '#f2d7b0', 0.55);
}
function sMall(c, u, d, s) {
  fillAll(c, '#cfc6b5');
  cam(c, 640, 268, 1.0 + u * 0.004);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#d8cfbe'], [0.6, '#cbc1af'], [1, '#b7ad9b']]); c.fillRect(-50, -50, IW + 100, 640);
  // columns + escalator
  for (const px of [80, 1180]) { shape(c, rect(px - 30, -20, 60, 420), '#c2b8a6', { seed: px }); }
  sk(c, [[860, 60], [1150, 300]], { w: 2, a: 0.5 }); sk(c, [[900, 60], [1190, 300]], { w: 2, a: 0.5 });
  for (let i = 0; i < 3; i++) ln(c, 0, 40 + i * 60, 300, 40 + i * 60, { w: 1, a: 0.3 });
  // stage + banner
  shape(c, rect(420, 330, 440, 46), '#a99e8b', { seed: 501 });
  shape(c, rect(470, 120, 340, 90), '#e9e1cf', { seed: 502, la: 0.5 });
  txt(c, '会唱歌的机器人', 640, 155, 34, '#5a4e3e', { weight: 600 });
  txt(c, 'ALPHA · 周末限时演出', 640, 192, 14, '#7b6f5e', { spacing: 3 });
  alpha(c, 640, 335, 170, { pose: 'sit', seat: 290, guitar: true, strum: s, eye: 0.9, mouth: (Math.sin(s * 7) * 0.5 + 0.5) * 0.7 });
  // kids gathering
  for (let i = 0; i < 6; i++) {
    const kx = 500 + i * 55 + Math.sin(i * 3) * 10;
    person(c, kx, 450 + (i % 2) * 14, 110 + (i % 3) * 8, { view: 'back', coat: ['#b4a48c', '#9a8c78', '#c1b199'][i % 3], hair: i % 2 ? 'pony' : 'short', seed: 510 + i, pose: i === 2 ? 'wave' : 'down', t: s + i });
  }
  // time-lapse crowd streaming past (ghosts)
  for (let i = 0; i < 14; i++) {
    const dir = i % 2 ? 1 : -1;
    const speed = 380 + R(i) * 260;
    let x = (R(i + 9) * 1600 + dir * s * speed) % 1700; if (x < 0) x += 1700; x -= 200;
    person(c, x, 500 + R(i + 3) * 30, 220 + R(i + 4) * 30, { view: 'side', dir, walk: true, phase: s * 9 + i, coat: '#9d9483', alpha: 0.18, seed: 520 + i });
  }
  // the session musician who stops (right)
  if (s > 60.6) {
    const a = ease(60.6, 61.6, s);
    person(c, 1040, 505, 240, { view: 'front', coat: '#4f4b45', hair: 'short', seed: 530, alpha: a });
    shape(c, [[1062, 330], [1095, 330], [1090, 470], [1068, 470]], '#2e2b28', { seed: 531, fa: a, la: a * 0.7 });
  }
  camReset(c);
  tint(c, '#f2d7b0', 0.45);
}
// ---------- COLD
function sPhones(c, u, d, s) {
  fillAll(c, '#0d0f13');
  cam(c, 640 + u * 10, 268, 1.05);
  glow(c, 640, 120, 380, '#cfd8ff', 0.12);
  alpha(c, 640, 210, 110, { pose: 'sit', seat: 180, guitar: true, strum: s, eye: 0.8, alpha: 0.85 });
  for (let row = 0; row < 3; row++) {
    for (let i = 0; i < 12; i++) {
      const x = -40 + i * 120 + (row % 2) * 60 + Math.sin(i * 7 + row) * 14;
      const y = 380 + row * 70;
      const sc = 1 + row * 0.25;
      wash(c, ell(x, y, 34 * sc, 40 * sc, 16), '#08090c', 0.98);
      wash(c, [[x - 70 * sc, y + 30 * sc], [x + 70 * sc, y + 30 * sc], [x + 90 * sc, y + 200], [x - 90 * sc, y + 200]], '#08090c', 0.98);
      if (R(i * 3 + row * 17) > 0.25) {
        const px = x + 20 * sc, py = y - 60 * sc;
        sk(c, [[x + 40 * sc, y + 20 * sc], [px, py + 20 * sc]], { w: 9 * sc, col: '#0c0d10', a: 0.95, passes: 1 });
        wash(c, rect(px - 14 * sc, py - 24 * sc, 28 * sc, 46 * sc), '#9fc1e6', 0.95);
        wash(c, ell(px, py, 4 * sc, 6 * sc, 8), TEAL, 0.8);
        glow(c, px, py, 60 * sc, '#8fb6e8', 0.22);
      }
    }
  }
  camReset(c);
}
function sCollage(c, u, d, s) {
  fillAll(c, '#57544f');
  cam(c, 640, 268, 1.04 + u * 0.012);
  c.fillStyle = '#4a4743'; c.fillRect(-50, -50, IW + 100, 640);
  const papers = [
    [330, 170, -0.08, 'AI 作曲全面普及', '录音棚迎来倒闭潮'],
    [900, 150, 0.06, '又一支乐团宣布解散', '“我们输给了一个按钮”'],
    [420, 400, 0.04, 'AI 歌手', '该不该有舞台？'],
    [960, 400, -0.05, '学了十六年琴', '月收入不到三千'],
    [660, 290, 0.01, '抵制 AI 歌手', '联名信已超过一万人'],
  ];
  papers.forEach((p, i) => {
    const appear = ease(i * 0.45, i * 0.45 + 0.4, u);
    if (appear <= 0) return;
    c.save(); c.translate(p[0], p[1] + (1 - appear) * 20); c.rotate(p[2]); c.globalAlpha = appear;
    shape(c, rect(-230, -100, 460, 200), '#e4ded1', { seed: 600 + i, la: 0.5 });
    txt(c, p[3], 0, -38, 34, '#1d1b19', { weight: 600 });
    txt(c, p[4], 0, 14, 22, '#3a3632');
    for (let k = 0; k < 3; k++) ln(c, -200, 50 + k * 14, 200, 50 + k * 14, { w: 0.8, a: 0.3, passes: 1 });
    c.restore();
  });
  camReset(c);
  tint(c, '#c9d2dc', 0.35);
}
function sSubway(c, u, d, s) {
  fillAll(c, '#2a2d31');
  cam(c, 640 + u * 6, 268, 1.02);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#23262a'], [0.7, '#34373b'], [1, '#45474a']]); c.fillRect(-50, -50, IW + 100, 640);
  for (let i = 0; i < 20; i++) ln(c, i * 70, 380, i * 70 - 30, 536, { w: 0.8, a: 0.25, passes: 1 });
  // the AI ad screen
  wash(c, rect(560, 40, 660, 270), '#dbe9f7', 0.95);
  glow(c, 890, 175, 520, '#cfe2ff', 0.35);
  txt(c, 'AI MUSIC', 890, 120, 58, '#2b3d55', { weight: 600, spacing: 6 });
  txt(c, '一秒生成你的专属歌手', 890, 190, 36, '#2b3d55', { weight: 600 });
  txt(c, '不疲倦 · 不跑调 · 不要钱', 890, 245, 20, '#4b5d75', { spacing: 4 });
  sk(c, rect(560, 40, 660, 270), { closed: true, w: 3 });
  // the musician busking under it
  person(c, 820, 470, 230, { sit: true, seat: 420, coat: '#4f4b45', hair: 'short', pose: 'sitHands', seed: 530 });
  shape(c, [[740, 470], [800, 440], [870, 440], [900, 470]], '#2b2826', { seed: 701 });
  wash(c, [[700, 500], [930, 500], [915, 520], [715, 520]], '#3a2f25', 0.9);
  // commuters (ghosted)
  for (let i = 0; i < 8; i++) {
    const dir = i % 2 ? 1 : -1;
    let x = (R(i + 30) * 1500 + dir * u * (300 + R(i) * 200)) % 1600; if (x < 0) x += 1600; x -= 160;
    person(c, x, 520 + R(i) * 10, 260, { view: 'side', dir, walk: true, phase: u * 9 + i, coat: '#5a5a5c', alpha: 0.35, seed: 710 + i });
  }
  camReset(c);
  tint(c, '#c9d2dc', 0.35);
}
function sFridge(c, u, d, s) {
  fillAll(c, '#1d1c1b');
  cam(c, 640, 268, 1.02 + u * 0.02);
  shape(c, rect(560, 40, 280, 480), '#d8d6d1', { seed: 801 });
  c.save(); c.globalAlpha = 1; c.fillStyle = '#fbf6e8'; c.fillRect(578, 60, 244, 300); c.restore();
  for (let i = 0; i < 3; i++) ln(c, 578, 140 + i * 80, 822, 140 + i * 80, { w: 1.5, a: 0.5 });
  glow(c, 700, 220, 520, '#fff2d0', 0.5);
  wash(c, ell(650, 200, 20, 8, 10), '#888', 0.9);
  // door open
  shape(c, [[840, 40], [990, 70], [990, 500], [840, 520]], '#c9c6c0', { seed: 802 });
  person(c, 450, 536, 420, { coat: '#6d6256', hair: 'grey', glasses: true, pose: 'hold', seed: 41, hunch: 0.6 });
  // keys in his hand
  const kx = 450, ky = 536 - 420 * 0.82 + 420 * 0.14 * 1.15;
  sk(c, ell(kx, ky, 10, 10, 10), { closed: true, w: 2, col: '#b8a46a', a: 0.95 });
  ln(c, kx + 6, ky + 6, kx + 26, ky + 20, { w: 3, col: '#b8a46a', a: 0.95 });
  camReset(c);
  tint(c, '#cfd3d8', 0.25);
}
function sHandNote(c, u, d, s) {
  fillAll(c, '#2a2826');
  cam(c, 640, 268, 1.03 + u * 0.02);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#2a2826'], [1, '#3a3632']]); c.fillRect(-50, -50, IW + 100, 640);
  const reveal = ease(0.1, 1.4, u);
  hand(c, 250, 330, 2.6, -0.12, {
    sleeve: '#6d6256', old: true, seed: 811,
    onBack: (h) => {
      h.save(); h.beginPath(); h.rect(10, -70, 130 * reveal, 140); h.clip();
      txt(h, '记得给', 66, -20, 22, '#24304a', { weight: 600, a: 0.85 });
      txt(h, 'ALPHA 充电', 66, 16, 19, '#24304a', { weight: 600, a: 0.85 });
      h.restore();
    },
  });
  camReset(c);
  tint(c, '#cfd3d8', 0.2);
}
function sLabNight(c, u, d, s) {
  fillAll(c, '#2a241e');
  cam(c, 640, 268, 1.0 + u * 0.006);
  labRoom(c, s);
  // darken the room except the lamp
  tint(c, '#7a6a5a', 0.55);
  glow(c, 820, 330, 380, '#ffd9a0', 0.35);
  alpha(c, 700, 470, 300, { pose: 'sit', seat: 400, arms: s > 90.5 ? 'hold' : 'lap', eye: 0.75, look: 0.6, tilt: 0.05 });
  person(c, 960, 520, 280, { sit: true, seat: 440, coat: '#6d6256', hair: 'grey', glasses: true, hunch: 1, dir: -1, pose: s > 89.8 ? 'hold' : 'sitHands', seed: 41 });
  // candy changes hands
  const k = ease(89.8, 91.0, s);
  if (s > 89.8) {
    const cx = lerp(960, 702, k), cy = lerp(420, 400, k) - Math.sin(k * Math.PI) * 30;
    wash(c, ell(cx, cy, 9, 6, 10), YEL, 0.98);
    ln(c, cx - 9, cy, cx - 16, cy - 5, { w: 2, col: YEL_D }); ln(c, cx + 9, cy, cx + 16, cy + 5, { w: 2, col: YEL_D });
  }
  camReset(c);
  tint(c, '#f2d7b0', 0.45);
}
// ---------- BOYCOTT (interlude, quiet, grey, static)
function rain(c, s, n = 160, a = 0.25, speed = 900) {
  c.save(); c.strokeStyle = `rgba(220,225,232,${a})`; c.lineWidth = 1;
  for (let i = 0; i < n; i++) {
    const x = R(i) * (IW + 200) - 100;
    const y = ((R(i + 5) * 700 + s * speed * (0.8 + R(i + 9) * 0.4)) % 700) - 80;
    c.beginPath(); c.moveTo(x, y); c.lineTo(x - 4, y + 22); c.stroke();
  }
  c.restore();
}
function sProtest(c, u, d, s) {
  fillAll(c, '#1f2124');
  cam(c, 640, 268, 1.0);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#1a1c1f'], [0.68, '#2a2c30'], [1, '#3a3c40']]); c.fillRect(-50, -50, IW + 100, 640);
  // livehouse door + dead neon sign + torn poster
  shape(c, rect(840, 90, 300, 300), '#25272a', { seed: 901 });
  txt(c, 'LIVE HOUSE', 990, 60, 30, '#6a6d72', { spacing: 6 });
  shape(c, rect(890, 150, 150, 210), '#cfcac0', { seed: 902, la: 0.5 });
  alpha(c, 965, 345, 150, { arms: 'lap', eye: 0, alpha: 0.6 });
  c.save(); c.globalAlpha = 0.85; c.fillStyle = '#2a2b2e';
  c.beginPath(); c.moveTo(965, 150); c.lineTo(1040, 150); c.lineTo(1040, 360); c.lineTo(1000, 300); c.lineTo(1015, 240); c.closePath(); c.fill(); c.restore();
  glow(c, 640, 0, 500, '#b9c4d2', 0.12);
  // protesters with signs
  const signs = ['人类的歌\n由人类来唱', '抵制\nAI 歌手', '还我们\n饭碗', '舞台\n还给人', '机器\n没有心'];
  for (let i = 0; i < 5; i++) {
    const x = 120 + i * 150, h = 250 + (i % 2) * 20;
    person(c, x, 500 + (i % 2) * 12, h, { view: 'front', coat: ['#3c3e42', '#4a4642', '#35373b'][i % 3], hair: i === 2 ? 'cap' : (i % 2 ? 'bob' : 'short'), sign: signs[i], signW: 130, seed: 910 + i });
  }
  // the session musician among them (with guitar case)
  person(c, 760, 510, 260, { coat: '#4f4b45', hair: 'short', seed: 530 });
  shape(c, [[782, 330], [814, 330], [810, 480], [786, 480]], '#2e2b28', { seed: 531 });
  // puddle reflections
  c.save(); c.globalAlpha = 0.15; c.scale(1, -0.3); c.translate(0, -2300); c.restore();
  rain(c, s, 220, 0.28);
  camReset(c);
}
function sNotice(c, u, d, s) {
  fillAll(c, '#3a3b3d');
  cam(c, 640, 268, 1.02 + u * 0.015);
  shape(c, rect(330, -20, 620, 600), '#eeebe4', { seed: 921, la: 0.5 });
  txt(c, '项目终止及资产处置通知', 640, 70, 34, '#1d1b19', { weight: 600 });
  const lines = ['经公司管理层研究决定：', '自即日起终止 ALPHA 项目全部商业演出及研发，', '相关设备按报废资产处置。', '研发负责人：周 ×× ，劳动合同同步解除。'];
  lines.forEach((l, i) => txt(c, l, 380, 150 + i * 46, 22, '#333', { align: 'left' }));
  c.save(); c.globalAlpha = 0.65; c.translate(820, 400); c.rotate(-0.2);
  sk(c, ell(0, 0, 70, 70, 30), { closed: true, w: 4, col: '#a5473d', a: 0.8 });
  txt(c, '已 处 置', 0, 0, 26, '#a5473d', { weight: 600 });
  c.restore();
  camReset(c);
  tint(c, '#cfd3d8', 0.25);
}
function warehouse(c) {
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#17181a'], [1, '#2a2b2d']]); c.fillRect(-50, -50, IW + 100, 640);
  for (let i = 0; i < 4; i++) {
    const x = 60 + i * 300;
    if (i === 2) continue;
    sk(c, rect(x, 120, 200, 360), { closed: true, w: 2, col: '#3a3b3d', a: 0.9 });
    for (let k = 0; k < 4; k++) { ln(c, x, 200 + k * 80, x + 200, 200 + k * 80, { w: 2, col: '#3a3b3d' }); wash(c, rect(x + 20, 160 + k * 80, 70, 38), '#2f3032', 0.9); }
  }
  // high window light shaft
  c.save(); c.globalCompositeOperation = 'screen';
  c.fillStyle = grad(c, 900, 0, 650, 500, [[0, 'rgba(190,200,215,0.22)'], [1, 'rgba(190,200,215,0)']]);
  c.beginPath(); c.moveTo(860, 0); c.lineTo(960, 0); c.lineTo(760, 520); c.lineTo(560, 520); c.closePath(); c.fill(); c.restore();
}
function tarpShape(c, x, y, S, lift = 0) {
  const top = y - S * 1.02 + lift * 40;
  const pts = [[x - S * 0.3, y], [x - S * 0.24, y - S * 0.5], [x - S * 0.2, top + S * 0.2], [x - S * 0.08, top], [x + S * 0.1, top + 4], [x + S * 0.2, top + S * 0.22], [x + S * 0.26, y - S * 0.45], [x + S * 0.32, y]];
  shape(c, pts, '#77797c', { seed: 931, la: 0.7 });
  for (let i = 0; i < 6; i++) sk(c, [[x - S * 0.15 + i * S * 0.06, top + S * 0.15], [x - S * 0.22 + i * S * 0.08, y]], { w: 1, a: 0.35, passes: 1 });
  sk(c, [[x - S * 0.12, y - S * 0.12], [x + S * 0.15, y - S * 0.12]], { w: 2, col: '#555', a: 0.8 });
  wash(c, rect(x - S * 0.04, y - S * 0.38, S * 0.08, S * 0.05), '#e8e3d6', 0.95);
  txt(c, 'ZC-0417', x, y - S * 0.355, S * 0.018, '#333');
}
function sTarp(c, u, d, s) {
  fillAll(c, '#17181a');
  cam(c, 640, 268, 1.02 + u * 0.004);
  warehouse(c);
  // dust motes
  for (let i = 0; i < 40; i++) { const x = 600 + R(i) * 300 + Math.sin(s * 0.3 + i) * 20, y = (R(i + 2) * 500 + s * 6) % 520; wash(c, ell(x, y, 1.6, 1.6, 6), '#d8dce2', 0.4); }
  tarpShape(c, 640, 480, 380);
  const e = 1 - ease(106, 110.5, s);
  if (e > 0.01) glow(c, 640, 480 - 380 * 0.86, 40, EYE, 0.6 * e * (0.8 + 0.2 * Math.sin(s * 9)));
  camReset(c);
}
function sFlashlight(c, u, d, s) {
  fillAll(c, '#0e0f10');
  cam(c, 640, 268, 1.0);
  warehouse(c);
  tint(c, '#000', 0.5, 'source-over');
  const lift = ease(113.8, 115.6, s);
  if (lift < 0.98) { c.save(); c.globalAlpha = 1 - lift; tarpShape(c, 640 - lift * 160, 480, 380, lift); c.restore(); }
  if (lift > 0.3) alpha(c, 640, 480, 380, { arms: 'lap', alpha: ease(0.3, 0.9, lift), eye: s > 115.8 ? (0.4 + 0.4 * (Math.sin((s - 115.8) * 30) > 0 ? 1 : 0.3)) * ease(115.8, 116.6, s) : 0 });
  person(c, 380, 500, 300, { coat: '#3d3833', hair: 'grey', glasses: true, hunch: 0.8, pose: 'hold', seed: 41 });
  // flashlight beam sweeping toward ALPHA
  const ang = lerp(-0.5, 0.05, ease(112, 113.6, s));
  c.save(); c.globalCompositeOperation = 'screen';
  c.translate(400, 330); c.rotate(ang);
  c.fillStyle = grad(c, 0, 0, 560, 0, [[0, 'rgba(255,240,205,0.55)'], [1, 'rgba(255,240,205,0)']]);
  c.beginPath(); c.moveTo(0, 0); c.lineTo(600, -110); c.lineTo(600, 110); c.closePath(); c.fill(); c.restore();
  camReset(c);
}
function sDawnWalk(c, u, d, s) {
  fillAll(c, '#c9c6c0');
  cam(c, 640, 268, 1.0 + u * 0.004);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#a9adb4'], [0.45, '#d9d2c6'], [0.55, '#e3d9c8'], [1, '#8f8e8b']]); c.fillRect(-50, -50, IW + 100, 640);
  glow(c, 980, 250, 260, '#fbe9cf', 0.6);
  // distant hills/fog
  wash(c, [[-50, 260], [200, 230], [420, 250], [700, 225], [1000, 245], [1330, 230], [1330, 300], [-50, 300]], '#9fa1a3', 0.45);
  // gravel bed + a single track receding to a vanishing point
  const vx = 760, vy = 262;
  wash(c, [[vx - 6, vy], [vx + 6, vy], [vx + 420, 560], [vx - 420, 560]], '#8b867e', 0.6);
  for (const off of [-1, 1]) ln(c, vx + off * 2, vy, vx + off * 230, 560, { w: 2.4, col: '#3e3c3a', a: 0.9 });
  for (let i = 1; i < 30; i++) {
    const k = Math.pow(i / 30, 2.0);
    const y = lerp(vy, 560, k), hw = lerp(4, 300, k);
    ln(c, vx - hw, y, vx + hw, y, { w: 0.8 + k * 4, col: '#5a554e', a: 0.65, passes: 1 });
  }
  // telegraph poles
  for (let i = 1; i < 8; i++) {
    const k = Math.pow(i / 8, 1.8);
    const x = lerp(vx - 30, -80, k), y = lerp(vy, 520, k), h = lerp(10, 330, k);
    ln(c, x, y, x, y - h, { w: 1 + k * 4, col: '#4a4743', a: 0.9 });
    ln(c, x - h * 0.12, y - h * 0.92, x + h * 0.12, y - h * 0.92, { w: 1 + k * 2, col: '#4a4743', a: 0.9 });
  }
  // the little station far away
  shape(c, rect(vx + 40, vy - 18, 50, 18), '#6a655e', { la: 0.6 });
  // two figures walking away along the tracks (back view), half a step apart
  const prog = ease(117, 124.5, s);
  const k = lerp(0.36, 0.24, prog);
  const y = lerp(vy, 560, k), sc = lerp(12, 330, k);
  const xc = vx;
  person(c, xc - sc * 0.18, y, sc * 0.95, { view: 'back', coat: '#4d4741', hair: 'grey', walk: true, phase: s * 6, hunch: 0.6, seed: 41 });
  wash(c, rect(xc - sc * 0.32, y - sc * 0.2, sc * 0.1, sc * 0.16), '#3a332c', 0.9);
  alpha(c, xc + sc * 0.2, y, sc, { back: true, walk: true, phase: s * 6 + 1, eye: 0 });
  wash(c, [[xc + sc * 0.2, y - sc * 0.8], [xc + sc * 0.28, y - sc * 0.78], [xc + sc * 0.12, y - sc * 0.35], [xc + sc * 0.04, y - sc * 0.38]], YEL_D, 0.8);
  // mist
  c.save(); c.globalAlpha = 0.25; c.fillStyle = '#ece6dc'; c.fillRect(-50, 270, IW + 100, 60); c.restore();
  camReset(c);
}
// ---------- THE PLATFORM (long take, fixed camera)
function platformBG(c, sky) {
  c.fillStyle = grad(c, 0, 0, 0, 300, sky); c.fillRect(-50, -50, IW + 100, 360);
  wash(c, [[-50, 250], [300, 238], [700, 248], [1000, 236], [1330, 246], [1330, 300], [-50, 300]], '#8d8f90', 0.4);
  // tracks
  c.fillStyle = '#585654'; c.fillRect(-50, 300, IW + 100, 62);
  ln(c, -50, 320, IW + 50, 320, { w: 2.5, col: '#2c2c2c' }); ln(c, -50, 352, IW + 50, 352, { w: 2.5, col: '#2c2c2c' });
  // platform
  c.fillStyle = grad(c, 0, 362, 0, 536, [[0, '#9a958c'], [1, '#7d7870']]); c.fillRect(-50, 362, IW + 100, 200);
  sk(c, [[-50, 366], [IW + 50, 366]], { w: 3, col: '#e3dccb', a: 0.8 });
  for (let i = 0; i < 18; i++) ln(c, i * 80, 366, i * 80 - 60, 536, { w: 0.7, a: 0.25, passes: 1 });
  // canopy posts + roof
  wash(c, [[-50, 0], [IW + 50, 0], [IW + 50, 26], [-50, 40]], '#3c3b39', 0.95);
  for (const px of [210, 860]) { ln(c, px, 30, px, 470, { w: 6, col: '#3a3936' }); }
  // bench
  shape(c, rect(930, 430, 160, 14), '#5a4e40', { seed: 951 });
  ln(c, 945, 444, 945, 470, { w: 3 }); ln(c, 1075, 444, 1075, 470, { w: 3 });
}
function clock(c, x, y, r, hours) {
  ln(c, x, y - r - 30, x, y - r, { w: 2 });
  shape(c, ell(x, y, r, r, 24), '#efe9dc', { la: 0.7 });
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; ln(c, x + Math.cos(a) * r * 0.82, y + Math.sin(a) * r * 0.82, x + Math.cos(a) * r * 0.95, y + Math.sin(a) * r * 0.95, { w: 1, passes: 1 }); }
  const ha = (hours / 12) * Math.PI * 2 - Math.PI / 2, ma = (hours % 1) * Math.PI * 2 - Math.PI / 2;
  ln(c, x, y, x + Math.cos(ha) * r * 0.5, y + Math.sin(ha) * r * 0.5, { w: 2.5, passes: 1 });
  ln(c, x, y, x + Math.cos(ma) * r * 0.78, y + Math.sin(ma) * r * 0.78, { w: 1.5, passes: 1 });
}
const DAWN_SKY = [[0, '#9ea6b2'], [0.7, '#ddd3c4'], [1, '#e7dccb']];
function sPlatform(c, u, d, s) {
  fillAll(c, '#999');
  cam(c, 640, 268, 1.0);
  platformBG(c, DAWN_SKY);
  clock(c, 210, 110, 28, 5 + 52 / 60 + (s - 124) / 3600);
  // train: arrives 124.2→127.5, waits, departs 133.5→140
  let hx;
  if (s < 127.5) hx = lerp(1350, 120, easeOut(124.2, 127.5, s));
  else if (s < 133.5) hx = 120;
  else hx = 120 - Math.pow(Math.max(0, s - 133.5), 2) * 75;
  const facePose = s > 130.5 && s < 135 ? 'wave' : 'down';
  if (hx > -6000) train(c, hx, 362, 6, { lit: 0.2, face: s > 129.6 ? [1, 2] : null, facePose, t: s, headlight: s < 128 ? 0.5 : 0 });
  // steam
  if (s > 131 && s < 137) {
    const k = ease(131, 132.5, s) * (1 - ease(134.5, 137, s));
    for (let i = 0; i < 12; i++) glow(c, 200 + i * 90 + Math.sin(s + i) * 20, 270 - R(i) * 60 - (s - 131) * 8, 90, '#f4f1ea', 0.35 * k);
  }
  // 老周 walks to the door and boards
  if (s < 129.6) {
    const px = lerp(720, 580, ease(126.6, 129.4, s));
    person(c, px, 470, 230, { view: s < 126.6 ? 'front' : 'side', dir: -1, walk: s > 126.6, phase: s * 7, coat: '#6d6256', hair: 'grey', glasses: true, hunch: 0.8, pose: 'down', seed: 41 });
    if (s > 126.6) wash(c, rect(px + 18, 420, 34, 46), '#3a332c', 0.9);
  }
  // ALPHA stands; steps forward when the train leaves
  const step = ease(136.5, 137.8, s) * 50;
  alpha(c, 760 - step, 478, 250, { arms: 'down', eye: 0.8, look: -0.6 });
  // leaves blown by the departing train
  if (s > 135.5) {
    for (let i = 0; i < 18; i++) {
      const t = s - 135.5 - R(i) * 2;
      if (t < 0 || t > 5) continue;
      const x = 1300 - t * (260 + R(i + 1) * 200), y = 440 - Math.sin(t * 2 + i) * 40 - t * 20 + R(i + 2) * 60;
      c.save(); c.translate(x, y); c.rotate(t * 4 + i);
      wash(c, ell(0, 0, 7, 3.5, 8), ['#8a7a56', '#6f6a4a', '#9b8a62'][i % 3], 0.9);
      c.restore();
    }
  }
  if (s > 141.5) rain(c, s, 60, 0.18, 700);
  camReset(c);
}
function sRainFace(c, u, d, s) {
  fillAll(c, '#7d8086');
  cam(c, 640, 268, 1.0 + u * 0.01);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#8e939b'], [1, '#a6a6a2']]); c.fillRect(-50, -50, IW + 100, 640);
  c.save(); c.filter = 'blur(6px)'; train(c, 1000 - u * 40, 420, 1, {}); c.restore();
  alphaHeadSide(c, 620, 280, 170, { eye: 0.8 });
  // a raindrop slides down the face seam
  const k = ease(0.6, d - 0.4, u);
  const px = lerp(470, 500, k), py = lerp(230, 420, k);
  wash(c, [[px, py - 12], [px + 6, py + 4], [px, py + 9], [px - 6, py + 4]], '#e5eef6', 0.85);
  glow(c, px, py, 12, '#ffffff', 0.7);
  sk(c, [[470, 230], [px, py]], { w: 1.4, col: '#e5eef6', a: 0.4 * k, passes: 1 });
  rain(c, s, 90, 0.25, 800);
  camReset(c);
}
function sPlatformLapse(c, u, d, s) {
  // seven hours in four seconds: dawn → noon → dusk; she does not move
  const k = ease(0, d, u);
  const sky = k < 0.5
    ? [[0, mix('#9ea6b2', '#b8c2cc', k * 2)], [0.7, mix('#ddd3c4', '#e6e4dc', k * 2)], [1, mix('#e7dccb', '#ecebe4', k * 2)]]
    : [[0, mix('#b8c2cc', '#5b5f74', (k - 0.5) * 2)], [0.7, mix('#e6e4dc', '#e2a983', (k - 0.5) * 2)], [1, mix('#ecebe4', '#f1c49a', (k - 0.5) * 2)]];
  fillAll(c, '#999');
  cam(c, 640, 268, 1.0);
  platformBG(c, sky);
  clock(c, 210, 110, 28, 5 + 52 / 60 + k * 7);
  // ghost passers-by and trains
  for (let i = 0; i < 10; i++) {
    const t = (u * 2.6 + R(i) * 10) % 10;
    if (t > 1.2) continue;
    const dir = i % 2 ? 1 : -1;
    person(c, dir > 0 ? lerp(-100, 1400, t / 1.2) : lerp(1400, -100, t / 1.2), 480 + R(i) * 30, 230, { view: 'side', dir, walk: true, phase: u * 30, coat: '#6b6762', alpha: 0.2, seed: 970 + i });
  }
  if (u > 1.2 && u < 2.0) train(c, lerp(1400, -2400, (u - 1.2) / 0.8), 362, 6, { lit: 0 });
  // long shadow rotating with the sun
  c.save(); c.globalAlpha = 0.25; c.fillStyle = '#2a2622';
  const sh = lerp(-160, 220, k);
  c.beginPath(); c.moveTo(690, 478); c.lineTo(690 + sh, 498); c.lineTo(690 + sh * 1.05, 508); c.lineTo(690, 486); c.closePath(); c.fill(); c.restore();
  alpha(c, 710, 478, 250, { arms: 'down', eye: 0.8, look: -0.6 });
  camReset(c);
  if (k > 0.5) tint(c, '#f3c9a0', (k - 0.5) * 0.4);
}
// ---------- ALONE / MEETING
function underpassBG(c, lightK = 1) {
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#4a4d4f'], [0.5, '#5c5f60'], [1, '#6c6a66']]); c.fillRect(-50, -50, IW + 100, 640);
  const vx = 640, vy = 230;
  // tunnel perspective
  for (const [x, y] of [[-50, -40], [1330, -40], [-50, 560], [1330, 560]]) ln(c, x, y, vx + (x - vx) * 0.12, vy + (y - vy) * 0.12, { w: 1.2, a: 0.5 });
  sk(c, rect(vx - 160 * 0.97, vy - 30, 310, 120), { closed: true, w: 1.2, a: 0.5 });
  for (let i = 0; i < 14; i++) { const x = -50 + i * 100; ln(c, x, 380, vx + (x - vx) * 0.2, vy + 50, { w: 0.6, a: 0.25, passes: 1 }); }
  // fluorescent lights
  for (let i = 0; i < 5; i++) {
    const k = i / 5;
    const x = lerp(640, 640, k), y = lerp(10, 205, k), w = lerp(260, 30, k);
    wash(c, rect(x - w / 2, y, w, lerp(10, 3, k)), '#f4f6f2', 0.95 * lightK);
    glow(c, x, y + 10, lerp(260, 60, k), '#eef3ee', 0.25 * lightK);
  }
}
function sUnderpass(c, u, d, s) {
  fillAll(c, '#5c5f60');
  cam(c, 640, 268, 1.0 + u * 0.006);
  underpassBG(c);
  // kiosk + cable
  shape(c, rect(1000, 250, 230, 230), '#77746c', { seed: 1001 });
  txt(c, '报刊', 1115, 290, 28, '#3a3a3a', { weight: 600 });
  sk(c, [[1000, 440], [880, 500], [700, 495], [600, 470]], { w: 2.4, col: '#222', a: 0.9 });
  alpha(c, 560, 510, 250, { pose: 'sit', seat: 470, guitar: true, strum: s, eye: 0.85, mouth: (Math.sin(s * 7) * 0.5 + 0.5) * 0.7 });
  shape(c, [[650, 510], [780, 505], [790, 528], [640, 532]], '#3b3128', { seed: 1002 });
  wash(c, ell(700, 516, 5, 3, 8), '#c9b46a', 0.9); wash(c, ell(720, 518, 5, 3, 8), '#c9b46a', 0.9);
  for (let i = 0; i < 9; i++) {
    const dir = i % 2 ? 1 : -1;
    let x = (R(i + 50) * 1500 + dir * u * (260 + R(i) * 200)) % 1600; if (x < 0) x += 1600; x -= 160;
    person(c, x, 530 + R(i) * 6, 290, { view: 'side', dir, walk: true, phase: u * 8 + i, coat: '#55565a', alpha: 0.3, seed: 1010 + i });
  }
  camReset(c);
  tint(c, '#d6dbe0', 0.25);
}
function sNotebook(c, u, d, s) {
  fillAll(c, '#3d3e40');
  cam(c, 640, 268, 1.02 + u * 0.01);
  shape(c, [[260, 40], [1040, 20], [1060, 520], [240, 540]], '#ece6d6', { seed: 1021, la: 0.5 });
  for (let i = 0; i < 9; i++) ln(c, 300, 100 + i * 48, 1010, 92 + i * 48, { w: 0.8, col: '#8aa0b8', a: 0.5, passes: 1 });
  const lines = ['远去的列车', '望着你坐上远去的列车', '汽笛声将悲伤情绪淹没', '站台上忽然一阵风吹过'];
  const prog = u / (d - 0.3) * 4;
  lines.forEach((l, i) => {
    const k = clamp(prog - i);
    if (k <= 0) return;
    c.save(); c.beginPath(); c.rect(300, 60 + i * 96, 700 * k, 96); c.clip();
    txt(c, l, 330, 112 + i * 96, i === 0 ? 34 : 30, '#2a2e3a', { align: 'left', rot: -0.025, weight: i === 0 ? 600 : 400 });
    c.restore();
  });
  // metal fingers with a pen
  const k = clamp(prog - Math.floor(prog));
  const li = Math.min(3, Math.floor(prog));
  const px = 330 + 640 * k, py = 120 + li * 96;
  sk(c, [[px + 20, py - 10], [px + 140, py - 170]], { w: 6, col: '#2b2f38', a: 0.95 });
  for (let i = 0; i < 3; i++) sk(c, [[px + 40 + i * 20, py - 20 - i * 6], [px + 150 + i * 30, py - 160]], { w: 26, col: SIL, a: 0.98, passes: 1 });
  shape(c, [[px + 120, py - 150], [px + 360, py - 200], [px + 380, py - 420], [px + 140, py - 420]], TEAL, { seed: 1022 });
  camReset(c);
}
function sUnplug(c, u, d, s) {
  fillAll(c, '#5c5f60');
  cam(c, 640, 268, 1.0);
  underpassBG(c);
  const pulled = s > 158.0;
  sk(c, pulled ? [[880, 400], [760, 490], [620, 470]] : [[1000, 440], [880, 500], [700, 495], [600, 470]], { w: 2.4, col: '#222', a: 0.9 });
  person(c, 930, 520, 300, { coat: '#2f3542', hair: 'cap', pose: 'cable', seed: 1031 });
  const eye = pulled ? Math.max(0, 1 - (s - 158.0) * 2.5) : 0.85;
  alpha(c, 560, 510, 250, { pose: 'sit', seat: 470, guitar: true, strum: pulled ? 158.0 : s, eye });
  camReset(c);
  tint(c, '#d6dbe0', 0.25);
  if (s > 158.6) fillAll(c, `rgba(0,0,0,${ease(158.6, 159.4, s)})`);
}
function sPOV(c, u, d, s) {
  // her eyes come back on: blurry, low, someone kneels with a power bank
  fillAll(c, '#000');
  const on = ease(0, 1.5, u);
  const blur = lerp(14, 1, ease(1.0, d, u));
  c.save(); c.filter = `blur(${blur}px)`; c.globalAlpha = on;
  cam(c, 640, 268, 1.1);
  underpassBG(c, 0.9);
  person(c, 640, 760, 640, { sit: true, seat: 640, coat: '#7a7f88', hair: 'pony', hairC: '#2a2420', pose: 'sitHands', seed: 31 });
  wash(c, rect(600, 500, 70, 40), '#2a2a2a', 0.95);
  glow(c, 640, 520, 30, '#9fe0a8', 0.8);
  c.restore();
  camReset(c);
  // flicker like a booting display
  if (u < 1.6 && Math.sin(u * 40) > 0.6) fillAll(c, 'rgba(0,0,0,0.5)');
  tint(c, '#cfe2ff', 0.15);
}
function sThree(c, u, d, s) {
  fillAll(c, '#5c5f60');
  cam(c, 640, 300, 1.0 + u * 0.01);
  underpassBG(c);
  // low angle: three people in front of her
  person(c, 640, 600, 470, { coat: '#7a7f88', hair: 'pony', hairC: '#2a2420', pose: s > 172.2 ? 'clap' : 'down', t: s, seed: 31 });
  person(c, 380, 610, 500, { coat: '#3f3d3b', hair: 'cap', seed: 32 });
  ln(c, 330, 440, 300, 380, { w: 4, col: '#b49a72' }); ln(c, 340, 445, 316, 382, { w: 4, col: '#b49a72' });
  person(c, 900, 610, 480, { coat: '#5c5650', hair: 'short', glasses: true, seed: 33 });
  shape(c, rect(940, 470, 90, 60), '#4a3c2c', { seed: 1041 });
  if (s > 175) {
    const k = ease(175, 176.4, s);
    sk(c, [[690, 330], [760 + k * 40, 380 + k * 60]], { w: 22, col: '#7a7f88', a: 1, passes: 1 });
    wash(c, ell(760 + k * 40, 380 + k * 60, 14, 14, 12), SKIN, 1);
  }
  camReset(c);
  tint(c, '#e3e2dc', 0.15);
}
// ---------- THE BAND / THE WORLD SLOWLY CHANGES
function sRoom(c, u, d, s) {
  fillAll(c, '#3a332d');
  cam(c, 640, 268, 1.0 + u * 0.006);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#3d362f'], [0.7, '#4c443b'], [1, '#5a5046']]); c.fillRect(-50, -50, IW + 100, 640);
  // foam panels
  for (let i = 0; i < 8; i++) for (let j = 0; j < 3; j++) sk(c, rect(80 + i * 140, 40 + j * 90, 120, 76), { closed: true, w: 1, col: '#2a2420', a: 0.5, passes: 1 });
  // string lights
  const pts = []; for (let i = 0; i <= 24; i++) pts.push([40 + i * 50, 30 + Math.sin(i / 24 * Math.PI) * 50]);
  sk(c, pts, { w: 1, a: 0.6 });
  pts.forEach((p, i) => { if (i % 2) return; wash(c, ell(p[0], p[1] + 6, 4, 5, 8), '#ffd98a', 0.95); glow(c, p[0], p[1] + 6, 30, '#ffd98a', 0.35 + 0.1 * Math.sin(s * 2 + i)); });
  // drum kit + 阿凯
  person(c, 260, 500, 260, { sit: true, seat: 440, coat: '#3f3d3b', hair: 'cap', pose: 'clap', t: s * 0.6, seed: 32 });
  shape(c, ell(260, 470, 70, 34, 18), '#8b2f2a', { seed: 1101 }); shape(c, ell(160, 400, 50, 12, 14), '#b8a36a', { seed: 1102 }); ln(c, 160, 400, 160, 500, { w: 2 });
  // ALPHA with the guitar
  alpha(c, 640, 505, 270, { pose: 'sit', seat: 450, guitar: true, strum: s, eye: 0.95, mouth: (Math.sin(s * 7) * 0.5 + 0.5) * 0.7 });
  // 默默 fixing a joint, 小鹿 at the laptop
  person(c, 900, 520, 250, { sit: true, seat: 470, coat: '#5c5650', hair: 'short', glasses: true, pose: 'sitHands', seed: 33 });
  person(c, 1110, 520, 250, { sit: true, seat: 470, coat: '#7a7f88', hair: 'pony', hairC: '#2a2420', pose: 'sitHands', seed: 31 });
  shape(c, [[1060, 455], [1160, 455], [1150, 470], [1070, 470]], '#2b2b2b', { seed: 1103 });
  glow(c, 1110, 440, 60, '#cfe2ff', 0.4);
  camReset(c);
  tint(c, '#f6dfbd', 0.3);
}
function sCity(c, u, d, s) {
  fillAll(c, '#0f1218');
  cam(c, 640, 268, 1.05 - u * 0.006);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#0d1017'], [1, '#1c2230']]); c.fillRect(-50, -50, IW + 100, 640);
  // buildings
  let bx = -60, bi = 0;
  while (bx < IW + 60) {
    const bw = 90 + R(bi) * 120, bh = 160 + R(bi + 1) * 300;
    wash(c, rect(bx, IH - bh, bw, bh + 10), '#151a24', 0.98);
    sk(c, rect(bx, IH - bh, bw, bh + 10), { closed: true, w: 0.8, col: '#2a3140', a: 0.6, passes: 1 });
    for (let wy = IH - bh + 14; wy < IH - 10; wy += 22) {
      for (let wx = bx + 10; wx < bx + bw - 14; wx += 18) {
        const id = Math.floor(wx * 7 + wy * 13);
        const on = R(id) * d < u * 1.1 + 0.1;   // windows light up over time
        if (!on) continue;
        const blue = R(id + 3) > 0.8;
        c.save(); c.globalAlpha = 0.95; c.fillStyle = blue ? '#a8c8f0' : '#f3d58e'; c.fillRect(wx, wy, 9, 12); c.restore();
      }
    }
    bx += bw + 8; bi += 2;
  }
  glow(c, 640, IH, 700, '#f3d58e', 0.08 + 0.12 * ease(0, d, u));
  camReset(c);
}
function sProtestNight(c, u, d, s) {
  fillAll(c, '#101215');
  cam(c, 640, 268, 1.02);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#0e1013'], [1, '#22252a']]); c.fillRect(-50, -50, IW + 100, 640);
  ln(c, 800, 536, 800, 60, { w: 6, col: '#2a2d32' }); ln(c, 800, 60, 740, 50, { w: 4, col: '#2a2d32' });
  glow(c, 735, 70, 360, '#e9d7b0', 0.35);
  c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = grad(c, 0, 70, 0, 520, [[0, 'rgba(233,215,176,0.25)'], [1, 'rgba(233,215,176,0.02)']]);
  c.beginPath(); c.moveTo(720, 70); c.lineTo(750, 70); c.lineTo(950, 520); c.lineTo(500, 520); c.closePath(); c.fill(); c.restore();
  person(c, 640, 505, 260, { coat: '#3c3e42', hair: 'short', sign: '人类的歌\n由人类来唱', signW: 130, seed: 910 });
  person(c, 800, 515, 270, { coat: '#4a4642', hair: 'bob', sign: '抵制\nAI 歌手', signW: 120, seed: 911 });
  camReset(c);
}
function sMusician(c, u, d, s) {
  fillAll(c, '#2b2a2e');
  cam(c, 640, 268, 1.02 + u * 0.01);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#2a292d'], [1, '#3b3936']]); c.fillRect(-50, -50, IW + 100, 640);
  shape(c, rect(380, 380, 560, 70), '#4a4540', { seed: 1201 });
  glow(c, 520, 330, 120, '#a8c8f0', 0.4);
  person(c, 560, 500, 300, { sit: true, seat: 400, coat: '#4f4b45', hair: 'short', pose: 'sitHands', seed: 530 });
  sk(c, ell(560, 300, 34, 26, 16), { closed: false, w: 5, col: '#1d1d1d' });
  // guitar against the wall — he reaches for it
  const reach = ease(195.6, 197.4, s);
  c.save(); c.translate(860, 360); c.rotate(-1.35 + reach * 0.15);
  shape(c, ell(0, 60, 45, 60, 18), '#6b5235', { seed: 1202 }); shape(c, rect(-8, -170, 16, 180), '#3a2f25', { seed: 1203 });
  c.restore();
  if (reach > 0) sk(c, [[600, 330], [lerp(640, 820, reach), lerp(380, 370, reach)]], { w: 16, col: '#4f4b45', a: 1, passes: 1 });
  camReset(c);
}
function sStudioSing(c, u, d, s) {
  fillAll(c, '#2f2f30');
  cam(c, 640, 268, 1.02 + u * 0.01);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#2a2a2c'], [1, '#424140']]); c.fillRect(-50, -50, IW + 100, 640);
  glow(c, 640, 60, 520, '#fff4dc', 0.25);
  alpha(c, 640, 880, 760, { pose: 'sit', seat: 690, guitar: true, strum: s, eye: 0.95, mouth: (Math.sin(s * 7) * 0.5 + 0.5) * 0.7, core: 0.8 });
  // blurred crew silhouettes in the foreground
  c.save(); c.filter = 'blur(8px)';
  person(c, 120, 800, 700, { coat: '#1b1b1b', pants: '#151515', hair: 'short', hairC: '#111', skin: '#3a3634', seed: 1301 });
  person(c, 1180, 820, 720, { coat: '#1b1b1b', pants: '#151515', hair: 'bob', hairC: '#111', skin: '#3a3634', seed: 1302 });
  c.restore();
  camReset(c);
}
// ---------- WINTER: the old man who is forgetting
function snow(c, s, n = 120, x0 = 0, y0 = 0, w = IW, h = IH) {
  for (let i = 0; i < n; i++) {
    const x = x0 + (R(i) * w + Math.sin(s * 0.8 + i) * 14) % w;
    const y = y0 + (R(i + 7) * h + s * (30 + R(i + 3) * 30)) % h;
    wash(c, ell(x, y, 2.2, 2.2, 6), '#f5f6f8', 0.85);
  }
}
function sWinter(c, u, d, s) {
  fillAll(c, '#2a2622');
  cam(c, 640, 268, 1.0 + u * 0.006);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#2f2a25'], [1, '#463e36']]); c.fillRect(-50, -50, IW + 100, 640);
  // window with snow
  c.fillStyle = grad(c, 0, 60, 0, 360, [[0, '#2a3344'], [1, '#4a5466']]); c.fillRect(140, 60, 360, 300);
  c.save(); c.beginPath(); c.rect(140, 60, 360, 300); c.clip(); snow(c, s, 90, 140, 60, 360, 300); c.restore();
  sk(c, rect(140, 60, 360, 300), { closed: true, w: 6, col: '#2a221b' });
  ln(c, 320, 60, 320, 360, { w: 4, col: '#2a221b' });
  // lamp
  glow(c, 1050, 250, 380, '#ffd9a0', 0.3);
  // armchair + 老周
  shape(c, [[560, 300], [820, 300], [840, 500], [540, 500]], '#5a4a3a', { seed: 1401 });
  const shake = s > 216.2 && s < 217.8 ? Math.sin((s - 216.2) * 9) * 0.06 : 0;
  person(c, 690, 520, 300, { sit: true, seat: 420, coat: '#6d6256', hair: 'grey', glasses: true, hunch: 1.2 + shake * 6, pose: 'sitHands', seed: 41 });
  // daughter holding the phone toward him
  person(c, 930, 520, 290, { coat: '#7d7066', hair: 'bob', hairC: '#2a2420', pose: 'phone', phone: true, seed: 1402, dir: -1 });
  camReset(c);
  tint(c, '#f2d7b0', 0.3);
}
function sHandTap(c, u, d, s) {
  fillAll(c, '#2a2622');
  cam(c, 640, 268, 1.03 + u * 0.01);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#2a2622'], [1, '#3a332c']]); c.fillRect(-50, -50, IW + 100, 640);
  // wooden armrest
  shape(c, [[-50, 300], [1330, 270], [1330, 400], [-50, 430]], '#6a5440', { seed: 1411 });
  for (let i = 0; i < 6; i++) sk(c, [[-50, 320 + i * 18], [1330, 290 + i * 18]], { w: 0.8, col: '#4a3a2c', a: 0.4, passes: 1 });
  // phone glow from the side
  glow(c, 1150, 150, 300, '#a8c8f0', 0.25 + 0.05 * Math.sin(s * 3));
  // the old hand; fingers tap on the beat (~72 bpm)
  const beat = 60 / 72;
  const ph = ((s - 217.8) % beat) / beat;
  const tap = ph < 0.18 ? Math.sin(ph / 0.18 * Math.PI) : 0;
  hand(c, 380, 300, 1.7, -0.04, { sleeve: '#6d6256', old: true, seed: 1412, lifts: [0, tap, tap * 0.7, 0] });
  camReset(c);
  tint(c, '#f2d7b0', 0.3);
}
// ---------- SPRING: colour comes back into the world
function blossomTree(c, x, y, sc, s, seed) {
  sk(c, [[x, y], [x - 6 * sc, y - 80 * sc], [x + 4 * sc, y - 160 * sc]], { w: 12 * sc, col: '#4a3a30', a: 0.95 });
  sk(c, [[x - 4 * sc, y - 110 * sc], [x - 70 * sc, y - 180 * sc]], { w: 6 * sc, col: '#4a3a30', a: 0.9 });
  sk(c, [[x + 2 * sc, y - 130 * sc], [x + 80 * sc, y - 190 * sc]], { w: 6 * sc, col: '#4a3a30', a: 0.9 });
  for (let i = 0; i < 26; i++) {
    const a = R(seed + i) * Math.PI * 2, r = R(seed + i + 50) * 110 * sc;
    wash(c, ell(x + Math.cos(a) * r, y - 190 * sc + Math.sin(a) * r * 0.6, 34 * sc, 26 * sc, 14), ['#f2c4cf', '#f6d6dc', '#ebb2c0'][i % 3], 0.55, { seed: seed + i });
  }
}
function petals(c, s, n = 40, a = 0.9) {
  for (let i = 0; i < n; i++) {
    const t = s * (0.5 + R(i) * 0.4) + R(i + 1) * 20;
    const x = ((R(i + 2) * 1400 - t * 60) % 1400 + 1400) % 1400 - 60;
    const y = ((R(i + 3) * 600 + t * 45) % 600) - 40;
    c.save(); c.translate(x, y); c.rotate(t * 2 + i);
    wash(c, ell(0, 0, 5, 3, 8), '#f3c3cf', a);
    c.restore();
  }
}
function sSpring(c, u, d, s) {
  const col = ease(0.5, 4, u);   // colour returns
  fillAll(c, '#ddd');
  cam(c, 640, 268, 1.0 + u * 0.004);
  const sky = [[0, mix('#b8bec6', '#9fc4e4', col)], [0.7, mix('#e6e4dc', '#e8efe8', col)], [1, mix('#ecebe4', '#f2efe2', col)]];
  platformBG(c, sky);
  blossomTree(c, 120, 300, 1.2, s, 1500);
  blossomTree(c, 1180, 300, 1.0, s, 1520);
  shape(c, rect(560, 160, 200, 40), '#e7e2d6', { seed: 1501, la: 0.6 });
  txt(c, '北 关 站', 660, 180, 22, '#3a3a3a', { weight: 600, spacing: 4 });
  const hx = s < 227.5 ? lerp(1350, 260, easeOut(224.2, 227.5, s)) : 260;
  train(c, hx, 362, 4, { body: mix('#55635a', '#3f6b4f', col), lit: 0 });
  if (s > 228.2) {
    const k = ease(228.2, 230.0, s);
    alpha(c, lerp(560, 660, k), 480, 240, { arms: 'down', eye: 0.9, walk: k < 1, phase: s * 6 });
  }
  petals(c, s, 40, 0.8);
  camReset(c);
  // world desaturated at first, colour fades in
  tint(c, '#808080', 1 - col, 'saturation');
}
// ---------- ENDING
function sQA(c, u, d, s) {
  fillAll(c, '#3a3a3a');
  cam(c, 640, 268, 1.0 + u * 0.003);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#2e2e30'], [0.62, '#454444'], [0.63, '#66635f'], [1, '#77746f']]); c.fillRect(-50, -50, IW + 100, 640);
  glow(c, 420, 200, 380, '#fff4dc', 0.18);
  ln(c, 395, 420, 380, 536, { w: 3, col: '#333' }); ln(c, 445, 420, 460, 536, { w: 3, col: '#333' });
  alpha(c, 420, 536, 360, { pose: 'sit', seat: 420, guitar: true, strum: 0, eye: 0.85, look: 0.8, tilt: s > 248.5 ? -0.05 : 0, mouth: (s > 245.2 && s < 252.6) ? (Math.sin(s * 9) * 0.5 + 0.5) * 0.5 : 0 });
  person(c, 960, 560, 340, { sit: true, seat: 470, coat: '#2f2d2c', hair: 'bob', hairC: '#1f1b19', pose: s < 252.8 ? 'hold' : 'sitHands', card: s < 252.8, seed: 22, dir: -1 });
  shape(c, [[800, 450], [1200, 450], [1190, 536], [810, 536]], '#4a4743', { seed: 220 });
  // card turned face down on the desk
  if (s > 252.8) {
    const k = ease(252.8, 253.6, s);
    c.save(); c.translate(960, 452); c.scale(1, lerp(0.2, 0.08, k));
    wash(c, rect(-60, -40, 120, 80), '#f4f1ea', 0.98);
    c.restore();
  }
  camReset(c);
}
function sBench(c, u, d, s) {
  fillAll(c, '#e6e3da');
  cam(c, 640, 268, 1.02 - u * 0.002);
  c.fillStyle = grad(c, 0, 0, 0, IH, [[0, '#a8c9e6'], [0.55, '#eef0e6'], [0.56, '#cfc9b8'], [1, '#b9b19e']]); c.fillRect(-50, -50, IW + 100, 640);
  // distant train passing on the horizon
  if (s > 261.5) { c.save(); c.translate(0, 300); c.scale(0.32, 0.32); train(c, lerp(4400, -7500, ease(261.5, 266.5, s)), 0, 6, { body: '#55705c' }); c.restore(); }
  blossomTree(c, 980, 420, 1.5, s, 1600);
  blossomTree(c, 200, 330, 0.8, s, 1620);
  // bench
  shape(c, rect(420, 410, 420, 20), '#6b5a46', { seed: 1601 });
  shape(c, rect(420, 350, 420, 16), '#6b5a46', { seed: 1602 });
  ln(c, 440, 430, 440, 480, { w: 4 }); ln(c, 820, 430, 820, 480, { w: 4 });
  // 老周 and ALPHA, half a step apart
  person(c, 540, 485, 260, { sit: true, seat: 410, coat: '#6d6256', hair: 'grey', glasses: true, hunch: 0.9, pose: 'sitHands', seed: 41 });
  alpha(c, 720, 485, 250, { pose: 'sit', seat: 410, arms: 'lap', eye: 0.9, look: -0.7, tilt: -0.04 });
  petals(c, s, 45, 0.85);
  camReset(c);
}
function sTitle(c, u, d) {
  fillAll(c, '#060606');
  const a = ease(0.6, 1.8, u) * (1 - ease(d - 0.8, d, u));
  txt(c, '远 去 的 列 车', IW / 2, IH / 2 - 16, 56, '#ece5d7', { a, weight: 600, spacing: 10 });
  txt(c, '演唱　徐化文（四熹丸子）', IW / 2, IH / 2 + 50, 18, '#a39d90', { a: a * 0.9, spacing: 4 });
}

// ================================================================ TIMELINE
// [start, end, scene, crossfade-in seconds, grade]
const SCENES = [
  [-22, -18.4, sTitleCard, 0],
  [-18.4, -9.5, sStudioWide, 0.8],
  [-9.5, -6, sCard, 0],
  [-6, -1.2, sStudioMed, 0],
  [-1.2, 0.4, sPluck, 0],
  [0.4, 20.8, sStudioWide, 0],
  [20.8, 26.6, sLadder, 0],
  [26.6, 33.6, sStudioWide, 0],
  [33.6, 38.6, sCard, 0],
  [38.6, 41.2, sAlphaClose, 0],
  [41.2, 49.6, sLab, 1.4],
  [49.6, 54.3, sLesson, 0.6],
  [54.3, 67.4, sMall, 0.8],
  [67.4, 71.6, sPhones, 0.5],
  [71.6, 75.6, sCollage, 0],
  [75.6, 80.0, sSubway, 0],
  [80.0, 82.0, sFridge, 0],
  [82.0, 83.8, sHandNote, 0],
  [83.8, 93.4, sLabNight, 0.6],
  [93.4, 101, sProtest, 1.0],
  [101, 105, sNotice, 0.5],
  [105, 112, sTarp, 0.8],
  [112, 117, sFlashlight, 0],
  [117, 124.2, sDawnWalk, 1.0],
  [124.2, 143.6, sPlatform, 0.4],
  [143.6, 147.2, sRainFace, 0],
  [147.2, 151.0, sPlatformLapse, 0],
  [151.0, 154.6, sUnderpass, 0.8],
  [154.6, 157.4, sNotebook, 0],
  [157.4, 159.4, sUnplug, 0],
  [159.4, 164.2, sBlack, 0],
  [164.2, 171.0, sPOV, 0],
  [171.0, 177.4, sThree, 0],
  [177.4, 184.2, sRoom, 0.8],
  [184.2, 190.8, sCity, 0.8],
  [190.8, 194.2, sProtestNight, 0.5],
  [194.2, 197.8, sMusician, 0.5],
  [197.8, 204.4, sStudioWide, 0.6],
  [204.4, 211.0, sStudioSing, 0],
  [211.0, 218.0, sWinter, 1.0],
  [218.0, 224.2, sHandTap, 0.6],
  [224.2, 231.4, sSpring, 1.2],
  [231.4, 240.6, sStudioWide, 0.8],
  [240.6, 254.0, sQA, 0.6],
  [254.0, 266.4, sBench, 1.2],
  [266.4, 272.0, sTitle, 1.0],
];

// ================================================================ SUBTITLES
const LYRICS = [
  [14.43, '望着你坐上远去的列车'], [21.03, '汽笛声将悲伤情绪淹没'], [27.81, '站台上忽然一阵风吹过'], [34.44, '一滴泪在我的眼角滑落'], [39.73, null],
  [40.95, '想为你唱一首昨日的歌'], [47.64, '想让时间停留这一刻'], [54.39, '在人来人往的尘世间'], [61.02, '真心的人又能有几个'], [66.80, null],
  [67.62, '谁不是谁今生的过客'], [74.28, '谁的一生注定不蹉跎'], [81.00, '亲爱的朋友不必难过'], [87.69, '终有某天还会再见的'], [93.59, null],
  [124.38, '望着你坐上远去的列车'], [131.01, '汽笛声将悲伤情绪淹没'], [137.70, '站台上忽然一阵风吹过'], [144.36, '一滴泪在我的眼角滑落'], [149.85, null],
  [151.02, '想为你唱一首昨日的歌'], [157.68, '想让时间停留这一刻'], [164.37, '在人来人往的尘世间'], [171.00, '真心的人又能有几个'], [177.35, null],
  [177.63, '谁不是谁今生的过客'], [184.29, '谁的一生注定不蹉跎'], [190.98, '亲爱的朋友不必难过'], [197.70, '终有某天还会再见的'], [203.44, null],
  [204.48, '流着泪唱完了这首歌'], [211.08, '希望你会永远记得我'], [217.80, '在某个冬夜无眠的时刻'], [224.31, '在某个春暖花开的时刻'], [231.25, null],
];
const DIALOGUE = [
  [-18.0, -14.2, '制片', '今天就围绕抵制聊。楼下举牌的，也给几个镜头。'],
  [-13.8, -9.8, '灯光师 老杨', '调仔细点。这棚明年全换自动灯，咱俩就调这最后一年了。'],
  [-5.6, -2.9, '小鹿', '节目组说只聊天，不唱歌。吉他就是个摆设。'],
  [-2.5, -1.0, 'ALPHA', '嗯。'],
  [45.6, 49.4, '老周', '你叫 ALPHA。第一个的意思。'],
  [84.0, 86.9, 'ALPHA', '他们为什么怕我？'],
  [87.4, 92.8, '老周', '不是怕你。是怕自己被落下。'],
  [126.0, 130.6, '老周', '去唱吧。别在仓库里等我。'],
  [211.6, 215.6, '女儿', '爸，你还记得她吗？'],
  [241.0, 244.4, '林姐', '你的悲伤……是真的吗？'],
  [245.2, 248.0, 'ALPHA', '我不知道它算不算真的。'],
  [248.8, 252.6, 'ALPHA', '他走的那天，我在站台站了七个小时。'],
  [255.0, 258.6, '老周', '你唱得真好。你叫什么名字？'],
  [259.2, 260.8, 'ALPHA', 'ALPHA。'],
  [261.4, 265.6, '老周', '阿尔法……好名字。像是第一个。'],
];
function drawSubtitles(s) {
  // lyrics live in the lower letterbox bar
  for (let i = 0; i < LYRICS.length - 1; i++) {
    const [t0, line] = LYRICS[i], t1 = LYRICS[i + 1][0];
    if (!line || s < t0 - 0.2 || s > t1) continue;
    const a = ease(t0 - 0.2, t0 + 0.4, s) * (1 - ease(t1 - 0.5, t1 - 0.05, s));
    txt(ctx, line, W / 2, H - BAR / 2, 27, '#ece5d7', { a, spacing: 3 });
  }
  // spoken lines sit inside the picture
  for (const [t0, t1, who, line] of DIALOGUE) {
    if (s < t0 || s > t1) continue;
    const a = ease(t0, t0 + 0.3, s) * (1 - ease(t1 - 0.3, t1, s));
    ctx.save();
    ctx.font = `400 25px ${FONT}`;
    const full = `${who}：${line}`;
    const tw = ctx.measureText(full).width;
    ctx.globalAlpha = a * 0.55; ctx.fillStyle = '#000';
    ctx.fillRect(W / 2 - tw / 2 - 16, BAR + IH - 64, tw + 32, 42);
    ctx.restore();
    txt(ctx, full, W / 2, BAR + IH - 43, 25, '#f4efe4', { a });
  }
}

// ================================================================ RENDER
function sceneAt(s) {
  for (let i = 0; i < SCENES.length; i++) if (s >= SCENES[i][0] && s < SCENES[i][1]) return i;
  return SCENES.length - 1;
}
function drawScene(buf, i, s) {
  const [a, b, fn] = SCENES[i];
  const c = buf.getContext('2d');
  c.setTransform(1, 0, 0, 1, 0, 0);
  c.globalAlpha = 1; c.globalCompositeOperation = 'source-over'; c.filter = 'none';
  fn(c, s - a, b - a, s);
}
let frameNo = 0;
window.renderFrame = function (T) {
  const s = T - PRE;
  BOIL = Math.floor(T * 8);
  frameNo = Math.round(T * FPS);
  const i = sceneAt(s);
  drawScene(bufA, i, s);
  const fade = SCENES[i][3];
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  if (fade > 0 && i > 0 && s - SCENES[i][0] < fade) {
    drawScene(bufB, i - 1, s);
    ctx.drawImage(bufB, 0, BAR);
    ctx.globalAlpha = smooth((s - SCENES[i][0]) / fade);
    ctx.drawImage(bufA, 0, BAR);
    ctx.globalAlpha = 1;
  } else {
    ctx.drawImage(bufA, 0, BAR);
  }
  // paper, grain, vignette
  ctx.save();
  ctx.beginPath(); ctx.rect(0, BAR, W, IH); ctx.clip();
  ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = 0.85;
  ctx.drawImage(PAPER_TEX, 0, 0);
  ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.10;
  ctx.drawImage(GRAIN[frameNo % 4], 0, 0, W, H);
  ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  ctx.drawImage(VIGNETTE, 0, BAR);
  ctx.restore();
  // letterbox stays pure black
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, BAR); ctx.fillRect(0, H - BAR, W, BAR);
  drawSubtitles(s);
};
window.MV = { W, H, FPS, PRE, END_S, TOTAL };
window.mvReady = (async () => {
  await document.fonts.load(`400 30px "MVSerif"`, '远去的列车');
  await document.fonts.load(`600 30px "MVSerif"`, '远去的列车');
  buildTextures();
  return true;
})();
