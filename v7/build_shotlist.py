# v7 shot list: one source of truth -> 03_分镜清单.csv, 04_双时间轴段落.csv, 05_逐镜提示词.md
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- timeline blocks (provisional)
OPEN = 52.0      # opening, no music
CH = 48.0        # no-music chapter
BREAK = 150.50   # song pauses here (measured RMS dip, see audio/)
SONG_END = 240.456
EPI = 28.0
B1_OFF = OPEN                     # mv = song + OPEN for song part 1
B3_OFF = OPEN + CH                # mv = song + OPEN + CH for song part 2
EPI_START = SONG_END + B3_OFF

# ---------------------------------------------------------------- identity / stage text
A_CN = "ALPHA 是同一位成年女性机器人：银色分片机械脸、蓝紫色虹膜、青色嘴唇、耳侧圆形涡轮，脖子、手指和关节都是完整机械结构，没有任何人类皮肤。"
A_EN = "ALPHA is the same adult female humanoid robot throughout: a segmented brushed-silver robotic face, blue-violet irises, teal lips, round silver turbine ear units, a fully mechanical neck, fingers and joints, no human skin anywhere."
STAGE = {
 "B1":     ("B1 初生本体：银白色机身带青色点缀，不穿外衣，不戴假发。", "B1 prototype body: pearl-white and silver segmented metal body with teal accents, no clothing, no wig."),
 "COAT":   ("B1 本体＋B3：黑色长羽绒服、灰色针织围巾、黑裤黑靴，不戴假发。", "B1 body with B3 outfit: long black puffer down coat, grey knitted scarf, black trousers and boots, no wig."),
 "LOW":    ("B1 本体＋B3 黑色长羽绒服和灰围巾，戴一顶廉价、不合适的黑色假发（假发不与耳侧涡轮穿插）。", "B1 body with the long black puffer coat and grey scarf, wearing a cheap ill-fitting black synthetic wig that sits around, not through, the round ear units."),
 "V2":     ("夜场 v2：黑色露肩短上装和短裙（不透的内衬）、饰链和耳饰，露出的肩、臂、腰、腿全是机械材质，戴廉价黑假发。", "Nightclub v2: black off-shoulder cropped top and short skirt with opaque lining, small chains and earrings; every exposed shoulder, arm, waist and leg is mechanical metal; cheap black wig."),
 "V2OUT":  ("室外 v2：敞开的黑色长羽绒服里是夜场舞台装，露出的部分全是机械材质，戴廉价黑假发。", "Outdoor v2: the long black puffer coat open over the nightclub stage outfit; everything exposed is mechanical metal; cheap black wig."),
 "TRANS":  ("过渡：B1 本体＋黑色长羽绒服＋灰围巾，不戴假发（摘假发之后到天台）。", "Transitional: B1 body, long black puffer coat and grey scarf, no wig (after taking off the wig, through the rooftop)."),
 "MATURE": ("成熟（已确认，用于现在时演播室和春天）：青黄银机械外壳、头部黄色翼片，同一张银色分片脸，不穿外套。", "Mature (confirmed for the present-day studio and spring): cyan, lemon-yellow and silver armoured shell with yellow head fins, the same segmented silver face, no coat."),
 "NONE":   ("画面里没有 ALPHA。", "ALPHA is not in this shot."),
}
GUIT = {
 "G-B": ("G-B 蜂蜜原木色木吉他（深棕背板、磨损、琴边金属修补、拾音改装和黑色线）", "the G-B honey-colored acoustic guitar with a dark brown back, worn finish, a metal repair on the edge and a pickup jack with a black cable"),
 "Y":   ("成熟黄色机械电吉他（银色齿轮轮毂）", "the angular yellow mechanical electric guitar with a silver gear hub"),
 "-":   ("无", "none"),
}
DISG_CN = "小鹿、阿凯、默默始终是普通人外观：不出现金属、线路或机械结构，影子和倒影正常。"
DISG_EN = "Xiaolu, Akai and Momo always look like ordinary people: no metal, wires or machinery, normal shadows and reflections."
VID_CN = "保持首帧的构图、机位、景别、人物大小、朝向、光线和色调；只做一个主动作；真实时间流速，不要慢动作、不要转场、不要字幕、不要背景音乐。"
VID_EN = "Keep the first frame's composition, camera position, framing, subject size, facing, lighting and grade; one main action only; real-time speed, no slow motion, no transitions, no subtitles, no background music."
IMG_CONS = "不改脸部身份；不加人类皮肤；不把配角机械化；不改构图和人物大小；不加无关道具；不生成牙齿和舌头；不做动画或渲染风格；新增中文字后期合成。"
MJ = "35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism, 2020s northeast China"
MJP = "--ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy, human skin on the robot"
ALPHA_EN = {
 "B1": "an adult female humanoid robot with a pearl-white and silver segmented metal body with teal accents, a segmented brushed-silver robotic face, blue-violet irises, teal lips and round silver turbine ear units",
}
ALPHA_EN["COAT"] = ALPHA_EN["B1"] + ", wearing a long black puffer down coat, a grey knitted scarf, black trousers and black boots"
ALPHA_EN["TRANS"] = ALPHA_EN["COAT"] + ", old scratches on her metal face"
ALPHA_EN["LOW"] = ALPHA_EN["COAT"] + ", a cheap crooked black synthetic wig on her metal head"
ALPHA_EN["MATURE"] = "an adult female humanoid robot with a glossy cyan, lemon-yellow and silver armoured shell, yellow head fins, a segmented brushed-silver robotic face, blue irises and teal lips"

S = []
def shot(**k): S.append(k)

def song(i, o): return dict(song_in=i, song_out=o)

# ================================================================ OPENING (现在访谈, no music)
t = 0.0
def op(d):
    global t
    r = (t, t+d); t += d; return r
STU_LIGHT_CN = "黑色空棚，一盏暖色落地灯为主光，摄影机和工作人员藏在暗处，空气里有薄烟"
STU_LIGHT_EN = "a dark empty studio, one warm floor lamp as key light, cameras and crew hidden in shadow, light haze"

shot(id="O1", src="O1", asset="（新出图）", story="现在访谈", stage="TRANS", mv=op(4.0), lyrics="", guitar="-",
 camera="大特写，85mm，固定", action="音频师用白胶带把领夹麦贴在她胸前的青黄外壳上，胶带翘起，又按了一次", motion="胶带边缘翘起", light="侧面一盏工作灯，背景全黑", emotion="她一动不动，视线平视前方",
 protect="音频师的手", mouth="否", lip="否", seg="", dlg="音频师（画外）：说两句，试一下音量。／ALPHA（画外）：一、二、三。", snd="胶带撕扯声、空调底噪",
 img_cn="新出图。大特写：音频师的手用白胶带把一枚黑色领夹麦贴在 ALPHA 胸前的青黄色外壳上。",
 img_en="extreme close-up, a sound engineer's hands using white gaffer tape to stick a tiny black lavalier microphone onto the glossy cyan and yellow chest plate of {A}, the tape peeling off the smooth metal and being pressed down again, a single side work light, black background, 85mm, shallow depth of field",
 an_cn="0–2 秒：胶带贴上去，边缘翘起；2–4 秒：手指把胶带重新按平，又多贴了一道。她的胸口没有呼吸起伏。", an_en="0–2s: the tape goes on and its edge lifts; 2–4s: the fingers press it flat and add a second strip. Her chest shows no breathing movement.")
shot(id="O2", src="O2", asset="（新出图）", story="现在访谈", stage="NONE", mv=op(5.0), lyrics="", guitar="-",
 camera="中景，40mm，固定", action="音频师盯着电平表和频谱，她的声音电平平稳，没有呼吸和底噪的起伏；制片俯身指着屏幕说话", motion="屏幕上的电平条跳动", light="屏幕光照在两人脸上，四周暗", emotion="音频师困惑，制片不耐烦",
 protect="真人工作人员", mouth="否（制片背光侧脸）", lip="否", seg="", dlg="音频师：她的声音太干净了，没有呼吸声。／制片：加点呼吸声。听着像个人。", snd="耳机漏音、按键声",
 img_cn="新出图。调音台角落，音频师戴耳机看电平表，制片俯身指屏幕，旁边小监视器里是 ALPHA 的脸。（不画成一条直线波形，原稿的技术隐喻已修正）",
 img_en="a TV studio audio desk in a dark corner, a sound engineer with headphones studying level meters and a spectrum display, a producer with a headset leaning over his shoulder pointing at the screen, a small video monitor beside them showing the silver robotic face of {A}, screen glow on their faces, cluttered cables, 40mm",
 an_cn="0–2 秒：音频师皱眉看电平表；2–5 秒：制片俯身指着屏幕说了一句话，音频师点头，伸手去推一个推子。", an_en="0–2s: the engineer frowns at the meters; 2–5s: the producer leans in, points at the screen and says something; the engineer nods and reaches for a fader.")
shot(id="O3", src="O3", asset="（新出图）", story="现在访谈", stage="TRANS", mv=op(3.0), lyrics="", guitar="-",
 camera="近景，50mm，固定", action="摄影助理把白卡贴在她的金属脸旁调白平衡", motion="白卡轻微晃动，金属脸上的反光变化", light="一盏柔光主灯，脸上强反光", emotion="她平视，像一台被校准的仪器",
 protect="摄影助理的手", mouth="是（闭合）", lip="否", seg="", dlg="摄影（画外）：反光太强，灯压一档。", snd="摄影机风扇声",
 img_cn="新出图。近景：摄影助理把一张白平衡卡贴在 ALPHA 的金属脸旁边，前景是虚焦的电影镜头，角落里的监视器显示她的脸。",
 img_en="close-up, a camera assistant holding a white balance card right next to the silver robotic face of {A}, a cinema lens blurred in the foreground, a camera monitor in the corner showing her face, harsh reflections on the metal, single soft key light, black background, 50mm",
 an_cn="0–3 秒：白卡停在她脸旁，主灯慢慢暗了一档，金属脸上的反光随之变柔；她不动。", an_en="0–3s: the card holds beside her face, the key light dims one step and the reflections on her metal face soften; she does not move.")
shot(id="O4", src="O4", asset="（新出图）", story="现在访谈", stage="TRANS", mv=op(4.0), lyrics="", guitar="-",
 camera="中景，50mm，固定", action="化妆师拿着刷子愣住，放下刷子，用擦镜布擦她的外壳", motion="化妆箱的小灯", light="一盏实用灯，暗棚", emotion="化妆师尴尬，ALPHA 平静",
 protect="化妆师（真人）", mouth="是（闭合）", lip="否", seg="", dlg="化妆师（小声）：……她不用化。", snd="布料摩擦声",
 img_cn="新出图。年轻化妆师举着化妆刷犹豫，站在坐着的 ALPHA 面前，打开的化妆箱在旁边。",
 img_en="a young Chinese makeup artist holding a makeup brush in mid-air and hesitating, standing in front of {A} who sits on a chair, an open makeup case beside the artist, one practical lamp, dark interview studio, 50mm",
 an_cn="0–2 秒：化妆师举着刷子停住；2–4 秒：她放下刷子，掏出擦镜布，轻轻擦了擦 ALPHA 脸侧的外壳。", an_en="0–2s: the artist freezes with the brush raised; 2–4s: she lowers it, takes out a lens cloth and gently wipes the side of ALPHA's metal face.")
shot(id="P1c", src="P1c", asset="K22（old / new 二选一）", frame="02_latest_frames/005_K22_P1c_演播室贴设备标签_OLD_前期过渡候选.png（推荐）；006_…_NEW_成熟造型候选.png", story="现在访谈", stage="TRANS", mv=op(4.0), lyrics="", guitar="-",
 camera="中景，原图机位，固定", action="场务把编号标签按在她肩头，拍了拍", motion="背景人影走动", light="原图：冷蓝背景墙、顶光", emotion="她的头极轻微地转向肩上的标签",
 protect="场务（真人）、桌上的嘉宾牌", mouth="否（远）", lip="否", seg="", dlg="制片（画外）：跟它不用客气，它听不懂。", snd="对讲机杂音",
 img_cn="用现有候选，不重出。嘉宾牌“ALPHA（设备）”后期合成。", img_en="",
 an_cn="0–2 秒：场务把标签按在她肩头，像给器材贴签一样拍了两下；2–4 秒：场务走开，ALPHA 的头极轻微地转向自己肩上的标签。", an_en="0–2s: the crew member presses the label onto her shoulder and pats it twice like tagging equipment; 2–4s: the crew member walks off and ALPHA's head turns very slightly toward the label.")
shot(id="P1b", src="P1b", asset="（新出图）", story="现在访谈", stage="NONE", mv=op(4.0), lyrics="", guitar="-",
 camera="中近景，仰拍，50mm", action="老杨在梯子上拧灯，低头对徒弟说话，扯了扯嘴角", motion="灯架轻晃，光束里的浮尘", light="头顶影视灯硬光，脸上深阴影", emotion="平淡、自嘲",
 protect="老杨（真人）、梯子", mouth="是", lip="对白（待录音）", seg="DLG_P1b", dlg="老杨：这棚明年全换自动灯，咱俩就调这最后一年了。", snd="灯具金属声",
 img_cn="新出图。仰拍：五十多岁的灯光师站在铝梯上拧影视灯，低头对扶梯的徒弟说话。",
 img_en="low angle, a Chinese lighting technician in his fifties with grey hair, stubble and a dark work vest standing on an aluminium ladder adjusting a film light, looking down and talking to a young assistant holding the ladder, a tired self-mocking half smile, hard light from above, black lighting grid, haze, 50mm",
 an_cn="0–3 秒：他低头对徒弟说了一句话；3–4 秒：他扯了扯嘴角，抬头继续拧灯。", an_en="0–3s: he looks down and says one line to his assistant; 3–4s: a wry half smile, then he looks up and keeps turning the knob.")
shot(id="P2", src="P2", asset="（新出图）", story="现在访谈", stage="NONE", mv=op(3.0), lyrics="", guitar="-",
 camera="俯拍，85mm 长焦，隔着窗玻璃", action="楼下雨里的抗议人群几乎不动", motion="雨水顺玻璃流下", light="阴天灰白光，湿街面", emotion="压抑",
 protect="", mouth="否", lip="否", seg="", dlg="", snd="远处的口号声、雨声",
 img_cn="新出图。隔着高楼窗玻璃俯拍：阴雨天，街口一群人撑黑伞举着被雨打湿的纸牌。牌子上的字后期合成。",
 img_en="high angle through a rain-streaked office window, a crowd of dozens of people with black umbrellas holding soaked handwritten protest signs on a street corner below, grey overcast daylight, wet glossy street, blurred window frame in the foreground, 85mm telephoto compression",
 an_cn="0–3 秒：雨水顺着玻璃往下流，楼下人群几乎不动，有人把牌子举高了一点。", an_en="0–3s: rain runs down the glass; the crowd below barely moves, one person lifts a sign a little higher.")
shot(id="O6", src="O6", asset="（新出图）", story="现在访谈", stage="TRANS", mv=op(4.0), lyrics="", guitar="G-B",
 camera="全景，40mm 变形宽银幕，固定", action="场记在前景打板；林姐翻着手卡，ALPHA 坐在对面，椅背上叠着老周那条旧灰围巾；她身后支架上立着黄色电吉他，挂着小纸牌", motion="打板", light=STU_LIGHT_CN, emotion="安静、准备",
 protect="林姐（真人）", mouth="否（远）", lip="否", seg="", dlg="场记：《对面》第四十七期，第一条。", snd="打板声",
 img_cn="新出图。访谈布景全景：两把旧扶手椅面对面，一盏落地灯；林姐翻手卡，成熟形象的 ALPHA 坐在对面，椅背上叠着一条旧灰围巾，身后支架上是黄色电吉他。",
 img_en="wide shot of a dark minimalist interview set in a large black studio, two worn armchairs facing each other and a single floor lamp, a Chinese female interviewer in her early forties with short bob hair and a black suit flipping through cue cards, {A} sitting in the other armchair with an old grey knitted scarf folded over its back, behind the robot {G} on a stand with a small paper tag, a clapperboard snapping in the foreground, cinema cameras and crew half hidden in the shadows, 40mm anamorphic",
 an_cn="0–1 秒：场记在前景打板；1–4 秒：场记退出画面，林姐合上手卡抬起头。", an_en="0–1s: the clapperboard snaps in the foreground; 1–4s: it leaves the frame and the interviewer closes her cue cards and looks up.")
shot(id="O7", src="O7", asset="（新出图）", story="现在访谈", stage="TRANS", mv=op(6.0), lyrics="", guitar="-",
 camera="过肩，50mm，固定", action="越过 ALPHA 的肩拍林姐提问，ALPHA 回答（只见后脑和耳侧涡轮）", motion="落地灯光", light=STU_LIGHT_CN, emotion="林姐平静、专业",
 protect="林姐（真人）", mouth="林姐是／ALPHA 否", lip="对白（待录音）", seg="DLG_O7", dlg="林姐：先介绍一下你自己吧。／ALPHA：我叫 ALPHA。是……第一个的意思。", snd="空调底噪",
 img_cn="新出图。从 ALPHA 身后过肩拍：前景是她的金属后脑和耳侧涡轮（虚焦），对面扶手椅上的林姐正在提问。",
 img_en="over-the-shoulder shot from behind {A}, the back of her silver metal head and turbine ear blurred in the foreground, across from her a Chinese female interviewer in her early forties with short bob hair and a black suit asking a question with calm eyes, a single floor lamp between them, dark interview studio, 50mm",
 an_cn="0–3 秒：林姐提问；3–6 秒：前景的 ALPHA 头部极轻微地动了一下，在回答，林姐安静地听。", an_en="0–3s: the interviewer asks a question; 3–6s: ALPHA's head in the foreground moves very slightly as she answers; the interviewer listens.")
shot(id="O8", src="O8", asset="（新出图）", story="现在访谈", stage="TRANS", mv=op(6.0), lyrics="", guitar="-",
 camera="近景，85mm，固定", action="林姐问出第一题后，ALPHA 长久地沉默", motion="背景虚焦人影互相看了一眼", light="落地灯照亮她半边金属脸，另一半在暗处", emotion="沉默、无法回答，眼睛慢慢垂下",
 protect="领夹麦和白胶带", mouth="是（闭合不动）", lip="否（沉默）", seg="", dlg="林姐（画外）：你的悲伤，是真的吗？　（随后沉默约 4 秒）", snd="只有空调声",
 img_cn="新出图。近景：ALPHA 坐在旧扶手椅里，胸前贴着领夹麦，落地灯照亮半边金属脸，背景是虚焦的工作人员剪影。",
 img_en="close-up of {A} sitting in a worn armchair in a dark interview studio, silent, her eyes lowered, a lavalier mic taped to her chest, warm floor lamp light on half of her metal face, the other half in darkness, out-of-focus crew silhouettes in the background, 85mm, tension and silence",
 an_cn="0–2 秒：她听完问题，一动不动；2–5 秒：眼睛慢慢垂下，嘴保持闭合；5–6 秒：背景里两个工作人员互相看了一眼。", an_en="0–2s: she hears the question and stays still; 2–5s: her eyes slowly lower, mouth stays closed; 5–6s: two crew members in the background glance at each other.")
shot(id="O9", src="O9", asset="（新出图）", story="现在访谈", stage="TRANS", mv=op(5.0), lyrics="", guitar="G-B",
 camera="中景，50mm，固定", action="她慢慢转头看向身后支架上的黄色电吉他，说出一句话", motion="落地灯光在吉他上", light=STU_LIGHT_CN, emotion="犹豫，然后决定",
 protect="吉他、纸牌", mouth="是", lip="对白（待录音）", seg="DLG_O9", dlg="ALPHA：我可以……唱出来吗？　（林姐看了她很久，点头）", snd="椅子轻响",
 img_cn="新出图。中景：ALPHA 坐在扶手椅里，慢慢转头看向身后支架上的黄色电吉他，前景是虚焦的林姐。",
 img_en="medium shot, {A} in an armchair slowly turning her head to look at {G} standing on a stand behind her with a small paper tag, the floor lamp light catching the guitar, the interviewer blurred in the foreground, dark studio, 50mm",
 an_cn="0–2 秒：她慢慢转头看向吉他；2–5 秒：她转回来，对着林姐说了一句短短的话。", an_en="0–2s: she slowly turns to look at the guitar; 2–5s: she turns back and says one short line to the interviewer.")
shot(id="P4", src="P4", asset="（新出图）", story="现在访谈", stage="TRANS", mv=op(2.5), lyrics="", guitar="G-B",
 camera="中景，50mm", action="小鹿把黄色电吉他递到她手里", motion="", light=STU_LIGHT_CN, emotion="小鹿平静，ALPHA 接住",
 protect="小鹿（真人外观）", mouth="否", lip="否", seg="", dlg="", snd="吉他碰到椅子的轻响",
 img_cn="新出图。小鹿（实习场务，牛仔外套，工作牌）把黄色电吉他递给坐在扶手椅里的 ALPHA。",
 img_en="a 23-year-old Chinese girl with a round face, a low ponytail, a faded blue denim jacket and a crew badge handing {G} to {A} who sits in an armchair, the robot's metal hands reaching for it, warm floor lamp light, dark interview studio, 50mm",
 an_cn="0–2.5 秒：小鹿把吉他递过去，ALPHA 的金属手接住琴颈。", an_en="0–2.5s: Xiaolu hands over the guitar and ALPHA's metal hands take the neck.")
shot(id="P5", src="P5", asset="K11（old）", frame="02_latest_frames/033_K11_PF2_手部与吉他特写_OLD_前期过渡候选.png", story="现在访谈", stage="TRANS", mv=op(1.5), lyrics="", guitar="G-B",
 camera="特写，原图，固定", action="拨弦手拨动一根弦", motion="琴弦振动", light="原图", emotion="—",
 protect="按弦手与拨弦手不互换、指板方向", mouth="否", lip="否", seg="", dlg="", snd="一声拨弦（母带从这里进入）",
 img_cn="复用 K11 old（与 PF2 同一画面，不新增素材）。", img_en="",
 an_cn="0–1.5 秒：拨弦的机械手指拨动一根弦，琴弦振动，另一只手不动。", an_en="0–1.5s: the picking hand plucks one string, the string vibrates, the fretting hand stays still.")
assert abs(t-OPEN) < 1e-6, t

# ================================================================ SONG part 1
def sg(i, o): return (i+B1_OFF, o+B1_OFF)
shot(id="S01", src="S01", asset="（新出图；备用 K21 new）", story="现在访谈", stage="TRANS", song=(0.0,14.43), lyrics="（前奏）", guitar="G-B",
 camera="全景，40mm 变形宽银幕，极慢推近", action="她在落地灯下弹起前奏，暗处的工作人员一个个放慢、停下", motion="烟、光", light=STU_LIGHT_CN+"；另有一束顶光", emotion="专注",
 protect="工作人员真人", mouth="否（远）", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。访谈布景全景：成熟形象的 ALPHA 抱着黄色电吉他坐在扶手椅里开始弹，周围暗处的工作人员停下动作。",
 img_en="wide shot of a dark minimalist interview set, {A} sitting in a worn armchair with {G} across her lap starting to play, a single floor lamp and one overhead spotlight cutting through haze, crew members slowly stopping in the shadows around her, 40mm anamorphic",
 an_cn="0–14 秒：她低头弹前奏；暗处的人一个接一个放慢脚步、停下；镜头极慢地推近。", an_en="0–14s: she plays the intro with her head down; crew members in the dark slow down and stop one by one; the camera pushes in very slowly.")
shot(id="S02", src="S02", asset="K20（old / new）", frame="02_latest_frames/007_K20_S02_面部与吉他极近景_OLD_前期过渡候选.png（推荐）", story="现在访谈", stage="TRANS", song=(14.43,21.03), lyrics="望着你坐上远去的列车", guitar="G-B",
 camera="极近景，原图，缓慢推近", action="她低头唱出第一句", motion="眼环轻微明暗", light="原图暖色背景光斑", emotion="克制、像在回忆",
 protect="木吉他、灰围巾", mouth="是", lip="是", seg="ALPHA_S02_01", dlg="", snd="母带",
 img_cn="用现有候选。", img_en="",
 an_cn="0–6.6 秒：她轻声唱出这一句，嘴唇随歌声开合（以 @音频1 为准），头微微偏向一侧，按弦的手指比人慢半拍。", an_en="0–6.6s: she sings this line softly, lips following @audio1, head tilting slightly, fretting fingers half a beat slower than a human.")
shot(id="PF1", src="PF1", asset="K21（old / new）", frame="02_latest_frames/037_K21_PF4_低角度弹唱中景_OLD_前期过渡候选.png（推荐）", story="现在访谈", stage="TRANS", song=(21.03,24.50), lyrics="汽笛声将悲伤情绪淹没（前半）", guitar="G-B",
 camera="中景，低机位，原图，固定", action="她仰头唱，身后梯子上的人影停住", motion="烟里的光柱", light="原图", emotion="投入",
 protect="背景梯子和人影", mouth="是", lip="是", seg="ALPHA_PF1_01", dlg="", snd="母带",
 img_cn="用现有候选（原稿 PF4 的 K21 改作此处 PF1）。", img_en="",
 an_cn="0–3.5 秒：她微微仰头唱，嘴唇随 @音频1 开合，扫弦的手稳定；背景梯子上的人影一动不动。", an_en="0–3.5s: she sings with her head slightly raised, lips following @audio1, steady strumming; the silhouette on the ladder behind stays still.")
shot(id="S03", src="S03", asset="（新出图）", story="现在访谈", stage="NONE", song=(24.50,27.81), lyrics="汽笛声将悲伤情绪淹没（后半）", guitar="-",
 camera="中近景，仰拍，50mm", action="老杨的手停在灯的旋钮上，慢慢转头看向她", motion="光束交错", light="身后影视灯把他勾成半剪影，舞台暖光照亮半边脸", emotion="眼睛发红，喉结动了一下",
 protect="老杨（真人）、梯子", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。仰拍：老杨停在铝梯上，一只手还搭在灯的旋钮上，转头望向舞台。",
 img_en="low angle, a Chinese lighting technician in his fifties with grey hair, stubble and a dark work vest frozen on an aluminium ladder with one hand still on a film light, slowly turning his head toward the stage, eyes slightly red, half silhouetted by the light behind him, warm stage light on one side of his face, haze, 50mm",
 an_cn="0–1.5 秒：他的手停在旋钮上；1.5–3.3 秒：他慢慢转头看向舞台，喉结动了一下。", an_en="0–1.5s: his hand stops on the knob; 1.5–3.3s: he slowly turns toward the stage and swallows.")
shot(id="S04", src="S04", asset="（新出图）", story="现在访谈", stage="TRANS", song=(27.81,33.00), lyrics="站台上忽然一阵风吹过", guitar="G-B",
 camera="中景，50mm，固定", action="制片起身要往舞台走，林姐没回头，抬手拦住他", motion="", light="两人近乎剪影，舞台暖光勾出侧脸", emotion="林姐坚决",
 protect="林姐、制片（真人）", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。林姐坐在暗处抬手拦住正要起身的制片，两人近乎剪影，远处光里是弹唱的 ALPHA。",
 img_en="a Chinese female interviewer in her early forties with short bob hair and a black suit sitting in the dark raising one hand, without looking back, to stop a producer with a headset who is getting up, both almost silhouettes, warm light from the set outlining their profiles, far in the blurred background {A} singing in a pool of light, 50mm",
 an_cn="0–2 秒：制片皱眉起身；2–3.5 秒：林姐不回头，抬手拦住；3.5–5 秒：两人都停下，看着舞台。", an_en="0–2s: the producer frowns and gets up; 2–3.5s: she raises a hand without looking back; 3.5–5s: both stop and watch the stage.")
shot(id="S05", src="S05", asset="（新出图）", story="现在访谈", stage="NONE", song=(33.00,38.00), lyrics="一滴泪在我的眼角滑落", guitar="-",
 camera="近景，85mm，焦点从手卡移到脸", action="林姐眼眶发红，一滴泪落在手卡上，墨迹晕开", motion="墨迹晕开", light="台灯暖光从下照亮手卡和下巴", emotion="克制，飞快擦掉眼泪坐直",
 protect="林姐（真人）", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。近景：林姐双手拿着手写手卡，眼眶发红。手卡上的字后期合成。",
 img_en="close-up of a Chinese female interviewer in her early forties with short bob hair holding a white handwritten cue card, her eyes red and wet, warm lamp light from below lighting the card and her chin, blurred warm bokeh behind, 85mm, restrained emotion",
 an_cn="0–2 秒：她盯着舞台，努力忍住；2–3 秒：一滴泪落在手卡上；3–5 秒：墨迹晕开，她飞快擦了一下眼角，坐直。", an_en="0–2s: she watches the stage, holding it in; 2–3s: a tear drops onto the card; 3–5s: the ink blooms, she quickly wipes her eye and sits up.")
shot(id="S06", src="S06", asset="（新出图）", story="现在访谈", stage="TRANS", song=(38.00,40.95), lyrics="（间隙）", guitar="-",
 camera="大特写，100mm，缓慢推近", action="推向她的眼睛，眼环像光圈一样转动", motion="", light="顶光，脸的下半在暗处", emotion="回忆开始",
 protect="", mouth="否（出画）", lip="否", seg="", dlg="字幕 IV1：问：第一次唱歌，是为谁唱的？", snd="母带",
 img_cn="新出图。ALPHA 的面部大特写，蓝紫色眼睛望向画外的黑暗。",
 img_en="extreme close-up of the face of {A}, blue-violet ring-shaped irises looking off-frame into the darkness, top light on brushed metal, lower half of the face in shadow, black background, 100mm",
 an_cn="0–3 秒：镜头缓慢推近她的眼睛，眼环像光圈一样慢慢转动。", an_en="0–3s: slow push into her eye; the ring iris turns slowly like an aperture.")
shot(id="S07", src="S07", asset="K24", frame="02_latest_frames/009_K24_S07_实验室与老周对视_最新候选.png", story="回忆", stage="B1", song=(40.95,47.64), lyrics="想为你唱一首昨日的歌", guitar="-",
 camera="中近景，原图，固定", action="她的眼睛第一次亮起，老周愣住，然后笑了", motion="窗外雨，台灯", light="原图：暖台灯、窗外冷蓝", emotion="老周湿了眼眶",
 protect="老周（真人）、实验室陈设", mouth="否", lip="否", seg="", dlg="字幕 IV1：答：为一个修我的人。他每天晚上放磁带，自己跟着哼，总是跑调。", snd="母带",
 img_cn="用现有候选。", img_en="",
 an_cn="0–2 秒：她的眼睛从暗到亮，第一次亮起蓝紫色光；2–6.7 秒：老周愣住，镜片上映着那点光，眼睛湿了，慢慢笑起来。", an_en="0–2s: her eyes light up blue-violet for the first time; 2–6.7s: Lao Zhou freezes with the light in his glasses, his eyes wet, then slowly smiles.")
shot(id="S08", src="S08", asset="（新出图）", story="回忆", stage="B1", song=(47.64,54.39), lyrics="想让时间停留这一刻", guitar="G-B",
 camera="特写，85mm，固定", action="老人的手覆在她的机械手指上，帮她按住 G-B 的弦", motion="灰尘", light="台灯暖光侧照", emotion="耐心",
 protect="老人的手（真人）、按弦手方向", mouth="否", lip="否", seg="", dlg="字幕（老周）：会唱歌，就有人愿意听你说话了。", snd="母带",
 img_cn="新出图。特写：满是皱纹的老人的手覆在银白色机械手指上，按在 G-B 木吉他的指板上，背景虚焦旧录音机。",
 img_en="close-up, a wrinkled old man's hand resting on top of pearl-white robotic fingers with teal joints, guiding them to press the strings of {G}, a warm tungsten desk lamp from the side, an old cassette recorder blurred in the background, dust in the light, 85mm",
 an_cn="0–4 秒：老人的手带着机械手指一根根按下去，第一下按错；4–6.7 秒：老人轻轻拍了拍她的手背，再来。", an_en="0–4s: the old hand guides the robotic fingers onto the frets one by one, the first one wrong; 4–6.7s: he pats the back of her hand and they try again.")
shot(id="S09", src="S09", asset="（新出图）", story="回忆", stage="B1", song=(54.39,61.02), lyrics="在人来人往的尘世间", guitar="G-B",
 camera="中景，35mm 手持", action="小女孩碰到她的手指，母亲把孩子拉开", motion="人流", light="商场天窗阴天柔光，偏暖", emotion="ALPHA 的手停在半空；老周的笑僵住",
 protect="孩子、母亲、老周（真人）", mouth="否", lip="否", seg="", dlg="字幕（母亲）：别碰，那是个东西。", snd="母带",
 img_cn="新出图。商场中庭小舞台，ALPHA 坐在凳子上弹 G-B 唱歌，台前孩子们，一个小女孩伸手碰她的机械手指，母亲正把她拉回去，人群最后是老周。",
 img_en="a small stage in a shopping mall atrium, {A} sitting on a stool playing {G} and singing, a crowd of children in front, a little girl touching the robot's metal fingers while her mother pulls her back with a disapproving look, a 62-year-old Chinese engineer with grey buzz-cut hair, old metal-framed reading glasses and a worn brown cardigan at the back of the crowd with his smile frozen, soft overcast skylight, slightly overexposed warm memory, 35mm handheld",
 an_cn="0–3 秒：小女孩碰到她的手指，笑了；3–5 秒：母亲一把拉回孩子，低声说了句话；5–6.6 秒：ALPHA 的手停在半空。", an_en="0–3s: the girl touches her finger and laughs; 3–5s: the mother pulls her back and mutters something; 5–6.6s: ALPHA's hand stays in mid-air.")
shot(id="S10", src="S10", asset="（新出图；演员同 R03）", story="回忆", stage="NONE", song=(61.02,67.62), lyrics="真心的人又能有几个", guitar="-",
 camera="近景，85mm 长焦，隔着人群", action="背琴包的年轻乐手握着刚挂断的手机，看向舞台", motion="前景人流", light="天窗半逆光", emotion="下颌绷紧",
 protect="年轻乐手（真人，与 R03 同一人、同一把琴）", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。与 R03 同一位真人乐手（卷发、旧外套、黑琴包），站在商场人群外看向舞台。",
 img_en="a young Chinese street musician in his late twenties with curly messy hair, stubble and an old jacket, a black guitar case on his back, standing still at the edge of a shopping mall crowd, holding a phone he just hung up, staring toward a distant stage, jaw tight, half backlit by a skylight, blurred people passing in the foreground, 85mm telephoto",
 an_cn="0–6.6 秒：他低头看了一眼手机，又抬头看向舞台，下颌绷紧；前景人流不断经过。", an_en="0–6.6s: he glances at his phone, then back at the stage, jaw tight; people keep passing in the foreground.")
shot(id="S11", src="S11", asset="（新出图）", story="回忆", stage="B1", song=(67.62,71.50), lyrics="谁不是谁今生的过客", guitar="G-B",
 camera="大全景，50mm，横移", action="黑暗中一排排手机举起，远处台上很小的 ALPHA", motion="越来越多手机举起", light="手机冷光、舞台一束小光", emotion="冷、压抑",
 protect="", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。从观众后方拍：一排排举起的手机，远处小舞台上很小的 ALPHA 在唱。",
 img_en="from behind a dark audience, rows of raised smartphones glowing cold white, silhouettes of heads, far away on a small stage a tiny {A} singing under one spotlight, haze above the crowd, cold oppressive mood, 50mm",
 an_cn="0–3.9 秒：镜头在人群后方缓慢横移，越来越多的手机举起来。", an_en="0–3.9s: slow lateral move behind the crowd as more phones rise.")
shot(id="H1", src="H1", asset="K19", frame="02_latest_frames/010_K19_H1_听证大厅俯拍全景_最新候选.png", story="回忆", stage="B1", song=(71.50,78.50), lyrics="谁的一生注定不蹉跎", guitar="-",
 camera="俯拍全景，原图", action="大屏幕投票一格格变红，她抬头看向高处", motion="人群细微动作", light="原图：顶灯只照最底下的她", emotion="渺小",
 protect="ALPHA 在画面中的小占比、人群", mouth="否", lip="否", seg="", dlg="字幕（专家）：它没有生命。它的悲伤，只是一段被训练出来的程序。", snd="母带",
 img_cn="用现有候选。", img_en="",
 an_cn="0–4 秒：顶上大屏幕的投票一格一格变红；4–7 秒：最底下的她慢慢抬头看向高处。镜头极慢下推。", an_en="0–4s: the voting screen above turns red cell by cell; 4–7s: far below, she slowly looks up at the tiers. Very slow push down.")
shot(id="IV2", src="IV2", asset="IV-A（新出图，IV1/IV2/IV5 共用）", story="现在访谈", stage="TRANS", song=(78.50,80.50), lyrics="（间隙）", guitar="-",
 camera="近景，85mm，固定", action="访谈插入：她低着头，金属手放在膝上", motion="", light="落地灯伦勃朗光，背景全黑", emotion="安静、沉重",
 protect="", mouth="是（闭合）", lip="否（字幕，无配音）", seg="", dlg="字幕 IV2：问：他们说你没有生命。／答：我不知道生命是什么。我只知道，断电的时候，很黑。", snd="母带",
 img_cn="新出图 IV-A：纪录片访谈近景，ALPHA 坐在旧扶手椅里，胸前贴领夹麦，落地灯从侧面照亮半边金属脸，背景全黑。",
 img_en="documentary interview close-up of {A} sitting in a worn armchair, a lavalier mic taped to her chest, a single warm floor lamp from the side lighting half of her metal face, pitch black background, slight film grain, 85mm, intimate and honest like a long-form TV interview",
 an_cn="0–2 秒：她低着头，眼睛的光暗了一点，嘴保持闭合。", an_en="0–2s: head lowered, the light in her eyes dims slightly, mouth closed.")
shot(id="S13", src="S13", asset="R03（保留原图）", frame="02_latest_frames/011_R03_S13_地铁广告与真人乐手_保留原图.png", story="回忆", stage="NONE", song=(80.50,83.00), lyrics="亲爱的朋友不必难过（前半）", guitar="-",
 camera="全景，原图，固定", action="没有人停下，乐手弹错一个和弦", motion="人流动态模糊", light="原图", emotion="疲惫",
 protect="真人乐手、AI MUSIC 广告，全部保持原图", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="原图保留，不替换。", img_en="",
 an_cn="0–2.5 秒：人流不停经过，乐手低头弹琴，停顿了一下又接着弹。", an_en="0–2.5s: commuters stream past; the musician falters on a chord, then keeps playing.")
shot(id="S14", src="S14", asset="（新出图）", story="回忆", stage="NONE", song=(83.00,86.00), lyrics="亲爱的朋友不必难过（后半）", guitar="-",
 camera="中近景，从冰箱里往外拍", action="老周拿着刚从冷藏室里找到的钥匙，愣住", motion="", light="冰箱冷光从下往上，厨房全黑", emotion="不安",
 protect="老周（真人）", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。深夜老厨房，从开着的冰箱里往外拍，老周拿着一串钥匙发愣。",
 img_en="late night in a small old kitchen, shot from inside an open refrigerator, a 62-year-old Chinese engineer with grey buzz-cut hair, old metal-framed reading glasses and a worn brown cardigan holding a bunch of keys he just found inside the fridge, frozen in confusion, cold fridge light from below on his face, the rest of the kitchen pitch black, rain on the window, 35mm",
 an_cn="0–3 秒：他看着钥匙，慢慢意识到什么，脸上闪过不安。", an_en="0–3s: he stares at the keys, slowly realising, unease crossing his face.")
shot(id="S16", src="S16", asset="（新出图）", story="回忆", stage="B1", song=(86.00,93.59), lyrics="终有某天还会再见的", guitar="-",
 camera="双人中景，侧面，40mm 变形宽银幕", action="老周把一颗黄色糖纸的润喉糖放进她的金属手心，她慢慢握住", motion="窗上雨", light="台灯暖光在两人之间", emotion="老周沉默很久",
 protect="老周（真人）、润喉糖", mouth="否（侧面远）", lip="否", seg="", dlg="字幕：ALPHA：他们为什么怕我？／老周：不是怕你。是怕自己被落下。", snd="母带",
 img_cn="新出图。深夜实验室，一盏台灯；ALPHA（B1）坐在工作台边，老周佝偻着坐在对面，把润喉糖放进她摊开的金属手心。",
 img_en="late night lab lit only by one warm desk lamp, {A} sitting on the edge of a workbench, a 62-year-old Chinese engineer with grey buzz-cut hair, old metal-framed reading glasses and a worn brown cardigan sitting hunched on an old chair across from her placing a yellow-wrapped throat lozenge into her open metal palm, the lamp between them, both outer sides in darkness, rain on the window, 40mm anamorphic, side view",
 an_cn="0–4 秒：老周低头搓了搓手；4–6 秒：他把糖放进她手心；6–7.6 秒：她的手指慢慢合上。", an_en="0–4s: Lao Zhou rubs his hands, head down; 4–6s: he places the lozenge in her palm; 6–7.6s: her fingers slowly close around it.")
shot(id="S18", src="S18", asset="（新出图）", story="回忆", stage="NONE", song=(93.59,96.50), lyrics="（间奏）", guitar="-",
 camera="特写，50mm", action="打印机吐出一张带红章的通知", motion="", light="日光灯冷光", emotion="冷",
 protect="", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。特写：打印机吐出一张 A4 通知，右下角红色印章（标题文字后期合成）。",
 img_en="close-up of an office printer slowly pushing out an A4 notice with a red official stamp in the corner, cold fluorescent light, grey rainy window behind, 50mm",
 an_cn="0–2.9 秒：纸从打印机里慢慢吐出，落下。", an_en="0–2.9s: the page slides out of the printer and drops.")
shot(id="S19", src="S19", asset="（新出图）", story="回忆", stage="B1", song=(96.50,102.50), lyrics="（间奏）", guitar="-",
 camera="全景，35mm，固定", action="篷布下的蓝光一点点暗下去，熄灭", motion="光柱里的灰尘、漏雨", light="高窗一道冷光柱", emotion="死寂",
 protect="", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。空仓库里一个被灰篷布盖住的人形，贴着资产编号签，篷布下透出微弱蓝光。",
 img_en="an empty old warehouse, a human-shaped figure completely covered by a grey tarp with an asset number tag, among rows of scrapped machines, a faint blue glow leaking from under the tarp, one cold shaft of light from a high window full of floating dust, roof leaking drops of water, 35mm",
 an_cn="0–6 秒：灰尘在光里慢慢飘，水滴落下；篷布下的蓝光一点点暗下去，熄灭。", an_en="0–6s: dust drifts in the light, drops fall; the blue glow under the tarp fades out.")
shot(id="S20", src="S20", asset="（新出图）", story="回忆", stage="B1", song=(102.50,108.00), lyrics="（间奏）", guitar="-",
 camera="中景，35mm 手持", action="老周掀开篷布，她的眼睛闪了两下，亮了", motion="手电光束里的灰尘", light="手电是唯一光源", emotion="老周长出一口气",
 protect="老周（真人）", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。深夜仓库，老周的背影拿着手电，掀开篷布，露出 ALPHA（B1）的头。",
 img_en="night in a dark warehouse, a 62-year-old Chinese engineer in a worn brown coat seen from behind holding a flashlight, pulling a grey tarp off a human-shaped figure, revealing the head of {A}, her eyes flickering on, the flashlight beam visible in the dust, 35mm handheld",
 an_cn="0–3 秒：他掀开篷布；3–5.5 秒：她的眼睛闪了两下，亮起来，他的肩膀松下来。", an_en="0–3s: he pulls the tarp away; 3–5.5s: her eyes flicker twice and come on; his shoulders drop with relief.")
shot(id="S21", src="S21", asset="（新出图）", story="回忆", stage="B1", song=(108.00,114.50), lyrics="（间奏）", guitar="G-B（背在身上）",
 camera="大远景，85mm 长焦，跟在后面", action="老人拖着行李箱，她背着吉他，两人并排走向雾里的小站", motion="雾", light="清晨细雨，灰蓝", emotion="沉默",
 protect="", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。清晨细雨浓雾，一条铁轨伸向小站，老人拖着行李箱和 ALPHA（B1，背着 G-B 吉他，还没有外套）背对镜头并排走，中间隔着半步。",
 img_en="extreme wide shot, early morning drizzle and thick fog in northeast China, a single railway track stretching toward a small distant station, an old man dragging a worn suitcase and {A} with {G} on her back walking side by side away from the camera half a step apart, telegraph poles fading into the fog, cold grey-blue light, 85mm telephoto",
 an_cn="0–6.5 秒：两人慢慢走远，老人放慢脚步等她。", an_en="0–6.5s: they walk slowly away; the old man slows down to wait for her.")
shot(id="H3", src="H3", asset="（新出图）", story="回忆", stage="NONE", song=(114.50,117.00), lyrics="（间奏）", guitar="-",
 camera="特写，50mm", action="雨水顺着车站告示流下，老人的手握紧行李箱拉杆", motion="雨", light="阴天冷光", emotion="无奈",
 protect="", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。车站墙上被雨打湿的告示（“机器人须按货物办理托运”后期合成），前景老人的手握着行李箱拉杆。",
 img_en="close-up of a printed notice on a railway station wall soaked by rain, water running down it, an old wrinkled hand gripping the handle of a worn suitcase in the blurred foreground, cold overcast light, 50mm",
 an_cn="0–2.5 秒：雨水顺着告示往下流，那只手握紧了一下。", an_en="0–2.5s: rain runs down the notice; the hand tightens on the handle.")
shot(id="S22a", src="S22a", asset="K25", frame="02_latest_frames/012_K25_S22a_车站老周披衣告别_最新候选.png", story="回忆", stage="COAT", song=(117.00,124.38), lyrics="（间奏）", guitar="G-B（背在身上）",
 camera="中景，原图，手持轻晃", action="老周给她拉好新买的黑羽绒服领口，把自己的灰围巾绕在她脖子上", motion="站台檐口的雨帘、蒸汽", light="原图", emotion="老周像叮嘱孩子；ALPHA 低头看着衣服",
 protect="老周（真人）、绿皮车", mouth="否", lip="否", seg="", dlg="字幕（老周）：天冷，穿上。／去唱吧。别在仓库里等我。", snd="母带",
 img_cn="用现有候选。服装交接：黑色长羽绒服是老周用最后的钱给她买的新衣，灰围巾是他自己的。", img_en="",
 an_cn="0–4 秒：老周替她拉好羽绒服的领口，把自己的灰围巾绕上她的脖子；4–7.4 秒：他拍拍她的胳膊，努力笑着，转身。", an_en="0–4s: Lao Zhou zips up the collar of her new black down coat and wraps his own grey scarf around her neck; 4–7.4s: he pats her arm, forces a smile and turns away.")
shot(id="S22b", src="S22b", asset="（新出图）", story="回忆", stage="COAT", song=(124.38,137.70), lyrics="望着你坐上远去的列车／汽笛声将悲伤情绪淹没", guitar="G-B（背在身上）",
 camera="中景，40mm 变形宽银幕，固定在站台", action="列车开走，她抬起一只手，站台上只剩她", motion="风掀起羽绒服下摆、落叶、蒸汽", light="阴天冷光，车窗里一点暖光", emotion="孤独",
 protect="绿皮车、老周（车窗内）", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。雨天站台，ALPHA（黑长羽绒服、灰围巾）的背影，一只机械手慢慢抬起；绿皮车正在开走，车窗里老人的手贴着起雾的玻璃。",
 img_en="from behind, {A} standing alone on a wet rainy rural train platform, one metal hand slowly raised, an old green train pulling away, an old man's palm pressed against the fogged train window, wind lifting dead leaves and the hem of her coat, steam drifting across the tracks, grey overcast sky, cold desaturated palette, 40mm anamorphic",
 an_cn="0–4 秒：汽笛响，车门关上，车窗里的手贴着玻璃；4–9 秒：列车慢慢开走，她抬起一只手，风掀起羽绒服下摆；9–13 秒：列车离开画面，站台上只剩她。", an_en="0–4s: whistle, doors close, a hand pressed to the window; 4–9s: the train pulls out, she raises one hand, wind lifts the hem of her coat; 9–13s: the train is gone and she stands alone.")
shot(id="S23", src="S23", asset="（新出图）", story="回忆", stage="COAT", song=(137.70,141.00), lyrics="站台上忽然一阵风吹过", guitar="-",
 camera="中景侧面，85mm", action="一滴雨顺着她脸上的金属接缝滑下", motion="细雨", light="灰白天光勾边", emotion="一动不动",
 protect="", mouth="否（侧面，闭合）", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。侧面中景：ALPHA（黑羽绒服、灰围巾）站在雨天站台望着列车离开的方向，一滴雨落在她的金属脸上。",
 img_en="medium profile shot of {A} standing on a rainy train platform looking toward where the train left, a single raindrop sliding down the seam of her silver metal face, grey sky rim light, blurred empty tracks behind, 85mm",
 an_cn="0–3.3 秒：雨滴顺着金属接缝慢慢滑下，她一动不动。", an_en="0–3.3s: the raindrop slides slowly down the metal seam; she does not move.")
shot(id="S24", src="S24", asset="（新出图：首帧 S24a ＋ 尾帧 S24b）", story="回忆", stage="COAT", song=(141.00,144.36), lyrics="（句间）", guitar="G-B（背在身上）",
 camera="大全景，24mm，三脚架固定（不晃）", action="延时：上午到黄昏，她始终不动", motion="云、光影、人和车像幻影", light="上午冷灰 → 黄昏暗橙", emotion="等待",
 protect="站台钟（11 点 → 6 点）", mouth="否", lip="否", seg="", dlg="字幕 IV3：问：你为什么会拿起吉他？／答：他走以后，站台太安静了。我需要一点声音。", snd="母带",
 img_cn="新出图两张：首帧上午细雨、钟 11 点；尾帧同机位黄昏、钟 6 点、站台灯亮。",
 img_en="extreme wide locked-off shot of an empty rural train platform in late morning drizzle, {A} standing alone in the middle looking down the tracks, a round platform clock on a pillar showing eleven o'clock, cold grey light, wet ground, 24mm  ||  END FRAME: the exact same locked-off shot at dusk, rain stopped, a thin line of dark orange light in the clouds, platform lights on, the same robot still standing in the same spot with a long shadow, the clock showing six o'clock",
 an_cn="@图片1 首帧，@图片2 尾帧。延时摄影：天光从上午变到黄昏，云快速流动，人和列车像影子一样快速来去，只有她一动不动。", an_en="@image1 first frame, @image2 last frame. Time-lapse: daylight shifts from late morning to dusk, clouds race, people and trains flicker past like shadows; only she stays still.")
shot(id="PF3", src="PF3", asset="K30", frame="02_latest_frames/013_K30_PF3_空站台坐着弹琴_最新候选.png", story="回忆", stage="COAT", song=(144.36,BREAK), lyrics="一滴泪在我的眼角滑落", guitar="G-B",
 camera="中景，原图，固定", action="她坐在长椅上，第一次弹唱这首歌", motion="风、湿地面倒影", light="原图：黄昏暗橙天边、冷白站台灯", emotion="轻声、专注",
 protect="不戴假发、木吉他", mouth="是（侧脸）", lip="可选", seg="ALPHA_PF3_01", dlg="", snd="母带，149.3 秒起淡出，150.50 暂停",
 img_cn="用现有候选。", img_en="",
 an_cn="0–6 秒：她低头拨弦，轻声唱，头慢慢转向列车离开的方向；风吹过，她没有停。", an_en="0–6s: head down, she plucks and sings softly, slowly turning toward where the train left; the wind passes and she keeps playing.")

# ================================================================ NO-MUSIC CHAPTER
c = 0.0
def ch(d):
    global c
    r = (c, c+d); c += d; return r
shot(id="L01", src="L01", asset="R02", frame="02_latest_frames/014_R02_L01_公厕镜前戴上假发_OLD_前期过渡候选.png", story="回忆", stage="LOW", ch=ch(4.0), lyrics="", guitar="-",
 camera="近景，过镜子，原图", action="她把假发往头上戴正（动作从未戴好开始）", motion="荧光灯闪烁", light="原图：病态青绿荧光", emotion="想看起来像个人",
 protect="镜中手与前景手一致；镜子里不能出现第二张脸；假发不穿过耳侧涡轮", mouth="否", lip="否", seg="", dlg="", snd="荧光灯电流声、滴水",
 img_cn="用现有候选。注意：候选是“戴到一半”的状态，动画从这里开始往下拉正。", img_en="",
 an_cn="0–2 秒：她双手把假发往下拉，扯正；2–4 秒：灯闪了一下，她拉起围巾遮住半张脸。镜中动作与前景完全同步。", an_en="0–2s: both hands pull the wig down and straighten it; 2–4s: the light flickers and she pulls the scarf up over half her face. The mirror image moves in exact sync.")
shot(id="H2", src="H2", asset="（新出图）", story="回忆", stage="LOW", ch=ch(3.5), lyrics="", guitar="-",
 camera="中景，从店里隔着起雾的玻璃门", action="面馆老板推门挥手赶走在屋檐下躲雨的她", motion="热气、雨线", light="店里暖黄，门外冷青", emotion="她点点头，走进雨里",
 protect="老板（真人）", mouth="否", lip="否", seg="", dlg="", snd="雨声、锅碗声",
 img_cn="新出图。雨夜老面馆，从店里隔着起雾的玻璃门拍，门外屋檐下躲雨的 ALPHA（黑羽绒服、灰围巾、廉价黑假发），胖老板推门挥手。告示字后期合成。",
 img_en="rainy night, seen from inside an old noodle shop through a fogged glass door, steaming bowls blurred in the foreground, outside under the dripping awning {A} sheltering from the rain, a heavy shop owner in a greasy apron pushing the door open and waving her away, warm yellow light inside, cold cyan night outside, 50mm",
 an_cn="0–2 秒：老板推门挥手；2–3.5 秒：她点点头，转身走进雨里。", an_en="0–2s: the owner pushes the door and waves her off; 2–3.5s: she nods and turns into the rain.")
shot(id="L02", src="L02", asset="K03", frame="02_latest_frames/015_K03_L02_劳务市场等待_最新候选.png", story="回忆", stage="LOW", ch=ch(3.5), lyrics="", guitar="-",
 camera="原图", action="面包车里的雇主看了她一眼，没停", motion="零工呼出白气（她没有）", light="原图", emotion="平静地等",
 protect="所有真人零工、面包车司机", mouth="否", lip="否", seg="", dlg="", snd="面包车引擎、人声",
 img_cn="用现有候选。纸板字“什么活都干 只要电”后期合成。", img_en="",
 an_cn="0–2 秒：车里的雇主看了她一眼；2–3.5 秒：他移开目光，车往前开走。周围的人都在呼白气，她没有。", an_en="0–2s: the driver glances at her; 2–3.5s: he looks away and drives on. Everyone around exhales white breath; she does not.")
shot(id="L03", src="L03", asset="K07", frame="02_latest_frames/016_K07_L03_拆解厂捧起机器人头部_最新候选.png", story="回忆", stage="LOW", ch=ch(4.0), lyrics="", guitar="-",
 camera="原图", action="她用金属手指按住同型号机器人头的眼睛，蓝光熄灭；对面的默默抬头看她", motion="焊花、烟尘", light="原图", emotion="哀悼",
 protect="默默（真人外观）", mouth="否", lip="否", seg="", dlg="", snd="切割机、焊枪",
 img_cn="用现有候选。", img_en="",
 an_cn="0–2.5 秒：她的手指轻轻合上那个头的眼睛，蓝光熄灭；2.5–4 秒：对面的男人抬头看了她一眼。", an_en="0–2.5s: her fingers gently close the head's eye and its blue light goes out; 2.5–4s: the man across looks up at her.")
shot(id="L04", src="L04", asset="K06（v2）", frame="02_latest_frames/017_K06_L04_雷雨中的输电塔_V2_最新候选.png", story="回忆", stage="V2OUT", ch=ch(3.0), lyrics="", guitar="-",
 camera="大远景，原图", action="闪电劈下，她背向镜头走向电塔", motion="闪电、暴雨", light="原图", emotion="背影的疲惫",
 protect="背向构图，不转正面", mouth="否", lip="否", seg="", dlg="", snd="雷声、暴雨",
 img_cn="用现有 v2 候选（待确认）。", img_en="",
 an_cn="0–3 秒：她背对镜头，一步一步走向电塔，闪电照亮整座塔又暗下去。", an_en="0–3s: back to camera, she trudges toward the tower; lightning lights it up, then darkness.")
shot(id="L05", src="L05", asset="K26", frame="02_latest_frames/018_K26_L05_冷库搬箱子_最新候选.png", story="回忆", stage="LOW", ch=ch(3.0), lyrics="", guitar="-",
 camera="原图", action="她背向镜头搬着箱子走过，工人们都在呼白气", motion="冷雾", light="原图", emotion="—",
 protect="背向搬箱，不转正面；真人工人", mouth="否", lip="否", seg="", dlg="", snd="冷机嗡鸣",
 img_cn="用现有候选。", img_en="",
 an_cn="0–3 秒：她背对镜头搬着箱子往前走；工人们呼出白气，她没有。", an_en="0–3s: back to camera, she carries the box forward; the workers exhale white breath, she does not.")
shot(id="L06", src="L06", asset="K31（v2）", frame="02_latest_frames/019_K31_L06_小巷黑市充电_V2_最新候选.png", story="回忆", stage="V2OUT", ch=ch(4.0), lyrics="", guitar="-",
 camera="原图", action="电贩子数钱；她靠墙，颈后接着线，眼睛慢慢亮起", motion="雨、乱线上的水珠", light="原图", emotion="得到电后的短暂放松",
 protect="电贩子（真人）", mouth="是（微笑弧度轻）", lip="否", seg="", dlg="", snd="雨、电流声",
 img_cn="用现有 v2 候选（待确认）。", img_en="",
 an_cn="0–2 秒：电贩子低头数钱；2–4 秒：她靠着湿墙，眼睛一点点亮起来，肩膀轻轻松下来。", an_en="0–2s: the dealer counts his cash; 2–4s: against the wet wall her eyes slowly brighten and her shoulders relax a little.")
shot(id="L07_01", src="L07", asset="K05（v2）", frame="02_latest_frames/021_K05_L07_红灯房间抱损坏部件_V2_最新候选.png", story="回忆", stage="V2", ch=ch(3.0), lyrics="", guitar="-",
 camera="原图", action="她蹲着，把自己掉下来的外壳碎片抱在怀里", motion="红灯", light="原图", emotion="悲伤、退缩",
 protect="背景虚影", mouth="否", lip="否", seg="", dlg="", snd="门外客人的笑声远去",
 img_cn="用现有 v2 候选（待确认）。", img_en="",
 an_cn="0–3 秒：她蹲着，慢慢把碎片抱紧，头低下去。", an_en="0–3s: crouching, she slowly hugs the broken piece closer and lowers her head.")
shot(id="L07_02", src="L07", asset="K04（v2）", frame="02_latest_frames/020_K04_L07_红灯房间靠墙坐着_V2_最新候选.png", story="回忆", stage="V2", ch=ch(3.0), lyrics="", guitar="-",
 camera="原图", action="她靠墙坐着，挤出一个苦涩的微笑", motion="红灯微闪", light="原图", emotion="苦涩、勉强的笑",
 protect="", mouth="是", lip="否", seg="", dlg="字幕 IV4：问：那时候，为什么要戴假发？／答：我想让他们以为我是人。这样，他们会听我唱完。", snd="空调声",
 img_cn="用现有 v2 候选（待确认）。", img_en="",
 an_cn="0–3 秒：她靠墙坐着，嘴角慢慢扯出一个勉强的笑，眼睛没有笑。", an_en="0–3s: sitting against the wall, the corners of her mouth pull into a forced smile; her eyes do not smile.")
shot(id="L08_01", src="L08", asset="K29（v2）", frame="02_latest_frames/022_K29_L08_包间拿麦克风演唱_V2_最新候选.png", story="回忆", stage="V2", ch=ch(6.0), lyrics="在人来人往的尘世间（画内，KTV 音箱声）", guitar="-",
 camera="原图", action="她站在包间中央拿着麦克风，职业性地笑着唱", motion="烟、电视屏幕光", light="原图", emotion="职业性的笑",
 protect="醉汉、门口的阿凯（真人外观）、酒桌", mouth="是（远）", lip="是（画内声）", seg="ALPHA_L08_01", dlg="", snd="画内：同一首歌经 KTV 音箱，压低、发闷（提案）",
 img_cn="用现有 v2 候选（待确认）。", img_en="",
 an_cn="0–6 秒：她笑着对着麦克风唱，嘴型跟 @音频1；沙发上的醉汉哄笑、举杯，门口的阿凯一动不动。", an_en="0–6s: she sings into the mic with a professional smile, lips following @audio1; the drunk men laugh and raise glasses; Akai stands motionless by the door.")
shot(id="L08_02", src="L08", asset="（新出图）", story="回忆", stage="V2", ch=ch(4.0), lyrics="", guitar="-",
 camera="近景，35mm 手持", action="醉汉拽住她的手腕，一只戴露指皮手套的手捏住了醉汉的手腕", motion="", light="紫红顶灯", emotion="醉汉的笑僵住；阿凯冷",
 protect="阿凯（真人外观，真实形态绝不出现）", mouth="否", lip="否", seg="", dlg="", snd="画内歌声戛然而止",
 img_cn="新出图。近景：醉汉的手拽着 ALPHA 的机械手腕，一只戴露指旧皮手套的男人的手从画外伸进来，捏住醉汉的手腕。",
 img_en="close-up in a purple-lit karaoke room, a drunk middle-aged man's hand gripping the mechanical wrist of {A}, a young man's hand in a worn fingerless leather glove reaching in from off-frame and clamping down on the drunk man's wrist, cigarette smoke, 35mm handheld",
 an_cn="0–2 秒：醉汉拽着她的手腕往沙发拉；2–4 秒：戴皮手套的手捏住醉汉的手腕，醉汉的手指慢慢松开。", an_en="0–2s: the drunk pulls her wrist toward the sofa; 2–4s: the gloved hand clamps his wrist and his fingers slowly let go.")
shot(id="M1", src="M1", asset="（新出图）", story="回忆", stage="LOW", ch=ch(5.0), lyrics="", guitar="-",
 camera="侧面平行跟拍，40mm 变形宽银幕", action="阿凯骑旧摩托，她坐后座，两人不说话", motion="雨、路灯一盏盏扫过、他肩背冒热气", light="橙色钠灯与冷青黑暗交替", emotion="孤独又温柔",
 protect="阿凯（真人外观）、摩托车", mouth="否", lip="否", seg="", dlg="", snd="摩托引擎、暴雨",
 img_cn="新出图。深夜大雨高架桥下，刺猬头黑皮夹克的年轻男人骑旧摩托，ALPHA（黑羽绒服、假发）坐后座。",
 img_en="late night heavy rain under an empty city overpass, a young Chinese man with spiky black hair and a worn black leather jacket riding an old modified motorcycle, {A} sitting behind him, neither speaking, faint steam rising from his shoulders in the cold rain, orange sodium streetlights sweeping across them with cold cyan darkness in between, side tracking shot, 40mm anamorphic",
 an_cn="0–3 秒：两人在雨里沉默地骑行，路灯一盏盏扫过；3–5 秒：她的手犹豫着碰了一下他的肩，又收回来，抓住后座扶手。", an_en="0–3s: they ride silently through the rain, streetlights sweeping over them; 3–5s: her hand hesitates on his shoulder, then pulls back to grip the rear handle.")
shot(id="L09_01", src="L09", asset="K01", frame="02_latest_frames/023_K01_L09_帘幕后候场唱歌_最新候选.png", story="回忆", stage="LOW", ch=ch(2.0), lyrics="", guitar="-",
 camera="原图", action="幕布后，她举起麦克风", motion="幕布缝隙外的彩色灯", light="原图", emotion="准备",
 protect="台前对口型的歌手（真人）", mouth="否", lip="否", seg="", dlg="", snd="隔着幕布的夜场声，她吸了一口“气”",
 img_cn="用现有候选。", img_en="",
 an_cn="0–2 秒：她在黑暗里慢慢把麦克风举到嘴边。", an_en="0–2s: in the dark she slowly raises the mic to her mouth.")
assert abs(c-CH) < 1e-6, c

# ================================================================ SONG part 2
shot(id="L09_02", src="L09", asset="K02", frame="02_latest_frames/024_K02_L09_侧脸对着麦克风_最新候选.png", story="回忆", stage="LOW", song=(BREAK,157.68), lyrics="想为你唱一首昨日的歌", guitar="-",
 camera="近景侧脸，原图", action="她对着麦克风唱，歌声从画内接回母带", motion="背景虚焦人群", light="原图", emotion="投入",
 protect="", mouth="是", lip="是", seg="ALPHA_L09_01", dlg="", snd="母带从 150.50 恢复（画内声渐变为全频）",
 img_cn="用现有候选。", img_en="",
 an_cn="0–7 秒：她侧脸对着麦克风唱，嘴型跟 @音频1，头随旋律轻轻前倾。", an_en="0–7s: in profile she sings into the mic, lips following @audio1, head leaning gently with the melody.")
shot(id="S25", src="S25", asset="K15", frame="02_latest_frames/025_K15_S25_地下通道坐着卖唱_最新候选.png", story="回忆", stage="LOW", song=(157.68,164.37), lyrics="想让时间停留这一刻", guitar="G-B",
 camera="低机位，原图", action="她靠墙弹唱；唱完这句，保安拔掉插头，她停住，眼睛暗下去", motion="前景行人腿", light="原图", emotion="动情 → 熄灭",
 protect="木吉他、电源线、前景行人", mouth="是", lip="是", seg="ALPHA_S25_01", dlg="", snd="母带",
 img_cn="用现有候选。", img_en="",
 an_cn="0–5.5 秒：她低头弹唱，嘴型跟 @音频1，唱到动情处头慢慢仰起；5.5–6.7 秒：电源线一松，她停在拨弦的那一下，眼睛暗下去。", an_en="0–5.5s: she plays and sings, lips following @audio1, slowly lifting her head; 5.5–6.7s: the power cord drops away, she freezes mid-strum and her eyes go dark.")
shot(id="S26", src="S26", asset="K09", frame="02_latest_frames/026_K09_S26_走廊里小鹿给电_最新候选.png", story="回忆", stage="LOW", song=(164.37,171.00), lyrics="在人来人往的尘世间", guitar="-",
 camera="原图", action="小鹿把袖口里的细线接到她身上，她的眼睛一点点亮起", motion="荧光灯一明一暗", light="原图", emotion="小鹿淡淡地笑",
 protect="小鹿（真人外观，线从袖口出来但皮肤完好）", mouth="否", lip="否", seg="", dlg="字幕（小鹿）：我们也是。", snd="母带",
 img_cn="用现有候选。", img_en="",
 an_cn="0–3 秒：小鹿把细线接好，一下也没眨眼；3–6.6 秒：ALPHA 的眼睛一点点亮起来，光照在小鹿脸上，小鹿轻声说了一句话，淡淡地笑。", an_en="0–3s: Xiaolu connects the thin cable without blinking; 3–6.6s: ALPHA's eyes slowly light up, glowing on Xiaolu's face; she says something softly and smiles faintly.")
shot(id="S27", src="S27", asset="K10（保留原图）", frame="02_latest_frames/027_K10_S27_三位伪装者_保留原图.png", story="回忆", stage="NONE", song=(171.00,177.63), lyrics="真心的人又能有几个", guitar="-",
 camera="低机位仰拍，原图，慢推", action="三人静静站着，低机位仰视", motion="", light="原图", emotion="冷静",
 protect="三人保持原图", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="原图保留。（“没有镜片的眼镜”这个破绽已取消，默默的破绽改由 L05 冷库里不呼白气承担。）", img_en="",
 an_cn="0–4 秒：三人静静站着，阿凯侧着脸不看镜头；4–6.6 秒：镜头慢慢推近。", an_en="0–4s: the three stand still, Akai looking away; 4–6.6s: slow push in.")
shot(id="S28_01", src="S28", asset="R04（尾帧）＋新首帧（R04 加回假发）", frame="02_latest_frames/029_R04_S28_出租屋摘假发后正面近景_OLD_前期过渡候选.png", story="回忆", stage="LOW→TRANS", song=(177.63,181.00), lyrics="谁不是谁今生的过客（前半）", guitar="-",
 camera="近景，原图，固定", action="她摘下假发（首帧戴着，尾帧摘掉）", motion="", light="原图：暖小灯泡与窗外冷光", emotion="决定",
 protect="身后三人", mouth="否（闭合）", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出首帧：在 R04 上局部编辑，给她戴回廉价黑假发，其余完全不变。尾帧用 R04 原候选。",
 img_en="(edit of R04) add a cheap crooked black synthetic wig onto the robot's metal head, keep everything else in the frame exactly the same",
 an_cn="@图片1 首帧（戴假发），@图片2 尾帧（R04）。0–3.4 秒：她抬起双手，慢慢把假发从头上摘下来，放低出画。", an_en="@image1 first frame (wig on), @image2 last frame (R04). 0–3.4s: she lifts both hands and slowly takes the wig off, lowering it out of frame.")
shot(id="S28_02", src="S28", asset="K16", frame="02_latest_frames/028_K16_S28_出租屋摘掉假发后_最新候选.png", story="回忆", stage="TRANS", song=(181.00,184.29), lyrics="谁不是谁今生的过客（后半）", guitar="-",
 camera="原图", action="身后三人看着她；小鹿轻轻点头", motion="", light="原图", emotion="平静",
 protect="三人（真人外观）", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="用现有候选。", img_en="",
 an_cn="0–3.3 秒：她一动不动；身后的小鹿轻轻点了点头，阿凯别过脸去。", an_en="0–3.3s: she stays still; behind her Xiaolu nods slightly and Akai looks away.")
shot(id="S29_01", src="S29", asset="K08", frame="02_latest_frames/030_K08_S29_雨夜天台合奏_最新候选.png", story="回忆", stage="TRANS", song=(184.29,187.60), lyrics="谁的一生注定不蹉跎（前半）", guitar="G-B",
 camera="原图", action="雨夜天台，她弹唱，阿凯跟着吼唱", motion="雨", light="原图", emotion="释放",
 protect="阿凯、小鹿（真人外观）", mouth="是", lip="是", seg="ALPHA_S29_01", dlg="", snd="母带",
 img_cn="用现有候选。", img_en="",
 an_cn="0–3.3 秒：她在雨里弹唱，嘴型跟 @音频1（前半句）；身后阿凯张口跟唱，小鹿举着手机。", an_en="0–3.3s: she plays and sings in the rain, lips following the first half of @audio1; Akai sings along behind her, Xiaolu films.")
shot(id="S29_02", src="S29", asset="K27", frame="02_latest_frames/031_K27_S29_雨夜天台仰头弹唱_最新候选.png", story="回忆", stage="TRANS", song=(187.60,190.98), lyrics="谁的一生注定不蹉跎（后半）", guitar="G-B",
 camera="原图", action="她仰头唱出这句的结尾，雨水顺着金属脸流下", motion="雨", light="原图", emotion="宣泄",
 protect="不戴假发", mouth="是", lip="是", seg="ALPHA_S29_01（后半）", dlg="", snd="母带",
 img_cn="用现有候选。", img_en="",
 an_cn="0–3.4 秒：她仰头唱，嘴型跟 @音频1 的后半句，雨水顺着脸往下流。", an_en="0–3.4s: head back, she sings the second half of @audio1, rain streaming down her face.")
shot(id="S32", src="城市空镜", asset="K14（保留原图）", frame="02_latest_frames/032_K14_城市空镜_夜色住宅区空镜_保留原图.png", story="回忆", stage="NONE", song=(190.98,194.50), lyrics="亲爱的朋友不必难过（前半）", guitar="-",
 camera="原图，固定", action="一扇扇窗户陆续亮起", motion="窗灯", light="原图", emotion="被听见",
 protect="原图", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="原图保留。尾帧可在原图上局部编辑：更多窗户亮起。", img_en="(optional end frame, edit of K14) many more windows lit warm yellow, a few with blue phone light, everything else unchanged",
 an_cn="0–3.5 秒：窗户一扇接一扇亮起暖黄的灯。", an_en="0–3.5s: windows light up warm yellow one after another.")
shot(id="IV5", src="IV5", asset="IV-A（共用）", story="现在访谈", stage="TRANS", song=(194.50,197.70), lyrics="亲爱的朋友不必难过（后半）", guitar="-",
 camera="近景，85mm，固定", action="访谈插入：她平视前方", motion="", light="落地灯", emotion="平静而坚定",
 protect="", mouth="是（闭合）", lip="否（字幕）", seg="", dlg="字幕 IV5：问：后来为什么不戴了？／答：戴着它，唱歌的就不是我了。", snd="母带",
 img_cn="共用 IV-A。", img_en="",
 an_cn="0–3 秒：她慢慢抬起眼睛，平视前方，嘴保持闭合。", an_en="0–3s: she slowly raises her eyes to look straight ahead, mouth closed.")
shot(id="PF2", src="PF2", asset="K11（old / new）", frame="02_latest_frames/033_K11_PF2_手部与吉他特写_OLD_前期过渡候选.png（推荐）", story="现在访谈", stage="TRANS", song=(197.70,200.00), lyrics="终有某天还会再见的（前半）", guitar="G-B",
 camera="特写，原图", action="按弦换和弦，扫弦越来越用力", motion="琴弦振动", light="原图", emotion="—",
 protect="按弦手与拨弦手不互换、指板方向、弦数", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="用现有候选。", img_en="",
 an_cn="0–2.3 秒：手指换和弦，扫弦越来越用力，琴弦在光里颤动；机械指节稳定。", an_en="0–2.3s: fingers change chords, strumming harder, strings shimmering in the light; mechanical knuckles stay stable.")
shot(id="PF4", src="PF4", asset="K13（old / new）", frame="02_latest_frames/035_K13_PF4_低角度仰拍弹唱_OLD_前期过渡候选.png（推荐）", story="现在访谈", stage="TRANS", song=(200.00,204.48), lyrics="终有某天还会再见的（后半）", guitar="G-B",
 camera="低角度仰拍，原图，慢慢上摇", action="她仰头唱出最高音，背后梯子上的老杨剪影", motion="光晕", light="原图", emotion="全场静止",
 protect="背后梯子与人影", mouth="是", lip="是", seg="ALPHA_PF4_01（取后半）", dlg="", snd="母带",
 img_cn="用现有候选。", img_en="",
 an_cn="0–3.4 秒：她仰头唱，嘴型跟 @音频1 的后半段；3.4–4.5 秒：歌声结束，她保持仰头。", an_en="0–3.4s: head raised, she sings the second half of @audio1; 3.4–4.5s: the line ends and she holds the pose.")
shot(id="S30", src="S30", asset="K18（old / new）", frame="02_latest_frames/039_K18_S30_演播室弹唱近景_OLD_前期过渡候选.png（推荐）", story="现在访谈", stage="TRANS", song=(204.48,209.00), lyrics="流着泪唱完了这首歌", guitar="G-B",
 camera="近景，原图，固定", action="她唱最后几句，头慢慢低下，手越弹越慢", motion="", light="原图", emotion="收",
 protect="前景虚焦肩膀", mouth="是", lip="是", seg="ALPHA_S30_01", dlg="", snd="母带",
 img_cn="用现有候选。", img_en="",
 an_cn="0–4.5 秒：她唱，嘴型跟 @音频1，声音越来越轻，头慢慢低下去。", an_en="0–4.5s: she sings, lips following @audio1, voice softening, head slowly lowering.")
shot(id="S31", src="S31", asset="（新出图）", story="现在访谈", stage="NONE", song=(209.00,211.08), lyrics="流着泪唱完了这首歌（尾）", guitar="-",
 camera="中景，85mm", action="侧台暗处，阿凯站在最前，小鹿默默在后，阿凯慢慢摘下一只皮手套", motion="", light="舞台暖光只碰到脸的边缘", emotion="动容",
 protect="三人（真人外观，阿凯真实形态不出现）", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。演播室侧台的黑暗里，刺猬头黑皮夹克的阿凯站在最前，小鹿和默默在他身后，都看向舞台。",
 img_en="in the darkness at the side of a studio set, a young Chinese man with spiky black hair and a worn black leather jacket standing in front, a 23-year-old girl with a low ponytail and denim jacket and a thin expressionless man with black-framed glasses behind him, all watching the stage, warm stage light only touching the edges of their faces, 85mm",
 an_cn="0–2 秒：三人一动不动地看着；阿凯慢慢摘下一只露指皮手套。", an_en="0–2s: the three watch without moving; Akai slowly pulls off one fingerless glove.")
shot(id="S33", src="S33", asset="（新出图）", story="之后", stage="NONE", song=(211.08,217.80), lyrics="希望你会永远记得我", guitar="-",
 camera="中景，40mm，门框前景", action="女儿递过手机，老人茫然地摇头，却一直看着屏幕", motion="窗外大雪", light="屋里一盏钨丝灯，窗外雪地冷蓝，手机光照脸", emotion="茫然；女儿别过脸擦眼睛",
 protect="老周、女儿（真人）", mouth="否", lip="否", seg="", dlg="字幕（女儿）：爸，你还记得她吗？", snd="母带",
 img_cn="新出图。东北县城老房子冬夜，窗外大雪；更老的老周坐在旧扶手椅里盖着毯子，三十多岁的女儿蹲在旁边递亮着的手机。",
 img_en="winter night in an old house in a small northeast Chinese town, heavy snow outside the frosted window, a very old frail Chinese man with white hair and metal-framed reading glasses sitting in a worn armchair under a blanket, his daughter in her thirties crouching beside him holding out a glowing phone, he looks at the screen with confused eyes, one warm tungsten lamp inside, cold blue snow light from the window, framed through a doorway, 40mm",
 an_cn="0–3 秒：女儿递过手机，轻声问了一句；3–5 秒：老人茫然地慢慢摇头；5–6.7 秒：他却一直看着屏幕，女儿别过脸擦了下眼睛。", an_en="0–3s: the daughter holds out the phone and asks softly; 3–5s: he slowly shakes his head, confused; 5–6.7s: yet he keeps watching the screen; she turns away and wipes her eyes.")
shot(id="S34", src="S34", asset="（新出图）", story="之后", stage="NONE", song=(217.80,224.31), lyrics="在某个冬夜无眠的时刻", guitar="-",
 camera="特写，100mm，固定", action="老人搭在扶手上的食指和中指跟着节拍轻敲", motion="手机光", light="台灯暖光与雪光交汇", emotion="记忆之外的东西",
 protect="老人的手（真人）", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。特写：满是皱纹和老年斑的手搭在旧木扶手上，两根手指微微抬起，手机微光照在手背上。",
 img_en="close-up of an old wrinkled hand with age spots resting on a worn wooden armrest, two fingers lifted mid-tap, the faint glow of a phone screen on the skin, warm lamp light and cold blue snow light from a window mixing, 100mm",
 an_cn="0–6.5 秒：他的食指和中指在扶手上跟着歌的拍子轻轻敲（按母带实际节拍对齐），身体一动不动。", an_en="0–6.5s: his index and middle fingers tap the armrest gently in time with the song (align to the master's actual beat); the rest of him is still.")
shot(id="S35", src="S35", asset="（新出图）", story="之后", stage="MATURE", song=(224.31,231.25), lyrics="在某个春暖花开的时刻", guitar="G-B（琴盒）",
 camera="全景，40mm 变形宽银幕，手持", action="她背着琴盒走下绿皮车，抬头看站台，风吹落花瓣", motion="花瓣", light="雨后初晴，全片第一次暖色自然光", emotion="平静的到来",
 protect="小鹿、阿凯、默默（真人外观）", mouth="否", lip="否", seg="", dlg="", snd="母带",
 img_cn="新出图。春天东北县城小站，雨后初晴，站台边开满桃花；成熟形象的 ALPHA 背着装着那把旧木吉他的琴盒走下绿皮车，身后跟着三位同伴。",
 img_en="spring after rain at a small northeast Chinese railway station, pink and white peach blossoms along the platform, an old green train stopped, {A_MATURE} stepping down from the train with a guitar case on her back, behind her a girl with a low ponytail and denim jacket, a young man with spiky black hair and a black leather jacket, and a thin man with black-framed glasses pushing a power case, soft diffused sunlight, the first warm saturated colors of the film, petals on the wet platform, 40mm anamorphic",
 an_cn="0–7 秒：她走下车，站定，抬头看着站台，风吹落花瓣；身后的女孩轻轻碰了碰她的胳膊。", an_en="0–7s: she steps down, stops and looks up at the platform as petals fall; the girl behind her touches her arm.")
shot(id="S36_01", src="S36", asset="K17（old / new）", frame="02_latest_frames/041_K17_S36_演播室座椅背侧面_OLD_前期过渡候选.png（推荐）", story="现在访谈", stage="TRANS", song=(231.25,236.00), lyrics="（尾奏）", guitar="G-B",
 camera="原图，固定", action="寂静后，右后方梯子上的老杨第一个鼓掌", motion="光晕、烟", light="原图", emotion="—",
 protect="老杨在梯子上（真人）、ALPHA 背侧角度不转正面", mouth="否", lip="否", seg="", dlg="", snd="母带尾奏＋第一声掌声",
 img_cn="用现有候选。", img_en="",
 an_cn="0–2 秒：一片寂静，她一动不动；2–4.7 秒：右后方梯子上的老杨抬起手，开始鼓掌。", an_en="0–2s: silence, she is still; 2–4.7s: on the ladder behind right, Lao Yang raises his hands and starts clapping.")
shot(id="S36_02", src="S36", asset="R05（old / new）", frame="02_latest_frames/043_R05_S36_演播室背侧近景_OLD_前期过渡候选.png（推荐）", story="现在访谈", stage="TRANS", song=(236.00,SONG_END), lyrics="（尾奏）", guitar="G-B",
 camera="原图，固定", action="掌声陆续响起，不整齐", motion="", light="原图", emotion="—",
 protect="同上", mouth="否", lip="否", seg="", dlg="", snd="母带尾奏＋掌声（掌声另录或取素材）",
 img_cn="用现有候选。", img_en="",
 an_cn="0–4.5 秒：老杨继续鼓掌，下面的人陆续跟着鼓掌；她的头极轻微地低了一下。", an_en="0–4.5s: Lao Yang keeps clapping and others join in unevenly; her head dips very slightly.")
# ================================================================ EPILOGUE
e = 0.0
def ep(d):
    global e
    r = (e, e+d); e += d; return r
shot(id="S37", src="S37", asset="（新出图）", story="现在访谈", stage="TRANS", ep=ep(14.0), lyrics="", guitar="G-B",
 camera="双人中景，侧面，40mm 变形宽银幕，固定", action="林姐问出第一题；她回答；林姐把手卡扣下，划掉嘉宾牌上的“（设备）”", motion="", light="两人各在一束光下，中间暗", emotion="安静的转变",
 protect="林姐（真人）、嘉宾牌", mouth="是", lip="对白（待录音）", seg="DLG_S37", dlg="林姐：你的悲伤……是真的吗？／ALPHA：我不知道它算不算真的。他走的那天，我在站台站了七个小时。", snd="空棚底噪",
 img_cn="新出图。纪录片访谈双人中景：左边抱黄色电吉他的成熟形象 ALPHA，右边林姐拿笔对着两人中间小桌上的白色嘉宾牌（字后期合成）。",
 img_en="documentary interview two-shot in a pitch black studio, {A} with {G} on the left, a Chinese female interviewer in her early forties with short bob hair and a black suit on the right holding a pen over a white name card on the small table between them, a single floor lamp between them, quiet resolution, 40mm anamorphic",
 an_cn="0–3 秒：林姐抬头提问；3–9 秒：ALPHA 停了很久，慢慢回答；9–11 秒：林姐把手卡扣在桌上；11–14 秒：她拿起笔，划掉嘉宾牌上的一个词。（超出模型时长可在 9 秒处拆成两段）", an_en="0–3s: the interviewer asks; 3–9s: ALPHA pauses a long time and answers slowly; 9–11s: the cue card is laid face down; 11–14s: she picks up the pen and crosses out a word on the name card. (Split at 9s if over the model limit.)")
shot(id="S38", src="S38", asset="K28", frame="02_latest_frames/045_K28_S38_春天与老周并坐长椅_最新候选.png", story="之后", stage="MATURE", ep=ep(12.0), lyrics="", guitar="-",
 camera="大全景，原图，固定", action="老人像对陌生人一样问她的名字，想了想，笑了；远处火车开过", motion="花瓣", light="原图", emotion="温柔",
 protect="老周（真人）、背向构图", mouth="否（背向）", lip="否", seg="DLG_S38", dlg="老周：你唱得真好。你叫什么名字？／ALPHA：ALPHA。／老周：阿尔法……好名字。像是第一个。", snd="风、鸟、远处火车",
 img_cn="用现有候选（成熟形象，待确认）。", img_en="",
 an_cn="0–4 秒：老人转头对她说话；4–7 秒：她转头回答；7–10 秒：老人慢慢笑了；10–12 秒：远处一列火车开过，花瓣飘落。", an_en="0–4s: the old man turns to speak to her; 4–7s: she turns to answer; 7–10s: he slowly smiles; 10–12s: a train passes far away as petals fall.")
shot(id="END", src="—", asset="—", story="—", stage="NONE", ep=ep(2.0), lyrics="", guitar="-",
 camera="黑场字幕", action="片名：远去的列车", motion="", light="", emotion="",
 protect="", mouth="否", lip="否", seg="", dlg="", snd="静",
 img_cn="后期制作。", img_en="", an_cn="", an_en="")
assert abs(e-EPI) < 1e-6, e


STUDIO = {"O1","O3","O4","P1c","O6","O7","O8","O9","P4","P5","S01","S02","PF1","S04","S06","IV2","IV5","PF2","PF4","S30","S36_01","S36_02","S37"}
NEWFRAME = {
 "P1c":"02_latest_frames/006_K22_P1c_演播室贴设备标签_NEW_成熟造型候选.png",
 "S02":"02_latest_frames/008_K20_S02_面部与吉他极近景_NEW_成熟造型候选.png",
 "PF1":"02_latest_frames/038_K21_PF4_低角度弹唱中景_NEW_成熟造型候选.png",
 "P5":"02_latest_frames/034_K11_PF2_手部与吉他特写_NEW_成熟造型候选.png",
 "PF2":"02_latest_frames/034_K11_PF2_手部与吉他特写_NEW_成熟造型候选.png",
 "PF4":"02_latest_frames/036_K13_PF4_低角度仰拍弹唱_NEW_成熟造型候选.png",
 "S30":"02_latest_frames/040_K18_S30_演播室弹唱近景_NEW_成熟造型候选.png",
 "S36_01":"02_latest_frames/042_K17_S36_演播室座椅背侧面_NEW_成熟造型候选.png",
 "S36_02":"02_latest_frames/044_R05_S36_演播室背侧近景_NEW_成熟造型候选.png",
}
for k in S:
    if k["id"] in STUDIO:
        if k["stage"] == "TRANS": k["stage"] = "MATURE"
        if k["guitar"].startswith("G-B"): k["guitar"] = "Y"
        if k["id"] in NEWFRAME:
            k["frame"] = NEWFRAME[k["id"]]
            k["asset"] = k["asset"].replace("（old / new 二选一）","（NEW）").replace("（old / new）","（NEW）").replace("（old）","（NEW）")
        for a,b in (("木吉他","黄色电吉他"),("木琴","电吉他")):
            for f in ("action","img_cn","an_cn","protect"): k[f] = k[f].replace(a,b)
        k["an_en"] = k["an_en"].replace("acoustic guitar","electric guitar")
    if k["lip"].startswith("对白"):
        k["lip"] = "否（对白只出字幕）"
    if k["seg"].startswith("DLG"): k["seg"] = ""
    k["dlg"] = k["dlg"].replace("对白（画外）","字幕（画外）")

# ================================================================ derive times + write
for k in S:
    if "mv" in k: k["mv_in"], k["mv_out"] = k["mv"]; k["song_in"]=k["song_out"]=None; k["block"]="B0 开场"
    elif "song" in k:
        a,b = k["song"]; k["song_in"], k["song_out"] = a,b
        off = B1_OFF if b <= BREAK + 1e-6 else B3_OFF
        k["mv_in"], k["mv_out"] = a+off, b+off; k["block"] = "B1 歌曲前段" if off==B1_OFF else "B3 歌曲后段"
    elif "ch" in k: a,b = k["ch"]; k["mv_in"],k["mv_out"] = OPEN+BREAK+a, OPEN+BREAK+b; k["song_in"]=k["song_out"]=None; k["block"]="B2 无音乐章节"
    elif "ep" in k: a,b = k["ep"]; k["mv_in"],k["mv_out"] = EPI_START+a, EPI_START+b; k["song_in"]=k["song_out"]=None; k["block"]="B4 结尾"
def fmt(x): return "" if x is None else f"{x:.2f}"
def fill(s, k):
    g = GUIT["Y"][1] if k["guitar"].startswith("Y") else GUIT["G-B"][1]
    return s.replace("{A}", ALPHA_EN.get(k["stage"].split("→")[0], ALPHA_EN["B1"])).replace("{A_MATURE}", ALPHA_EN["MATURE"]).replace("{G}", g)
def a_cons(k):
    st = k["stage"].split("→")[-1]
    parts_cn, parts_en = [], []
    if st != "NONE": parts_cn += [A_CN, STAGE[st][0]]; parts_en += [A_EN, STAGE[st][1]]
    if any(n in (k["protect"]+k["action"]+k["img_cn"]) for n in ("小鹿","阿凯","默默")): parts_cn.append(DISG_CN); parts_en.append(DISG_EN)
    return " ".join(parts_cn), " ".join(parts_en)
def cam_en(cn):
    out = []; rest = cn
    for key, en in [("大特写","extreme close-up"),("极近景","extreme close-up"),("特写","close-up"),("近景","close shot"),("中近景","medium close-up"),("中景","medium shot"),("双人中景","two-shot"),("大全景","extreme wide shot"),("全景","wide shot"),("大远景","extreme long shot"),
                    ("过肩","over-the-shoulder"),("仰拍","low angle"),("低机位","low angle"),("俯拍","high angle"),("侧面","side view"),("侧脸","profile"),("原图","framing as in the first frame"),
                    ("门框","framed through a doorway"),("隔着","through glass"),("从冰箱","from inside the fridge"),("从店里","from inside the shop")]:
        if key in rest and en not in out: out.append(en); rest = rest.replace(key, "")
    mv = "locked-off"
    for key, en in [("推近","slow push in"),("慢推","slow push in"),("手持","handheld, subtle breathing movement"),("横移","slow lateral move"),("跟拍","side tracking shot"),("上摇","slow tilt up"),("下推","slow push down"),("三脚架","locked-off tripod, no shake"),("轻晃","handheld, slight sway")]:
        if key in cn: mv = en
    lens = [w for w in ("24mm","35mm","40mm","50mm","85mm","100mm") if w in cn]
    if "变形宽银幕" in cn: lens.append("anamorphic")
    return ", ".join(out + lens + [mv])

def anim(k):
    if not k["an_cn"]: return "",""
    has_frame = bool(k.get("frame")) or k["img_cn"].startswith("新出图") or "首帧" in k["an_cn"]
    ref_cn = "" if k["an_cn"].startswith("@图片") else "@图片1 作为首帧。"
    ref_en = "" if k["an_en"].startswith("@image") else "@image1 as the first frame. "
    if k["lip"].startswith("是") or k["lip"]=="可选":
        ref_cn += f"@音频1 为本镜演唱音频（{k['seg'].split('（')[0]}_MIX_v001.wav），嘴型与之同步；若平台不支持音频参考，生成后再用口型工具对齐。"
        ref_en += f"@audio1 is this shot's vocal ({k['seg'].split('（')[0]}_MIX_v001.wav); sync the lips to it. If audio reference is unsupported, lip-sync afterwards."
    cc, ce = a_cons(k)
    return (ref_cn + k["an_cn"] + " 镜头：" + k["camera"] + "。" + cc + VID_CN,
            ref_en + k["an_en"] + " Camera: " + cam_en(k["camera"]) + ". " + ce + " " + VID_EN)
rows = []
for k in S:
    acn, aen = anim(k)
    ien = fill(k["img_en"], k) if k["img_en"] else ""
    if ien and not ien.startswith("(edit") and "||" not in ien: ien = f"{ien}, {MJ} {MJP}"
    elif "||" in ien: ien = ien.replace("  ||  END FRAME:", f", {MJ} {MJP}  ||  END FRAME:") + f", {MJ} {MJP}"
    card = {"B1":"B1","COAT":"B1+B3","LOW":"B1+B3（+假发）","V2":"B1（v2 舞台装）","V2OUT":"B1+B3（v2）","TRANS":"B1+B3","LOW→TRANS":"B1+B3（摘假发）","MATURE":"MATURE","NONE":"—"}[k["stage"]]
    if k["guitar"].startswith("G-B"): card += "；G-B"
    wig = {"LOW":"戴","V2":"戴","V2OUT":"戴","LOW→TRANS":"摘下"}.get(k["stage"],"无")
    costume = {"B1":"无外衣","COAT":"黑长羽绒服＋灰围巾","LOW":"黑长羽绒服＋灰围巾","V2":"夜场舞台装（v2）","V2OUT":"敞开羽绒服＋舞台装（v2）","TRANS":"黑长羽绒服＋灰围巾","LOW→TRANS":"黑长羽绒服＋灰围巾","MATURE":"成熟青黄银外壳","NONE":"—"}[k["stage"]]
    approval = "原图保留" if "保留原图" in k["asset"] else ("candidate_pending" if k.get("frame") else ("proposal_pending" if k["id"]!="END" else ""))
    rows.append({
        "shot_id":k["id"],"source_shot_id":k["src"],"source_asset_id":k["asset"],"story_time":k["story"],"stage":k["stage"],"approval_status":approval,
        "song_in":fmt(k["song_in"]),"song_out":fmt(k["song_out"]),"mv_in":fmt(k["mv_in"]),"mv_out":fmt(k["mv_out"]),"duration":fmt(k["mv_out"]-k["mv_in"]),
        "time_status":"provisional_lrc" if k["song_in"] is not None else "provisional_from_script","fps":"待确认","lyrics":k["lyrics"],
        "character_card":card,"frame_image":k.get("frame",""),"costume":costume,"wig":wig,"guitar":GUIT.get(k["guitar"].split("（")[0],("",""))[0] or k["guitar"],
        "camera":k["camera"],"action":k["action"],"motion":k["motion"],"lighting":k["light"],"emotion":k["emotion"],"protected_elements":k["protect"],
        "mouth_visible":k["mouth"],"lip_sync_required":k["lip"],"audio_segment_id":k["seg"],"dialogue":k["dlg"],"sound_design":k["snd"],
        "sync_notes":("母带区间见 audio/audio_segments.csv；生成用整句，剪辑只取本镜区间" if k["seg"].startswith("ALPHA") else ("对白音频尚未录制" if k["seg"].startswith("DLG") else "")),
        "image_prompt_cn":k["img_cn"],"image_prompt_en":ien,"animation_prompt_cn":acn,"animation_prompt_en":aen,
        "constraints":IMG_CONS,"output_filename":f"ALPHA_{k['id']}_v001.mp4" if k["id"]!="END" else "","version":"v001","block":k["block"]})
FIELDS = ["shot_id","source_shot_id","source_asset_id","story_time","stage","approval_status","song_in","song_out","mv_in","mv_out","duration","time_status","fps","lyrics","character_card","frame_image","costume","wig","guitar","camera","action","motion","lighting","emotion","protected_elements","mouth_visible","lip_sync_required","audio_segment_id","dialogue","sound_design","sync_notes","image_prompt_cn","image_prompt_en","animation_prompt_cn","animation_prompt_en","constraints","output_filename","version"]
with open(os.path.join(HERE,"03_分镜清单.csv"),"w",newline="",encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
with open(os.path.join(HERE,"04_双时间轴段落.csv"),"w",newline="",encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["block_id","block_type","source_file","song_in","song_out","mv_in","mv_out","duration","dialogue_file","ambience_file","transition","approval_status","notes"])
    w.writerow(["B0","开场（无音乐）","","","",f"0.00",f"{OPEN:.2f}",f"{OPEN:.2f}","待录制","待准备","硬切进 P5 拨弦","proposal_pending","对白需录音"])
    w.writerow(["B1","歌曲前段","1dd96bd4-_____.mp3","0.00",f"{BREAK:.2f}",f"{B1_OFF:.2f}",f"{BREAK+B1_OFF:.2f}",f"{BREAK:.2f}","","","149.30–150.50 淡出","proposal_pending","150.50 处 RMS 约 −16 dB 的换气凹陷（实测）"])
    w.writerow(["B2","无音乐章节","","","",f"{BREAK+B1_OFF:.2f}",f"{BREAK+B3_OFF:.2f}",f"{CH:.2f}","","待准备","L09_01 幕布后吸气，接回母带","proposal_pending","是否保留整章待用户确认；L08 含同曲画内声（提案）"])
    w.writerow(["B3","歌曲后段","1dd96bd4-_____.mp3",f"{BREAK:.2f}",f"{SONG_END:.3f}",f"{BREAK+B3_OFF:.2f}",f"{SONG_END+B3_OFF:.2f}",f"{SONG_END-BREAK:.2f}","","","从 150.50 原位接回，不重复歌词","proposal_pending",""])
    w.writerow(["B4","结尾（无音乐）","","","",f"{EPI_START:.2f}",f"{EPI_START+EPI:.2f}",f"{EPI:.2f}","待录制","待准备","黑场片名","proposal_pending",""])
# readable prompt book
L = []; w = L.append
w("# 《远去的列车》第七版：逐镜图片与 sd2.5 动画提示词\n")
w("> 由 `build_shotlist.py` 生成，与 `03_分镜清单.csv` 同源。**已按 2026-10-06 的决定更新：演播室用 NEW 成熟形象＋黄色电吉他；春天用成熟形象；v2 全部采用；对白只出字幕。**时间均为暂定：歌曲时间取自母带内嵌歌词（未逐句听辨），成片时间按推荐结构推算。")
w("> **用现有候选的镜头**直接拿候选图做首帧；**新出图的镜头**先用英文图片提示词在 MJ 出图，再做动画。所有候选和新图都待逐帧确认。\n")
w(f"成片总长（暂定）：{EPI_START+EPI:.1f} 秒 ≈ {int((EPI_START+EPI)//60)} 分 {int((EPI_START+EPI)%60)} 秒\n")
w("**sd2.5 使用说明**")
w("- `@图片1` = 本镜首帧（现有候选或新出的图）；有尾帧的镜头另传 `@图片2`。")
w("- 有口型的镜头上传 `@音频1`（`audio/` 里对应的 WAV）。切片前后各留 0.5 秒余量，生成后按 CSV 的 trim_in/trim_out 裁掉。")
w("- 首帧里有真人正脸、上传被拦截时：改用文生视频，只上传 B1/B3 设定卡当 ALPHA 参考，把“画面”写进提示词。")
w("- 时长以本表为准；超过模型上限就在动作停顿处拆成子镜。\n")
cur = None
for k, r in zip(S, rows):
    if k["block"] != cur:
        cur = k["block"]; w(f"\n---\n\n## {cur}\n")
    if k["id"] == "END": continue
    tm = f"歌曲 {r['song_in']}–{r['song_out']}｜" if r["song_in"] else ""
    import re as _re
    title = _re.split(r"[，；、（]", k["action"])[0]
    w(f"### {k['id']}　{title}")
    w(f"`{tm}成片 {r['mv_in']}–{r['mv_out']}（{r['duration']} 秒）` · {k['story']} · 造型 {r['character_card']} · 假发：{r['wig']} · 口型：{k['lip']}\n")
    w(f"- **素材**：{k['asset']}" + (f"　`{k['frame']}`" if k.get('frame') else ""))
    if k["lyrics"]: w(f"- **歌词**：{k['lyrics']}")
    if k["dlg"]: w(f"- **对白／字幕**：{k['dlg']}")
    w(f"- **保护**：{k['protect'] or '—'}")
    w(f"- **图片**：{k['img_cn']}")
    if r["image_prompt_en"]:
        w("```\n" + r["image_prompt_en"] + "\n```")
    w("**sd2.5 动画（中文）**\n```\n" + r["animation_prompt_cn"] + "\n```")
    w("**sd2.5 animation (EN)**\n```\n" + r["animation_prompt_en"] + "\n```\n")
open(os.path.join(HERE,"05_逐镜提示词.md"),"w").write("\n".join(L))
print(len(S),"shots; total", round(EPI_START+EPI,2), "s")
