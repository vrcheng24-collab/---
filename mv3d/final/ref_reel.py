#!/usr/bin/env python3
"""Animation reference reel for the physical robot.

The MV's singing close-ups, re-rendered with the motion channels drawn under the picture: jaw angle (deg), head pitch and roll (deg),
eye glow (0–1), on a 4-second scrolling window with a playhead. Every value is in out/final/motion_channels.csv at 24 fps.

    python3 ref_reel.py [--workers 4]
"""
import os, subprocess, sys, time
from multiprocessing import Pool
import cv2, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import timeline as TL

OUT = os.path.join(MV3D, "out", "final"); RC = os.path.join(OUT, "ref_chunks")
PARTS = [  # song in, out, title
    (111.60, 118.00, "下颌舵机行程演示 · JAW RANGE 0–9°"),
    (14.43, 21.03, "L01 近景 · 6eb86e · 望着你坐上远去的列车"),
    (34.44, 39.73, "L04 正脸 · 20ea29 · 一滴泪在我的眼角滑落（含泪光）"),
    (61.02, 66.80, "L08 正脸 · 真心的人又能有几个"),
    (171.00, 177.35, "L20 正脸 · 真心的人又能有几个"),
    (184.29, 188.00, "L22 近景 · 谁的一生注定不蹉跎"),
    (203.44, 211.08, "L25 正脸 · 流着泪唱完了这首歌（含泪光）"),
]
GH = H - PH                                                               # 276 px of graphs under the picture
CHAN = [("JAW", "下颌 deg", (255, 204, 60), 0, 9.5), ("PITCH", "点头 deg", (90, 210, 220), -2.5, 3.5),
        ("ROLL", "侧倾 deg", (230, 120, 170), -1.2, 1.2), ("EYE", "眼光 0–1", (120, 150, 255), 0, 1)]

def channels(t):
    import hero
    if 111.6 <= t < 118.0:                                                # the jaw demo drives the jaw directly; head still
        import spec
        return [spec.jaw_demo(t, 111.6), 0.0, 0.0, 0.2 + 0.7 * spec.jaw_demo(t, 111.6) / 9]
    nod, tilt = hero.head_motion(t)
    return [jaw_at(t), nod, tilt, hero.eye_glow(t)]

def graphs(t, title):
    g = Image.new("RGB", (W, GH), (10, 10, 12)); d = ImageDraw.Draw(g)
    x0, x1 = 300, W - 60; span = 4.0
    ts = np.linspace(t - span / 2, t + span / 2, 400)
    vals = np.array([channels(u) for u in ts])
    rows = len(CHAN); rh = (GH - 40) / rows
    for k, (key, zh, col, lo, hi) in enumerate(CHAN):
        y0 = 30 + k * rh; y1 = y0 + rh - 8
        d.line([(x0, y1), (x1, y1)], fill=(40, 40, 46))
        pts = [(x0 + (x1 - x0) * i / (len(ts) - 1), y1 - (y1 - y0) * (np.clip(v, lo, hi) - lo) / (hi - lo)) for i, v in enumerate(vals[:, k])]
        d.line(pts, fill=col, width=2)
        v = channels(t)[k]
        d.text((30, y0 + 2), f"{key}", font=font(F_MONO, 16), fill=col)
        d.text((110, y0 + 2), f"{v:6.2f}", font=font(F_MONO, 22), fill=(236, 230, 220))
        d.text((210, y0 + 6), zh, font=font(F_SERIF, 14), fill=(150, 144, 136))
    xm = (x0 + x1) / 2; d.line([(xm, 26), (xm, GH - 8)], fill=(236, 230, 220), width=1)
    d.text((x0, 6), title, font=font(F_SERIF, 16), fill=(200, 194, 184))
    d.text((x1, 6), f"song {t:7.2f} s   frame {int(round(t * FPS)):5d} @24fps", font=font(F_MONO, 14), fill=(150, 144, 136), anchor="ra")
    return np.asarray(g)

def ref_frame(t, title):
    img, warm = TL.picture(t)
    img = finish(img, t, warm, grain=0.015)
    out = np.zeros((H, W, 3), np.uint8); out[:PH] = (np.clip(img, 0, 1) * 255).astype(np.uint8); out[PH:] = graphs(t, title)
    return out

def render_part(i):
    cv2.setNumThreads(1)
    a, b, title = PARTS[i]; path = os.path.join(RC, f"r{i:02d}.mp4")
    if os.path.exists(path): return i
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", MASTER, "-map", "0:v", "-map", "1:a",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", path + ".part.mp4"],
                         stdin=subprocess.PIPE)
    for n in range(int(round(a * FPS)), int(round(b * FPS))): p.stdin.write(ref_frame(n / FPS, title).tobytes())
    p.stdin.close(); p.wait(); os.replace(path + ".part.mp4", path)
    return i

if __name__ == "__main__":
    os.makedirs(RC, exist_ok=True); build_jaw()
    nw = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 4
    with Pool(nw) as pool:
        for i in pool.imap_unordered(render_part, range(len(PARTS))): print("part", i, "done", flush=True)
    lst = os.path.join(RC, "list.txt")
    with open(lst, "w") as f:
        for i in range(len(PARTS)): f.write(f"file 'r{i:02d}.mp4'\n")
    out = os.path.join(OUT, "ALPHA_动画参考_口型与头部通道.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", out], check=True)
    print(out)
