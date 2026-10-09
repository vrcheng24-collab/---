#!/usr/bin/env python3
"""《远去的列车》 ALPHA — final MV. Timeline, renderer and exports.

Outside: a live performance in a small bar at night (the real robot, from photos, relit; jaw/head/eyes driven by the vocal).
Inside: a machine's memories (the user's footage as small-gauge film; point clouds when memory is written or blown away).

    python3 timeline.py [--workers 4] [--still t1,t2,...] [--only a-b] [--edl]
Writes out/final/: chunks, the master mp4, edl.csv, motion_channels.csv.
"""
import csv, math, os, subprocess, sys, time
from multiprocessing import Pool
import cv2, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

OUT = os.path.join(MV3D, "out", "final"); CH = os.path.join(OUT, "chunks")
END = SONG_END + 5.0                                                     # 5 s end card

# ------------------------------------------------------------------ framings for the bar shots (photo height, centre x, photo top, camera x)
PRE = {"FW": (1150, 960, -30), "FM": (1750, 960, -110), "SD": (1700, 1300, -150), "CL": (1500, 960, -260), "FC": (1300, 960, -180)}
PHOTO = {"FW": "front", "FM": "front", "SD": "side", "CL": "close", "FC": "face"}
LOOK = {"front": {}, "side": dict(key_h=2.6, key_w=2.6, fg=2), "close": dict(key_h=1.7, key_w=2.0, fg=2), "face": dict(key_h=1.0, key_w=1.6, amb=0.06, fg=2)}
def mv(a, b=None, dh=(0, 0), camx=(0, 0), dtop=(0, 0)):
    b = b or a; A, B = PRE[a], PRE[b]
    return dict(h0=A[0] + dh[0], h1=B[0] + dh[1], cx0=A[1], cx1=B[1], top0=A[2] + dtop[0], top1=B[2] + dtop[1], camx0=camx[0], camx1=camx[1])

# kind, start, end, args. Memory args: clip, source in-point. Hero args: preset, framing move, extra look.
EDL = [
    ("intro", 0.00, 14.43, dict(fr=mv("FW", "FW", dh=(-60, 160), dtop=(10, -50)))),
    ("hero", 14.43, 21.03, dict(p="CL", fr=mv("CL", dh=(-50, 150), dtop=(30, -40), camx=(30, -30)))),
    ("mem", 21.03, 24.50, dict(clip="B05", src=0.0)),
    ("hero", 24.50, 27.81, dict(p="SD", fr=mv("SD", dh=(-50, 50), camx=(-40, 20)))),
    ("mem", 27.81, 31.00, dict(clip="B06", src=0.3)),
    ("hero", 31.00, 34.44, dict(p="FM", fr=mv("FM", dh=(-50, 60), camx=(20, -20)))),
    ("hero", 34.44, 39.73, dict(p="FC", fr=mv("FC", dh=(-40, 80), dtop=(20, -20)), tear=37.6)),
    ("mem", 39.73, 44.50, dict(clip="B15", src=0.0)),
    ("hero", 44.50, 47.64, dict(p="CL", fr=mv("CL", camx=(-60, 40)))),
    ("mem", 47.64, 51.50, dict(clip="B03", src=6.0)),
    ("hero", 51.50, 54.39, dict(p="FW", fr=mv("FW", dh=(0, 100), dtop=(0, -20)))),
    ("mem", 54.39, 58.00, dict(clip="B07", src=9.8)),
    ("hero", 58.00, 61.02, dict(p="SD", fr=mv("SD", dh=(0, 80), camx=(30, -30)))),
    ("hero", 61.02, 66.80, dict(p="FC", fr=mv("FC", dh=(60, -20), camx=(-30, 30)))),
    ("mem", 66.80, 71.00, dict(clip="B04", src=2.7)),
    ("hero", 71.00, 74.28, dict(p="FW", fr=mv("FW", camx=(-80, 80)), seed=7)),
    ("mem", 74.28, 78.00, dict(clip="B02", src=0.0)),
    ("hero", 78.00, 81.00, dict(p="CL", fr=mv("CL", dh=(100, 0), dtop=(-30, 0)))),
    ("hero", 81.00, 87.69, dict(p="FM", fr=mv("FM", "FW", dh=(0, 0)))),
    ("pc_write", 87.69, 98.00, {}),
    ("spec1", 98.00, 105.60, {}),
    ("spec2", 105.60, 111.60, {}),
    ("spec3", 111.60, 118.00, {}),
    ("mem", 118.00, 122.10, dict(clip="B12", src=3.93)),
    ("hero", 122.10, 124.38, dict(p="FW", fr=mv("FW", dh=(40, 80)), spot_ramp=(122.3, 124.2))),
    ("mem", 124.38, 128.60, dict(clip="B05", src=5.25)),
    ("hero", 128.60, 131.01, dict(p="CL", fr=mv("CL", camx=(40, -20)))),
    ("mem", 131.01, 134.80, dict(clip="B13", src=16.8)),
    ("hero", 134.80, 137.70, dict(p="SD", fr=mv("SD", dh=(80, 0)))),
    ("pc_wind", 137.70, 151.02, {}),
    ("hero", 151.02, 157.68, dict(p="FW", fr=mv("FW", "FM", dh=(0, -150), dtop=(0, 30)))),
    ("mem", 157.68, 161.00, dict(clip="B15", src=6.63)),
    ("hero", 161.00, 164.37, dict(p="CL", fr=mv("CL", dh=(0, 120), camx=(-40, 0)))),
    ("mem", 164.37, 168.00, dict(clip="B07", src=0.0)),
    ("hero", 168.00, 171.00, dict(p="SD", fr=mv("SD", camx=(50, -10)))),
    ("hero", 171.00, 177.35, dict(p="FC", fr=mv("FC", dh=(-40, 100), dtop=(20, -30)))),
    ("mem", 177.35, 181.00, dict(clip="B13", src=6.0)),
    ("hero", 181.00, 184.29, dict(p="FW", fr=mv("FW", camx=(90, -60)), seed=11, spot=1.15)),
    ("hero", 184.29, 188.00, dict(p="CL", fr=mv("CL", dh=(-60, 160), dtop=(30, -50)))),
    ("mem", 188.00, 190.98, dict(clip="B07", src=4.7)),
    ("hero", 190.98, 197.70, dict(p="FM", fr=mv("FM", "FW", dh=(0, -60)), seed=11, spot=1.25)),
    ("mem", 197.70, 200.40, dict(clip="B14", src=22.75)),
    ("mem", 200.40, 203.44, dict(clip="B14", src=18.9)),
    ("hero", 203.44, 211.08, dict(p="FC", fr=mv("FC", dh=(-60, 120), dtop=(30, -40)), tear=207.4)),
    ("mem", 211.08, 214.50, dict(clip="B11", src=0.0)),
    ("hero", 214.50, 217.80, dict(p="CL", fr=mv("CL", dh=(80, 0), camx=(0, 30)))),
    ("pc_snow", 217.80, 224.31, {}),
    ("mem", 224.31, 226.11, dict(clip="B09", src=0.0)),
    ("mem", 226.11, 228.36, dict(clip="B09", src=5.75)),
    ("hero", 228.36, 231.25, dict(p="SD", fr=mv("SD", dh=(0, -100)))),
    ("outro", 231.25, SONG_END, dict(fr=mv("FW", dh=(80, -120), dtop=(-10, 30)))),
    ("end", SONG_END, END, {}),
]
MEM_NOTE = {"B02": "粉丝举着手机", "B03": "老周教她", "B04": "老周揭开帆布", "B05": "列车", "B06": "黄昏站台", "B07": "老周修理 / 演出", "B09": "春天，被运走",
            "B11": "老周鼓掌", "B12": "摄影棚，众人仰望", "B13": "演出 / 观众", "B14": "老周与女儿", "B15": "工坊里的老周"}

def seg_at(t):
    for i, (k, a, b, args) in enumerate(EDL):
        if a <= t < b: return i
    return len(EDL) - 1

# ------------------------------------------------------------------ pictures
def title_overlay(img, t, a0, a1):
    a = ease((t - a0) / 1.2) * (1 - ease((t - a1 + 1.2) / 1.2))
    if a <= 0: return img
    lay = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((W / 2, PH * 0.43), "远  去  的  列  车", font=font(F_SERIF, 74), fill=(240, 234, 224, int(235 * a)), anchor="mm")
    d.text((W / 2, PH * 0.43 + 70), "A L P H A", font=font(F_MONO, 20), fill=(255, 204, 60, int(220 * a)), anchor="mm")
    L = np.asarray(lay).astype(np.float32) / 255.0
    return img * (1 - L[..., 3:]) + L[..., :3] * L[..., 3:]

def end_card(t):
    img = np.zeros((PH, W, 3), np.float32) + 0.01
    a = ease((t - SONG_END - 0.3) / 1.0) * (1 - ease((t - END + 0.8) / 0.8))
    lay = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((W / 2, PH * 0.42), "远  去  的  列  车", font=font(F_SERIF, 60), fill=(240, 234, 224, int(235 * a)), anchor="mm")
    d.text((W / 2, PH * 0.42 + 70), "ALPHA  ·  3.5 m  演 出 机 器 人", font=font(F_SERIF, 24), fill=(200, 194, 184, int(220 * a)), anchor="mm")
    L = np.asarray(lay).astype(np.float32) / 255.0
    return img * (1 - L[..., 3:]) + L[..., :3] * L[..., 3:]

def picture(t):
    import hero, memory, pcloud, spec
    i = seg_at(t); kind, a, b, A = EDL[i]
    if kind in ("hero", "intro", "outro"):
        name = PHOTO.get(A.get("p", "FW"))
        look = dict(LOOK[name]); spot = A.get("spot", 1.0)
        if kind == "intro":                                              # the room first, then the spot finds her
            spot = ease((t - 5.5) / 4.0); look.update(amb=lerp(0.035, 0.10, ease((t - 5.5) / 4.0)))
        if kind == "outro":                                              # the spot fades; only her eyes remain
            k = 1 - ease((t - 234.5) / 5.5); spot = k; look.update(amb=lerp(0.03, 0.10, k))
        if "spot_ramp" in A:
            r0, r1 = A["spot_ramp"]; spot = lerp(0.15, 1.0, ease((t - r0) / (r1 - r0)))
        img = hero.shot(t, name, a, b, A["fr"], spot=spot, seed=A.get("seed", 3), tear=A.get("tear"), **look)
        if kind == "intro": img = title_overlay(img, t, 2.0, 8.6) * ease(t / 2.5)
        if kind == "outro": img = img * (1 - ease((t - SONG_END + 1.2) / 1.2))
        return img, 0.02
    if kind == "mem": return memory.memory(t, A["clip"], A["src"], a, b), 0.0
    if kind == "pc_write": return pcloud.write_seq(t, a, b), -0.02
    if kind == "pc_wind": return pcloud.wind_seq(t, a, b), -0.02
    if kind == "pc_snow": return pcloud.snow_seq(t, a, b), -0.02
    if kind == "spec1": return spec.s1(t, a, b), -0.01
    if kind == "spec2": return spec.s2(t, a, b), -0.01
    if kind == "spec3": return spec.s3(t, a, b), -0.01
    return end_card(t), 0.0

def frame(t):
    img, warm = picture(t)
    img = finish(img, t, warm, grain=0.022)
    out = np.zeros((H, W, 3), np.uint8); out[BAR:BAR + PH] = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    pil = Image.fromarray(out); lyric_bar(pil, t)
    return np.asarray(pil)

# ------------------------------------------------------------------ render
def chunks():
    out = []; n_end = int(round(END * FPS))
    for i, (k, a, b, A) in enumerate(EDL):
        f0, f1 = int(round(a * FPS)), min(n_end, int(round(b * FPS)))
        for s in range(f0, f1, 48): out.append((len(out), i, s, min(f1, s + 48)))
    return out
def render_chunk(c):
    idx, seg, f0, f1 = c
    cv2.setNumThreads(1)
    path = os.path.join(CH, f"c{idx:04d}.mp4")
    if os.path.exists(path): return idx, 0.0
    t0 = time.time(); tmp = path + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-g", "48", tmp], stdin=subprocess.PIPE)
    for n in range(f0, f1): p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait(); os.replace(tmp, path)
    return idx, (time.time() - t0) / (f1 - f0)

def export_tables():
    import hero
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "edl.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["#", "in", "out", "dur", "kind", "source", "note", "lyric"])
        for i, (k, a, b, A) in enumerate(EDL):
            lyr = " / ".join(l[3] for l in LINES if l[1] < b and l[2] > a)
            src = f'{A["clip"]} @ {A["src"]:.2f}s' if k == "mem" else (hero.PHOTOS[PHOTO[A.get("p", "FW")]]["f"] + " " + A.get("p", "FW") if k in ("hero", "intro", "outro") else "")
            note = MEM_NOTE.get(A.get("clip"), "") if k == "mem" else {"intro": "黑暗中的酒吧，追光找到她 + 片名", "outro": "追光熄灭，只剩眼睛", "pc_write": "记忆写入：点云面孔成形后散开",
                    "pc_wind": "站台记忆被风吹散 → 点云面孔 + 泪", "pc_snow": "点云面孔像雪一样落下", "spec1": "实物介绍：部件标注", "spec2": "工作室实物照片 · 3.5 m",
                    "spec3": "下颌舵机演示 0–9°", "end": "片尾"}.get(k, "酒吧演出 · 下颌随人声" + (" · 泪" if A.get("tear") else ""))
            w.writerow([i + 1, f"{a:.2f}", f"{b:.2f}", f"{b - a:.2f}", k, src, note, lyr])
    with open(os.path.join(OUT, "motion_channels.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["frame", "time_s", "jaw_deg", "head_pitch_deg", "head_roll_deg", "eye_glow_0to1", "vocal_0to1", "on_screen"])
        for n in range(int(round(SONG_END * FPS)) + 1):
            t = n / FPS; nod, tilt = hero.head_motion(t)
            w.writerow([n, f"{t:.3f}", f"{jaw_at(t):.2f}", f"{nod:.2f}", f"{tilt:.2f}", f"{hero.eye_glow(t):.3f}", f"{vocal_level(t):.3f}", EDL[seg_at(t)][0]])

def assemble():
    lst = os.path.join(OUT, "chunks.txt")
    with open(lst, "w") as f:
        for c in chunks(): f.write(f"file 'chunks/c{c[0]:04d}.mp4'\n")
    master = os.path.join(OUT, "ALPHA_远去的列车_final_1080p.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", MASTER, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "apad", "-c:a", "aac", "-b:a", "256k", "-t", f"{END:.3f}", "-movflags", "+faststart", master], check=True)
    return master

if __name__ == "__main__":
    os.makedirs(CH, exist_ok=True)
    build_jaw()
    if "--edl" in sys.argv: export_tables(); sys.exit()
    if "--still" in sys.argv:
        for tt in sys.argv[sys.argv.index("--still") + 1].split(","):
            Image.fromarray(frame(float(tt))).save(os.path.join(OUT, f"still_{float(tt):07.2f}.jpg"), quality=90)
        sys.exit()
    C = chunks()
    if "--only" in sys.argv:
        lo, hi = map(float, sys.argv[sys.argv.index("--only") + 1].split("-"))
        C = [c for c in C if c[3] / FPS > lo and c[2] / FPS < hi]
    nw = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 4
    C.sort(key=lambda c: EDL[c[1]][0] not in ("pc_wind", "pc_write", "pc_snow", "intro"))     # slow ones first
    t0 = time.time(); done = 0
    with Pool(nw) as pool:
        for idx, spf in pool.imap_unordered(render_chunk, C):
            done += 1; print(f"[{time.time() - t0:7.0f}s] chunk {idx:4d} done ({spf:.2f} s/frame)  {done}/{len(C)}", flush=True)
    if "--only" not in sys.argv:
        export_tables(); print(assemble())
