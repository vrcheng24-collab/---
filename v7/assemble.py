#!/usr/bin/env python3
"""Assemble the v7 MV from the shot list.

For every shot in 03_分镜清单.csv (in order) the picture comes from, in priority:
  1. a generated clip   clips/ALPHA_<shot_id>*.mp4   (first match in sort order; rename the pick to sort first)
  2. the keyframe image frames/<basename of frame_image>  (slow push-in)
  3. a placeholder card with the shot id and action      (animatic)
Lip-sync clips are assumed to be generated with the matching audio slice (which starts 0.5 s before the line),
so their in-point is offset by the handle plus the shot's position inside the line.

Sound: the master in two parts (paused at the measured breath dip, resumed from the same spot), the L08 in-scene
KTV vocal, the opening pluck, and room tone / rain under the non-music blocks. Lyrics and dialogue go in as
burned-in ASS subtitles (dialogue is subtitle-only by decision).

    python3 assemble.py                 # 1920x1080 render
    python3 assemble.py --preview       # 1280x720, faster
"""
import argparse, csv, glob, os, subprocess, tempfile, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ap = argparse.ArgumentParser()
ap.add_argument("--clips", default=os.path.join(HERE, "clips"))
ap.add_argument("--frames", default=os.path.join(HERE, "frames"))
ap.add_argument("--preview", action="store_true")
ap.add_argument("--out", default=None)
args = ap.parse_args()

W, H = (1280, 720) if args.preview else (1920, 1080)
IH = round(W / 2.39 / 2) * 2                   # 2.39:1 picture
BAR = (H - IH) // 2
FPS = 24
FONT = os.path.join(ROOT, "mv", "fonts", "serif600.ttf")
FONT_R = os.path.join(ROOT, "mv", "fonts", "serif400.ttf")
MASTER = os.path.join(HERE, "audio", "_master_decoded.wav")
if not os.path.exists(MASTER):
    MASTER = "/root/.claude/uploads/244b6930-24ca-5e89-bb8e-bcf0d6db12f0/1dd96bd4-_____.mp3"
PLUCK = os.path.join(ROOT, "mv", "pluck.wav")
OUT = args.out or os.path.join(HERE, "out", "远去的列车_v7_" + ("animatic" if not glob.glob(os.path.join(args.clips, "*.mp4")) else "cut") + ".mp4")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

shots = list(csv.DictReader(open(os.path.join(HERE, "03_分镜清单.csv"), encoding="utf-8-sig")))
segs = {r["segment_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "audio", "audio_segments.csv"), encoding="utf-8-sig"))}
lines = list(csv.DictReader(open(os.path.join(HERE, "audio", "song_lines.csv"), encoding="utf-8-sig")))
blocks = {r["block_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "04_双时间轴段落.csv"), encoding="utf-8-sig"))}
BREAK = float(blocks["B1"]["song_out"])
B1_OFF = float(blocks["B1"]["mv_in"])
B3_OFF = float(blocks["B3"]["mv_in"]) - BREAK
TOTAL = float(blocks["B4"]["mv_out"])

def run(cmd):
    subprocess.run(cmd, check=True)

def song_to_mv(t):
    return t + (B1_OFF if t < BREAK else B3_OFF)

tmp = tempfile.mkdtemp(prefix="v7_")
vf_fit = f"scale={W}:{IH}:force_original_aspect_ratio=increase,crop={W}:{IH},pad={W}:{H}:0:{BAR}:black,fps={FPS},format=yuv420p"
parts = []
report = []
for i, s in enumerate(shots):
    dur = float(s["mv_out"]) - float(s["mv_in"])
    out = os.path.join(tmp, f"{i:03d}.mp4")
    sid = s["shot_id"]
    clip = sorted(glob.glob(os.path.join(args.clips, f"ALPHA_{sid}_*.mp4")) + glob.glob(os.path.join(args.clips, f"ALPHA_{sid}.mp4")))
    frame = ""
    if s["frame_image"]:
        base = os.path.basename(s["frame_image"].split("（")[0].split("；")[0].strip())
        cand = glob.glob(os.path.join(args.frames, "**", base), recursive=True)
        frame = cand[0] if cand else ""
    if clip:
        start = 0.0
        seg = segs.get(s["audio_segment_id"].split("（")[0])
        if seg and s["song_in"]:
            start = float(seg["handle_in"]) + float(s["song_in"]) - float(seg["song_in"])
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-i", clip[0], "-t", f"{dur:.3f}", "-an",
             "-vf", vf_fit + f",tpad=stop_mode=clone:stop_duration={dur:.3f}", "-t", f"{dur:.3f}",
             "-c:v", "libx264", "-crf", "18", "-preset", "medium", out])
        report.append((sid, "clip", os.path.basename(clip[0]), f"in {start:.2f}s"))
    elif frame:
        n = max(1, round(dur * FPS))
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", frame, "-t", f"{dur:.3f}",
             "-vf", f"scale={W}:{IH}:force_original_aspect_ratio=increase,crop={W}:{IH},"
                    f"zoompan=z='1+0.04*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{IH}:fps={FPS},"
                    f"pad={W}:{H}:0:{BAR}:black,format=yuv420p",
             "-c:v", "libx264", "-crf", "18", "-preset", "medium", out])
        report.append((sid, "keyframe", os.path.basename(frame), "still + push-in"))
    else:
        txt = os.path.join(tmp, f"{i:03d}.txt")
        wrap = "\n".join(textwrap.wrap(s["action"], 26)[:3])
        with open(txt, "w") as f:
            f.write(f"{sid}　·　{s['story_time']}　·　{s['character_card']}\n\n{wrap}\n\n素材：{s['source_asset_id']}")
        fs = 30 if not args.preview else 22
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x15171a:s={W}x{IH}:d={dur:.3f}:r={FPS}",
             "-vf", f"drawtext=fontfile={FONT_R}:textfile={txt}:fontcolor=0xd8d2c4:fontsize={fs}:line_spacing={fs//2}:x=(w-tw)/2:y=(h-th)/2,"
                    f"pad={W}:{H}:0:{BAR}:black,format=yuv420p",
             "-t", f"{dur:.3f}", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", out])
        report.append((sid, "placeholder", "", ""))
    parts.append(out)

with open(os.path.join(tmp, "list.txt"), "w") as f:
    f.write("\n".join(f"file '{p}'" for p in parts))
picture = os.path.join(tmp, "picture.mp4")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "list.txt"), "-c", "copy", picture])

# ---------------------------------------------------------------- subtitles (ASS)
def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s_ = t % 60
    return f"{h}:{m:02d}:{s_:05.2f}"
fsL = 46 if not args.preview else 30
fsD = 40 if not args.preview else 27
ass = [
 "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
 "[V4+ Styles]",
 "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
 f"Style: Lyric,Noto Serif SC,{fsL},&H00D7E5EC,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,0,2,40,40,{BAR//2 - fsL//2},1",
 f"Style: Dialog,Noto Serif SC,{fsD},&H00F0F4F6,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,1.5,1,2,80,80,{BAR+30},1",
 f"Style: InScene,Noto Serif SC,{fsD},&H00B8D8F0,&H000000FF,&H00000000,&H80000000,0,1,0,0,100,100,1,0,1,1.5,1,2,80,80,{BAR+30},1",
 "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
]
for k, ln in enumerate(lines):
    a, b = float(ln["song_in"]), float(ln["song_out"])
    if a < BREAK <= b: b = BREAK                       # the line before the pause
    ma, mb = song_to_mv(a), song_to_mv(b) - 0.15
    ass.append(f"Dialogue: 0,{ts(ma)},{ts(mb)},Lyric,,0,0,0,,{{\\fad(250,250)}}{ln['lyrics']}")
for s in shots:
    d = s["dialogue"].strip()
    if not d: continue
    pieces = []
    for p in d.replace("　", " ").split("／"):
        p = p.strip()
        for pre in ("字幕（画外）", "字幕"):
            if p.startswith(pre): p = p[len(pre):].strip()
        p = p.lstrip("：: ")
        if p and not p.startswith("（随后") and not p.startswith("（林姐"): pieces.append(p)
    if not pieces: continue
    a, b = float(s["mv_in"]), float(s["mv_out"])
    step = (b - a) / len(pieces)
    for j, p in enumerate(pieces):
        ass.append(f"Dialogue: 1,{ts(a + j*step + 0.1)},{ts(a + (j+1)*step - 0.1)},Dialog,,0,0,0,,{{\\fad(200,200)}}{p}")
l08 = next(s for s in shots if s["shot_id"] == "L08_01")
ass.append(f"Dialogue: 1,{ts(float(l08['mv_in'])+0.3)},{ts(float(l08['mv_out'])-0.2)},InScene,,0,0,0,,{{\\fad(200,200)}}「在人来人往的尘世间」")
assf = os.path.join(tmp, "subs.ass")
open(assf, "w").write("\n".join(ass))

# ---------------------------------------------------------------- sound
p5 = next(s for s in shots if s["shot_id"] == "P5")
l08seg = segs["ALPHA_L08_01"]
fc = [
 f"[1:a]atrim=0:{BREAK},asetpts=PTS-STARTPTS,afade=t=out:st={BREAK-1.2}:d=1.2,adelay={int(B1_OFF*1000)}|{int(B1_OFF*1000)}[m1]",
 f"[1:a]atrim={BREAK},asetpts=PTS-STARTPTS,afade=t=in:d=0.25,adelay={int((BREAK+B3_OFF)*1000)}|{int((BREAK+B3_OFF)*1000)}[m2]",
 f"[1:a]atrim={l08seg['song_in']}:{float(l08seg['song_in'])+float(l08['duration'])-0.3},asetpts=PTS-STARTPTS,highpass=f=250,lowpass=f=3200,aecho=0.8:0.5:40:0.25,volume=0.55,afade=t=out:st={float(l08['duration'])-0.6}:d=0.3,adelay={int((float(l08['mv_in'])+0.3)*1000)}|{int((float(l08['mv_in'])+0.3)*1000)}[ktv]",
 f"[2:a]volume=0.8,adelay={int(float(p5['mv_in'])*1000)}|{int(float(p5['mv_in'])*1000)}[pl]",
 f"anoisesrc=color=brown:amplitude=0.05:duration={TOTAL}:sample_rate=48000,lowpass=f=600,"
 f"volume='if(lt(t,{B1_OFF}),0.9,if(between(t,{BREAK+B1_OFF},{BREAK+B3_OFF}),0.7,if(gt(t,{float(blocks['B4']['mv_in'])}),0.9,0)))':eval=frame[room]",
 f"anoisesrc=color=pink:amplitude=0.03:duration={TOTAL}:sample_rate=48000,highpass=f=1500,"
 f"volume='if(between(t,{BREAK+B1_OFF},{BREAK+B3_OFF}),1,0)':eval=frame[rain]",
 f"[m1][m2][ktv][pl][room][rain]amix=inputs=6:normalize=0,atrim=0:{TOTAL},afade=t=out:st={TOTAL-2}:d=2[a]",
]
inputs = ["-i", MASTER, "-i", PLUCK if os.path.exists(PLUCK) else MASTER]
run(["ffmpeg", "-v", "error", "-y", "-i", picture] + inputs + [
     "-filter_complex", ";".join(fc) + f";[0:v]subtitles={assf}:fontsdir={os.path.dirname(FONT)}[v]",
     "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "256k",
     "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", OUT])
with open(os.path.splitext(OUT)[0] + "_report.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(["shot_id", "picture_source", "file", "note"]); w.writerows(report)
print("done:", OUT, f"({TOTAL:.2f}s)")
print("clips:", sum(1 for r in report if r[1] == "clip"), " keyframes:", sum(1 for r in report if r[1] == "keyframe"), " placeholders:", sum(1 for r in report if r[1] == "placeholder"))
