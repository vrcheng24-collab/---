#!/usr/bin/env python3
"""Assemble the v8 MV from the shot list (10 s cold open -> continuous song -> 20 s epilogue).

For every shot in 03_分镜清单.csv (in order) the picture comes from, in priority:
  1. a generated clip   clips/ALPHA_<clip_from or shot_id>*.mp4   (first match in sort order; rename the pick to sort first)
     flash cuts and match cuts reuse another shot's clip from clip_in seconds
  2. the keyframe image frames/<basename of frame_image>  (slow push-in)
  3. a placeholder card with the shot id and action      (animatic)
Lip-sync clips are assumed to be generated with the matching audio slice (which starts 0.5 s before the line),
so their in-point is offset by the handle plus the shot's position inside the line.

Transitions: hard cut; flash cut (two overexposed frames); 0.6 s dissolve (the shot before is extended under it).
Sound: the master from mv 10 s without a break, room tone under the cold open and the epilogue. Lyrics and dialogue go in as
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
XF = 0.6                                       # dissolve length
FONT = os.path.join(ROOT, "mv", "fonts", "serif600.ttf")
FONT_R = os.path.join(ROOT, "mv", "fonts", "serif400.ttf")
MASTER = os.path.join(HERE, "audio", "_master_decoded.wav")
if not os.path.exists(MASTER):
    MASTER = "/root/.claude/uploads/244b6930-24ca-5e89-bb8e-bcf0d6db12f0/1dd96bd4-_____.mp3"
OUT = args.out or os.path.join(HERE, "out", "远去的列车_v8_" + ("animatic" if not glob.glob(os.path.join(args.clips, "*.mp4")) else "cut") + ".mp4")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

shots = list(csv.DictReader(open(os.path.join(HERE, "03_分镜清单.csv"), encoding="utf-8-sig")))
segs = {r["segment_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "audio", "audio_segments.csv"), encoding="utf-8-sig"))}
lines = list(csv.DictReader(open(os.path.join(HERE, "audio", "song_lines.csv"), encoding="utf-8-sig")))
blocks = {r["block_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "04_时间轴段落.csv"), encoding="utf-8-sig"))}
SONG_AT = float(blocks["B1"]["mv_in"])
SONG_END = float(blocks["B1"]["mv_out"])
TOTAL = float(blocks["B2"]["mv_out"])

def run(cmd):
    subprocess.run(cmd, check=True)

def find_clip(name):
    return sorted(glob.glob(os.path.join(args.clips, f"ALPHA_{name}_*.mp4")) + glob.glob(os.path.join(args.clips, f"ALPHA_{name}.mp4")))

def find_frame(s):
    if not s["frame_image"]: return ""
    base = os.path.basename(s["frame_image"].split("（")[0].split("；")[0].strip())
    cand = glob.glob(os.path.join(args.frames, "**", base), recursive=True) + glob.glob(os.path.join(args.frames, f"{s['shot_id']}.*"))
    return cand[0] if cand else ""

tmp = tempfile.mkdtemp(prefix="v8_")
vf_fit = f"scale={W}:{IH}:force_original_aspect_ratio=increase,crop={W}:{IH},pad={W}:{H}:0:{BAR}:black,fps={FPS},format=yuv420p"
by_id = {s["shot_id"]: s for s in shots}
report = []
runs = [[]]                                    # runs of hard/flash cuts, joined to each other by dissolves
for i, s in enumerate(shots):
    sid = s["shot_id"]
    nxt = shots[i + 1] if i + 1 < len(shots) else None
    dissolve_next = nxt is not None and nxt["transition"].startswith("叠化")
    dur = float(s["mv_out"]) - float(s["mv_in"]) + (XF if dissolve_next else 0.0)
    flash = s["transition"].startswith("闪切")
    pop = ",eq=brightness=0.35:contrast=0.8:enable='lt(t,0.09)'" if flash else ""
    out = os.path.join(tmp, f"{i:03d}.mp4")
    owner = s["clip_from"] or sid
    clip = find_clip(owner)
    frame = find_frame(s) or (find_frame(by_id[owner]) if owner in by_id else "")
    if clip:
        if s["clip_in"]:
            start = float(s["clip_in"])
        else:
            start = 0.0
            seg = segs.get(s["audio_segment_id"])
            if seg and s["song_in"]:
                start = float(seg["handle_in"]) + float(s["song_in"]) - float(seg["song_in"])
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-i", clip[0], "-t", f"{dur:.3f}", "-an",
             "-vf", vf_fit + pop + f",tpad=stop_mode=clone:stop_duration={dur:.3f}", "-t", f"{dur:.3f}",
             "-c:v", "libx264", "-crf", "18", "-preset", "medium", out])
        report.append((sid, "clip", os.path.basename(clip[0]), f"in {start:.2f}s"))
    elif frame:
        n = max(1, round(dur * FPS))
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", frame, "-t", f"{dur:.3f}",
             "-vf", f"scale={W}:{IH}:force_original_aspect_ratio=increase,crop={W}:{IH},"
                    f"zoompan=z='1+0.04*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{IH}:fps={FPS},"
                    f"pad={W}:{H}:0:{BAR}:black,format=yuv420p" + pop,
             "-c:v", "libx264", "-crf", "18", "-preset", "medium", out])
        report.append((sid, "keyframe", os.path.basename(frame), "still + push-in"))
    elif sid == "END":                         # black; the title is a subtitle event
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:d={dur:.3f}:r={FPS}",
             "-vf", "format=yuv420p", "-t", f"{dur:.3f}", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", out])
        report.append((sid, "black", "", "title card"))
    else:
        txt = os.path.join(tmp, f"{i:03d}.txt")
        wrap = "\n".join(textwrap.wrap(s["action"], 26)[:3])
        tag = f"{s['transition']} ← {s['clip_from']}" if s["clip_from"] else s["transition"]
        with open(txt, "w") as f:
            f.write(f"{sid}　·　{s['story_time']}　·　{tag}{'　·　机器人演绎' if s['robot_performance'] else ''}\n\n{wrap}\n\n素材：{s['source_asset_id']}")
        fs = 30 if not args.preview else 22
        bg = "0x2a2620" if flash else ("0x101418" if s["story_time"].startswith("现在") else "0x15171a")
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={bg}:s={W}x{IH}:d={dur:.3f}:r={FPS}",
             "-vf", f"drawtext=fontfile={FONT_R}:textfile={txt}:fontcolor=0xd8d2c4:fontsize={fs}:line_spacing={fs//2}:x=(w-tw)/2:y=(h-th)/2,"
                    f"pad={W}:{H}:0:{BAR}:black,format=yuv420p" + pop,
             "-t", f"{dur:.3f}", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", out])
        report.append((sid, "placeholder", "", ""))
    if s["transition"].startswith("叠化") and runs[-1]:
        runs.append([])
    runs[-1].append((out, float(s["mv_in"])))

# concat each run, then chain the runs with dissolves (the run before carries XF extra seconds)
run_files = []
for k, r in enumerate(runs):
    lst = os.path.join(tmp, f"run{k:02d}.txt")
    with open(lst, "w") as f:
        f.write("\n".join(f"file '{p}'" for p, _ in r))
    rf = os.path.join(tmp, f"run{k:02d}.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", rf])
    run_files.append((rf, r[0][1]))
picture = os.path.join(tmp, "picture.mp4")
if len(run_files) == 1:
    os.replace(run_files[0][0], picture)
else:
    inp, fc, prev = [], [], "0:v"
    for k, (rf, _) in enumerate(run_files):
        inp += ["-i", rf]
    for k in range(1, len(run_files)):
        lab = f"x{k}"
        fc.append(f"[{prev}][{k}:v]xfade=transition=fade:duration={XF}:offset={run_files[k][1]:.3f}[{lab}]")
        prev = lab
    run(["ffmpeg", "-v", "error", "-y"] + inp + ["-filter_complex", ";".join(fc), "-map", f"[{prev}]",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-r", str(FPS), picture])

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
 f"Style: VO,Noto Serif SC,{fsD},&H00B8D8F0,&H000000FF,&H00000000,&H80000000,0,1,0,0,100,100,1,0,1,1.5,1,2,80,80,{BAR+30},1",
 f"Style: Title,Noto Serif SC,{fsL+14},&H00E8EEF0,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,12,0,1,0,0,5,40,40,0,1",
 "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
]
for ln in lines:
    a, b = float(ln["song_in"]) + SONG_AT, float(ln["song_out"]) + SONG_AT - 0.15
    ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},Lyric,,0,0,0,,{{\\fad(250,250)}}{ln['lyrics']}")

def clean(p):
    """'字幕（老周）：xx' -> ('Dialog', '老周：xx'); '问：xx' / '答：xx' -> ('VO', 'xx')"""
    p = p.replace("　", " ").strip()
    if p.startswith("字幕"): p = p[2:].strip()
    if p.startswith("IV"): p = p.split("：", 1)[1] if "：" in p else p
    p = p.lstrip("：: ").strip()
    if p.startswith("（") and "）" in p:
        who, rest = p[1:].split("）", 1)
        p = (who if who != "画外" else "") + rest
        p = p.lstrip("：: ") if who == "画外" else p
    if p.startswith("问：") or p.startswith("答："):
        return "VO", p[2:]
    return "Dialog", p
for s in shots:
    d = s["dialogue"].strip()
    if not d: continue
    pieces = [clean(p) for p in d.split("／") if p.strip()]
    a, b = float(s["mv_in"]), float(s["mv_out"])
    step = (b - a) / len(pieces)
    for j, (st, p) in enumerate(pieces):
        ass.append(f"Dialogue: 1,{ts(a + j*step + 0.1)},{ts(a + (j+1)*step - 0.1)},{st},,0,0,0,,{{\\fad(200,200)}}{p}")
end = next((s for s in shots if s["shot_id"] == "END"), None)
if end:
    ass.append(f"Dialogue: 2,{ts(float(end['mv_in'])+0.2)},{ts(TOTAL-0.2)},Title,,0,0,0,,{{\\fad(600,600)}}远去的列车")
assf = os.path.join(tmp, "subs.ass")
open(assf, "w").write("\n".join(ass))

# ---------------------------------------------------------------- sound
ms = int(SONG_AT * 1000)
fc = [
 f"[1:a]asetpts=PTS-STARTPTS,adelay={ms}|{ms}[m]",
 f"anoisesrc=color=brown:amplitude=0.05:duration={TOTAL}:sample_rate=48000,lowpass=f=600,"
 f"volume='if(lt(t,{SONG_AT}),0.9,if(lt(t,{SONG_AT+3}),0.9*({SONG_AT+3}-t)/3,if(gt(t,{SONG_END}),0.9*min(1,(t-{SONG_END})/2),0)))':eval=frame[room]",
 f"[m][room]amix=inputs=2:normalize=0,atrim=0:{TOTAL},afade=t=out:st={TOTAL-2}:d=2[a]",
]
run(["ffmpeg", "-v", "error", "-y", "-i", picture, "-i", MASTER,
     "-filter_complex", ";".join(fc) + f";[0:v]subtitles={assf}:fontsdir={os.path.dirname(FONT)}[v]",
     "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "256k",
     "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", OUT])
with open(os.path.splitext(OUT)[0] + "_report.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(["shot_id", "picture_source", "file", "note"]); w.writerows(report)
print("done:", OUT, f"({TOTAL:.2f}s)")
print("clips:", sum(1 for r in report if r[1] == "clip"), " keyframes:", sum(1 for r in report if r[1] == "keyframe"), " placeholders:", sum(1 for r in report if r[1] == "placeholder"))
