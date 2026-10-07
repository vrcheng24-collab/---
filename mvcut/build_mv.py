#!/usr/bin/env python3
"""ALPHA《远去的列车》首版 MV：可复现的剪辑脚本。

    python3 build_mv.py            # 渲染全部（854x480 原生母版 + 歌词版 + 1080p 上采样版）
    python3 build_mv.py --edl-only # 只生成 EDL/CSV，不渲染

时间线 = 歌曲时间：完整母带从 0 秒开始，结尾加 3 秒片尾卡。
每条镜头只写源片、入点和“出点或到达时间”，脚本按顺序串起来；
标了 anchor 的镜头必须精确落在指定的歌曲时间（对口型），否则报错。
"""
import csv, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "ALPHA_导演素材", "ALPHA_导演素材")
OUT = os.path.join(HERE, "out")
SEG = os.path.join(HERE, "work", "seg")
FPS = 24
W, H = 854, 480
MASTER = os.path.join(SRC, "09_整首音乐候选", "远去的列车.mp3")
LINES = os.path.join(HERE, "..", "v8", "audio", "song_lines.csv")
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

CLIP = {
    "B02": "01_原片_未定稿/ALPHA_B02_G03_原片.mp4", "B03": "01_原片_未定稿/ALPHA_B03_G05_原片.mp4",
    "B04": "01_原片_未定稿/ALPHA_B04_G05_原片.mp4", "B05": "01_原片_未定稿/ALPHA_B05_G06_原片.mp4",
    "B06": "01_原片_未定稿/ALPHA_B06_G07_原片.mp4", "B07": "01_原片_未定稿/ALPHA_B07_G11B_原片.mp4",
    "B09": "01_原片_未定稿/ALPHA_B09_G13_原片.mp4", "B11": "01_原片_未定稿/ALPHA_B11_G14_原片.mp4",
    "B12": "01_原片_未定稿/ALPHA_B12_G00_原片.mp4", "B13": "01_原片_未定稿/ALPHA_B13_G04_原片.mp4",
    "B14": "01_原片_未定稿/ALPHA_B14_G12_原片.mp4", "B15": "01_原片_未定稿/ALPHA_B15_G01_原片.mp4",
    "G01v2": "08_历史候选_需审片/G01_v2_14.4-22.4_原片.mp4", "G01t": "08_历史候选_需审片/G01_tail_22.4-28_原片.mp4",
}
# 生成这些演唱镜头时绑定的音频起点（歌曲时间）。镜头源时间 t 对应歌曲时间 base+t。
SYNC_BASE = {"G01v2": 14.40, "G01t": 22.40, "B13": 60.70, "B06": 137.40, "B14": 197.40}
REPEAT = 109.98  # 第二遍主歌/副歌与第一遍歌词、旋律相同，整体晚 109.98 秒（L09→L21 等）

# 调色：现在（演出）/ 回忆 / 春天
GRADE = {
    "now": "eq=contrast=1.05:saturation=0.93:gamma=0.98,colorbalance=rs=-0.02:bs=0.03:rh=0.03:bh=-0.03",
    "mem": "eq=contrast=0.93:saturation=0.80:brightness=0.012,colorbalance=rs=0.05:gs=0.015:bs=-0.04:rm=0.03:bm=-0.03,curves=all='0/0.035 1/0.97'",
    "spring": "eq=contrast=0.97:saturation=0.90,colorbalance=rh=0.02:bh=-0.02,curves=all='0/0.02 1/0.98'",
}
OPS = {
    "crop_b06": "crop=632:356:111:62,scale=854:480:flags=lanczos",           # 去掉 B06 前 6 秒的大圆形暗边
    "punch": "crop=iw/1.12:ih/1.12,scale=854:480:flags=lanczos",             # 重复使用时换景别，避免同一画面
    "blur_sign": ("split[a][b];[b]crop=172:118:330:64,boxblur=7:2[s];[a][s]overlay=330:64,"
                  "split[c][d];[d]crop=80:80:600:160,boxblur=10:2[t];[c][t]overlay=600:160"),  # B09 站牌与告示可读文字
}

# (源, 入点, 出点或None, 到达时间或None, 速度, 调色, 操作, 标记, 说明)
# 出点和到达时间二选一可省：给出点+速度→自动算长度；给到达时间且速度=None→按出点拟合速度；给到达时间且出点=None→按速度裁出点。
E = []
def s(src, i, o=None, until=None, speed=1.0, grade="now", ops=(), tags=(), note=""):
    E.append(dict(src=src, i=i, o=o, until=until, speed=speed, grade=grade, ops=list(ops), tags=list(tags), note=note))

# ---------------- 前奏 0–14.4：演出前的场地，她注意到身边的人，闪回旧工坊
s("B12", 0.00, until=3.83, tags=["fadein"], note="开场全景：工业演出场地，她坐在支撑座上，工作人员在准备")
s("B12", 3.93, until=7.86, note="年轻场务抬头看她，她把注意力转向他")
s("B15", 0.00, until=14.40, grade="mem", note="回忆入口：同一种坐姿，在老周的旧工坊，工人在理线，老周在后面看着")
# ---------------- A1 14.4–40：她开口唱
s("G01v2", 0.00, until=22.40, tags=["sync"], note="L01 望着你坐上远去的列车（对口型，原绑定位置）")
s("G01t", 0.00, until=25.36, tags=["sync"], note="L02 汽笛声将悲伤情绪淹没（对口型）")
s("B14", 22.75, until=28.00, note="观众背影：工坊里的人在听")
s("B07", 9.83, until=33.19, note="L03 全景：灯光、举着手机的人群")
s("B14", 0.00, until=40.06, note="L04 工坊中全景，她坐着弹唱（距离较远，不作逐字口型）")
# ---------------- B1 40–60.7：回忆，学琴
s("B15", 6.63, until=46.56, grade="mem", note="L05 想为你唱一首昨日的歌：老周俯身看她弹琴")
s("B03", 6.04, until=52.56, grade="mem", note="L06 老周在工作台边教她按弦")
s("B07", 0.00, until=57.18, grade="mem", note="L07 老周给她检修头部")
s("B14", 12.83, until=60.70, note="回到现在：琴手特写，接副歌")
# ---------------- C1 60.7–87.7：副歌，整段按原绑定位置播放（源片内部已有 5 个镜头）
s("B13", 0.00, until=87.74, tags=["sync", "anchor:60.70"], note="L08–L11：脸（对口型）→全景→低角度→流泪的观众→脸（对口型）")
# ---------------- L12 + 间奏 87.7–124.4：被遗弃与被找回，老周开始忘事
s("B04", 0.00, 2.62, until=93.59, speed=None, grade="mem", note="L12 终有某天还会再见的：仓库里盖着篷布的她（慢放）")
s("B04", 2.71, 8.04, speed=0.80, grade="mem", note="老周掀开篷布，她醒来先找他的脸（0.8x）")
s("B07", 4.71, 9.75, speed=0.85, grade="mem", note="他扶着她的手按弦（0.85x）")
s("B14", 16.35, 18.79, note="现在：间奏里她的手在弹")
s("B03", 0.00, 3.83, speed=0.75, grade="mem", note="老周在冰箱里找到钥匙，想不起为什么（0.75x）")
s("B13", 10.92, 16.92, speed=0.90, tags=["reuse"], note="现在：低角度弹奏（0.9x，重复使用）")
s("B15", 13.13, 15.04, until=124.38, speed=None, grade="mem", note="老周看着她（慢放），接离别")
# ---------------- A2 124.4–151.4：离别与空站台
s("B05", 0.00, 5.17, speed=0.85, grade="mem", note="L13 望着你坐上远去的列车：车窗里的老周，她挥手（0.85x）")
s("B05", 5.25, 10.04, until=137.40, speed=None, grade="mem", note="L14 汽笛声：列车开走，雨中站台（慢放）")
s("B06", 0.00, 6.17, grade="mem", ops=["crop_b06"], tags=["sync", "anchor:137.40"], note="L15 站台上忽然一阵风吹过：黄昏空站台全景（裁掉圆形暗边，1.35x 放大）")
s("B06", 6.17, 14.04, grade="mem", tags=["sync"], note="L16 一滴泪在我的眼角滑落：站台中景演唱（对口型）")
# ---------------- B2 151.4–176.7：一个人，被围观
s("B02", 11.08, 15.04, grade="mem", note="L17 地下通道里没人听的真人乐手")
s("B09", 5.75, 8.04, grade="mem", note="她被绑在平板车上运走（腿与支柱）")
s("B02", 0.00, 5.12, grade="mem", note="L18 举着手机笑着围观她的人")
s("B12", 0.00, 3.83, tags=["reuse"], ops=["punch"], note="L19 现在：演出前的场地（重复使用，换景别）")
s("B12", 3.93, until=170.68, tags=["reuse"], ops=["punch"], note="场务抬头看她（重复使用，换景别）")
s("B13", 0.00, 6.04, tags=["sync", "reuse", "anchor:170.68"], ops=["punch"], note="L20 真心的人又能有几个：与 L08 同词同旋律，按 109.98 秒平移对口型")
# ---------------- C2 176.7–197.4：副歌第二遍，演出与记忆闪回交叉
s("B13", 6.04, 8.32, tags=["reuse"], note="L21 全景")
s("B15", 9.50, 11.10, grade="mem", tags=["reuse"], note="闪回：老周")
s("B05", 1.50, 3.10, grade="mem", tags=["reuse"], note="闪回：车窗挥手")
s("B13", 8.32, 10.41, tags=["reuse"], note="L22 全景续")
s("B04", 4.60, 6.20, grade="mem", tags=["reuse"], note="闪回：篷布下醒来")
s("B03", 8.00, 9.60, grade="mem", tags=["reuse"], note="闪回：教琴")
s("B14", 25.39, 27.04, note="观众背影")
s("B06", 10.60, until=191.35, grade="mem", tags=["reuse"], note="闪回：空站台演唱")
s("B13", 20.67, until=197.40, tags=["sync", "reuse", "anchor:191.35"], note="L23 亲爱的朋友不必难过：与 L11 同词，平移对口型")
# ---------------- 尾段 197.4–231.3：重逢
s("B14", 0.00, 3.00, tags=["sync", "reuse", "anchor:197.40"], note="L24 终有某天还会再见的（原绑定位置）")
s("B14", 18.88, 22.67, until=204.36, speed=None, note="揭示：老周和女儿坐在观众里")
s("B14", 6.96, 12.75, tags=["sync", "anchor:204.36"], note="L25 流着泪唱完了这首歌：她的脸（对口型）")
s("B11", 0.00, 3.50, note="L26 希望你会永远记得我：老周在人群里听着")
s("G01v2", 3.89, 8.04, tags=["reuse"], note="她在追光里继续唱（不作逐字口型）")
s("B03", 0.00, 3.83, grade="mem", tags=["reuse"], note="L27 在某个冬夜无眠的时刻：深夜冰箱前的老周")
s("B15", 6.63, until=224.31, grade="mem", tags=["reuse"], note="老周俯身看她")
s("B09", 0.00, 1.83, speed=0.50, grade="spring", note="L28 在某个春暖花开的时刻：春天的小站，她在平板车上（0.5x）")
s("B09", 1.92, 5.67, grade="spring", ops=["blur_sign"], note="老周和年轻人在她身边（站牌文字模糊处理）")
s("B11", 3.50, 8.04, speed=0.50, tags=["fadeout"], note="尾奏：老周站起来鼓掌（0.5x），渐黑")

SONG_END = 240.456
ENDCARD = 3.0

def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)

def resolve():
    t = 0.0
    for k, e in enumerate(E):
        e["start"] = t
        if e["until"] is not None and e["o"] is None:
            e["o"] = e["i"] + (e["until"] - t) * e["speed"]
        elif e["until"] is not None and e["speed"] is None:
            e["speed"] = (e["o"] - e["i"]) / (e["until"] - t)
        e["end"] = t + (e["o"] - e["i"]) / e["speed"]
        src_len = dur(os.path.join(SRC, CLIP[e["src"]]))
        assert 0 <= e["i"] < e["o"] <= src_len + 1e-3, (k, e["src"], e["i"], e["o"], src_len)
        assert 0.30 <= e["speed"] <= 1.0001, (k, e["speed"])
        for tag in e["tags"]:
            if tag.startswith("anchor:"):
                assert abs(float(tag[7:]) - t) < 0.5 / FPS, (k, "anchor", tag, t)
        if "sync" in e["tags"]:  # 对口型镜头：源时间与歌曲时间的对应
            base = SYNC_BASE[e["src"]]
            song_at = base + e["i"]
            shift = t - song_at
            assert abs(shift) < 0.5 / FPS or abs(shift - REPEAT) < 0.5 / FPS, (k, "sync drift", shift)
            e["sync_shift"] = round(shift, 3)
        t = e["end"]
    assert abs(t - 240.80) < 0.05, t  # 画面覆盖整首歌（240.456 秒），尾奏镜头渐黑后进入片尾卡
    return t

def section(t):
    for name, a in (("片尾", 240.46), ("尾奏", 231.25), ("尾段", 197.4), ("副歌2", 176.7), ("导歌2", 151.0), ("主歌2", 124.38),
                    ("间奏", 93.59), ("副歌1", 60.7), ("导歌1", 40.0), ("主歌1", 14.43), ("前奏", 0)):
        if t >= a - 1e-6: return name

def lyric(t):
    for r in csv.DictReader(open(LINES, encoding="utf-8-sig")):
        if float(r["song_in"]) <= t + 0.5 < float(r["song_out"]): return r["lyrics"]
    return ""

def write_edl(total):
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for k, e in enumerate(E):
        rows.append({"镜号": k + 1, "成片入点": f"{e['start']:.3f}", "成片出点": f"{e['end']:.3f}", "时长": f"{e['end'] - e['start']:.3f}",
                     "源片": CLIP[e["src"]], "源入点": f"{e['i']:.3f}", "源出点": f"{e['o']:.3f}", "速度": f"{e['speed']:.3f}",
                     "音乐位置(歌曲秒)": f"{e['start']:.2f}–{min(e['end'], SONG_END):.2f}", "段落": section(e["start"]),
                     "歌词": lyric(e["start"]), "调色": e["grade"], "画面操作": "+".join(e["ops"]),
                     "对口型": ("原位" if e.get("sync_shift") == 0 else f"平移+{e['sync_shift']}s") if "sync" in e["tags"] else "",
                     "重复使用": "是" if "reuse" in e["tags"] else "", "变速": "" if abs(e["speed"] - 1) < 1e-3 else f"{e['speed']:.2f}x",
                     "说明": e["note"]})
    rows.append({"镜号": len(E) + 1, "成片入点": f"{total:.3f}", "成片出点": f"{total + ENDCARD:.3f}", "时长": f"{ENDCARD:.3f}",
                 "源片": "（生成）黑底片尾卡", "说明": "片名与“首版候选”字样；此时歌曲已结束"})
    with open(os.path.join(OUT, "EDL_远去的列车_首版.csv"), "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
    # CMX3600 风格 EDL（视频轨，供剪辑软件参考）
    def tc(x):
        fr = round(x * FPS); return f"{fr // (3600 * FPS):02d}:{fr // (60 * FPS) % 60:02d}:{fr // FPS % 60:02d}:{fr % FPS:02d}"
    L = ["TITLE: ALPHA_YUANQU_DE_LIECHE_V1", "FCM: NON-DROP FRAME", ""]
    for k, e in enumerate(E):
        L.append(f"{k + 1:03d}  {e['src']:<8} V     C        {tc(e['i'])} {tc(e['o'])} {tc(e['start'])} {tc(e['end'])}")
        if abs(e["speed"] - 1) > 1e-3: L.append(f"M2   {e['src']:<8}      {e['speed'] * FPS:05.1f}                {tc(e['i'])}")
        L.append(f"* FROM CLIP NAME: {os.path.basename(CLIP[e['src']])}")
    open(os.path.join(OUT, "EDL_远去的列车_首版.edl"), "w").write("\n".join(L) + "\n")
    json.dump({"fps": FPS, "size": [W, H], "audio": {"file": os.path.relpath(MASTER, HERE), "song_start_on_timeline": 0.0,
               "status": "完整候选母带，未经用户最终确认；未拉伸、未覆盖"}, "endcard": ENDCARD,
               "shots": [{k: v for k, v in e.items()} for e in E]},
              open(os.path.join(OUT, "timeline.json"), "w"), ensure_ascii=False, indent=1)

def render_segments():
    os.makedirs(SEG, exist_ok=True)
    grain = "noise=c0s=5:c0f=t+u"
    for k, e in enumerate(E):
        f0, f1 = round(e["start"] * FPS), round(e["end"] * FPS)
        n = f1 - f0
        vf = [f"trim=start={e['i']}:end={e['o'] + 0.2}", "setpts=PTS-STARTPTS"]
        vf += [OPS[o] for o in e["ops"]]
        if abs(e["speed"] - 1) > 1e-3:
            vf += [f"setpts=PTS/{e['speed']:.5f}", f"framerate=fps={FPS}:interp_start=0:interp_end=255:scene=100"]
        vf += [f"fps={FPS}", f"scale={W}:{H}:flags=lanczos", "setsar=1", GRADE[e["grade"]], grain]
        if "fadein" in e["tags"]: vf.append("fade=t=in:st=0:d=1.2")
        if "fadeout" in e["tags"]: vf.append(f"fade=t=out:st={n / FPS - 2.4:.3f}:d=2.4")
        vf += ["tpad=stop_mode=clone:stop_duration=1", "format=yuv420p"]
        out = os.path.join(SEG, f"{k + 1:03d}.mp4")
        key = json.dumps([e["src"], e["i"], vf, n])
        if os.path.exists(out) and os.path.exists(out + ".key") and open(out + ".key").read() == key: continue  # 未改动的镜头不重渲
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(SRC, CLIP[e["src"]]), "-filter_complex", ",".join(vf),
                        "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-r", str(FPS), out], check=True)
        open(out + ".key", "w").write(key)
    # 片尾卡
    n = round(ENDCARD * FPS)
    txt = (f"drawtext=fontfile={FONT}:text='远去的列车':fontcolor=white:fontsize=34:x=(w-tw)/2:y=h/2-40,"
           f"drawtext=fontfile={FONT}:text='ALPHA':fontcolor=0xBBBBBB:fontsize=20:x=(w-tw)/2:y=h/2+12,"
           f"drawtext=fontfile={FONT}:text='首版候选 · 待确认':fontcolor=0x777777:fontsize=14:x=(w-tw)/2:y=h-40,"
           f"fade=t=in:st=0:d=0.6,fade=t=out:st={ENDCARD - 0.6}:d=0.6,format=yuv420p")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={W}x{H}:r={FPS}:d={ENDCARD}", "-vf", txt,
                    "-frames:v", str(n), "-c:v", "libx264", "-crf", "12", os.path.join(SEG, "endcard.mp4")], check=True)

def ass_subs(path):
    def t(x): return f"{int(x // 3600)}:{int(x // 60) % 60:02d}:{x % 60:05.2f}"
    L = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
         "[V4+ Styles]", "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
         "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
         "Style: Lyric,WenQuanYi Zen Hei,22,&H00F2F2F2,&H00F2F2F2,&H00000000,&H64000000,0,0,0,0,100,100,2,0,1,1.2,0.6,2,20,20,26,1", "",
         "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for r in csv.DictReader(open(LINES, encoding="utf-8-sig")):
        a, b = float(r["song_in"]), float(r["song_out"]) - 0.15
        L.append(f"Dialogue: 0,{t(a)},{t(b)},Lyric,,0,0,0,,{{\\fad(250,250)}}{r['lyrics']}")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")
    # 同时给一份 SRT
    srt = []
    for k, r in enumerate(csv.DictReader(open(LINES, encoding="utf-8-sig"))):
        def st(x): return f"{int(x // 3600):02d}:{int(x // 60) % 60:02d}:{int(x) % 60:02d},{int(round((x % 1) * 1000)) % 1000:03d}"
        srt += [str(k + 1), f"{st(float(r['song_in']))} --> {st(float(r['song_out']) - 0.15)}", r["lyrics"], ""]
    open(os.path.join(OUT, "歌词_远去的列车.srt"), "w", encoding="utf-8").write("\n".join(srt))

def assemble(total):
    lst = os.path.join(SEG, "list.txt")
    with open(lst, "w") as f:
        for k in range(len(E)): f.write(f"file '{k + 1:03d}.mp4'\n")
        f.write("file 'endcard.mp4'\n")
    video = os.path.join(SEG, "video_all.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video], check=True)
    full = total + ENDCARD
    base = os.path.join(OUT, "ALPHA_远去的列车_首版_854x480")
    # 母带从 0 秒开始，原样解码，不拉伸；尾部补静音到片尾卡结束
    common = ["-map", "0:v", "-map", "1:a", "-af", f"apad=whole_dur={full:.3f}", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
              "-t", f"{full:.3f}", "-movflags", "+faststart"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", MASTER, "-c:v", "libx264", "-preset", "slow", "-crf", "14",
                    "-pix_fmt", "yuv420p", *common, base + ".mp4"], check=True)
    ass = os.path.join(SEG, "lyrics.ass"); ass_subs(ass)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", MASTER, "-vf", f"ass={ass}:fontsdir=/usr/share/fonts/truetype/wqy",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", *common, base + "_歌词版.mp4"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base + "_歌词版.mp4", "-vf", "scale=1920:1080:flags=lanczos",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
                    os.path.join(OUT, "ALPHA_远去的列车_首版_1080p上采样_非原生高清_歌词版.mp4")], check=True)

if __name__ == "__main__":
    total = resolve()
    write_edl(total)
    print(f"{len(E)} shots, picture {total:.3f}s + endcard {ENDCARD}s; reuse {sum('reuse' in e['tags'] for e in E)}; "
          f"sync {sum('sync' in e['tags'] for e in E)}; speed-changed {sum(abs(e['speed'] - 1) > 1e-3 for e in E)}")
    if "--edl-only" not in sys.argv:
        render_segments(); assemble(total); print("done")
