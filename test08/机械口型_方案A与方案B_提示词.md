# 机械口型：方案 A（白模＋文字）和方案 B（程序图）

> 两个方案都**不传视频参考**。我写的“图片模型”指你说的 Imagen 2.5（im2.5）；“视频模型”指 Seedance 2.5（8 秒测试也可以用 2.0）。
> 测试句：“真心的人又能有几个”。音频用你分离出来的机械人声，8 秒，0.5 秒开口。

---

## 方案 A：白模＋文字，先出影视级状态卡，再出视频

### A1 图片模型：口型状态卡（四格）

**上传**
- 图 1：`A_白模结构参考.jpg`（白模的正面、侧面、嘴部特写）— 结构
- 图 2：角色卡.PNG — 配色和外观

**提示词（中文）**
```
以图1的白色机器人头部为结构依据，以图2的角色配色为外观，生成一张横向四格的电影概念设定图：同一个女性机器人 ALPHA 的四分之三侧面头部特写，同一机位、同一光线，只有嘴的开合不同。
第1格嘴闭合；第2格下颌微开一条缝；第3格下颌中开；第4格下颌开到最大（上下唇之间的缝约等于上唇厚度）。
机械结构严格按白模：上唇是固定的多面硬壳，鼻子和颊板固定不动；下唇和下巴连成一体的下颌绕两侧铰链向下、向后转；张开时露出黑色口腔和里面的金色减速电机、红色舵机和细活塞；嘴宽和嘴角不变，嘴唇不变形。
外观：银色拉丝金属面板拼成的脸，面板之间有细缝和倒角，青色车漆嘴唇，蓝紫色发光镜头眼，头部黄色车漆头盔和翼片，耳侧涡轮。
风格：《变形金刚》电影级硬表面机械设计，工业光魔式写实 CG，像实拍：真实金属反射、细微划痕和磨损、电影布光（暖色顶光、冷色轮廓光）、黑色背景、浅景深、35mm 胶片颗粒。
不要：牙齿、舌头、人类皮肤、柔软的嘴唇、卡通、玩具感、文字。
```

**Prompt (EN)**
```
Using image 1 (white robot head model) as the exact mechanical structure and image 2 as the colour scheme, create a horizontal four-panel film concept sheet: the same female robot ALPHA, three-quarter close-up of the head, identical camera and lighting in every panel, only the jaw position changes. Panel 1 mouth closed; panel 2 jaw slightly parted; panel 3 jaw half open; panel 4 jaw fully open (gap between the lips about the thickness of the upper lip).
Mechanics follow the white model exactly: the upper lip is a fixed faceted hard shell, nose and cheek plates do not move; the lower lip and chin form one jaw that rotates down and back around side hinges; when open it reveals a dark mouth cavity with small brass gear motors, red servos and thin pistons; mouth width and corners never change, the lips never deform.
Look: face made of brushed silver metal plates with fine seams and bevels, teal painted lips, glowing blue-violet camera-lens eyes, yellow painted helmet with fins, turbine ears.
Style: Transformers movie-grade hard-surface design, ILM-style photoreal CG that reads like live action: real metal reflections, fine scratches and wear, cinematic lighting (warm top key, cool rim), black background, shallow depth of field, 35mm film grain.
No teeth, no tongue, no human skin, no soft lips, no cartoon, no toy look, no text.
```

### A1b 图片模型：眼睛和表情状态卡（四格）

上传同上。

```
以图1的白色机器人头部为结构依据、图2为配色，生成一张2×2四格的电影设定图：同一个女性机器人 ALPHA 的眼部特写（含眉毛），同机位同光线，只有表情不同。
左上：平静，虹膜光圈正常打开；右上：深情，链条眉毛内侧上抬，上眼睑的叠层金属快门片落下一半，光圈收小；左下：唱高音，眉毛整条上扬，眼睛睁大，光圈张开；右下：唱完，眼睑快门片缓缓合下大半，光圈重新张开。
眼睛是玻璃镜头：里面是发蓝紫光的虹膜和8片金属光圈叶片，外圈有镜头环；上眼睑3层、下眼睑2层弧形金属快门片；眉毛是一节一节的链条金属条。
《变形金刚》电影级硬表面机械设计，写实 CG，真实金属反射，电影布光，黑色背景，35mm 胶片颗粒。不要人类皮肤、卡通、文字。
```

### A2 视频模型：用状态卡出视频

**上传**
- @图片1：角色卡.PNG — 外观
- @图片2：`A_白模结构参考.jpg` — 结构
- @图片3：A1 生成的口型状态卡
- @图片4：A1b 生成的眼睛状态卡
- @图片5：K18 NEW — 只当光影参考
- @音频1：机械人声，8 秒

**提示词**
```
人物外观参考 @图片1；面部机械结构参考 @图片2；@图片3 是她嘴部从闭合到最大张开的四个状态，@图片4 是她眼睛和眉毛的四种表情状态：唱歌时只在这些状态之间连续过渡，不要出现图里没有的嘴型。@图片5 只作为光影和胶片质感参考。@音频1 是她的演唱，口型与它同步；视频不要生成声音。

《变形金刚》电影级的机械面部表演，像实拍：她的脸由许多块独立的银色金属面板组成。唱歌时，只有下唇和下巴连成的下颌绕两侧铰链向下、向后转开、再合上；上唇、鼻子固定不动；嘴角两侧的小面板和颊板跟着下颌联动，只有一两毫米的轻微位移，面板之间的细缝随之微微开合；口腔里的金色电机和细活塞随下颌运转。下颌像舵机：起步快，到位硬停，有一点回弹。嘴宽和嘴角不变，嘴唇是硬壳，不变形。
逐字：0.5 秒“真”中开，1.0 秒“心”小开，1.4 秒“的”小开，1.75 秒“人”中开，2.4 秒换气合上；2.6 秒“又”中开，3.05 秒“能”中开，3.6 秒短暂合上；3.9 秒“有”中开，4.6 秒短暂合上；4.8 秒“几”小开，5.2 秒“个”开到最大并停住拖长音；6.2 秒合上。
眼睛：前半段是深情状态，链条眉毛内侧上抬，眼睑快门片半落，光圈收小；5.2 秒唱高音时眉毛上扬，眼睛睁开，光圈张开；6.2 秒以后眼睑快门片一层层缓缓合下。头部按小角度一格一格地偏向一侧，耳侧涡轮慢慢旋转。

写实电影镜头：黑色演播室，暖色顶光从左后上方打下，冷色轮廓光，背景只有黑暗、薄烟和虚焦光点；35mm 胶片颗粒；手持摄影机轻微呼吸感晃动；中近景，四分之三侧脸，镜头几乎不推。
不要：牙齿、舌头、横贯整张脸的大嘴、软嘴唇、嘴唇拉伸或嘟嘴、面板裂开错位、人类皮肤、卡通、玩具感、字幕、慢动作、转场。
```

---

## 方案 B：用我渲染的程序图教模型

方案 B 跳过 A1 和 A1b，直接用我在 Blender 里渲染的图。这些图的结构和开合幅度是程序算出来的，**完全准确**；但面部造型比较简化，所以只让模型学“怎么动”，不学“长什么样”。

| 文件 | 内容 |
|---|---|
| `B1_口型四态_四分之三侧.jpg` | 闭合、微开、中开、最大，四分之三侧 |
| `B2_眼睛表情四态.jpg` | 平静、深情、高音、收尾（顺序：左上、右上、左下、右下） |
| `B3_嘴部闭合与张开.jpg` | 嘴部特写：闭合与最大张开，能看到口腔里的电机 |

### B 视频模型

**上传**
- @图片1：角色卡.PNG — 外观
- @图片2：`A_白模结构参考.jpg` — 真实结构
- @图片3：`B1_口型四态_四分之三侧.jpg`
- @图片4：`B3_嘴部闭合与张开.jpg`
- @图片5：`B2_眼睛表情四态.jpg`
- @图片6：K18 NEW — 光影
- @音频1：机械人声

**提示词**
把 A2 提示词开头的第一段换成下面这段，其余不变：
```
人物外观参考 @图片1；真实的面部机械结构参考 @图片2。@图片3、@图片4 是同一结构的三维机构渲染：@图片3 是她嘴部从闭合到最大张开的四个状态，@图片4 是嘴部特写的闭合与张开；@图片5 是她眼睛和眉毛的四种表情状态。这三张只用来理解运动方式和幅度：不要复制它们简化的几何造型和光线，外观以 @图片1 为准。唱歌时只在这些状态之间连续过渡。@图片6 只作为光影和胶片质感参考。@音频1 是她的演唱，口型与它同步；视频不要生成声音。
```

---

## 建议的测试顺序

1. **先跑方案 B。** 不用先出图，最快。
2. **同时让图片模型跑 A1。** 如果出来的状态卡够漂亮，就跑 A2。
3. 两条视频都发我。我对比口型、机械感和画质，定下最终写法，再套到 16 组提示词里。

A1 出的图如果好，还有一个额外的用处：它就是“影视级的 ALPHA 面部定妆照”，以后所有特写都可以拿它当人物参考。
