# Test MV "real-robot performance" package: grouped Seedance prompts with real-robot constraints and real scale,
# vocal cut list (cut from the user's own separated vocal stem), and a draft motion table for the physical robot.
# Outputs: 03_分组分镜与视频提示词.md, 03_分组清单.csv, 04_人声切片表.csv, 05_实体机器人动作表_v0.csv
import csv, json, math, os, subprocess, array

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LINES = [(r["line_id"], float(r["song_in"]), float(r["song_out"]), r["lyrics"])
         for r in csv.DictReader(open(os.path.join(ROOT, "v8", "audio", "song_lines.csv"), encoding="utf-8-sig"))]
SONG_END = 240.456
COLD = 12.0                                  # cold open length; song starts at mv 12 s
H_ROBOT = 3.5                                # metres, to be confirmed by the user

# ------------------------------------------------------------------ shared prompt blocks
REAL = (f"她是一台真实存在的大型演出机器人，约 {H_ROBOT:.1f} 米高，双脚固定在一个黑色钢制底座上，底座后面拖着粗线缆；"
        "她不会走路，不会挪步，腿和腰以下始终不动。能动的只有：头部左右转和上下点（舵机一格一格地动，起步快、到位硬停、有一点回弹）、"
        "下颌开合、叠层眼睑快门片、链条眉毛、镜头眼光圈、耳侧涡轮、双臂和手指（右手扫弦，左手换和弦，慢而稳），上身最多前倾或后仰 10 度。"
        "所有动作都有重量和惯性，速度比人慢。")
SCALE = (f"真实比例：她比人大得多。成年工作人员站在她身旁，头顶只到她的腰；灯光师站在约 2 米高的铝梯顶上，才和她的肩膀一样高；"
         "她的头比一个成年人的上半身还宽；她抱的黄色电吉他比一个成年人还长。镜头里只要有人，就必须保持这个比例。")
FACE = ("她的脸由银色金属面板拼成：上唇、鼻子、颊板固定不动，只有下唇和下巴连成的下颌绕铰链开合，嘴唇是青色硬壳，不噘、不收圆、不卷；"
        "表情只来自链条眉毛的上抬、叠层眼睑快门片的落下和光圈的收放。")
LOOK = ("外观以 @图片1 为准：青黄银三色机械外壳、黄色头盔和翼片、蓝紫色发光镜头眼、青色嘴唇、耳侧涡轮，胸前和腿上有 ALPHA 字样涂装。")
DOC = ("真实演出现场的纪录片：黑色演播室，地上有胶带标记和线缆，灯架、三脚架、监视器，穿黑衣的工作人员；"
       "手持摄影机，跟焦，偶尔被前景的人和器材挡住一下；光线和颜色像实拍，不像 CG。"
       "电影质感：暖色顶光和舞台追光，冷色轮廓光，薄烟，35mm 胶片颗粒，2.39:1 宽银幕，暗部偏青绿，高光偏暖黄。")
NO = ("不要：走路、迈步、跳跃、腿部动作、弯腰下蹲；比例错误（人和她一样高）；软嘴唇、噘嘴、圆口、舌头、牙齿、面板变形裂开；"
      "人类皮肤；卡通、玩具、3D 渲染感；字幕和文字；慢动作；转场特效。")
SND_SING = "@音频1 是她的演唱，口型与它同步；视频不要生成声音。"
SND_NONE = "视频不要生成声音。"

def refs(face=True, guitar=True, light="K13"):
    r = [("实拍定妆图", "她的外观和真实材质（第一步做的定妆图或实拍照片）"),
         ("比例图", "她和工作人员的真实比例（第一步做的比例图）")]
    if face: r.append(("合法状态卡", "她面部机械动作的全部合法状态（test10 的状态卡）：只在这些状态之间过渡"))
    r.append((light, "演播室光影、人群和胶片质感的参考（不要复制它的构图）"))
    if guitar: r.append(("新吉他卡", "黄色电吉他"))
    return r

G = []
def group(**k): G.append(k); return k

group(id="P0", title="冷开场·她被推上场", model="2.0", dur=12, song=None, light="K17",
      shots=[(0, 4, "全景，平视 35mm：四个工作人员推着她的底座进入演播室，人只到她的腰；她低着头，眼睛的光是暗的。"),
             (4, 8, "仰拍：灯光师老杨站在铝梯顶上调灯，正好和她的肩膀一样高；他转头看她。"),
             (8, 12, "近景：她的眼睛亮起来，光圈张开；头一格一格地抬起来，转向老杨，微微点头致意；老杨笑着抬了抬手。")],
      use="成片 0:00–0:12，冷开场，只有环境声。")
group(id="P1", title="前奏与开口", model="2.5", dur=28, song=(0.00, 27.60), light="K13",
      shots=[(0, 5, "手部特写：她的金属手指扫弦弹前奏，琴弦震动，吉他比旁边工作人员的身体还宽。"),
             (5, 10, "全景，低机位广角：她站在底座上弹前奏，工作人员一个个停下手里的事，抬头看她，人只到她的腰。"),
             (10, 14.4, "中近景：她低着头，链条眉毛内侧微抬，眼睑快门片落下一层。"),
             (14.4, 21, "特写：她唱第一句，下颌一开一合，口腔里的机构若隐若现。"),
             (21, 28, "过肩：越过梯子上老杨的肩膀拍她的脸，她唱第二句，头一格一格地转向镜头。")],
      use="歌曲 0–27.6 秒（前奏、第 1–2 句）。")
group(id="P2", title="第3–6句", model="2.5", dur=26, song=(27.60, 53.60), light="R05",
      shots=[(0, 6, "中景：她唱第三句，头微微抬起，耳侧涡轮转动；画面前景有一个工作人员的背影，只到她的腰。"),
             (6, 12, "特写：她唱第四句，光圈慢慢收小，眼睑快门片落下一层。"),
             (12, 18, "反应：主持人林姐坐在监视器旁，抬头看她，慢慢放下手卡。"),
             (18, 26, "仰拍中近景：她唱第五、六句，上身微微前倾，左手换和弦。")],
      use="歌曲 27.6–53.6 秒。")
group(id="P3", title="第7–10句", model="2.5", dur=27, song=(53.60, 80.30), light="K17",
      shots=[(0, 7, "侧面中景：她唱第七句，头一格一格地转向一侧，像在人群里找一个人。"),
             (7, 13, "特写：她唱“真心的人又能有几个”，下颌开合，最后停住。"),
             (13, 19, "全景，从观众席后方拍：一排排人的后脑勺，舞台上的她比所有人都高出一大截。"),
             (19, 27, "特写：她的手指在琴弦上，按弦的金属指节有细微的伺服颤动。")],
      use="歌曲 53.6–80.3 秒。")
group(id="P4", title="第11–12句", model="2.0", dur=14, song=(80.30, 94.20), light="K13",
      shots=[(0, 7, "近景：她唱第十一句，眉毛内侧上抬，眼睑半落。"),
             (7, 14, "特写：她唱第十二句，句尾左手离开琴颈，五指慢慢合拢，像握着什么。")],
      use="歌曲 80.3–94.2 秒。")
group(id="P5", title="间奏·机械细节", model="2.5", dur=30, song=None, light="R05",
      shots=[(0, 6, "特写：她颈部的舵机和连杆随着头部转动一格一格地动。"),
             (6, 12, "近景：梯子上的老杨慢慢摘下一只手套。"),
             (12, 18, "特写：她的叠层眼睑快门片一层层落下，又一层层抬起。"),
             (18, 24, "低机位：她的底座和粗线缆，地面随着她的扫弦轻微震动，灰尘在追光里浮动。"),
             (24, 30, "全景：她闭着眼弹间奏，工作人员在她脚边坐下来听，显得很小。")],
      use="间奏 94.2–124.05 秒，不对口型。")
group(id="P6", title="第13–16句", model="2.5", dur=27, song=(124.05, 150.70), light="K17",
      shots=[(0, 7, "中近景：她唱第十三句，追光从头顶打下，薄烟里有光柱。"),
             (7, 14, "特写：她唱第十四句，光圈收小。"),
             (14, 20, "过肩：越过工作人员的肩膀仰拍她，人的后脑勺在画面下方很小。"),
             (20, 27, "特写：她唱第十五、十六句，眼睑快门片缓缓落下一层，头微微低下。")],
      use="歌曲 124.05–150.7 秒。")
group(id="P7", title="第17–20句", model="2.5", dur=27, song=(150.70, 177.40), light="K13",
      shots=[(0, 7, "全景，侧面：她弹唱，追光打在她身上，梯子上的老杨在画面边缘只到她的肩膀。"),
             (7, 14, "特写：她唱第十八句，链条眉毛整条微抬。"),
             (14, 20, "手部特写：右手扫弦越来越有力。"),
             (20, 27, "特写：她唱第十九、二十句，头一格一格地转向镜头。")],
      use="歌曲 150.7–177.4 秒。")
group(id="P8", title="第21–24句·高潮", model="2.5", dur=27, song=(177.40, 204.25), light="K13",
      shots=[(0, 7, "低机位广角仰拍：她仰头唱，背后是梯子上老杨的剪影和顶光，显得非常高大。"),
             (7, 14, "全景：工作人员们一个个站起来，人头只到她的腰。"),
             (14, 20, "特写：她唱第二十三句，眉毛抬起、眼睛全开、光圈全开，耳侧涡轮转得很快。"),
             (20, 27, "仰拍特写：她唱第二十四句的最高音，下颌开到最大并停住，上身微微后仰。")],
      use="歌曲 177.4–204.25 秒。")
group(id="P9", title="第25–28句·收", model="2.5", dur=28, song=(204.25, 231.45), light="R05",
      shots=[(0, 7, "近景：她唱第二十五句，头一格一格地低下来，手越弹越慢。"),
             (7, 14, "反应：林姐眼眶发红，一滴泪落在手卡上。"),
             (14, 21, "手部特写：她不再扫弦，两根金属手指在琴身上轻轻敲拍子。"),
             (21, 28, "特写：她唱最后一句，眼睑快门片缓缓落下大半，光圈重新张开。")],
      use="歌曲 204.25–231.45 秒。")
group(id="P10", title="尾奏·掌声与鞠躬", model="2.0", dur=12, song=None, light="R05",
      shots=[(0, 4, "近景：最后一个和弦结束，梯子上的老杨第一个鼓掌。"),
             (4, 12, "全景：工作人员都站起来鼓掌；她慢慢向他们鞠了一躬——只有上身和头一格一格地前倾，腿和底座不动，人只到她的腰。")],
      use="尾奏 231.45–240.46 秒和掌声。")
group(id="P11", title="收工", model="2.0", dur=12, song=None, light="K17",
      shots=[(0, 6, "全景：演播室的灯一盏盏关掉，工作人员给她盖上一块防尘布，布只盖到她的胸口。"),
             (6, 12, "近景：防尘布下，她的眼睛的光慢慢暗下去，最后一点蓝光熄灭。")],
      use="结尾。")

for g in G:
    assert (g["model"] == "2.0" and g["dur"] <= 15) or (g["model"] == "2.5" and g["dur"] <= 30), g["id"]
    assert g["shots"][0][0] == 0 and abs(g["shots"][-1][1] - g["dur"]) < 1e-6
    if g["song"]: assert g["song"][1] - g["song"][0] <= g["dur"] + 1e-6, g["id"]

def lyr(g):
    a0, b0 = g["song"]; out = []
    for lid, a, b, t in LINES:
        if min(b, b0) - max(a, a0) < 0.6: continue
        out.append((lid, max(0.0, a - a0), min(b, b0) - a0, t))
    return out

def prompt(g):
    rs = refs(face=g["song"] is not None, light=g["light"])
    p = ["参考：" + "；".join(f"@图片{i+1} 是{why}" for i, (k, why) in enumerate(rs)) + "。" + ("@音频1 是她的演唱。" if g["song"] else "")]
    p += [LOOK, REAL, SCALE, FACE, DOC, f"一共 {len(g['shots'])} 个镜头，按时间硬切："]
    for i, (a, b, s) in enumerate(g["shots"]): p.append(f"镜头{i+1}（{a:.1f}–{b:.1f} 秒）：{s}")
    if g["song"]:
        p.append("演唱：" + "；".join(f"{a:.1f}–{b:.1f} 秒唱「{t}」" for _, a, b, t in lyr(g)) +
                 "。只有她的脸在画面里时才对口型；手部、全景和反应镜头里歌声照常继续。" + SND_SING)
    else:
        p.append(SND_NONE)
    p.append(NO)
    return "\n".join(p)

# ------------------------------------------------------------------ outputs
L = []; w = L.append
w("# 实体演出测试版：分组分镜与视频提示词\n")
w(f"> {len(G)} 组，共 {sum(g['dur'] for g in G)} 秒素材；成片约 {COLD + SONG_END + 12:.0f} 秒。比例按她约 {H_ROBOT} 米高来写（待你确认）。")
w("> 上传顺序就是 @图片 的编号。“实拍定妆图”“比例图”是第一步要先做的两张图；“合法状态卡”是 test10 的那张。\n")
w("| 组 | 内容 | 模型 | 时长 | 母带时间 | 人声切片 |\n|---|---|---|---|---|---|")
for g in G:
    w(f"| {g['id']} | {g['title']} | {g['model']} | {g['dur']} 秒 | {'%.2f–%.2f' % g['song'] if g['song'] else '—'} | {'人声_' + g['id'] + '.mp3' if g['song'] else '不传'} |")
w("")
for g in G:
    w(f"## {g['id']}　{g['title']}")
    w(f"**Seedance {g['model']} · {g['dur']} 秒 · 21:9 · 生成声音关闭**　　{g['use']}\n")
    w("**上传**")
    for i, (k, why) in enumerate(refs(face=g["song"] is not None, light=g["light"])): w(f"- @图片{i+1}：{k}")
    if g["song"]:
        w(f"- @音频1：`人声_{g['id']}.mp3`（{g['dur']} 秒，从你的人声分轨里按切片表切出）")
    w("\n**提示词**\n```\n" + prompt(g) + "\n```\n")
open(os.path.join(HERE, "03_分组分镜与视频提示词.md"), "w").write("\n".join(L))

with open(os.path.join(HERE, "03_分组清单.csv"), "w", newline="", encoding="utf-8-sig") as f:
    wr = csv.writer(f); wr.writerow(["group", "title", "model", "duration_s", "song_in", "song_out", "mv_in", "shots", "prompt"])
    mv = 0.0
    for g in G:
        mvin = (COLD + g["song"][0]) if g["song"] else (0.0 if g["id"] == "P0" else None)
        wr.writerow([g["id"], g["title"], "Seedance " + g["model"], g["dur"], *(("%.2f" % g["song"][0], "%.2f" % g["song"][1]) if g["song"] else ("", "")),
                     "" if mvin is None else "%.2f" % mvin, len(g["shots"]), prompt(g)])
with open(os.path.join(HERE, "04_人声切片表.csv"), "w", newline="", encoding="utf-8-sig") as f:
    wr = csv.writer(f); wr.writerow(["file", "group", "stem_in_s", "stem_out_s", "pad_to_s", "lyrics_in_clip"])
    for g in G:
        if not g["song"]: continue
        wr.writerow([f"人声_{g['id']}.mp3", g["id"], "%.2f" % g["song"][0], "%.2f" % g["song"][1], g["dur"],
                     "；".join(f"{a:.1f}–{b:.1f} {t}" for _, a, b, t in lyr(g))])

# ------------------------------------------------------------------ draft motion table for the physical robot (mv timeline, 25 fps)
FPS = 25
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "v8", "audio", "_master_decoded.wav"), "-af",
                      "highpass=f=300,lowpass=f=3500", "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
x = array.array("f"); x.frombytes(raw); hop = 80                                  # 100 Hz envelope
env = [10 * math.log10(sum(v * v for v in x[i:i + hop]) / hop + 1e-12) for i in range(0, len(x) - hop, hop)]
def sung(t): return any(a <= t < b - 0.2 for _, a, b, _ in LINES)
SECTION = [("A1", 14.4, 39.8, "tender"), ("B1", 40.9, 66.8, "tender"), ("C1", 67.6, 93.6, "lift"), ("间奏", 93.6, 124.4, "inst"),
           ("A2", 124.4, 149.9, "tender"), ("B2", 151.0, 177.4, "tender"), ("C2", 177.6, 203.5, "high"), ("尾段", 204.5, 231.3, "closing")]
def section(t):
    for name, a, b, mood in SECTION:
        if a <= t < b: return name, mood
    return ("前奏" if t < 14.4 else "尾奏"), "inst"
EXPR = {"tender": (0.55, 0.0, 35, 55), "lift": (0.4, 0.3, 25, 70), "high": (0.8, 0.7, 10, 95), "closing": (0.3, 0.0, 60, 70), "inst": (0.2, 0.0, 30, 80)}
# servo-filtered jaw from the vocal-band envelope (draft: the user's clean vocal stem will replace the master here)
jaw, pos, vel = [], 0.0, 0.0
wn, zeta, vmax, dt = 2 * math.pi * 7.0, 0.55, 9.0, 0.001
target = [min(1, max(0, (d + 24) / 11)) ** 0.8 if sung(k / 100) else 0.0 for k, d in enumerate(env)]
for i in range(int(SONG_END / dt)):
    k = min(len(target) - 1, int((i * dt + 0.04) * 100))
    acc = wn * wn * (target[k] - pos) - 2 * zeta * wn * vel
    vel = max(-vmax, min(vmax, vel + acc * dt)); pos += vel * dt
    if pos < 0: pos, vel = 0.0, -vel * 0.25
    if i % int(1 / (dt * FPS)) == 0: jaw.append(pos)
starts = [a for _, a, _, _ in LINES]
def head(t):                                                                   # stepped yaw toward alternating sides per line
    yaw, pitch = 0.0, 0.0
    for n, s in enumerate(starts):
        if t >= s: yaw = (8 if n % 2 else -8) * (1 if n % 4 < 2 else 0.5)
    name, mood = section(t)
    if mood == "high": pitch = 8
    if mood == "closing": pitch = -6
    return yaw, pitch
rows, sy, sp = [], 0.0, 0.0
RATE = 40.0 / FPS                                                              # neck servo speed limit, deg per frame
for f_ in range(int((COLD + SONG_END + 24) * FPS)):
    t_mv = f_ / FPS; t = t_mv - COLD
    if t < 0:
        name, mood = "冷开场", "inst"; j = 0.0; yaw, pitch = (0.0, -15.0) if t_mv < 8 else (10.0, 0.0); strum = 0
    elif t > SONG_END:
        name, mood = "掌声/收工", "closing"; j = 0.0; yaw, pitch = 0.0, -12.0 if t - SONG_END < 12 else -20.0; strum = 0
    else:
        name, mood = section(t); i = min(len(jaw) - 1, int(t * FPS)); j = jaw[i] * 9.0; yaw, pitch = head(t)
        strum = 0 if name == "尾段" and 217.8 <= t < 224.3 else 1
    sy += max(-RATE, min(RATE, yaw - sy)); sp += max(-RATE, min(RATE, pitch - sp)); yaw, pitch = sy, sp
    bi, bo, lid, iris = EXPR[mood]
    rows.append([f_, f"{t_mv:.2f}", f"{max(t, 0):.2f}" if 0 <= t <= SONG_END else "", name, f"{j:.2f}", f"{yaw:.1f}", f"{pitch:.1f}",
                 lid, f"{bi:.2f}", f"{bo:.2f}", iris, strum, 1 if (name == "尾段" and 217.8 <= t < 224.3) else 0])
with open(os.path.join(HERE, "05_实体机器人动作表_v0.csv"), "w", newline="", encoding="utf-8-sig") as f:
    wr = csv.writer(f)
    wr.writerow(["frame_25fps", "mv_time_s", "song_time_s", "section", "jaw_deg(0-9)", "neck_yaw_deg", "neck_pitch_deg",
                 "upper_lid_pct(0open-100closed)", "brow_inner(0-1)", "brow_outer(0-1)", "iris_open_pct", "right_arm_strum(0/1)", "finger_tap(0/1)"])
    wr.writerows(rows)
print(len(G), "groups,", sum(g["dur"] for g in G), "s;", len(rows), "motion frames")
