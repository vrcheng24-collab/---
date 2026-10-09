# v8: simple humble opening, continuous song, montage editing, robot-style performance.
# Reuses the v7 shot descriptions (executed from ../v7/build_shotlist.py) and re-times / rewrites them.
import csv, os, re, copy
HERE = os.path.dirname(os.path.abspath(__file__))
V7 = os.path.join(os.path.dirname(HERE), "v7", "build_shotlist.py")
ns = {"__file__": V7}
exec(open(V7).read(), ns)
V7S = {k["id"]: k for k in ns["S"]}
fill, a_cons, cam_en = ns["fill"], ns["a_cons"], ns["cam_en"]
MJ, MJP, IMG_CONS, VID_CN, VID_EN, GUIT = ns["MJ"], ns["MJP"], ns["IMG_CONS"], ns["VID_CN"], ns["VID_EN"], ns["GUIT"]

COLD = 10.0
SONG_END = 240.456
EPI = 20.0
OFF = COLD
EPI_START = COLD + SONG_END

# robot-style emotional performance vocabulary
ROBOT_CN = ("机器人式的深情演唱：头部按小角度分段转动，每段之间有一次细微停顿；唱长音时耳侧涡轮缓缓旋转；"
            "蓝色虹膜像相机光圈一样随情绪收缩、张开；胸甲的散热缝随乐句开合，代替呼吸；嘴唇是金属分片的开合，没有牙齿和舌头；"
            "情绪最满时手指出现伺服电机般的细微颤动。")
ROBOT_EN = ("Robot-style heartfelt singing: the head turns in small stepped increments with a tiny pause between each; the ear turbines spin slowly on held notes; "
            "the blue irises contract and open like a camera aperture with the emotion; the chest-plate vents open and close with each phrase instead of breathing; "
            "the lips move as segmented metal plates, no teeth or tongue; at the emotional peak the fingers show a faint servo tremor.")

S = []
def use(vid, nid=None, **over):
    k = copy.deepcopy(V7S[vid]); k["id"] = nid or vid
    for f in ("mv","song","ch","ep","mv_in","mv_out","song_in","song_out","block"): k.pop(f, None)
    k.update(over); k.setdefault("trans", "cut"); S.append(k); return k
def new(**k):
    base = dict(src="—", asset="（新出图）", story="现在访谈", stage="MATURE", lyrics="", guitar="-", camera="", action="", motion="", light="", emotion="",
                protect="", mouth="否", lip="否", seg="", dlg="", snd="母带", img_cn="", img_en="", an_cn="", an_en="", trans="cut")
    base.update(k); S.append(base); return base
def flash(vid, nid, song, clip_in, note=""):
    k = use(vid, nid, song=song, trans="flash", clip=vid, clip_in=clip_in)
    k["img_cn"] = f"闪切：复用 {vid} 的视频片段（从第 {clip_in} 秒起），不单独出图、不单独生成。{note}"
    k["img_en"] = ""; k["an_cn"] = ""; k["an_en"] = ""; k["dlg"] = ""; k["lip"] = "否"; k["seg"] = ""
    k["asset"] = f"复用 {vid}"; return k
def sing(k, seg):
    k["lip"] = "是"; k["seg"] = seg; k["mouth"] = "是"; k["robot"] = True; return k

STUDIO_LIGHT_CN = "黑色空棚，一盏暖色落地灯和一束顶光，薄烟，工作人员在暗处"

# ================================================================ COLD OPEN (mv 0–10, ambience only)
co = use("P1c", "CO1", mv=(0.0, 3.5))
co.update(img_cn="用现有 NEW 候选（K22），不重出。原图里的“设备”嘉宾牌不再使用，若画面里有就后期擦掉。",
          action="场务小心地替她别好领夹麦，她微微点头致谢", emotion="谦和、安静", protect="场务（真人）",
          dlg="字幕　ALPHA：谢谢。", snd="环境：空棚底噪、远处有人轻声说“各部门准备”",
          an_cn="0–2 秒：场务小心地替她把领夹麦别在胸甲边缘，动作很轻；2–3.5 秒：她转过头，向场务微微点头致谢，场务笑着退开。",
          an_en="0–2s: a crew member carefully clips a lavalier mic to the edge of her chest plate; 2–3.5s: she turns her head and gives a small grateful nod, the crew member smiles and steps back.")
new(id="CO2", src="新增", story="现在访谈", stage="NONE", mv=(3.5, 6.0),
    camera="中景，仰拍，50mm", action="梯子上的老杨调好最后一盏灯，低头看见她在向他点头致意，笑着抬了抬手", emotion="温暖、被尊重", light="头顶影视灯，薄烟",
    protect="老杨（真人）、梯子", snd="环境：灯具金属声",
    img_cn="新出图。仰拍：五十多岁的灯光师站在铝梯上，刚调好一盏影视灯，低头笑着朝下方抬手致意。",
    img_en="low angle, a Chinese lighting technician in his fifties with grey hair, stubble and a dark work vest standing on an aluminium ladder after adjusting a film light, looking down with a warm smile and raising one hand in greeting, haze, black lighting grid, 50mm",
    an_cn="0–1.5 秒：他拧紧灯，低头；1.5–2.5 秒：他看见下面的她在点头致意，笑着抬了抬手。", an_en="0–1.5s: he tightens the lamp and looks down; 1.5–2.5s: seeing her nod to him, he smiles and raises a hand.")
new(id="CO3", src="O7", story="现在访谈", stage="MATURE", mv=(6.0, 8.5),
    camera="过肩，50mm，固定", action="越过 ALPHA 的肩拍林姐，她温和地问出第一个问题", emotion="林姐温和、真诚", light=STUDIO_LIGHT_CN,
    protect="林姐（真人）", dlg="字幕　林姐：第一个问题……你的悲伤，是真的吗？", snd="环境：空棚底噪",
    img_cn="新出图。从成熟形象 ALPHA 身后过肩拍：前景是她的金属后脑、黄色翼片和耳侧涡轮（虚焦），对面扶手椅里的林姐温和地看着她。",
    img_en="over-the-shoulder shot from behind {A}, the back of her silver and yellow metal head, yellow fin and turbine ear blurred in the foreground, across from her a Chinese female interviewer in her early forties with short bob hair and a black suit looking at her warmly as she asks a question, a single floor lamp between them, dark interview studio, 50mm",
    an_cn="0–2.5 秒：林姐温和地问出一句话，然后安静地等。", an_en="0–2.5s: the interviewer gently asks one question, then waits quietly.")
new(id="CO4", src="O9", story="现在访谈", stage="MATURE", guitar="Y", mv=(8.5, 10.0),
    camera="近景，85mm，固定", action="她沉默了一下，看向身旁的电吉他，轻声问能不能唱出来", emotion="谦逊、有点不好意思", light=STUDIO_LIGHT_CN,
    protect="", mouth="是", lip="否（字幕）", dlg="字幕　ALPHA：我可以……唱出来吗？", snd="环境：空棚底噪",
    img_cn="新出图。近景：成熟形象的 ALPHA 坐在扶手椅里，微微低头，目光看向靠在椅边的黄色电吉他，落地灯照亮半边金属脸。",
    img_en="close-up of {A} sitting in a worn armchair, head slightly lowered, eyes turned toward {G} leaning against the side of the chair, warm floor lamp light on half of her metal face, dark interview studio, 85mm, humble and shy",
    an_cn="0–1 秒：她的眼睛看向身边的吉他；1–1.5 秒：她抬眼，轻声说了一句话。", an_en="0–1s: her eyes go to the guitar beside her; 1–1.5s: she looks up and says one soft line.")

# ================================================================ SONG (mv = song + 10)
s = use("S01", song=(0.0, 5.5))
s.update(action="她在落地灯下抱着电吉他弹起前奏，暗处的工作人员轻手轻脚地停下手里的事、坐下来", emotion="专注",
         an_cn="0–5.5 秒：她低头弹前奏；暗处的工作人员轻轻放下手里的东西，一个个安静地坐下来听；镜头极慢推近。",
         an_en="0–5.5s: she plays the intro, head down; in the dark the crew quietly put things down and sit to listen one by one; very slow push in.")
use("PF2", "PF2_01", song=(5.5, 8.8))
use("S06", song=(8.8, 11.8))["dlg"] = ""
flash("S22b", "F01", (11.8, 12.8), 3.0, "第一次闪回：列车开走的车窗。")
new(id="RG0", src="新增", story="现在访谈", stage="MATURE", song=(12.8, 14.43),
    camera="大特写，100mm，固定", action="第一句之前，她胸甲上的散热缝缓缓张开，像吸了一口气", motion="散热缝开合", light="顶光侧打在金属上", emotion="准备",
    img_cn="新出图。大特写：成熟形象 ALPHA 的胸甲与锁骨处，一排细窄的散热缝正在张开，青黄色外壳，金属反光。",
    img_en="extreme close-up of the chest plate and collarbone area of {A}, a row of narrow cooling vents slowly opening like an intake of breath, glossy cyan and yellow armour, metal reflections, top light from the side, black background, 100mm",
    an_cn="0–1.6 秒：胸甲上的散热缝缓缓张开，停住，像吸了一口气。", an_en="0–1.6s: the chest vents slowly open and hold, like taking a breath.", robot=True)
sing(use("S02", "S02_01", song=(14.43, 18.0)), "ALPHA_S02_01")
flash("S22a", "F02", (18.0, 19.2), 1.0, "闪回：老周替她拉上羽绒服领口。")
sing(use("S02", "S02_02", song=(19.2, 21.03), clip="S02_01"), "ALPHA_S02_01")
sing(use("PF1", song=(21.03, 24.5)), "ALPHA_PF1_01")
s = use("S03", song=(24.5, 26.3))
s.update(action="老杨停在梯子上，慢慢摘下一只手套，听她唱", emotion="动容",
         an_cn="0–1.8 秒：他停在梯子上，慢慢摘下一只手套，看着她。", an_en="0–1.8s: he stops on the ladder, slowly pulls off one glove and watches her.")
flash("S21", "F03", (26.3, 27.81), 1.0, "闪回：雾里的铁轨，两人并排走。")
new(id="RG1", src="新增", story="现在访谈", stage="MATURE", song=(27.81, 31.2),
    camera="大特写，100mm，缓慢绕行", action="她唱长音时，耳侧的涡轮缓缓转动，叶片间透出微光", motion="涡轮旋转", light="顶光、薄烟", emotion="投入",
    img_cn="新出图。大特写：成熟形象 ALPHA 的耳侧圆形涡轮和黄色翼片，涡轮叶片清晰，背景虚焦的演播室光斑。",
    img_en="extreme close-up of the round silver turbine ear unit and yellow head fin of {A}, turbine blades in sharp detail, a faint glow between the blades, blurred studio bokeh behind, 100mm",
    an_cn="0–3.4 秒：涡轮随歌声缓缓转动，叶片间的微光一明一暗；镜头沿着头部轮廓缓慢绕行。", an_en="0–3.4s: the turbine spins slowly with her voice, the glow between the blades pulsing; the camera slowly arcs along the contour of her head.", robot=True)
new(id="S04", src="S04", story="现在访谈", stage="NONE", song=(31.2, 33.0),
    camera="近景，85mm", action="林姐把手卡慢慢放到腿上，摘下一边耳返，安静地听", emotion="被打动", light="舞台暖光勾出侧脸",
    protect="林姐（真人）",
    img_cn="新出图。近景：林姐坐在暗处，手卡放在腿上，正摘下一边耳返，侧脸被舞台暖光勾出轮廓。",
    img_en="close-up of a Chinese female interviewer in her early forties with short bob hair and a black suit sitting in the dark, cue cards resting on her lap, slowly removing one earpiece, her profile outlined by warm stage light, 85mm",
    an_cn="0–1.8 秒：她把手卡放到腿上，摘下一边耳返，安静地听。", an_en="0–1.8s: she lays the cue cards on her lap, removes one earpiece and listens.")
flash("S23", "F04", (33.0, 34.44), 0.5, "闪回：雨滴顺着她的金属脸滑下。")
use("S05", song=(34.44, 38.2))
iv = use("IV2", "IV1", song=(38.2, 40.95), trans="dissolve")
iv.update(dlg="字幕　问：第一次唱歌，是为谁唱的？", action="访谈插入：她低头，像在回忆",
          an_cn="0–2.7 秒：她低着头，虹膜像光圈一样慢慢收小，嘴保持闭合。", an_en="0–2.7s: head lowered, her irises slowly narrow like an aperture, mouth closed.")
use("S07", "S07_01", song=(40.95, 45.0), trans="dissolve")
s = use("S08", song=(45.0, 49.0))
use("PF2", "PF2_02", song=(49.0, 51.0), clip="PF2_01", clip_in=1.5)["img_cn"] = "匹配剪辑：老周带着她按弦的手 → 现在她自己扫弦的手。复用 PF2 片段。"
s = use("S07", "S07_02", song=(51.0, 54.39), clip="S07_01", clip_in=3.0)
s["img_cn"] = "复用 S07 片段的后半段（老周笑了）。"; s["an_cn"] = ""; s["an_en"] = ""; s["dlg"] = ""
use("S09", song=(54.39, 59.0))
use("S10", song=(59.0, 61.02))
new(id="RG2", src="新增", story="现在访谈", stage="MATURE", guitar="Y", song=(61.02, 66.8),
    camera="中景，50mm，缓慢推近", action="她抱着电吉他唱，头一格一格地偏向一侧，像在找一个人", motion="涡轮转动、散热缝开合", light="落地灯与顶光，薄烟", emotion="深情",
    img_cn="新出图。中景：成熟形象的 ALPHA 坐在扶手椅里抱着黄色电吉他唱歌，头微微偏向一侧，落地灯照着她，背景暗处坐着安静的工作人员。",
    img_en="medium shot of {A} sitting in a worn armchair singing with {G}, head tilted slightly to one side as if looking for someone, warm floor lamp and one top light through haze, quiet crew sitting in the dark background, 50mm",
    an_cn="0–5.8 秒：她唱这一句，嘴型跟 @音频1；头一格一格地偏向一侧，每格之间停顿一下；唱到句尾，耳侧涡轮缓缓转动。", an_en="0–5.8s: she sings the line, lips following @audio1; her head tilts to one side in small steps with a pause between each; at the end of the line the ear turbines turn slowly.")
sing(S[-1], "ALPHA_RG2_01")
use("S11", song=(66.8, 70.5))
use("H1", song=(70.5, 76.5))
flash("S06", "F05", (76.5, 77.8), 1.0, "现在：她的虹膜暗了一下。")
use("S13", song=(77.8, 80.5))
use("S14", song=(80.5, 82.8))
s = new(id="S15", src="S15", story="回忆", stage="NONE", song=(82.8, 84.0),
    camera="特写，100mm", action="老人的手背上写着“记得给 ALPHA 充电”", light="台灯暖光斜照",
    img_cn="新出图。特写：满是皱纹的老人手背，用蓝色圆珠笔写着字（文字后期合成）。",
    img_en="macro close-up of the back of an old wrinkled hand with age spots, words handwritten in blue ballpoint pen on the skin, warm desk lamp light raking across the skin texture, dark background, 100mm macro",
    an_cn="0–1.2 秒：那只手轻轻握成拳。", an_en="0–1.2s: the hand slowly closes into a fist.")
s["story"] = "回忆"
use("S16", song=(84.0, 90.5))
new(id="RG3", src="新增", story="现在访谈", stage="MATURE", guitar="Y", song=(90.5, 93.59),
    camera="近景，85mm，固定", action="她唱完这一句，左手离开琴颈，五指慢慢合拢，像握着什么", motion="手指合拢", light="顶光", emotion="思念",
    img_cn="新出图。近景：成熟形象的 ALPHA 抱着黄色电吉他，左手离开琴颈举在胸前，金属手指半合，像握着一样看不见的小东西。",
    img_en="close shot of {A} holding {G}, her left hand lifted off the neck and held before her chest, metal fingers half closed as if holding something small and invisible, top light, dark background, 85mm",
    an_cn="0–3 秒：她唱完句尾，嘴型跟 @音频1；左手离开琴颈，五指一节一节慢慢合拢。", an_en="0–3s: she finishes the line, lips following @audio1; her left hand leaves the neck and the fingers close joint by joint.")
sing(S[-1], "ALPHA_RG3_01")
use("S18", song=(93.59, 95.8))
use("S19", song=(95.8, 100.3))
use("S20", song=(100.3, 104.5))
use("S21", song=(104.5, 109.5))
use("H3", song=(109.5, 111.8))
use("S22a", song=(111.8, 117.5))
new(id="RG4", src="新增", story="现在访谈", stage="MATURE", guitar="Y", song=(117.5, 121.0),
    camera="中近景，50mm，固定", action="间奏里她低头弹琴，眼睛的光调到最暗，头一格一格地低下去", motion="眼光变暗", light="只剩顶光", emotion="沉入回忆",
    img_cn="新出图。中近景：成熟形象的 ALPHA 低头弹黄色电吉他，眼睛的光很暗，只有一束顶光，背景全黑。",
    img_en="medium close-up of {A} playing {G} with her head bowed, the light in her eyes dimmed almost to nothing, only one top light, black background, 50mm",
    an_cn="0–3.5 秒：她弹着间奏，眼睛的光慢慢调暗，头一格一格地低下去。", an_en="0–3.5s: she plays the interlude, her eye light slowly dims and her head lowers in small steps.", robot=True)
use("S22b", song=(121.0, 131.5))
use("S23", song=(131.5, 134.8))
s = use("S24", song=(134.8, 140.5))
s["dlg"] = ""
s = use("PF3", song=(140.5, 151.02), trans="dissolve")
s["dlg"] = "字幕　问：你为什么会拿起吉他？／答：站台太安静了。我需要一点声音。"
sing(s, "ALPHA_PF3_01")
# ---- low-life montage
use("L01", song=(151.02, 153.2))
use("H2", song=(153.2, 155.2))
use("L02", song=(155.2, 157.68))
use("L03", song=(157.68, 160.0))
use("L04", song=(160.0, 162.0))
use("L05", song=(162.0, 164.37))
use("L06", song=(164.37, 166.4))
use("L07_01", song=(166.4, 168.0))
use("L07_02", song=(168.0, 169.6))["dlg"] = ""
s = sing(use("L08_01", song=(169.6, 172.6)), "ALPHA_L08_01")
s.update(lyrics="在人来人往的尘世间（尾）／真心的人又能有几个", snd="母带",
         an_cn="0–3 秒：她站在包间中央笑着对麦克风唱，嘴型跟 @音频1 的对应部分；醉汉哄笑举杯，门口的阿凯一动不动。",
         an_en="0–3s: she sings into the mic with a professional smile, lips following the matching part of @audio1; the drunk men laugh and raise glasses; Akai stands still by the door.")
use("L08_02", song=(172.6, 174.4))["snd"] = "母带"
use("M1", song=(174.4, 176.4))
s = use("L09_02", "L09", song=(176.4, 177.63))
s.update(lip="否", seg="", mouth="是（侧脸）", snd="母带")
# ---- meeting the hidden ones
s = sing(use("S25", song=(177.63, 181.2)), "ALPHA_S25_01")
s.update(lyrics="谁不是谁今生的过客（前半）", an_cn="0–3 秒：她靠墙弹唱，嘴型跟 @音频1；3–3.6 秒：电源线一松，她停在拨弦的那一下，眼睛暗下去。",
         an_en="0–3s: she plays and sings against the wall, lips following @audio1; 3–3.6s: the power cord drops, she freezes mid-strum and her eyes go dark.")
use("S26", song=(181.2, 184.29))
use("S27", song=(184.29, 186.3))
s = use("S28_01", song=(186.3, 188.8))
s["dlg"] = "字幕　问：后来为什么不戴了？／答：戴着它，唱歌的就不是我了。"
use("S28_02", song=(188.8, 190.98))
sing(use("S29_01", song=(190.98, 194.3)), "ALPHA_S29_01")["lyrics"] = "亲爱的朋友不必难过（前半）"
sing(use("S29_02", song=(194.3, 197.7)), "ALPHA_S29_01")["lyrics"] = "亲爱的朋友不必难过（后半）"
use("S32", song=(197.7, 199.4))
sing(use("PF4", song=(199.4, 204.48)), "ALPHA_PF4_01")
sing(use("S30", song=(204.48, 208.6)), "ALPHA_S30_01")
use("S31", song=(208.6, 211.08))
use("S33", song=(211.08, 217.8), trans="dissolve")
use("S34", song=(217.8, 221.0))
new(id="RG5", src="新增", story="现在访谈", stage="MATURE", guitar="Y", song=(221.0, 224.31),
    camera="特写，100mm，固定", action="她不再扫弦，两根金属手指在琴身上轻轻敲拍子，和冬夜里老周的手指一样", motion="手指敲击", light="顶光", emotion="温柔",
    img_cn="新出图。特写：成熟形象 ALPHA 的两根银色机械手指搭在黄色电吉他的琴身上，像在打拍子。（与 S34 老周敲扶手的手构成匹配剪辑）",
    img_en="close-up of two silver mechanical fingers of {A} resting on the body of {G} mid-tap like keeping time, top light, black background, 100mm",
    an_cn="0–3.3 秒：两根金属手指在琴身上跟着拍子轻轻敲，节奏和上一镜老周的手指一致。", an_en="0–3.3s: two metal fingers tap the guitar body gently in time, matching the rhythm of the old man's fingers in the previous shot.", robot=True)
use("S35", song=(224.31, 231.25), trans="dissolve")
s = use("S36_01", song=(231.25, 235.5))
s.update(action="寂静之后，梯子上的老杨第一个鼓掌，工作人员都站了起来", an_cn="0–2 秒：一片寂静；2–4.3 秒：右后方梯子上的老杨第一个鼓掌，下面的工作人员陆续站起来。",
         an_en="0–2s: silence; 2–4.3s: on the ladder behind right, Lao Yang starts clapping first and the crew below stand up one after another.")
s = use("S36_02", song=(235.5, SONG_END))
s.update(action="她站起来，向工作人员鞠了一躬，动作一格一格的", an_cn="0–5 秒：掌声里，她慢慢站起来，转向工作人员，向他们鞠了一躬，鞠躬的动作一格一格的。",
         an_en="0–5s: amid the applause she slowly stands, turns to the crew and bows to them, the bow moving in small mechanical steps.", robot=True)
# ================================================================ EPILOGUE
s = use("S37", "EP1", ep=(0.0, 8.0))
s.update(action="林姐轻声再问一遍；她回答", dlg="字幕　林姐：所以……你的悲伤，是真的吗？／ALPHA：我不知道它算不算真的。他走的那天，我在站台站了七个小时。",
         img_cn="新出图。纪录片访谈双人中景：左边抱黄色电吉他的成熟形象 ALPHA，右边林姐，一盏落地灯在两人之间，背景全黑。",
         img_en="documentary interview two-shot in a pitch black studio, {A} with {G} on the left, a Chinese female interviewer in her early forties with short bob hair and a black suit on the right leaning forward to listen, a single floor lamp between them, quiet, 40mm anamorphic",
         an_cn="0–3 秒：林姐身体前倾，轻声问；3–8 秒：ALPHA 停了很久，慢慢回答，头一格一格地低下。", an_en="0–3s: the interviewer leans in and asks softly; 3–8s: ALPHA pauses a long time and answers slowly, head lowering in small steps.",
         protect="林姐（真人）")
use("S38", "EP2", ep=(8.0, 18.0), trans="dissolve")
new(id="END", src="—", asset="—", story="—", stage="NONE", ep=(18.0, 20.0), camera="黑场字幕", action="片名：远去的列车", snd="静")

# ================================================================ times, checks
for k in S:
    if "mv" in k: k["mv_in"], k["mv_out"] = k["mv"]; k["song_in"] = k["song_out"] = None; k["block"] = "冷开场"
    elif "song" in k: k["song_in"], k["song_out"] = k["song"]; k["mv_in"], k["mv_out"] = k["song_in"]+OFF, k["song_out"]+OFF; k["block"] = "歌曲"
    elif "ep" in k: k["mv_in"], k["mv_out"] = EPI_START + k["ep"][0], EPI_START + k["ep"][1]; k["song_in"] = k["song_out"] = None; k["block"] = "结尾"
prev = 0.0
for k in S:
    assert abs(k["mv_in"] - prev) < 1e-6, (k["id"], k["mv_in"], prev); prev = k["mv_out"]
assert abs(prev - (EPI_START + EPI)) < 1e-6

def anim(k):
    if not k["an_cn"]: return "", ""
    rc = "" if k["an_cn"].startswith("@图片") else "@图片1 作为首帧。"
    re_ = "" if k["an_en"].startswith("@image") else "@image1 as the first frame. "
    if k["lip"] == "是":
        rc += f"@音频1 为本镜演唱音频（{k['seg']}_MIX_v001.wav），嘴型与之同步；若平台不支持音频参考，生成后再对口型。"
        re_ += f"@audio1 is the vocal ({k['seg']}_MIX_v001.wav); sync the lips to it, or lip-sync afterwards if audio reference is unsupported."
    cc, ce = a_cons(k)
    rob_c = ROBOT_CN if k.get("robot") else ""
    rob_e = ROBOT_EN + " " if k.get("robot") else ""
    return (rc + k["an_cn"] + " " + rob_c + "镜头：" + k["camera"] + "。" + cc + VID_CN,
            re_ + k["an_en"] + " " + rob_e + "Camera: " + cam_en(k["camera"]) + ". " + ce + " " + VID_EN)
# lyrics heard under each song shot (recomputed from the LRC, the v7 text no longer matches the new timing)
_sl = os.path.join(HERE, "audio", "song_lines.csv")
if os.path.exists(_sl):
    LINES = [(float(r["song_in"]), float(r["song_out"]), r["lyrics"]) for r in csv.DictReader(open(_sl, encoding="utf-8-sig"))]
    for k in S:
        if k["song_in"] is None: continue
        hit = []
        for a_, b_, txt in LINES:
            ov = min(b_, k["song_out"]) - max(a_, k["song_in"])
            if ov > 0.25:
                part = "" if (k["song_in"] <= a_ + 0.25 and k["song_out"] >= b_ - 0.25) else ("（前段）" if k["song_in"] <= a_ + 0.25 else ("（尾）" if k["song_out"] >= b_ - 0.25 else "（中段）"))
                hit.append(txt + part)
        k["lyrics"] = "／".join(hit) if hit else ("（前奏）" if k["song_in"] < LINES[0][0] else ("（尾奏）" if k["song_in"] >= LINES[-1][1] - 0.25 else "（间奏）"))

# how long each generated clip must be (its own shot, plus the parts other shots reuse)
SEGT = {}
_sc = os.path.join(HERE, "audio", "audio_segments.csv")
if os.path.exists(_sc):
    SEGT = {r["segment_id"]: (float(r["song_in"]), float(r["handle_in"])) for r in csv.DictReader(open(_sc, encoding="utf-8-sig"))}
def _start(k):
    if k.get("clip_in") is not None: return float(k["clip_in"])
    if k["seg"] in SEGT and k["song_in"] is not None: return SEGT[k["seg"]][1] + k["song_in"] - SEGT[k["seg"]][0]
    return 0.0
NEED = {}
for i, k in enumerate(S):
    owner = k.get("clip") or k["id"]
    tail = 0.6 if i + 1 < len(S) and S[i + 1]["trans"] == "dissolve" else 0.0     # runs under the next shot's dissolve
    NEED[owner] = max(NEED.get(owner, 0.0), _start(k) + k["mv_out"] - k["mv_in"] + tail)
for k in S:
    k["gen_len"] = max(4, -(-NEED.get(k["id"], 0) // 1)) if not (k["trans"] == "flash" or k.get("clip") or k["id"] == "END") else ""
rows = []
for k in S:
    acn, aen = anim(k)
    ien = fill(k["img_en"], k) if k["img_en"] else ""
    if ien and not ien.startswith("(edit") and "||" not in ien: ien = f"{ien}, {MJ} {MJP}"
    elif "||" in ien: ien = ien.replace("  ||  END FRAME:", f", {MJ} {MJP}  ||  END FRAME:") + f", {MJ} {MJP}"
    rows.append({"shot_id": k["id"], "source_shot_id": k["src"], "source_asset_id": k["asset"], "story_time": k["story"], "stage": k["stage"],
        "transition": {"cut": "硬切", "flash": "闪切（1–1.5 秒）", "dissolve": "叠化 0.6 秒"}[k["trans"]],
        "clip_from": k.get("clip", ""), "clip_in": "" if k.get("clip_in") is None else k.get("clip_in"),
        "song_in": "" if k["song_in"] is None else f"{k['song_in']:.2f}", "song_out": "" if k["song_out"] is None else f"{k['song_out']:.2f}",
        "mv_in": f"{k['mv_in']:.2f}", "mv_out": f"{k['mv_out']:.2f}", "duration": f"{k['mv_out']-k['mv_in']:.2f}",
        "time_status": "provisional_lrc" if k["song_in"] is not None else "provisional_from_script", "fps": "24（建议）",
        "lyrics": k["lyrics"], "frame_image": k.get("frame", ""), "guitar": k["guitar"], "camera": k["camera"], "action": k["action"], "emotion": k["emotion"],
        "protected_elements": k["protect"], "mouth_visible": k["mouth"], "lip_sync_required": k["lip"], "audio_segment_id": k["seg"],
        "dialogue": k["dlg"], "sound_design": k["snd"], "robot_performance": "是" if k.get("robot") else "",
        "image_prompt_cn": k["img_cn"], "image_prompt_en": ien, "animation_prompt_cn": acn, "animation_prompt_en": aen,
        "constraints": IMG_CONS, "generate_seconds": "" if k["gen_len"] == "" else int(k["gen_len"]), "output_filename": "" if (k["trans"] == "flash" or k.get("clip") or k["id"] == "END") else f"ALPHA_{k['id']}_v001.mp4", "version": "v001"})
with open(os.path.join(HERE, "03_分镜清单.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(os.path.join(HERE, "04_时间轴段落.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["block_id", "block_type", "song_in", "song_out", "mv_in", "mv_out", "duration", "notes"])
    w.writerow(["B0", "冷开场（环境声＋字幕）", "", "", "0.00", f"{COLD:.2f}", f"{COLD:.2f}", "第 10 秒进歌"])
    w.writerow(["B1", "歌曲（连续，不中断）", "0.00", f"{SONG_END:.3f}", f"{COLD:.2f}", f"{EPI_START:.3f}", f"{SONG_END:.3f}", "mv = song + 10"])
    w.writerow(["B2", "结尾（环境声＋字幕）", "", "", f"{EPI_START:.3f}", f"{EPI_START+EPI:.3f}", f"{EPI:.2f}", ""])
# prompt book
gen = [k for k in S if k["trans"] != "flash" and not k.get("clip") and k["id"] != "END"]
L = []; w = L.append
w("# 《远去的列车》第八版：逐镜提示词\n")
w(f"> 成片约 {EPI_START+EPI:.0f} 秒（{int((EPI_START+EPI)//60)} 分 {int((EPI_START+EPI)%60)} 秒）：冷开场 10 秒 → 歌曲 240.5 秒连续不断 → 结尾 20 秒。")
w(f"> 一共 {len(S)} 个剪辑镜头，其中 **需要生成的视频 {len(gen)} 条**；其余是闪切或匹配剪辑，复用已生成的片段，不用单独生成。")
w("> 标 🤖 的是机器人式演绎镜头，提示词里已加入整段“机器人式深情演唱”的动作描述。时间暂定：歌曲时间取自母带内嵌歌词。\n")
for k, r in zip(S, rows):
    if k["id"] == "END": continue
    title = re.split(r"[，；、（]", k["action"])[0]
    tag = {"flash": "⚡闪切", "dissolve": "〰叠化", "cut": ""}[k["trans"]]
    w(f"### {k['id']}　{title}　{tag}{' 🤖' if k.get('robot') else ''}")
    tm = f"歌曲 {r['song_in']}–{r['song_out']}｜" if r["song_in"] else ""
    gl = f" · **生成 {r['generate_seconds']} 秒**" if r["generate_seconds"] else ""
    w(f"`{tm}成片 {r['mv_in']}–{r['mv_out']}（{r['duration']} 秒）` · {k['story']} · 口型：{k['lip']}{gl}\n")
    if k["trans"] == "flash" or k.get("clip"):
        w(f"- {r['image_prompt_cn']}\n"); continue
    w(f"- **素材**：{k['asset']}" + (f"　`{k['frame']}`" if k.get('frame') else ""))
    if k["lyrics"]: w(f"- **歌词**：{k['lyrics']}")
    if k["dlg"]: w(f"- **字幕**：{k['dlg'].replace('字幕　','')}")
    w(f"- **图片**：{k['img_cn']}")
    if r["image_prompt_en"]: w("```\n" + r["image_prompt_en"] + "\n```")
    if r["animation_prompt_cn"]:
        w("**sd2.5（中文）**\n```\n" + r["animation_prompt_cn"] + "\n```")
        w("**sd2.5 (EN)**\n```\n" + r["animation_prompt_en"] + "\n```\n")
open(os.path.join(HERE, "05_逐镜提示词.md"), "w").write("\n".join(L))
print(len(S), "edit shots;", len(gen), "clips to generate; total", round(EPI_START+EPI, 2), "s")
print("new images:", sum(1 for k in gen if k["img_cn"].startswith("新出")))
print("lip-sync:", [k["id"] for k in S if k["lip"] == "是"])
