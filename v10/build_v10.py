# v10: the v9 grouping (16 multi-shot groups, Seedance 2.0 <=15 s, 2.5 <=30 s), re-mapped onto the 34 images the user
# picked (挑选 folder, MAT-001..035) and the reference rules of the 2026-10-06 prompt handoff. No new MJ images.
# Singing groups get an exact-length audio file cut from the master at measured quiet points, padded with silence.
# Outputs: 02_分组提示词.md, 03_分组清单.csv, 05_镜头卡对照.csv, audio/*.mp3|wav
import csv, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MASTER = os.path.join(ROOT, "v8", "audio", "_master_decoded.wav")
if not os.path.exists(MASTER):
    MASTER = "/root/.claude/uploads/244b6930-24ca-5e89-bb8e-bcf0d6db12f0/1dd96bd4-_____.mp3"
AUD = os.path.join(HERE, "audio")
os.makedirs(AUD, exist_ok=True)
LINES = [(r["line_id"], float(r["song_in"]), float(r["song_out"]), r["lyrics"])
         for r in csv.DictReader(open(os.path.join(ROOT, "v8", "audio", "song_lines.csv"), encoding="utf-8-sig"))]

# ------------------------------------------------------------------ the user's picked images (挑选, 34 unique files)
IMG = {
 "角色卡": "MAT-035　角色卡.PNG", "吉他卡": "MAT-034　新吉他卡.PNG",
 "K22": "MAT-001　006_K22_P1c_演播室贴设备标签_NEW_成熟造型候选.png",
 "K20": "MAT-002　008_K20_S02_面部与吉他极近景_NEW_成熟造型候选.png",
 "K24": "MAT-003　009_K24_S07_实验室与老周对视_最新候选.png",
 "K19": "MAT-004　010_K19_H1_听证大厅俯拍全景_最新候选.png",
 "K25": "MAT-005　012_K25_S22a_车站老周披衣告别_最新候选.png",
 "K30": "MAT-006　013_K30_PF3_空站台坐着弹琴_最新候选.png",
 "R02": "MAT-007　014_R02_L01_公厕镜前戴上假发_OLD_前期过渡候选.png",
 "K03": "MAT-008　015_K03_L02_劳务市场等待_最新候选.png",
 "K07": "MAT-009　016_K07_L03_拆解厂捧起机器人头部_最新候选.png",
 "K06": "MAT-010　017_K06_L04_雷雨中的输电塔_V2_最新候选.png",
 "K26": "MAT-011　018_K26_L05_冷库搬箱子_最新候选.png",
 "K31": "MAT-012　019_K31_L06_小巷黑市充电_V2_最新候选.png",
 "K05": "MAT-013　021_K05_L07_红灯房间抱损坏部件_V2_最新候选.png",
 "K29": "MAT-014　022_K29_L08_包间拿麦克风演唱_V2_最新候选.png",
 "K01": "MAT-015　023_K01_L09_帘幕后候场唱歌_最新候选.png",
 "K15": "MAT-016　025_K15_S25_地下通道坐着卖唱_最新候选.png",
 "K09": "MAT-017　026_K09_S26_走廊里小鹿给电_最新候选.png",
 "R04": "MAT-018　029_R04_S28_出租屋摘假发后正面近景_OLD_前期过渡候选.png",
 "K08": "MAT-019　030_K08_S29_雨夜天台合奏_最新候选.png",
 "K27": "MAT-020　031_K27_S29_雨夜天台仰头弹唱_最新候选.png",
 "K11": "MAT-021　033_K11_PF2_手部与吉他特写_OLD_前期过渡候选.png（MAT-022 是同一张）",
 "K13": "MAT-023　036_K13_PF4_低角度仰拍弹唱_NEW_成熟造型候选.png",
 "K18": "MAT-024　040_K18_S30_演播室弹唱近景_NEW_成熟造型候选.png",
 "K17": "MAT-025　042_K17_S36_演播室座椅背侧面_NEW_成熟造型候选.png",
 "R05": "MAT-026　044_R05_S36_演播室背侧近景_NEW_成熟造型候选.png",
 "K28": "MAT-027　045_K28_S38_春天与老周并坐长椅_最新候选.png",
 "窗暗": "MAT-028　0_0 (7).png（住宅楼夜景，窗户少）",
 "窗亮": "MAT-029　0_2 (6).png（住宅楼夜景，窗户亮满）",
 "R03": "MAT-030　vrcheng23_a_subway_passage_a_huge_glowing_white_billboard…_副本.png（AI MUSIC 广告与真人乐手，保留原图）",
 "篷布": "MAT-031　vrcheng23_an_empty_old_warehouse_a_human-shaped_figure…png（仓库里盖着篷布的人形）",
 "打印机": "MAT-032　vrcheng23_close-up_of_an_office_printer…png（打印机吐出带红章的通知）",
 "黄琴手": "MAT-033　vrcheng23_close-up_of_scratched_silver_robotic_fingers…png（机械手指按黄色电吉他）",
}

# ------------------------------------------------------------------ shared prompt text
STYLE = ("写实电影质感，像真实发生的事：35mm 变形宽银幕镜头，柯达 500T 胶片颗粒，低调的动机光源，深阴影，低饱和，"
         "2020 年代中国东北的真实街道和室内，轻微手持感。")
ALPHA = "ALPHA 是同一位成年女性机器人：银色分片机械脸、蓝紫色虹膜、青色嘴唇、耳侧圆形涡轮，脖子、手指和关节都是机械结构，身上没有任何人类皮肤。"
LOOK = {
 "MATURE": "现在的她：青、黄、银三色机械外壳，头部黄色翼片（以角色卡为准），抱黄色机械电吉他（以吉他卡为准，银色齿轮轮毂）。",
 "B1": "初生的她：银白色机身带青色点缀，不穿衣服，不戴假发，用蜂蜜色旧木吉他（G-B）。",
 "COAT": "她穿黑色长羽绒服、围灰色针织围巾（老周的围巾），不戴假发，背蜂蜜色旧木吉他（G-B）。",
 "LOW": "低谷期的她：黑色长羽绒服、灰围巾，头上一顶廉价、戴歪的黑色假发（假发绕开耳侧涡轮，不穿插）。",
 "V2": "夜场装的她：黑色露肩短上装和短裙，露出的肩、臂、腰、腿全是机械材质，戴廉价黑假发。",
}
PEOPLE = {
 "老周": "老周：七十岁左右的中国老工程师，花白寸头，旧眼镜，棕色旧夹克（以参考图里的老人为准）。",
 "林姐": "林姐：四十出头的中国女主持人，齐耳短发，黑色西装，说话温和。",
 "老杨": "老杨：六十岁上下的灯光师，花白头发和白胡子，深色工装马甲（以参考图里梯子上的老人为准）。",
 "伪装者": ("小鹿、阿凯、默默始终是普通人外观：没有任何金属、线路或机械结构，影子和倒影正常。"
           "阿凯是穿黑色夹克的年轻男人，戴露指皮手套；小鹿是穿牛仔外套的年轻女人；默默是戴眼镜的中年男人。"),
}
ROBOT = ("机器人式的深情演唱：头部按小角度一格一格地转动，每格之间停顿一下；唱长音时耳侧涡轮慢慢旋转；"
         "虹膜像相机光圈一样随情绪收缩、张开；胸甲的散热缝随乐句开合，代替呼吸；嘴唇是金属分片的开合，没有牙齿和舌头；"
         "情绪最满时手指有伺服电机般的细微颤动。")
NO = ("不要动画、3D 渲染或塑料玩具质感；ALPHA 身上不出现人类皮肤；不要牙齿和舌头；配角不出现机械结构；"
      "画面里不要字幕和文字；不要慢动作；人物脸和服装在各镜头之间保持一致。")
SND_SING = "声音：以 @音频1 为准，不要另加背景音乐。"
SND_STORY = "声音：只要现场环境声（风、雨、火车、机器、人群），不要背景音乐，不要人唱歌，人物说话不出声（对白后期加字幕）。"

G = []
def group(**k):
    G.append(k); return k

# ------------------------------------------------------------------ groups (song = (clip_in, vocal_cut)); cards = the 76 shot cards each group covers
group(id="G00", title="冷开场·演播室", model="2.0", dur=15, kind="剧情", look="MATURE", people=["林姐", "老杨"],
      cards=["P1", "P1c", "O1", "P1b", "O8", "O9"],
      refs=[("角色卡", "ALPHA 现在的造型"), ("K22", "第 1 镜的首帧和演播室"), ("K17", "第 2 镜：梯子上的白胡子老人就是老杨"), ("吉他卡", "黄色电吉他")],
      shots=[(0, 3.5, "中景，K22 的机位：场务弯腰，小心地把一枚小领夹麦贴在 ALPHA 肩甲上；她转头向场务微微点头致谢，场务笑着退开。去掉桌上的嘉宾牌，画面里没有任何标签文字。"),
             (3.5, 6, "仰拍：K17 里那位白胡子老人（老杨）站在铝梯上拧好最后一盏影视灯，低头看见 ALPHA 在向他点头，笑着朝她抬了抬手。"),
             (6, 9.5, "过肩：越过 ALPHA 的金属后脑和黄色翼片（虚焦）拍对面扶手椅里的林姐，她温和地问了一句话，然后安静地等。"),
             (9.5, 12, "近景：ALPHA 沉默了一下，目光一格一格地移向靠在椅边的黄色电吉他，再抬眼，轻声说了一句话，有点不好意思。"),
             (12, 15, "全景：她把吉他抱到腿上；暗处的工作人员轻轻放下手里的东西，一个个坐下来。")],
      dlg=["ALPHA：谢谢。", "林姐：第一个问题……你的悲伤，是真的吗？", "ALPHA：我可以……唱出来吗？"],
      use="成片 0:00–0:10 冷开场，以及前奏里工作人员坐下的镜头。林姐清楚的一帧截下来给 G14 用。")
group(id="G01", title="演播室·开口", model="2.5", dur=28, kind="演唱", song=(0.00, 27.60), look="MATURE", people=["林姐", "老杨"],
      cards=["P5", "S01", "S02", "PF1", "S03", "S04", "S06"],
      refs=[("角色卡", "ALPHA 现在的造型"), ("黄琴手", "第 1 镜：手和黄色电吉他"), ("K20", "第 4 镜：唱第一句的极近景"),
            ("K13", "第 5 镜：低角度弹唱，背后梯子上是老杨"), ("K17", "演播室空间和老杨"), ("吉他卡", "黄色电吉他")],
      shots=[(0, 5, "手部特写（黄琴手）：金属手指按弦、扫弦，弹前奏；手的颜色和角色卡一致（银色和青色）。"),
             (5, 10, "全景（K17 的空间）：灯下她低头弹前奏，暗处的工作人员和观众都安静地听；慢慢推近。"),
             (10, 14.4, "胸口大特写：第一句之前，胸甲上一排细窄的散热缝缓缓张开，像吸了一口气。"),
             (14.4, 21, "极近景（K20）：她低头唱第一句，金属分片嘴唇随音频开合，虹膜像光圈一样慢慢收小。"),
             (21, 24.5, "低角度（K13）：她仰头唱第二句，头一格一格地抬起来，耳侧涡轮开始转动；背后梯子上的老杨停住了。"),
             (24.5, 28, "反应镜头：梯子上的老杨慢慢摘下一只手套；暗处林姐把手卡放到腿上，摘下一边耳返。")],
      use="歌曲 0–28 秒（前奏、第 1–2 句）。中间我会插回忆闪切。")
group(id="G02", title="回忆·诞生", model="2.5", dur=30, kind="剧情", look="B1", people=["老周"],
      cards=["S07", "S08", "S09", "S10"],
      refs=[("K24", "第 1 镜的首帧：实验室、老周、初生的 ALPHA"), ("K11", "第 2 镜：她的手和蜂蜜色木吉他"), ("R03", "第 5 镜：那个真人乐手（同一个演员）")],
      shots=[(0, 6, "K24：夜里的旧实验室，她的眼睛第一次亮起，蓝光一格一格地变亮；对面的老周愣住，然后笑了。"),
             (6, 11, "特写（K11）：老周的手覆在她的银色机械手指上，帮她按住木吉他的弦；她的手指很生硬。"),
             (11, 16, "中景：桌上的旧录音机在放磁带，老周跟着哼，她歪着头听，头一格一格地转向他。"),
             (16, 21, "商场里的小演出：她抱着木吉他唱完；一个小女孩伸手碰了碰她的金属手指，母亲立刻把孩子拉开，没有看她。"),
             (21, 25, "人群外，R03 里那个背琴包的年轻乐手握着刚挂断的手机，看了她一眼，转身走了。"),
             (25, 30, "她独自站在原地，低头看着自己被碰过的手指。")],
      dlg=["老周：会唱歌，就有人愿意听你说话了。", "母亲：别碰，那是个东西。"],
      use="B1 段（第 5–7 句）的回忆。")
group(id="G03", title="回忆·被否定", model="2.0", dur=15, kind="剧情", look="B1", people=[],
      cards=["S11", "H1", "S13"],
      refs=[("K24", "初生的 ALPHA 的样子（只看人物）"), ("K19", "第 2 镜的首帧：听证大厅"), ("R03", "第 3 镜的首帧：地铁通道（保留原图）")],
      shots=[(0, 5, "黑暗的演出场地，一排排手机举起来，远处小舞台上很小的 ALPHA 在唱，人群在拍她、笑她。"),
             (5, 10, "K19 俯拍：听证大厅，大屏幕上的投票一格一格变红；一位专家指着屏幕说话；她站在大厅中央，抬头看向高处。"),
             (10, 15, "R03：地铁通道里巨大的 AI 音乐广告亮着，广告下的真人乐手在弹唱，人流从他身边走过，没有人停下，他弹错了一个和弦。")],
      dlg=["专家：它没有生命。它的悲伤，只是一段被训练出来的程序。"],
      use="C1 段（第 9–11 句）的回忆，快剪。")
group(id="G04", title="演播室·真心的人", model="2.5", dur=27, kind="演唱", song=(60.70, 87.00), look="MATURE", people=["林姐"],
      cards=["S05", "S06", "P3"],
      refs=[("角色卡", "ALPHA 现在的造型"), ("K18", "第 1 镜：弹唱近景"), ("K13", "第 3 镜：低角度仰拍"), ("K20", "第 5 镜：极近景"), ("吉他卡", "黄色电吉他")],
      shots=[(0, 6, "近景（K18）：她唱“真心的人又能有几个”，头一格一格地偏向一侧，像在找一个人。"),
             (6, 10, "耳侧大特写：唱长音时耳侧涡轮缓缓旋转，叶片之间透出微光。"),
             (10, 17, "低角度（K13）：她闭上眼唱，胸甲散热缝随乐句开合。"),
             (17, 21, "林姐近景：她眼眶发红，一滴泪落在手卡上，墨迹晕开。"),
             (21, 27, "极近景（K20）：她睁开眼继续唱，虹膜慢慢张开；句尾左手离开琴颈，五指慢慢合拢，像握着什么，手指有细微颤动。")],
      use="歌曲 61–87 秒（第 8–11 句），和 G03、G05 交叉剪。")
group(id="G05", title="回忆·照顾与报废", model="2.5", dur=30, kind="剧情", look="B1", people=["老周"],
      cards=["S14", "S15", "S16", "S18", "S19", "S20"],
      refs=[("K24", "老周、实验室和初生的 ALPHA"), ("打印机", "第 4 镜的首帧"), ("篷布", "第 5 镜的首帧：仓库里的篷布")],
      shots=[(0, 4, "厨房：老周打开冰箱，钥匙放在里面，他拿着钥匙愣住，想不起来自己为什么放在这里。"),
             (4, 7, "特写：老人的手背上用圆珠笔写着几个字（字迹看不清）。"),
             (7, 13, "实验室：老周把一颗黄色糖纸的润喉糖放进她的金属手心，她慢慢握住；两人说话。"),
             (13, 17, "打印机：吐出一张带红章的通知。"),
             (17, 23, "篷布：空旷的旧仓库，篷布下透出的蓝光一点点暗下去，熄灭。"),
             (23, 30, "手电光照进仓库，老周掀开篷布，她的眼睛闪了两下，亮了；老人松了一口气。")],
      dlg=["ALPHA：他们为什么怕我？", "老周：不是怕你。是怕自己被落下。"],
      use="C1 段尾和间奏（88–110 秒）。手背上的字“记得给 ALPHA 充电”后期合成。")
group(id="G06", title="回忆·告别", model="2.5", dur=30, kind="剧情", look="COAT", people=["老周"],
      cards=["S21", "H3", "S22a", "S22b", "S23", "S24"],
      refs=[("K25", "ALPHA 和老周的稳定参考，也是第 3 镜的首帧"), ("K24", "第 1 镜 ALPHA 还没穿外衣的样子"), ("K30", "第 6 镜：站台环境")],
      shots=[(0, 6, "雨中的铁轨边：老周拖着行李箱，她背着木吉他（还没穿外衣，银白色机身，K24 的样子），两人并排走向小站，都不说话。"),
             (6, 9, "雨水顺着车站告示往下流，老人的手握紧行李箱拉杆。"),
             (9, 16, "K25：站台上，老周给她穿上新买的黑色长羽绒服，拉好领口，把自己的灰围巾绕在她脖子上，说了一句话。"),
             (16, 22, "列车开走，车窗里的老周越来越小；她抬起一只手，站台上只剩下她。"),
             (22, 26, "大特写：一滴雨顺着她脸上的金属接缝滑下。"),
             (26, 30, "固定机位（K30 的站台）：她一动不动地站着，天色从白天慢慢变成黄昏，再到夜里亮起站灯。")],
      dlg=["老周：天冷，穿上。", "老周：去唱吧。别在仓库里等我。"],
      use="间奏到 A2（110–144 秒）。列车和雨的镜头也会在开头当闪切用。")
group(id="G07", title="站台·第一次弹唱", model="2.0", dur=14, kind="演唱", song=(137.40, 150.85), look="COAT", people=[],
      cards=["PF3"],
      refs=[("K30", "首帧：空站台"), ("K25", "ALPHA 的稳定参考（羽绒服、围巾）")],
      shots=[(0, 6, "K30 远景：雨后的空站台，她坐着，第一次抱起木吉他弹唱这首歌。"),
             (6, 14, "侧脸近景：她低头唱“一滴泪在我的眼角滑落”，嘴唇金属分片开合，雨水从站台棚檐滴下。")],
      use="A2 段尾（137–151 秒）。")
group(id="G08", title="低谷蒙太奇", model="2.5", dur=30, kind="剧情", look="LOW", people=["伪装者"],
      cards=["L01", "H2", "L02", "L03", "L04", "L05", "L06", "L07"],
      refs=[("K25", "ALPHA 的脸和机身参考（只看她本人，服装和场景以本组描述为准）"), ("R02", "第 1 镜：公厕镜子"), ("K03", "第 3 镜：劳务市场"), ("K07", "第 4 镜：拆解厂，对面戴眼镜的是默默"),
            ("K06", "第 5 镜：雷雨电塔"), ("K26", "第 6 镜：冷库"), ("K31", "第 7 镜：黑市充电"), ("K05", "第 8 镜：红灯房间")],
      shots=[(0, 4, "R02：公厕镜前，她把一顶廉价黑假发往金属头上戴正；镜子里只有一张脸，镜中手和前景手同步。"),
             (4, 7, "雨夜：面馆老板推开门，挥手把在屋檐下躲雨的她赶走。"),
             (7, 10, "K03：劳务市场，她站在等活的人群里，一辆面包车开过来，车里的人看了她一眼，没停。"),
             (10, 14, "K07：拆解厂，她用金属手指按住一个同型号机器人头的眼睛，蓝光熄灭；对面的默默抬头看她。"),
             (14, 17, "K06：闪电劈下，她背对镜头走向输电塔。"),
             (17, 21, "K26：冷库，她背对镜头搬着箱子走过，工人们都在呼白气，只有她和默默不呼白气。"),
             (21, 25, "K31：小巷黑市，电贩子数钱；她靠墙，颈后接着线，眼睛慢慢亮起。"),
             (25, 30, "K05：红灯房间，她蹲着，把自己掉下来的外壳碎片抱在怀里，挤出一个苦涩的笑。")],
      use="B2 段（151–164 秒）快剪，每个镜头大约只用 1.5–2 秒。")
group(id="G09", title="夜场·卖唱·摩托", model="2.5", dur=18, kind="演唱＋剧情", song=(164.00, 177.45), look="V2", people=["伪装者"],
      cards=["L08", "L09", "M1"],
      refs=[("K29", "第 1 镜的首帧：包间；画面右侧穿黑夹克的年轻男人就是阿凯"), ("K01", "第 3 镜：帘幕后"), ("K25", "ALPHA 的脸和机身参考（只看她本人，服装和场景以本组描述为准）")],
      shots=[(0, 6, "K29：包间中央，她拿着麦克风职业性地笑着唱，沙发上的人在喝酒，没人听；右边的阿凯靠墙站着。"),
             (6, 9, "一个醉汉伸手拽住她的手腕，她还在唱；一只戴露指皮手套的手伸进来，捏住醉汉的手腕（阿凯）。"),
             (9, 13.5, "K01：后台帘幕边，她侧脸对着麦克风继续唱，灯光很暗。"),
             (13.5, 18, "雨夜，阿凯骑一辆旧摩托车，她披着羽绒服坐在后座，两人都不说话。")],
      silent_after=True,
      use="B2 段（164–177 秒），第 19–20 句；摩托车镜头接在后面。")
group(id="G10", title="地下通道·同类", model="2.5", dur=20, kind="演唱＋剧情", song=(177.35, 184.15), look="LOW", people=["伪装者"],
      cards=["S25", "S26", "S27", "S28"],
      refs=[("K15", "第 1 镜的首帧：地下通道"), ("K09", "第 3 镜：小鹿给电"), ("R04", "第 4 镜的尾帧：摘掉假发后，身后是小鹿、阿凯、默默"), ("K25", "ALPHA 的脸和机身参考（只看她本人，服装和场景以本组描述为准）")],
      shots=[(0, 7, "K15：地下通道，她靠墙坐着弹唱木吉他（戴假发、羽绒服）。"),
             (7, 9, "保安弯腰拔掉她音箱的插头，她停住，眼睛的光暗下去。"),
             (9, 13, "K09：走廊里，小鹿蹲下，把从袖口里拉出的一根细线接到她身上，她的眼睛一点点亮起来；小鹿的皮肤完好。"),
             (13, 20, "R04：出租屋里，小鹿、阿凯、默默站在她身后看着她；她抬手摘下假发，露出完整的金属头（开始时戴着，结束时和 R04 一样）。")],
      dlg=["小鹿：我们也是。"],
      use="C2 开头（177–191 秒）。音频只有第 21 句，之后是静音：拔插头以后她不再唱。")
group(id="G11", title="雨夜天台", model="2.5", dur=20, kind="演唱", song=(184.00, 204.00), look="COAT", people=["伪装者"],
      cards=["S29", "S32", "S32a/b"],
      refs=[("K08", "第 1 镜的首帧：天台合奏"), ("K27", "第 2 镜：仰头弹唱"), ("窗暗", "第 4 镜的首帧：窗户还没亮"), ("窗亮", "第 4 镜的尾帧：窗户都亮了")],
      shots=[(0, 7, "K08：雨夜天台，她不戴假发，抱着木吉他弹唱；阿凯在旁边跟着大声吼唱，小鹿在后面。"),
             (7, 13, "K27：她仰头唱，雨水顺着金属脸流下，耳侧涡轮转动。"),
             (13, 16, "近景：阿凯闭着眼跟着吼，手里打着拍子。"),
             (16, 20, "对面的住宅楼：从窗暗的样子开始，一扇扇窗户陆续亮起来，结束时像窗亮。")],
      use="C2 段（184–204 秒），第 22–24 句。")
group(id="G12", title="演播室·最高音到最后", model="2.5", dur=27, kind="演唱", song=(197.40, 224.15), look="MATURE", people=["老杨", "伪装者"],
      cards=["PF4", "S30", "S31", "PF2"],
      refs=[("角色卡", "ALPHA 现在的造型"), ("K13", "第 1 镜：低角度仰拍，背后梯子上是老杨"), ("K18", "第 2 镜：弹唱近景"),
            ("黄琴手", "第 5 镜：手和黄色电吉他"), ("K29", "阿凯的样子（只看右侧穿黑夹克的男人）"), ("吉他卡", "黄色电吉他")],
      shots=[(0, 7, "低角度（K13）：她仰头唱出最高音，背后梯子上是老杨的剪影，耳侧涡轮转得很快。"),
             (7, 14, "近景（K18）：她唱最后几句，头一格一格地低下来，手越弹越慢。"),
             (14, 18, "侧台暗处：阿凯站在最前，小鹿和默默在后；阿凯慢慢摘下一只皮手套。"),
             (18, 23, "近景：她唱，虹膜慢慢张开，散热缝轻轻开合。"),
             (23, 27, "手部特写（黄琴手）：她不再扫弦，两根金属手指在琴身上轻轻敲拍子；手的颜色和角色卡一致（银色和青色）。")],
      use="歌曲 197–224 秒（第 24–27 句），和 G11、G13 交叉剪。")
group(id="G13", title="之后·冬与春", model="2.5", dur=25, kind="剧情", look="MATURE", people=["老周", "伪装者"],
      cards=["S33", "S34", "S35"],
      refs=[("K28", "老周和春天的 ALPHA"), ("K25", "老周的脸（冬天）"), ("角色卡", "春天 ALPHA 的造型"), ("R04", "小鹿、阿凯、默默的样子（只看人物）")],
      shots=[(0, 7, "冬夜，养老院的房间：女儿把手机递给坐在扶手椅上的老周，屏幕上是 ALPHA 唱歌的视频；老人茫然地摇头，眼睛却一直看着屏幕。"),
             (7, 12, "特写：老人搭在扶手上的食指和中指，跟着节拍轻轻敲。"),
             (12, 19, "春天：一列绿皮火车进站，她背着旧琴盒走下车；小鹿、阿凯、默默提着行李跟在后面下车。"),
             (19, 25, "她抬头看站台，风吹落一阵花瓣。")],
      dlg=["女儿：爸，你还记得她吗？"],
      use="尾段（211–231 秒）。")
group(id="G14", title="演播室·掌声与回答", model="2.0", dur=15, kind="剧情", look="MATURE", people=["林姐", "老杨"],
      cards=["S36", "S37", "IV1–IV5"],
      refs=[("R05", "第 1 镜的首帧：梯子上的老杨在鼓掌"), ("K17", "第 2 镜：座椅背侧面"), ("角色卡", "ALPHA 现在的造型"), ("G00 截帧", "林姐的脸（从 G00 里截一帧）")],
      shots=[(0, 5, "R05：最后一个和弦结束，棚里安静了两秒；梯子上的老杨第一个鼓掌，工作人员和观众一个个站起来。"),
             (5, 9, "K17：她站起来，转向工作人员，向他们鞠了一躬，鞠躬的动作一格一格的。"),
             (9, 15, "双人中景：一盏落地灯在两人之间，林姐身体前倾轻声问；ALPHA 停了很久，慢慢回答，头一格一格地低下。")],
      dlg=["林姐：所以……你的悲伤，是真的吗？", "ALPHA：我不知道它算不算真的。他走的那天，我在站台站了七个小时。"],
      use="尾奏（231–240 秒）和结尾访谈；双人镜头也用作歌里的访谈插入（IV1–IV5 只上字幕）。")
group(id="G15", title="春天长椅", model="2.0", dur=12, kind="剧情", look="MATURE", people=["老周"],
      cards=["S38"],
      refs=[("K28", "首帧：春天长椅"), ("角色卡", "ALPHA 的造型")],
      shots=[(0, 6, "K28：春天的长椅，老人像对陌生人一样问她的名字，她回答。"),
             (6, 12, "老人想了想，笑了；远处一列火车开过，两人一起看着。")],
      dlg=["老周：你唱得真好。你叫什么名字？", "ALPHA：ALPHA。", "老周：阿尔法……好名字。像是第一个。"],
      use="结尾最后一场。")
DROPPED = {
 "O2": "开场简化：调呼吸声的情节不拍", "O3": "开场简化", "O4": "开场简化", "O6": "开场简化：打板不拍",
 "O7": "开场简化：自我介绍不拍", "P2": "开场改成工作人员尊重她，楼下抗议不拍", "P4": "小鹿只在回忆和春天出现",
}

# ------------------------------------------------------------------ checks
for g in G:
    assert g["model"] == "2.0" and g["dur"] <= 15 or g["model"] == "2.5" and g["dur"] <= 30, g["id"]
    assert len(g["refs"]) <= 9, g["id"]
    assert g["shots"][0][0] == 0 and abs(g["shots"][-1][1] - g["dur"]) < 1e-6, g["id"]
    for a, b in zip(g["shots"], g["shots"][1:]): assert abs(a[1] - b[0]) < 1e-6, g["id"]
    if "song" in g: assert g["song"][1] - g["song"][0] <= g["dur"] + 1e-6, g["id"]

# ------------------------------------------------------------------ audio
def fmt(t): return f"{t:.1f}"
def lyrics_in(g):
    a0, cut = g["song"]
    out = []
    for lid, a, b, txt in LINES:
        if min(b, cut) - max(a, a0) < 0.6: continue          # LRC out = next line's in, so skip slivers
        out.append((lid, max(0.0, a - a0), min(b, cut) - a0, txt, a < a0 - 0.4))
    return out
SR = 48000
for g in G:
    if "song" not in g: continue
    a0, cut = g["song"]
    real = cut - a0
    base = os.path.join(AUD, f"{g['id']}_{g['title'].replace('·', '_')}")
    af = (f"atrim=start={a0}:end={cut},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={real-0.15:.3f}:d=0.15,"
          f"apad=whole_dur={g['dur']}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", MASTER, "-af", af, "-ar", str(SR), "-c:a", "pcm_s16le", base + ".wav"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base + ".wav", "-c:a", "libmp3lame", "-b:a", "320k", base + ".mp3"], check=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", base + ".wav"], capture_output=True, text=True).stdout)
    assert abs(d - g["dur"]) < 0.01, (g["id"], d)
    g["audio"] = os.path.basename(base)
    g["lyr"] = lyrics_in(g)

# ------------------------------------------------------------------ prompt text
def prompt(g):
    p = []
    refs = "；".join(f"@图片{i+1} 是 {why}" for i, (k, why) in enumerate(g["refs"]))
    p.append("参考：" + refs + "。" + ("@音频1 是这一段的演唱音频。" if "song" in g else ""))
    p.append(STYLE)
    p.append(ALPHA + LOOK[g["look"]] + "".join(PEOPLE[x] for x in g["people"]))
    p.append(f"一共 {len(g['shots'])} 个镜头，按时间切换（硬切）：")
    for i, (a, b, s) in enumerate(g["shots"]):
        for j, (k, _) in enumerate(g["refs"]):               # K-numbers mean nothing to the model: point at the upload
            s = re.sub(rf"(?<![A-Za-z0-9@-]){re.escape(k)}(?![0-9])", f"@图片{j+1}", s)
        p.append(f"镜头{i+1}（{fmt(a)}–{fmt(b)} 秒）：{s}")
    if "song" in g:
        ly = "；".join(f"{fmt(a)}–{fmt(b)} 秒唱「{t}」" for _, a, b, t, part in g["lyr"])
        tail = g["song"][1] - g["song"][0]
        extra = f"{fmt(tail)} 秒以后音频是静音，她不再唱，嘴闭上。" if g["dur"] - tail > 0.3 else ""
        p.append(f"演唱：ALPHA 的嘴型与 @音频1 同步，{ly}。{extra}只有她的脸在画面里时才对口型，手部、背影、反应镜头里音频照常继续。")
        p.append(ROBOT)
    p.append("对白：" + "／".join(g["dlg"]) + "（只做说话的动作，不出声，后期加字幕）。" if g.get("dlg") else "")
    p.append(SND_SING if "song" in g else SND_STORY)
    p.append("禁止：" + NO)
    return "\n".join(x for x in p if x)

# ------------------------------------------------------------------ write files
total = sum(g["dur"] for g in G)
with open(os.path.join(HERE, "03_分组清单.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["group_id", "title", "model", "duration_s", "kind", "song_in", "vocal_out", "audio_file", "lyrics_timing",
                "reference_images", "shots", "dialogue", "edit_use", "prompt_cn", "output_filename"])
    for g in G:
        w.writerow([g["id"], g["title"], "Seedance " + g["model"], g["dur"], g["kind"],
                    f"{g['song'][0]:.2f}" if "song" in g else "", f"{g['song'][1]:.2f}" if "song" in g else "",
                    (g["audio"] + ".mp3") if "song" in g else "",
                    "；".join(f"{lid} {a:.2f}–{b:.2f}「{t}」" for lid, a, b, t, _ in g.get("lyr", [])),
                    "；".join(f"@图片{i+1}={IMG.get(k, k)}" for i, (k, _) in enumerate(g["refs"])),
                    len(g["shots"]), "／".join(g.get("dlg", [])), g["use"], prompt(g), f"ALPHA_{g['id']}_v001.mp4"])

L = []; w = L.append
w("# 《远去的列车》第十版：分组生成提示词\n")
w(f"> {len(G)} 组，共 {total} 秒素材。**不需要出新图**，只用你「挑选」文件夹里的 34 张图（MAT 编号）。")
w("> 每组复制「提示词」整段，按「上传」一栏的顺序上传图片（顺序就是 @图片1、@图片2……），演唱组再上传音频。")
w("> 时长、比例照写；比例统一 **21:9**。生成出来不完美没关系，我会挑能用的部分重新剪。\n")
w("| 组 | 内容 | 模型 | 时长 | 类型 | 音频 |\n|---|---|---|---|---|---|")
for g in G:
    w(f"| {g['id']} | {g['title']} | {g['model']} | {g['dur']} 秒 | {g['kind']} | {g['audio'] + '.mp3' if 'song' in g else '不上传'} |")
w("")
for g in G:
    w(f"## {g['id']}　{g['title']}")
    w(f"**Seedance {g['model']}　·　{g['dur']} 秒　·　21:9　·　{g['kind']}**　　剪辑用途：{g['use']}\n")
    w("**上传**")
    for i, (k, why) in enumerate(g["refs"]):
        w(f"- @图片{i+1}：{IMG.get(k, k)}　— {why}")
    if "song" in g:
        w(f"- @音频1：`audio/{g['audio']}.mp3`（{g['dur']} 秒；母带 {g['song'][0]:.2f}–{g['song'][1]:.2f} 秒" +
          ("，之后补静音）" if g["dur"] - (g["song"][1] - g["song"][0]) > 0.05 else "）"))
        w("\n**这段音频里的歌词**（秒，从音频开头算）")
        for lid, a, b, t, part in g["lyr"]:
            w(f"- {a:5.1f}–{b:5.1f}　{t}" + ("　（只有半句）" if part else ""))
    w("\n**提示词**\n```\n" + prompt(g) + "\n```\n")
open(os.path.join(HERE, "02_分组提示词.md"), "w").write("\n".join(L))
print(len(G), "groups,", total, "s;", sum(1 for g in G if "song" in g), "with audio;",
      sum(1 for g in G if g["model"] == "2.0"), "x 2.0,", sum(1 for g in G if g["model"] == "2.5"), "x 2.5")
print("max prompt chars:", max(len(prompt(g)) for g in G))

# ------------------------------------------------------------------ the handoff's 76 shot cards -> groups
cards = list(csv.DictReader(open(os.path.join(HERE, "交接参考", "全片镜头卡_提示词与素材映射.csv"), encoding="utf-8-sig")))
where = {}
for g in G:
    for c in g["cards"]:
        where.setdefault(c, []).append(g["id"])
def lookup(sid):
    if sid in where: return where[sid]
    if sid.startswith("IV"): return where.get("IV1–IV5", [])
    if sid.startswith("S24"): return where.get("S24", [])
    return []
miss = []
with open(os.path.join(HERE, "05_镜头卡对照.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["order", "shot_id", "title", "handoff_status", "v10_group", "note"])
    for c in cards:
        gs = lookup(c["shot_id"])
        note = DROPPED.get(c["shot_id"], "")
        if not gs and not note: miss.append(c["shot_id"])
        w.writerow([c["order"], c["shot_id"], c["title"], c["status"], "、".join(gs) if gs else "不拍", note])
print("cards:", len(cards), "unmapped:", miss)
used = sorted({k for g in G for k, _ in g["refs"] if k in IMG})
print("images used:", len(used), "of", len(IMG), "; unused:", sorted(set(IMG) - set(used)))
