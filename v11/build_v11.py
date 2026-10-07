# v11: full story with a living, Chinese-context ALPHA and a new "metamorphosis" group (G11B).
# Inputs it relies on: the lip-sync mp3s already in final/audio (the user has processed them; same names, same timing).
# Outputs: 03_MJ关键帧提示词.md, 04_分组提示词.md, 05_分组清单.csv, 06_关键帧清单.csv
import csv, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LINES = [(r["line_id"], float(r["song_in"]), float(r["song_out"]), r["lyrics"])
         for r in csv.DictReader(open(os.path.join(ROOT, "v8", "audio", "song_lines.csv"), encoding="utf-8-sig"))]

# ================================================================== MJ keyframes
FACE_EN = ("her face is a rigid mask of cracked brushed-silver metal plates joined by fine dark seams, a straight narrow metal nose "
           "with tiny screws along the bridge, full glossy teal hard-shell lips, almond-shaped glowing violet-blue camera-lens eyes "
           "with metal iris blades, teal metal eyeliner and thin teal brow strips, a yellow V-shaped crest across the forehead with a "
           "small sensor plate in the middle, yellow cheek frames with slatted vent grilles, round silver turbine speakers over her ears")
NOW_EN = "ALPHA, a 3.5-meter-tall teal-and-yellow female humanoid stage robot"
NOW_LOOK = ("ALPHA's look: glossy teal and lemon-yellow painted armor over brushed-silver mechanics, a yellow helmet with swept-back "
            "yellow fins, small wheels built into her heels, a thick power cable trailing from her back; " + FACE_EN)
SCALE_EN = "true giant scale: the adult crew around her only reach her waist, her head is as wide as a man's shoulders"
PAST_EN = "ALPHA's first body, a human-sized silver-white female humanoid robot"
PAST_LOOK = ("first body's look: scratched unpainted silver-white metal limbs and exposed joints, the same face as today with silver "
             "instead of yellow trim; " + FACE_EN.replace("yellow", "silver"))
COAT = ", wearing an oversized black down jacket and a grey wool scarf"
WIG = ", wearing a crooked cheap black wig, an oversized black down jacket and a grey wool scarf, her shell dirty and chipped"
GUIT = "a large angular yellow electric guitar with a silver gear-shaped hub in its body"
WOOD = "an old honey-colored acoustic guitar"
ZHOU = "Lao Zhou, a 62-year-old Chinese engineer with grey buzz-cut hair, old metal-framed glasses and a worn brown cardigan"
ZHOU_OLD = "Lao Zhou, a very old frail Chinese man with white hair and metal-framed glasses"
LIN = "Lin, a Chinese female TV host in her early forties with short bob hair and a black suit"
YANG = "Lao Yang, a Chinese lighting technician in his fifties with grey hair, stubble and a dark work vest"
LU = "Xiaolu, a 23-year-old Chinese girl with a round face, a low ponytail and a faded denim jacket"
KAI = "Akai, a young Chinese man with spiky black hair, a worn black leather jacket and fingerless leather gloves"
MO = "Momo, a thin quiet Chinese man in his thirties with black-framed glasses and a grey work jacket"
CREW = "Chinese TV crew members in black work clothes"
STUDIO = "a large dark Chinese TV studio, black lighting grid overhead, a cold blue LED wall behind"
FILM_EN = ("cinematic film still, shot on 35mm Kodak Vision3 500T, motivated practical lighting, volumetric haze, deep clean blacks, "
           "soft halation on highlights, fine film grain, rich tactile detail of scratches, dust and fabric, grounded realism")
PARAM = " --ar 16:9 --v 8.1 --style raw --s {s} --no cartoon, anime, 3d render, plastic toy, text, watermark"
VARIANT = {
 "A": "",
 "B": ", artistic composition, strong silhouette and negative space, backlit rim light, painterly chiaroscuro",
 "C": ", handheld documentary feel, available light, a candid in-between moment, slight motion blur on the people",
}
KF = []
def kf(i, group, title, prio, old, body, s=150):
    tail = "".join(", " + t for key, t in (("{NOW}", NOW_LOOK), ("{PAST}", PAST_LOOK)) if key in body)
    KF.append(dict(id=i, group=group, title=title, prio=prio, old=old, body=body.format(
        NOW=NOW_EN, SCALE=SCALE_EN, PAST=PAST_EN, COAT=COAT, WIG=WIG, G=GUIT, W=WOOD, ZHOU=ZHOU, ZO=ZHOU_OLD, LIN=LIN, YANG=YANG,
        LU=LU, KAI=KAI, MO=MO, CREW=CREW, ST=STUDIO) + tail, s=s))
P1, P2, P3 = "必出", "建议重出", "可沿用旧图"

kf("KF00-1", "G00", "她自己驶入演播室", P1, "新", "wide eye-level shot of {ST}, {NOW} rolling slowly into the center of the stage on her own heel wheels, her eyes lit, following the raised hand of a Chinese floor manager walking backwards in front of her, two {CREW} jogging beside her guiding her power cable and looking up at her, {SCALE}, 35mm")
kf("KF00-2", "G00", "老杨在梯子顶与她平视", P1, "MAT-025 K17", "medium shot, {YANG} standing on top of a 2-meter aluminium ladder, his face level with the shoulder of {NOW}, she turns her head toward him, he grins and gives her a thumbs up while tightening a film light, hard top light and haze, {ST}, 50mm")
kf("KF00-3", "G00", "贴领夹麦，她压低肩膀配合", P1, "MAT-001 K22", "medium close-up, a young Chinese sound assistant standing on a small step ladder taping a lavalier mic to the yellow shoulder armor of {NOW}, she lowers her huge shoulder toward him to help, her lens eyes watching his hands, he smiles nervously, single tungsten spotlight through haze, {ST}, 50mm")
kf("KF01-1", "G01", "低机位全景·前奏", P1, "MAT-023 K13", "low-angle wide shot, {NOW} standing in a shaft of overhead light holding {G}, starting to play, {CREW} sitting on the floor around her feet looking up, one slowly lowering a phone, {YANG} frozen on a ladder in silhouette, {SCALE}, 24mm, {ST}", 200)
kf("KF01-2", "G01", "四分之三侧脸·开口唱", P1, "MAT-024 K18 / MAT-002 K20", "three-quarter close-up of the face of {NOW}, singing softly with her teal lips slightly parted, eyelid shutters half lowered, looking off-frame as if watching a train leave, warm top light on brushed metal, cold blue rim light, black studio background, 85mm", 200)
kf("KF01-3", "G01", "金属手指扫弦", P2, "MAT-033", "extreme close-up of the giant silver robotic fingers with yellow fingertips of {NOW} strumming {G}, the guitar body wider than the shoulders of a Chinese crew member sitting blurred in the foreground, strings vibrating, warm top light, 100mm")
kf("KF02-1", "G02", "实验室·第一次亮眼", P2, "MAT-003 K24", "late night in a cluttered old Chinese university lab, a warm desk lamp, {PAST} sitting on a workbench, her eyes lighting up for the first time, {ZHOU} across from her pushing up his glasses, frozen, then starting to smile, rain on the window, 40mm")
kf("KF02-2", "G02", "老周的手覆在她手上", P3, "MAT-021 K11", "close-up, a wrinkled old Chinese man's hand with a band-aid on the thumb resting on silver robotic fingers, guiding them to press the strings of {W}, warm tungsten desk lamp, dust in the light, 85mm")
kf("KF02-3", "G02", "商场中庭·小女孩碰她的手指", P1, "新", "a small stage in a Chinese shopping mall atrium, {PAST} sitting on a stool holding {W}, a little Chinese girl reaching out to touch her metal fingers while her mother pulls her back frowning, a few passers-by clapping half-heartedly, {ZHOU} at the back of the crowd, soft skylight, 35mm handheld")
kf("KF03-1", "G03", "听证大厅", P3, "MAT-004 K19", "high-angle wide shot of a vast circular Chinese hearing hall, rows of officials and experts, a huge screen of red votes, {PAST} standing alone in a pool of light in the center looking up, cold top light, 24mm", 200)
kf("KF03-2", "G03", "AI 音乐广告下的真人乐手", P3, "MAT-030 R03", "a Chinese subway passage, a huge glowing white digital billboard with a cold synthetic singer face, beneath it a young Chinese street musician sitting on the floor with a guitar and an empty case, commuters rushing past in motion blur, wet floor reflections, 28mm")
kf("KF04-1", "G04", "观众席后方·她高出所有人", P1, "新", "wide shot from behind the last row of a Chinese TV studio audience, backs of heads, a woman covering her mouth, a man wiping his eyes, far ahead on the stage {NOW} singing with {G} in a shaft of light, towering over the crew at her feet, {SCALE}, 35mm", 200)
kf("KF04-2", "G04", "林姐落泪", P1, "新", "close-up of {LIN} behind a monitor holding a handwritten cue card, eyes red, a tear falling on the card and blurring the ink, a Chinese director beside her silently handing her a tissue, warm light from the stage, 85mm")
kf("KF05-1", "G05", "钥匙在冰箱里", P1, "新", "late night in a small old Chinese apartment kitchen, shot from inside an open refrigerator, {ZHOU} holding a bunch of keys he just found inside, frozen in confusion, cold fridge light on his face, 35mm")
kf("KF05-2", "G05", "黄色糖纸的润喉糖", P1, "新", "late-night lab lit by one warm desk lamp, {ZHOU} placing a yellow-wrapped throat lozenge into the open silver palm of {PAST}, she slowly closes her fingers around it, rain on the window, 50mm, side view")
kf("KF05-3", "G05", "仓库篷布下的光熄灭", P3, "MAT-031 篷布", "an empty old warehouse, a human-shaped figure covered by a grey tarp with an asset tag, a faint blue glow leaking from under it, a forklift driver passing without stopping, one cold shaft of light with floating dust, 35mm")
kf("KF06-1", "G06", "站台·老周给她披衣", P2, "MAT-005 K25", "a rainy small Chinese railway platform beside an old green train, {ZHOU} wrapping his grey scarf around the neck of {PAST}{COAT}, a train attendant in uniform blowing a whistle behind them, steam and rain, 50mm")
kf("KF06-2", "G06", "黄昏的空站台", P3, "MAT-006 K30", "extreme wide locked-off shot of an empty rural Chinese railway platform at dusk after rain, {PAST}{COAT} standing alone looking down the tracks, platform lights just turning on, a thin line of orange in the clouds, 24mm", 200)
kf("KF07-1", "G07", "空站台·第一次弹唱", P2, "MAT-006 K30", "night after rain on an empty small Chinese railway platform, {PAST}{COAT} sitting on a bench playing {W} and singing, a night-shift station worker with a lantern stopping in the distance to look back, wet reflections, 35mm")
kf("KF08-1", "G08", "公厕镜前戴假发", P3, "MAT-007 R02", "a grimy public restroom in a Chinese city, {PAST}{WIG} straightening the wig in a cracked mirror, a drunk man leaving a stall glancing at her, flickering green fluorescent light, 35mm")
kf("KF08-2", "G08", "劳务市场", P3, "MAT-008 K03", "a crowded Chinese day-labor market at dawn, men in worn jackets crowding a van, {PAST}{WIG} standing among them, the driver looking at her and rolling up the window, cold mist, 50mm")
kf("KF08-3", "G08", "拆解厂", P3, "MAT-009 K07", "a Chinese robot scrapyard at night with sparks, {PAST}{WIG} pressing her fingers over the eyes of a scrapped robot head of her own model, {MO} across from her with a screwdriver frozen in his hand, 35mm")
kf("KF08-4", "G08", "雷雨电塔", P3, "MAT-010 K06", "a thunderstorm over a field, lightning striking a high-voltage tower, a small figure of {PAST}{COAT} walking toward it in the rain, seen from behind, 24mm", 200)
kf("KF08-5", "G08", "冷库搬箱子", P3, "MAT-011 K26", "a Chinese cold-storage warehouse, workers breathing white mist carrying boxes, {PAST}{WIG} carrying a box without breath mist, {MO} the same, cold fluorescent light, 35mm")
kf("KF08-6", "G08", "小巷黑市充电", P3, "MAT-012 K31", "a narrow wet Chinese back alley black market at night, a dealer counting cash, {PAST}{WIG} leaning on a wall with a cable plugged into the back of her neck, her eyes slowly glowing, 35mm")
kf("KF08-7", "G08", "红灯房间", P3, "MAT-013 K05", "a small room bathed in red light, {PAST}{WIG} crouching and holding broken pieces of her own shell, a bitter mechanical smile, 35mm")
kf("KF09-1", "G09", "包间卖唱", P2, "MAT-014 K29", "a garish Chinese KTV private room, {PAST}{WIG} singing into a microphone in the middle, people on sofas drinking and playing finger-guessing games, nobody listening, {KAI} leaning on the wall watching her, purple and red neon, 35mm")
kf("KF09-2", "G09", "雨夜摩托", P1, "新", "rainy night at a red light in a Chinese city, {KAI} on an old motorcycle, {PAST}{WIG} sitting behind him, he glances back at her, neon reflections on wet asphalt, 50mm")
kf("KF10-1", "G10", "地下通道卖唱", P2, "MAT-016 K15", "a Chinese pedestrian underpass at night, {PAST}{WIG} sitting against the tiled wall playing {W}, a delivery rider in a yellow jacket pausing to listen, commuters rushing past, 35mm")
kf("KF10-2", "G10", "走廊里小鹿给电", P2, "MAT-017 K09", "a dim corridor, {LU} kneeling and connecting a thin cable from her own sleeve to {PAST}{WIG} slumped against the wall, the robot's eyes slowly lighting up, Xiaolu smiling, her skin intact, 35mm")
kf("KF10-3", "G10", "出租屋·摘下假发", P1, "MAT-018 R04", "a cramped Chinese rental room with warm bulbs, {LU}, {KAI} and {MO} standing behind {PAST}{COAT} as she takes off her black wig and puts it on the table, showing her whole metal head, 40mm")
kf("KF11-1", "G11", "雨夜天台合奏", P1, "MAT-019 K08", "a rooftop of an old Chinese residential block on a rainy night, {PAST}{COAT} without the wig playing {W} and singing, {KAI} shouting along beside her, {LU} lighting them with a phone, {MO} holding an umbrella over a small amplifier, 35mm", 200)
kf("KF11-2", "G11", "天台仰头", P1, "MAT-020 K27", "low angle, {PAST}{COAT} singing with her head tilted up into the rain, water running down her metal face, the lit windows of Chinese apartment blocks behind, 50mm", 200)
kf("KF11B-1", "G11B", "车间：吊起的巨大新机体", P1, "新", "a huge industrial workshop at night, {NOW} hanging limp and unpowered from crane chains like merchandise, Chinese marketing staff in suits pointing up at her and taking photos, a big screen on the wall playing a rainy rooftop video, Chinese workers in blue uniforms, sodium and cold work lights, {SCALE}, 24mm", 200)
kf("KF11B-2", "G11B", "取出核心", P1, "新", "close-up on a workbench, {PAST} lying with her chest panel open, a Chinese technician's gloved hands lifting out a small glowing blue core, her eyes still lit and following the core, cold work light, 50mm")
kf("KF11B-3", "G11B", "巨人从垃圾桶捏起糖纸", P1, "新", "medium wide shot in a workshop, {NOW} bending down and pinching a tiny yellow candy wrapper out of a trash bin with two giant fingers, Chinese workers stopping and looking up at her, behind them her old silver-white first body slumped in a corner under a grey tarp, {SCALE}, 35mm")
kf("KF11B-4", "G11B", "发布会：手机的海", P1, "新", "a glitzy product launch stage in a Chinese mall, {NOW} standing under a spotlight, a sea of raised smartphones and camera flashes below her, an excited Chinese crowd cheering and taking selfies with her behind them, {SCALE}, 24mm", 200)
kf("KF11B-5", "G11B", "她的视角：人群最后的三个人", P1, "新", "high-angle point of view from 3.5 meters above a cheering Chinese crowd holding up phones, at the very back {LU}, {KAI} and {MO} standing still without phones, looking up, 50mm")
kf("KF12-1", "G12", "低角度仰拍·最高音", P1, "MAT-023 K13", "extreme low-angle wide shot, {NOW} singing the highest note with her head raised and eyes wide open, {YANG} silhouetted on a ladder behind her against the top light, {SCALE}, 18mm, {ST}", 250)
kf("KF12-2", "G12", "侧台三人", P1, "新", "dark side stage of a Chinese TV studio, {KAI} in front slowly taking off one leather glove, {LU} resting her hand on his shoulder, {MO} behind, all looking toward the stage light, 50mm")
kf("KF13-1", "G13", "冬夜养老院", P1, "新", "winter night in a Chinese nursing home room, {ZO} in an armchair, his daughter kneeling beside him holding a phone showing a robot singing, his two fingers tapping on the armrest, warm lamp and cold window, 50mm")
kf("KF13-2", "G13", "春天小站·平板货车", P1, "新", "spring at a small Chinese railway station with blossoming trees, a flatbed freight car stopping, {NOW} standing on it strapped beside an old guitar case, Chinese station workers looking up at her, {LU}, {KAI} and {MO} jumping down to untie the straps, petals in the wind, {SCALE}, 35mm", 200)
kf("KF14-1", "G14", "掌声", P2, "MAT-026 R05", "{ST}, {YANG} on a ladder clapping first, {CREW} standing up one by one applauding, {NOW} lowering her guitar, {SCALE}, 35mm")
kf("KF14-2", "G14", "林姐在她脚边仰头问话", P1, "新", "medium wide shot, {LIN} standing at the feet of {NOW} looking up and asking a quiet question, the robot bending her upper body and head down toward her to listen, {SCALE}, warm spotlight, 35mm")
kf("KF15-1", "G15", "春天长椅·她单膝跪下", P1, "MAT-027 K28", "spring at a small Chinese railway platform with falling blossoms, {ZO} sitting on a wooden bench, {NOW} kneeling on one knee beside the bench and leaning toward him, her head still above his, he looks up at her like a stranger and smiles, an old green train passing in the distance, soft warm sun, {SCALE}, 35mm", 200)

def mj(k, v):
    return k["body"] + ", " + FILM_EN + VARIANT[v] + PARAM.format(s=k["s"])

# ================================================================== Seedance groups
IMG = {
 "三视图": "MAT-035 角色卡.PNG（三视图定妆照：现在的她的全身外观）",
 "面部": "面部定妆.jpg（随包：脸的结构和质感，以此为准）",
 "状态卡": "状态卡_彩色.jpg（随包：嘴的三种合法状态）",
 "吉他卡": "MAT-034 新吉他卡.PNG",
 "打印机": "MAT-032 打印机通知（沿用）", "窗暗": "MAT-028 住宅楼夜景·窗暗（沿用）", "窗亮": "MAT-029 住宅楼夜景·窗亮（沿用）",
}
for k in KF: IMG[k["id"]] = f"{k['id']} {k['title']}（MJ 新图）"
ROLE = {"三视图": "现在的 ALPHA 的全身外观（三视图定妆照）", "面部": "她的脸：结构、零件和质感以这张为准",
        "状态卡": "她嘴部的三种合法状态（闭合、小开、最大张开）", "吉他卡": "她的黄色机械电吉他"}

FILM = ("院线电影级画面，像真实拍摄：大画幅数字电影机质感，球面电影镜头，16:9。光线全部有来源（顶灯、追光、窗、路灯、霓虹、屏幕），"
        "体积光和薄烟，深而干净的黑位，高光有柔和的光晕，细腻的 35mm 胶片颗粒。细节丰富：金属的划痕、指纹、灰尘、螺丝、接缝、线缆、"
        "冷凝水、雨珠、布料纹理都清楚可见。镜头运动克制，有轻微手持呼吸感，焦点在人物之间缓慢转移。")
GRADE = {
 "现在": "调色：演播室的冷青色暗部和暖黄色高光，饱和度克制。",
 "回忆": "调色：回忆的暖琥珀色，柔和的高光，略低对比，像旧胶片。",
 "低谷": "调色：低谷期的冷蓝灰，夹杂钠灯橙和霓虹红，脏、潮湿。",
 "蜕变": "调色：车间是冷白工作灯和钠灯橙；发布会是刺眼的白光和闪光灯，过饱和、过亮，像一场促销。",
 "之后": "调色：冬夜冷蓝，春天转为柔和的粉绿和暖阳。",
}
CN = ("所有人物都是中国人：中国面孔、发型、衣着和举止；场景是当代中国的地方（电视台演播室、北方小站和绿皮火车、老小区、城中村、"
      "KTV、劳务市场、地下通道）。画面里不出现可读的文字。")
LIFE = ("她是活的，不是被摆放的装置：每个镜头里她都在注意某个人或某件事。注意力先到眼睛（光圈对焦、眼睑抬起），再到头，最后到肩和手；"
        "她会停顿、犹豫、回应别人。不动的时候也在“呼吸”：胸前散热缝轻轻开合，耳侧涡轮慢慢转，光圈微微收放。动作流畅、有重量，"
        "像一个很大的人在小心地动，不是一格一格的抽动，也不是僵直的展示品。身边的人也把她当成一个表演者：看她、等她回应、和她配合。")
NOW = ("现在的 ALPHA 以 @{三视图} 的全身和 @{面部} 的脸为准：青黄银三色机械外壳、黄色头盔和翼片、蓝紫色发光镜头眼、耳侧涡轮。"
       "她是一台真实的大型演出机器人，高 3.5 米。她不迈步走路：移动靠脚跟里的轮子（三视图侧面和背面能看到），像滑行；"
       "背后连着一根粗供电线缆，由场务理线。腰可以左右转、上身可以前倾，头、手臂、手指、下颌、眼睑、眉条、光圈、耳侧涡轮都能动。")
SCALE = ("比例：成年人站在她身旁，头顶只到她的腰；灯光师站在 2 米高的铝梯顶上才和她的肩膀一样高；她的头和成年人的肩一样宽；"
         "她怀里的黄色电吉他比一个成年人还长。画面里只要有人，就保持这个比例。")
PAST = ("回忆里的 ALPHA 是她的初代机体，和成年人一样高（约 1.7 米），能走路；没有上漆的银白色金属四肢和外露关节；"
        "脸和现在是同一张脸（同样的裂纹面板、青色硬壳嘴唇、蓝紫色镜头眼），只是头盔和饰条是银色，不是黄色。身上没有任何人类皮肤。")
FACE = ("面部{src}：脸是一块块固定的银色金属面板拼成的，接缝像瓷器的裂纹；鼻梁、额中传感板、颊侧格栅、上唇都固定不动。"
        "只有下唇和下巴连成的一整块刚性下颌绕耳下的铰链开合；嘴的形状只有三种：闭合、小开（正常唱歌的上限）、最大张开（只在最高音）。"
        "嘴里是深色的机械腔，上沿是一排灰色金属支架，下面是连杆，没有牙齿和舌头，嘴唇不变软、不噘、不变圆。表情来自零件：青色眉条内侧或整条抬起、"
        "叠层眼睑快门片一层层落下或收起（眨眼也是这样）、镜头眼光圈收放、嘴角小板微微上扬或下压、耳侧涡轮快慢。")
SING = ("唱歌：@音频1 从视频第 0 帧原位对应，包括开头的静音，保持原来的语速和停顿，不加前导静音，不新增台词或配乐。第一个字出声前嘴闭合；"
        "每个字下颌转开一次、字尾回落，换气时合上，只有拖长的尾音可以停在小开；起步快、到位稳、轻微回弹。只有她的脸在画面里时才需要对口型，"
        "其他镜头里歌声照常继续。生成声音开启。")
DISG = "小鹿、阿凯、默默看上去就是普通的中国年轻人：没有任何金属、线路或机械结构，影子和倒影正常。阿凯穿黑色皮夹克、戴露指皮手套；小鹿穿牛仔外套；默默戴黑框眼镜。"
NO = ("不要：牙齿、舌头、圆口、噘嘴、软嘴唇、面板弯曲裂开、零件消失；比例错误；现在的 ALPHA 迈步走路；她像被搬运的货物一样僵着不动；"
      "人类皮肤长在机器人身上；外国人面孔；卡通、玩具、3D 渲染感、塑料感；字幕和文字；慢动作；转场特效。")
FEEL = {
 "A": "情绪是思念和克制：眼睑快门片半垂，目光低落；头慢慢转开，像目送远去的列车；光圈收小，蓝光变暗一点。",
 "B": "情绪是怀念和寻找：青色眉条内侧上抬；头偏向一侧，目光在人群里找一个人；光圈随乐句收放。",
 "C": "情绪是温暖和释然：头抬起；眼睑快门片收起，光圈张开，蓝光变亮；嘴角小板微微上扬，像一个机械的微笑；唱高音时整条眉条上抬，耳侧涡轮转快。",
}

G = []
def group(**k): G.append(k); return k

group(id="G00", title="冷开场·开机前", era="现在", model="2.0", dur=15,
      refs=["三视图", "面部", "KF00-1", "KF00-2", "KF00-3"],
      shots=[(0, 4, "@{KF00-1} 全景平视：她自己靠脚跟的轮子缓缓滑进演播室中央，眼睛亮着；场务主管倒退着走在她前面打手势引导，她的目光跟着他的手；两个场务小跑着在旁边理她背后的线缆，抬头看她。主管握拳示意停，她停稳，向他轻轻点了一下头。"),
             (4, 7, "@{KF00-2} 中景：老杨站在 2 米铝梯顶上拧灯，正好和她的肩膀一样高；灯一亮，她眯起眼睑、抬手挡了一下光；老杨看见了，笑着把灯调暗一档，冲她竖起大拇指，她点头。"),
             (7, 10, "@{KF00-3} 中近景：年轻的录音助理踩着小梯子给她贴领夹麦，手有点抖；她低头看着他的手，慢慢把肩膀压低一点方便他够到；他贴好，拍了拍她的外壳，咧嘴一笑。"),
             (10, 13, "从她肩后俯拍：监视器后面，主持人林姐抬头看她，温和地问了一句话；她把目光从录音助理移到林姐身上，眼睑快门片收起，认真地听；导播摘下耳机，抬手示意全场安静。"),
             (13, 15, "全景：她把黄色电吉他抱进怀里，轻声说了一句话；脚边的工作人员一个个放下手里的活，在地上坐下，抬头看她。")],
      dlg=["ALPHA：谢谢。", "林姐：第一个问题……你的悲伤，是真的吗？", "ALPHA：我可以……唱出来吗？"],
      use="成片开头 0:00–0:15，环境声加对白字幕。")
group(id="G01", title="演播室·前奏与开口", era="现在", model="2.5", dur=28, song=(0.00, 27.60), feel="A",
      refs=["三视图", "面部", "状态卡", "吉他卡", "KF01-1", "KF01-2", "KF01-3"],
      shots=[(0, 5, "@{KF01-3} 特写：她的金属手指扫弦弹前奏，琴弦震动；手指停了一下，像在找一个音，又落下去；吉他琴身比旁边坐着的工作人员的肩膀还宽。"),
             (5, 10, "@{KF01-1} 低机位全景：她站在追光里弹前奏，目光扫过脚边坐着的工作人员，在一个举着手机的年轻人身上停了一下；年轻人慢慢放下手机；梯子上的老杨停住了手。"),
             (10, 14.4, "近景：她低下头，眼睑快门片落下三分之一，青色眉条内侧微抬；胸前散热缝随前奏轻轻开合，像在吸一口气。"),
             (14.4, 21, "@{KF01-2} 四分之三侧特写：她唱第一句；目光慢慢移向远处，像在看一列开走的火车；光圈缓缓收小。"),
             (21, 24.5, "低角度中近景：她唱第二句，头抬起来，眼睑快门片一层层收起，耳侧涡轮开始转动。"),
             (24.5, 28, "反应：梯子上的老杨慢慢摘下一只手套；监视器后的林姐放下手卡，摘下一边耳返；导播靠回椅背，一动不动。")],
      use="歌曲 0–27.6 秒：前奏和第 1–2 句。")
group(id="G02", title="回忆·诞生", era="回忆", model="2.5", dur=30,
      refs=["面部", "KF02-1", "KF02-2", "KF02-3"],
      shots=[(0, 6, "@{KF02-1} 旧实验室，深夜台灯：她的眼睛第一次亮起，光圈来回对焦，最后停在老周脸上；老周推了推眼镜，愣住，然后笑了，眼角挤出皱纹。她歪了一下头，学他的样子。"),
             (6, 11, "@{KF02-2} 特写：老周粗糙的手覆在她的银色机械手指上，帮她按住木吉他的弦；他拇指上贴着创可贴；她的手指先很僵，第三次终于按对了，她抬眼看他。"),
             (11, 16, "中景：桌上的旧录音机转着磁带，老周闭着眼跟着哼，用脚打拍子，跑了调；她看着他的脚，也用手指在桌上敲起拍子。"),
             (16, 21, "@{KF02-3} 商场中庭的小演出：她抱着木吉他唱完，几个路人稀稀拉拉地鼓掌；一个小女孩跑过来碰了碰她的金属手指，她把手掌慢慢翻过来递给小女孩；母亲立刻把孩子拉走，皱着眉没看她。"),
             (21, 25, "人群外，一个背琴包的年轻乐手握着刚挂断的手机，看了她一眼，叹口气，转身走进人流。"),
             (25, 30, "她独自站在原地，看着被碰过的手指，慢慢把手握起来；台下的老周朝她用力鼓掌，她看见了他。")],
      dlg=["老周：会唱歌，就有人愿意听你说话了。", "母亲：别碰，那是个东西。"],
      use="A1 尾到 B1（第 3–7 句）的回忆。")
group(id="G03", title="回忆·被否定", era="回忆", model="2.0", dur=15,
      refs=["面部", "KF03-1", "KF03-2"],
      shots=[(0, 5, "黑暗的演出场地：一排排手机屏幕举起，人群在拍她、笑她，有人吹口哨；远处小舞台上的她很小，她停下来，看着那些手机。"),
             (5, 10, "@{KF03-1} 听证大厅俯拍：大屏幕上的投票一格一格变红，一位专家站起来指着她说话，旁边的人纷纷点头；她站在大厅中央，抬头，在一排排人里找一张愿意看她的脸。"),
             (10, 15, "@{KF03-2} 地铁通道：巨大的 AI 音乐广告亮着，广告下的真人乐手弹唱，人流从他身边匆匆走过；他弹错一个和弦，停下来，低头看着自己的手。")],
      dlg=["专家：它没有生命。它的悲伤，只是一段被训练出来的程序。"],
      use="C1 段的回忆，快剪。")
group(id="G04", title="演播室·真心的人", era="现在", model="2.5", dur=27, song=(60.70, 87.00), feel="B",
      refs=["三视图", "面部", "状态卡", "吉他卡", "KF04-1", "KF04-2", "KF01-2"],
      shots=[(0, 6, "@{KF01-2} 近景：她唱这一句，目光在台下慢慢移动，像在人群里找一个人；青色眉条内侧上抬，光圈收放。"),
             (6, 11, "@{KF04-1} 全景，从观众席后方拍：一排排观众的后脑勺，有人捂住嘴，有人悄悄擦眼睛；舞台上的她比所有人高出一大截。"),
             (11, 17, "低角度：她唱这一句，眼睑快门片半垂，上身微微前倾，靠近台下第一排；左手换和弦。"),
             (17, 21, "@{KF04-2} 林姐近景：她眼眶发红，一滴泪落在手卡上，墨迹晕开；身旁的导播默默递过一张纸巾。"),
             (21, 27, "特写：她唱这一句，看见了林姐的眼泪，眼睑快门片收起，光圈张开，嘴角小板微微上扬，像一个机械的微笑。")],
      use="歌曲 60.7–87 秒（第 8–11 句），和 G03、G05 交叉剪。")
group(id="G05", title="回忆·照顾与报废", era="回忆", model="2.5", dur=30,
      refs=["面部", "KF05-1", "KF05-2", "打印机", "KF05-3"],
      shots=[(0, 4, "@{KF05-1} 厨房：老周打开冰箱，钥匙放在里面；他拿着钥匙愣住，挠了挠头，想不起来为什么。"),
             (4, 7, "特写：老人的手背上用圆珠笔写着几行字，字迹被汗晕开。"),
             (7, 13, "@{KF05-2} 实验室：老周把一颗黄色糖纸的润喉糖放进她的金属手心，她慢慢握住，低头看了很久；老周拍拍她的手背。"),
             (13, 17, "@{打印机}：打印机吐出一张带红章的通知，一只穿西装的手把它抽走。"),
             (17, 23, "@{KF05-3}：空旷的旧仓库，篷布下透出的蓝光一点点暗下去，熄灭；叉车司机从旁边经过，没有停。"),
             (23, 30, "手电光照进仓库，老周气喘吁吁地掀开篷布，她的眼睛闪了两下，亮了，第一眼就找到他；老人一屁股坐在地上，松了一口气，她伸手扶住他的肩。")],
      dlg=["ALPHA：他们为什么怕我？", "老周：不是怕你。是怕自己被落下。"],
      use="C1 段尾和间奏。")
group(id="G06", title="回忆·告别", era="回忆", model="2.5", dur=30,
      refs=["面部", "KF06-1", "KF06-2"],
      shots=[(0, 6, "雨中的铁轨边：老周拖着行李箱，她背着木吉他走在他身边，替他挡着雨；两人并排走向小站，路过的扳道工抬头看了他们一眼。"),
             (6, 9, "雨水顺着车站告示往下流，老人的手握紧行李箱拉杆，指节发白。"),
             (9, 16, "@{KF06-1} 站台：老周给她穿上新买的黑色长羽绒服，拉好领口，把自己的灰围巾绕在她脖子上，说了一句话；她低头看着围巾，又抬头看他；身后的列车员吹响哨子，挥手催人上车。"),
             (16, 22, "绿皮火车开动，车窗里的老周贴着玻璃，越来越小；她跟着车走了几步，抬起一只手；站台上的乘客散去，只剩下她。"),
             (22, 26, "大特写：一滴雨顺着她脸上的金属接缝滑下，眼睑快门片慢慢落下一层。"),
             (26, 30, "@{KF06-2} 空站台，固定机位：她一动不动地站着，看着铁轨的尽头；天色从白天变成黄昏，站灯一盏盏亮起。")],
      dlg=["老周：天冷，穿上。", "老周：去唱吧。别在仓库里等我。"],
      use="间奏到 A2。")
group(id="G07", title="站台·第一次弹唱", era="回忆", model="2.0", dur=14, song=(137.40, 150.85), feel="A",
      refs=["面部", "状态卡", "KF07-1", "KF06-2"],
      shots=[(0, 6, "@{KF07-1} 远景：雨后的空站台，她坐在长椅上，第一次抱起木吉他弹唱这首歌；远处一个夜班站务员提着灯停下脚步，回头看她。"),
             (6, 14, "侧脸近景：她低头唱这一句，眼睑快门片半垂，手指在弦上停了一下又继续；雨水从站台棚檐滴下，打在她的肩上，她没有躲。")],
      use="A2 段尾（137.4–151 秒）。")
group(id="G08", title="低谷蒙太奇", era="低谷", model="2.5", dur=30,
      refs=["面部", "KF08-1", "KF08-2", "KF08-3", "KF08-4", "KF08-5", "KF08-6", "KF08-7"],
      shots=[(0, 4, "@{KF08-1}：公厕镜前，她把一顶廉价黑假发往金属头上戴正，对着镜子看了很久；隔间门开了，一个醉醺醺的男人出来，看了她一眼，躲开了。"),
             (4, 7, "雨夜：面馆老板推开门，挥手把在屋檐下躲雨的她赶走，店里的食客隔着玻璃往外看。"),
             (7, 10, "@{KF08-2}：劳务市场，一辆面包车开过来，一群人围上去抢活；她也往前挤了一步，车里的人看了她一眼，摇上车窗，开走了。"),
             (10, 14, "@{KF08-3}：拆解厂，她用金属手指轻轻合上一个同型号机器人头的眼睛；对面戴眼镜的默默抬头看她，手里的螺丝刀停住。"),
             (14, 17, "@{KF08-4}：闪电劈下，她背对镜头走向输电塔，雨水砸在羽绒服上。"),
             (17, 21, "@{KF08-5}：冷库，工人们呼着白气搬箱子、跺脚取暖；她搬着箱子走过，只有她和默默不呼白气，两人对视了一眼。"),
             (21, 25, "@{KF08-6}：小巷黑市，电贩子舔着手指数钱；她靠墙，颈后接着线，眼睛慢慢亮起。"),
             (25, 30, "@{KF08-7}：红灯房间，她蹲着，把自己掉下来的外壳碎片抱在怀里，挤出一个苦涩的机械笑容——嘴角小板微微上扬又落下。")],
      use="B2 段快剪，每个镜头只用 1.5–2 秒。")
group(id="G09", title="夜场·卖唱·摩托", era="低谷", model="2.5", dur=18, song=(164.00, 177.45), feel="B",
      refs=["面部", "状态卡", "KF09-1", "KF09-2"],
      shots=[(0, 6, "@{KF09-1}：KTV 包间中央，她拿着麦克风唱，沙发上的人在划拳、喝酒，没人听；她的目光扫过一张张脸，停在墙边穿黑夹克的阿凯身上——只有他在看她。"),
             (6, 9, "一个醉汉站起来拽住她的手腕，她还在唱；一只戴露指皮手套的手伸进来，捏住醉汉的手腕，醉汉疼得松手（阿凯）。"),
             (9, 13.5, "后台帘幕边，她侧脸对着麦克风继续唱，眉条内侧上抬；帘子外有人影走过。"),
             (13.5, 18, "@{KF09-2} 雨夜，阿凯骑着一辆旧摩托，她披着羽绒服坐在后座；红灯前他回头看了她一眼，她犹豫了一下，把手搭在他的肩上。")],
      use="B2 段（164–177 秒）。")
group(id="G10", title="地下通道·同类", era="低谷", model="2.5", dur=20, song=(177.35, 184.15), feel="B",
      refs=["面部", "状态卡", "KF10-1", "KF10-2", "KF10-3"],
      shots=[(0, 7, "@{KF10-1}：地下通道，她靠墙坐着弹唱木吉他（戴假发、羽绒服）；过路的人匆匆走过，一个外卖员停下来听了两秒，她朝他微微点头。"),
             (7, 9, "音乐断了：保安弯腰拔掉她音箱的插头，指着出口；她停住，眼睛的光暗下去。"),
             (9, 13, "@{KF10-2}：走廊里，小鹿蹲下，把从袖口里拉出的一根细线接到她身上，她的眼睛一点点亮起来，先看到的是小鹿的笑；小鹿的皮肤完好。"),
             (13, 20, "@{KF10-3}：出租屋里，小鹿、阿凯、默默站在她身后；她犹豫了一下，抬手摘下假发，放在桌上，露出完整的金属头。阿凯把手插回兜里，默默推了推眼镜，小鹿轻轻点头。")],
      dlg=["小鹿：我们也是。"],
      use="C2 开头。音频只有第 21 句，后面是静音：拔掉插头以后她不再唱。")
group(id="G11", title="雨夜天台", era="低谷", model="2.5", dur=20, song=(184.00, 204.00), feel="C",
      refs=["面部", "状态卡", "KF11-1", "KF11-2", "窗暗", "窗亮"],
      shots=[(0, 7, "@{KF11-1}：雨夜天台，她不戴假发，抱着木吉他弹唱；阿凯在旁边仰头跟着大声吼唱，她转头看他，跟着他的节奏加重了扫弦；小鹿用手机打着光，默默撑着一把伞挡在音箱上。"),
             (7, 13, "@{KF11-2}：她仰头唱，雨水顺着金属脸流下，光圈张开，嘴角小板微微上扬；耳侧涡轮转动，甩出水珠。"),
             (13, 16, "近景：阿凯闭着眼跟着吼，用拳头打着拍子；小鹿笑着抹了一下脸上的雨。"),
             (16, 20, "对面的住宅楼：从 @{窗暗} 的样子开始，一扇扇窗户陆续亮起来，有人拉开窗帘探出头，有人举起手机，结束时像 @{窗亮}。")],
      use="C2 段（184–204 秒）。")
group(id="G11B", title="蜕变·更大的她", era="蜕变", model="2.5", dur=30,
      refs=["三视图", "面部", "KF11B-1", "KF11B-2", "KF11B-3", "KF11B-4", "KF11B-5"],
      shots=[(0, 5, "@{KF11B-1} 深夜的改装车间：一台 3.5 米高的青黄银新机体用铁链吊在半空，像一件待售的商品；墙上的大屏在循环播放她在雨夜天台唱歌的画面；穿西装的市场经理指着新机体，对同事比划“再大一点”，同事们点头、拍照。"),
             (5, 10, "@{KF11B-2} 工作台上，初代银白机身躺着，胸口打开；技术员双手捧出一颗发蓝光的小核心；她的头还连着线，眼睛一直跟着那颗核心移动，光圈收小——她知道发生了什么。"),
             (10, 15, "核心被推进巨大机体的胸腔，舱门合上；巨大的头部里，眼睛从暗到亮，光圈一层层张开；她低头看着自己巨大的手，一根一根地弯曲手指，又停住，像不认识它们。"),
             (15, 20, "@{KF11B-3} 角落里，初代机身被盖上篷布；一个工人从旧机身的手心里抠出一张黄色糖纸，随手丢进垃圾桶；巨大的她弯下腰，用两根手指从垃圾桶里捏起那张糖纸，工人们愣住，仰头看她。"),
             (20, 25, "@{KF11B-4} 发布会：舞台下挤满举着手机的人群，欢呼、尖叫、闪光灯；人群里有那个拔掉她插头的保安、那个赶她走的面馆老板、那个说她没有生命的专家，他们都在拍照、鼓掌、背对她自拍。她唱的还是同一首歌。"),
             (25, 30, "@{KF11B-5} 她的视角，从 3.5 米高往下看：一片手机屏幕的海；人群最后面，小鹿、阿凯、默默没有举手机，只是站着看她。她找到了他们，停住，轻轻点了一下头。")],
      dlg=["市场经理：观众不在乎她唱什么。观众要新的。"],
      use="尾段（204–217 秒），和 G12 交叉剪。新增组：从小到大的蜕变。")
group(id="G12", title="演播室·最高音到最后", era="现在", model="2.5", dur=27, song=(197.40, 224.15), feel="C",
      refs=["三视图", "面部", "状态卡", "吉他卡", "KF12-1", "KF12-2", "KF01-2"],
      shots=[(0, 7, "@{KF12-1} 低角度广角仰拍：她仰头唱出最高音，下颌停在最大张开；背后梯子上是老杨的剪影和顶光，她显得非常高大；眉条整条上抬，耳侧涡轮转得很快。"),
             (7, 14, "@{KF01-2} 近景：她唱这一句，情绪转为温柔的告别：头慢慢低下来，手越弹越慢，眼睑快门片缓缓落下一层。"),
             (14, 18, "@{KF12-2} 侧台暗处：阿凯站在最前，小鹿和默默在后；阿凯慢慢摘下一只皮手套，小鹿把手搭在他的肩上。她的目光越过台下，找到了侧台的他们。"),
             (18, 23, "近景：她唱这一句，光圈慢慢张开，嘴角小板微微上扬。"),
             (23, 27, "手部特写：她不再扫弦，两根金属手指在琴身上轻轻敲拍子——和老周在病房扶手上敲拍子的节奏一样。")],
      use="歌曲 197.4–224 秒（第 24–27 句），和 G11、G11B、G13 交叉剪。")
group(id="G13", title="之后·冬与春", era="之后", model="2.5", dur=25,
      refs=["三视图", "面部", "KF13-1", "KF13-2"],
      shots=[(0, 7, "@{KF13-1} 冬夜，养老院的房间：女儿蹲在扶手椅旁，替老周擦了擦眼镜，再把手机递给他，屏幕上是 ALPHA 唱歌的视频；老人茫然地摇头，眼睛却一直看着屏幕。"),
             (7, 12, "特写：老人搭在扶手上的食指和中指，跟着节拍轻轻敲；女儿看见了，捂住了嘴。"),
             (12, 19, "@{KF13-2} 春天的小站：一节平板货车车厢缓缓停靠，她站在车厢上（3.5 米高），身边用绑带固定着装木吉他的旧琴盒；站台上的工人仰头看她，小鹿、阿凯、默默从车厢上跳下来，帮着解开绑带。"),
             (19, 25, "她抬头看站台，在等车的人里一个一个地找；风吹落一阵花瓣，落在她的肩甲上；她的光圈慢慢张开。")],
      dlg=["女儿：爸，你还记得她吗？"],
      use="尾段（217–231 秒）。")
group(id="G14", title="演播室·掌声与回答", era="现在", model="2.0", dur=15,
      refs=["三视图", "面部", "KF14-1", "KF14-2"],
      shots=[(0, 5, "@{KF14-1}：最后一个和弦结束，棚里安静了两秒；梯子上的老杨第一个鼓掌，工作人员一个个站起来，有人吹了声口哨，导播也站了起来。她看着他们，不知道该怎么办，慢慢把吉他放低。"),
             (5, 9, "全景：她向工作人员鞠了一躬，上身前倾、头低下；脚边的人仰头看她，只到她的腰。"),
             (9, 15, "@{KF14-2} 中景：林姐走到她脚边，仰头轻声问了一句话；ALPHA 弯下上身凑近她，停了很久，慢慢回答，眼睑快门片落下一半。")],
      dlg=["林姐：所以……你的悲伤，是真的吗？", "ALPHA：我不知道它算不算真的。他走的那天，我在站台站了七个小时。"],
      use="尾奏后的结尾访谈。")
group(id="G15", title="春天·长椅", era="之后", model="2.0", dur=15,
      refs=["三视图", "面部", "KF15-1"],
      shots=[(0, 7, "@{KF15-1} 春天的站台：老周坐在长椅上，她在长椅旁单膝跪下，上身向他俯过来，头仍然比他高；老人仰头，像对陌生人一样问她的名字，她回答。"),
             (7, 15, "老人想了想，笑了，拍拍长椅的扶手；她把两根手指轻轻放在扶手上，跟着他一起敲起拍子；远处一列绿皮火车开过，花瓣被风卷起，两人一起看着火车。")],
      dlg=["老周：你唱得真好。你叫什么名字？", "ALPHA：ALPHA。", "老周：阿尔法……好名字。像是第一个。"],
      use="结尾最后一场。")

for g in G:
    assert (g["model"] == "2.0" and g["dur"] <= 15) or (g["model"] == "2.5" and g["dur"] <= 30), g["id"]
    assert g["shots"][0][0] == 0 and abs(g["shots"][-1][1] - g["dur"]) < 1e-6, g["id"]
    for a, b in zip(g["shots"], g["shots"][1:]): assert abs(a[1] - b[0]) < 1e-6, g["id"]
    for r in g["refs"]: assert r in IMG, (g["id"], r)

def lyr(g):
    a0, cut = g["song"]
    return [(i, max(0, a - a0), min(b, cut) - a0, t) for i, a, b, t in LINES if b > a0 + 0.3 and a < cut - 0.3]

def at(g, s):
    for k in sorted(g["refs"], key=len, reverse=True):
        s = s.replace("@{" + k + "}", f"@图片{g['refs'].index(k) + 1}")
    return s

def prompt(g):
    p = []
    refs = "；".join(f"@图片{i + 1} 是{ROLE[k] if k in ROLE else '「' + IMG[k].split(' ', 1)[-1].split('（')[0] + '」的构图、人物和光影参考'}"
                    for i, k in enumerate(g["refs"]))
    p.append("参考：" + refs + "。" + ("@音频1 是她的歌声。" if "song" in g else ""))
    p.append(FILM + GRADE[g["era"]])
    p.append(CN)
    if g["era"] in ("现在", "蜕变") or g["id"] in ("G13", "G15"): p.append(NOW + SCALE)
    if g["era"] in ("回忆", "低谷", "蜕变"): p.append(PAST)
    p.append(LIFE)
    src = "、".join(t for k, t in (("面部", "@{面部} 的脸"), ("状态卡", "@{状态卡} 的嘴部状态")) if k in g["refs"])
    p.append(FACE.format(src=f"（以 {src} 为准）" if src else ""))
    if g["era"] in ("低谷", "蜕变") or g["id"] in ("G12", "G13"): p.append(DISG)
    if g.get("feel"): p.append("演唱时的表情：" + FEEL[g["feel"]] + "动作是机器的，感情是真的，深情而克制。")
    p.append(f"一共 {len(g['shots'])} 个镜头，按时间硬切：")
    for i, (a, b, s) in enumerate(g["shots"]): p.append(f"镜头{i + 1}（{a:.1f}–{b:.1f} 秒）：{s}")
    if "song" in g:
        p.append("演唱时间：" + "；".join(f"{a:.1f}–{b:.1f} 秒唱「{t}」" for _, a, b, t in lyr(g)) + "。")
        tail = g["song"][1] - g["song"][0]
        if g["dur"] - tail > 1.0: p.append(f"{tail:.1f} 秒以后音频是静音，她不再唱，嘴闭合。")
        p.append(SING)
    else:
        p.append("这一组没有歌声：人物说话只做口型动作，对白后期加字幕；只要现场环境声，不要音乐和人声。生成声音关闭。" if g.get("dlg") else
                 "这一组没有歌声：只要现场环境声（风、雨、火车、机器、人群），不要音乐和人声。生成声音关闭。")
    if g.get("dlg"): p.append("对白（只出字幕）：" + "／".join(g["dlg"]))
    p.append(NO)
    return at(g, "\n".join(p))

# ================================================================== write
L = []; w = L.append
w("# 03　MJ 关键帧提示词（v11，16:9）\n")
w(f"> 共 {len(KF)} 张关键帧：必出 {sum(k['prio'] == P1 for k in KF)}，建议重出 {sum(k['prio'] == P2 for k in KF)}，"
  f"可沿用旧图 {sum(k['prio'] == P3 for k in KF)}（旧图能用就不用重出；想统一中国人物和质感再出）。")
w("> 每张给 3 条：**A 标准**、**B 艺术**（剪影、留白、逆光）、**C 纪实**（手持、抓拍）。每条出 4 张，一张关键帧就有 12 张候选。")
w("> 选中的图请按编号命名，例如 `KF00-1.png`。视频提示词（04）就按这个编号引用。")
w("> 参数沿用你原来的写法：`--ar 16:9 --v 8.1 --style raw`。如果你的 MJ 版本支持全能参考（Omni Reference，`--oref` / `--ow`），"
  "现在的她加 `--oref 全身正面_MJ用.jpg --ow 100`，回忆里的她加 `--oref 面部定妆.jpg --ow 60`；不支持就只用文字。\n")
w("**3.5 米的比例，尽量在出图时就做对，不要靠后期改：**")
w("1. 先在 A/B/C 的 12 张里挑**人和她的比例已经对的**：人头顶只到她的腰。")
w("2. 只差一点的，用 MJ 的局部重绘（Vary Region）只框住**人**，改写成 `a small Chinese crew member who only reaches her waist`，不要去重绘她。")
w("3. 画面里放不下全身的，用 Zoom Out 往外扩，让比例尺（人、梯子、门）进到画面里。")
w("4. 仍然不行的再交给修图，而且只缩人，不放大她，这样她的脸和细节不会被破坏。\n")
cur = None
for k in KF:
    if k["group"] != cur:
        cur = k["group"]; w(f"\n## {cur}　{next(g['title'] for g in G if g['id'] == cur)}")
    w(f"\n### {k['id']}　{k['title']}　【{k['prio']}】　替换：{k['old']}")
    for v, name in (("A", "A 标准"), ("B", "B 艺术"), ("C", "C 纪实")):
        w(f"{name}\n```\n{mj(k, v)}\n```")
open(os.path.join(HERE, "03_MJ关键帧提示词.md"), "w").write("\n".join(L))

with open(os.path.join(HERE, "06_关键帧清单.csv"), "w", newline="", encoding="utf-8-sig") as f:
    wr = csv.writer(f); wr.writerow(["编号", "组", "内容", "优先级", "替换旧图", "用在"])
    for k in KF:
        wr.writerow([k["id"], k["group"], k["title"], k["prio"], k["old"], "、".join(g["id"] for g in G if k["id"] in g["refs"])])

total = sum(g["dur"] for g in G)
L = []; w = L.append
w("# 04　Seedance 分组提示词（v11）\n")
w(f"> {len(G)} 组，共 {total} 秒素材；16:9；Seedance 2.0 每组不超过 15 秒，2.5 每组不超过 30 秒。")
w("> 上传顺序就是 @图片 的编号。KF 开头的图是 03 里的 MJ 新图，按编号命名后上传。")
w("> 演唱组的 @音频1 就是你已经处理好的 `口型_Gxx.mp3`：文件名、起点和长度都没变，直接用。\n")
w("| 组 | 内容 | 时期 | 模型 | 时长 | 口型音频 |\n|---|---|---|---|---|---|")
for g in G: w(f"| {g['id']} | {g['title']} | {g['era']} | {g['model']} | {g['dur']} 秒 | {'口型_' + g['id'] + '.mp3' if 'song' in g else '—'} |")
w("")
for g in G:
    w(f"## {g['id']}　{g['title']}")
    w(f"**Seedance {g['model']} · {g['dur']} 秒 · 16:9 · 生成声音{'开启' if 'song' in g else '关闭'}**　　{g['use']}\n")
    w("**上传**")
    for i, k in enumerate(g["refs"]): w(f"- @图片{i + 1}：{IMG[k]}")
    if "song" in g: w(f"- @音频1：`口型_{g['id']}.mp3`（{g['dur']} 秒）")
    w("\n**提示词**\n```\n" + prompt(g) + "\n```\n")
open(os.path.join(HERE, "04_分组提示词.md"), "w").write("\n".join(L))
with open(os.path.join(HERE, "05_分组清单.csv"), "w", newline="", encoding="utf-8-sig") as f:
    wr = csv.writer(f); wr.writerow(["group", "title", "era", "model", "duration_s", "song_in", "song_out", "audio", "refs", "prompt"])
    for g in G:
        wr.writerow([g["id"], g["title"], g["era"], "Seedance " + g["model"], g["dur"], *(("%.2f" % g["song"][0], "%.2f" % g["song"][1]) if "song" in g else ("", "")),
                     f"口型_{g['id']}.mp3" if "song" in g else "", "；".join(IMG[k] for k in g["refs"]), prompt(g)])

used = {r for g in G for r in g["refs"]}
unused = [k["id"] for k in KF if k["id"] not in used]
left = [m for g in G for m in re.findall(r"@\{[^}]+\}", prompt(g))]
print(len(G), "groups,", total, "s;", len(KF), "keyframes; unused:", unused, "; max prompt", max(len(prompt(g)) for g in G), "chars")
assert not left, left
