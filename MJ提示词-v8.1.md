# 《远去的列车》Midjourney V8.1 提示词·全片版（纯文本，不用角色卡）

> 直接复制到 Midjourney，不用上传任何参考图。参数统一为 `--ar 239:100 --v 8.1 --style raw --s 150`。
> 按成片顺序排列。标着 **【已出】** 的 15 条是上一版给的，原样保留；其余是新写的。
> 画面里的中文字（手卡、嘉宾牌、告示、价目单）先不让 MJ 写，后期我统一加。

**统一说明**
- 所有提示词里，ALPHA、老周、林姐、阿凯等人物都用**同一段英文外貌描述**，靠文字保持前后一致。
- 访谈镜头（IV1–IV5）用同一个布景：黑色空棚，两把旧扶手椅，一盏落地灯。五段访谈可以都从 IV1 那张图里挑同一张做视频，再按问答换字幕。
- 有首帧和尾帧的镜头（S24a/b、S32a/b），先出首帧，再用 MJ 的 Vary Region 或 Editor 改出尾帧，保证构图不变。
- 出视频时：画面里没有真人正脸的镜头，可以直接拿 MJ 图做 sd2.5 图生视频；有真人正脸的镜头，用 sd2.5 文生视频（视频提示词见《真人版关键帧提示词.md》）。

---

## 开场：调试（无音乐）

### 1. O1　贴领夹麦
```
extreme close-up, a sound engineer's hands taping a tiny black lavalier microphone onto the mint-teal chest plate of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head with white gaffer tape, the tape peeling off the glossy metal and being pressed down again, she sits perfectly still, a single work light from the side, dark studio background, 85mm, shallow depth of field, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 2. O2　“加点呼吸声”
```
a TV studio audio control desk in a dark corner, a sound engineer with headphones looking at a monitor where a voice waveform is almost a perfectly flat clean line, a producer with a headset leaning over his shoulder pointing at the screen, a small video monitor beside them showing the face of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, glow of the screens on their faces, cluttered cables, 40mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 3. O3　白卡调白平衡
```
close-up, a camera assistant holding a white balance card right next to the brushed-silver robotic face of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, her blue ring eyes looking straight ahead, a cinema camera lens in the blurred foreground, the camera monitor in the corner showing her face, harsh reflections on her metal face, single soft key light, black background, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 4. O4　擦一擦外壳
```
a young Chinese makeup artist standing in front of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head holding a makeup brush in mid-air, hesitating, an open makeup case beside her, then wiping the robot's metal shell with a lens cloth instead, awkward and quiet, one practical lamp, dark interview studio, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 5. P1c　嘉宾牌上的“设备”　**【已出】**
```
a lonely female humanoid robot sitting on a tall stool in the center of an empty TV talk show studio before recording, glossy mint-teal and lemon-yellow painted metal shell, segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears, a yellow fin on one side of her head, a crew member sticking a white inventory label on her yellow shoulder like tagging equipment, a blank white name card on the desk in the foreground, single tungsten spotlight from above cutting through haze, dark studio with cold blue LED wall behind, crew silhouettes, 35mm anamorphic film still, Kodak Vision3 500T, low-key lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 6. P1b　老杨的那句话
```
low angle, a Chinese lighting technician in his fifties with grey hair, stubble and a dark work vest standing on an aluminium ladder adjusting a film light, looking down and talking to a young assistant holding the ladder, a tired self-mocking half smile, hard light from above leaving deep shadows on his face, black lighting grid behind him, haze, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 7. P2　楼下的抗议
```
high angle through a rain-streaked office window, a crowd of dozens of people with black umbrellas holding soaked handwritten protest signs on a street corner below, grey overcast daylight, wet glossy street, blurred window frame in the foreground, 85mm telephoto compression, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 8. O6　打板
```
wide shot of a dark minimalist interview set inside a large black studio, two worn armchairs facing each other, a single floor lamp, cinema cameras on tripods and crew half hidden in the shadows, a Chinese female interviewer in her early forties with short bob hair and a black suit sitting in one armchair flipping through cue cards, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head sitting in the other armchair facing her, behind the robot a yellow electric guitar on a stand with a small paper tag, a clapperboard snapping in the foreground, the floor lamp the only warm light, 40mm anamorphic, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 200 --no cartoon, anime, 3d render, plastic toy
```

### 9. O7　“我叫 ALPHA”
```
over-the-shoulder shot from behind a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, the edge of her metal head and turbine ear blurred in the foreground, a Chinese female interviewer in her early forties with short bob hair and a black suit sitting in an armchair across from her asking a question with calm eyes, a single floor lamp between them, dark interview studio, cameras in the shadows, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 10. O8　“你的悲伤，是真的吗？”（沉默）
```
close-up of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head sitting in a worn armchair in a dark interview studio, silent, her blue ring eyes lowered, a lavalier mic taped to her chest, warm floor lamp light on half of her metal face, the other half in darkness, out-of-focus crew silhouettes glancing at each other in the background, 85mm, tension and silence, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 11. O9　“我可以……唱出来吗？”
```
medium shot, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head in an armchair slowly turning her head to look at a yellow electric guitar standing on a stand behind her with a small paper tag, the floor lamp light catching the guitar's silver gear hub, the interviewer blurred in the foreground, dark studio, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 12. P4　小鹿递来吉他
```
a 23-year-old Chinese girl with a round face, a low ponytail and a faded blue denim jacket wearing a crew badge handing a yellow electric guitar to a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head who sits in an armchair, the robot's metal hands reaching for it, warm floor lamp light, dark interview studio with cameras in the shadows, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 13. P5　第一根弦
```
macro close-up, silver robotic fingers with yellow fingertips hovering over the strings of an angular yellow electric guitar with a silver gear-shaped hub in its body, one string catching a thin line of warm light, pitch black background, 100mm macro, extremely shallow depth of field, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

---

## 0:00–0:41 演播室，她开始唱

### 14. S01　前奏·全景 ★
```
wide shot of a dark minimalist interview set inside a large black studio, two worn armchairs facing each other, a single floor lamp, cinema cameras on tripods and crew half hidden in the shadows, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head sitting in an armchair with an angular yellow electric guitar with a silver gear-shaped hub in its body across her lap, starting to play, the single floor lamp and one overhead spotlight cutting through haze, crew members slowly stopping in the shadows around her, 40mm anamorphic, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 200 --no cartoon, anime, 3d render, plastic toy
```

### 15. S02　她开口了 ★　**【已出】**
```
close-up of a female humanoid robot singing softly while playing an angular yellow electric guitar with a silver gear-shaped hub in its body, segmented brushed-silver robotic face, teal lips slightly parted, glowing blue ring LED eyes half lowered, head tilted as if remembering someone, glossy mint-teal and yellow shell with scratches, warm top light carving shadows into the metal seams, cold rim light behind her, out-of-focus haze and bokeh of a dark TV studio, 85mm lens, shallow depth of field, 35mm film still, Kodak Vision3 500T, intimate, melancholic, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render
```

### 16. S03　老杨停下了
```
low angle, a Chinese lighting technician in his fifties with grey hair, stubble and a dark work vest frozen on an aluminium ladder with one hand still on a film light, slowly turning his head toward the stage, eyes slightly red, half silhouetted by the light behind him, warm stage light on one side of his face, haze, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 17. PF1　光柱里的她 ★
```
extreme wide shot from the last row of an empty dark studio, rows of out-of-focus empty seat backs in the foreground, far away in the center a single shaft of light through thick haze, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head sitting in the light singing with an angular yellow electric guitar with a silver gear-shaped hub in its body, crew members only dark silhouettes around the edges, 40mm anamorphic, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 250 --no cartoon, anime, 3d render, plastic toy
```

### 18. S04　林姐拦住了制片
```
a Chinese female interviewer in her early forties with short bob hair and a black suit sitting in the dark raising one hand without looking back to stop a producer with a headset who is getting up to walk toward the set, both almost silhouettes, warm light from the set outlining their profiles, far in the blurred background a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head singing in a pool of light, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 19. S05　一滴泪落在手卡上
```
close-up of a Chinese female interviewer in her early forties with short bob hair and a black suit holding a white handwritten cue card, her eyes red and wet, a single tear falling onto the card and blurring the ink, warm lamp light from below lighting the card and her chin, blurred warm bokeh behind, 85mm, restrained emotion, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 20. S06　推向她的眼睛
```
extreme close-up of the face of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, glowing blue concentric ring eyes looking off-frame into the darkness, top light falling on brushed metal, lower half of the face in shadow, black background, 100mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 21. IV1　访谈：第一次唱歌，是为谁唱的
```
documentary interview close-up of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head sitting in a worn armchair, speaking softly, a lavalier mic taped to her chest, a single warm floor lamp from the side lighting half of her metal face in Rembrandt style, pitch black background, slight film grain, 85mm, intimate and honest like a long-form TV interview, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

---

## 0:41–1:33 回忆：诞生与冷眼

### 22. S07　实验室·第一次开机　**【已出】**
```
late night in an old factory turned into a cramped robotics lab, a 62-year-old Chinese engineer with grey buzz-cut hair, old metal-framed reading glasses and a worn brown cardigan leaning over a workbench, a female humanoid robot with a mint-teal and yellow metal shell and silver robotic face sitting on the edge of the bench with cables plugged into her neck, her blue ring LED eyes lighting up for the very first time and reflecting in his glasses, his eyes wet, a single warm tungsten desk lamp as the only light, cold blue night and railway tracks outside the rain-streaked window, solder smoke in the lamp light, 35mm film still, Kodak Vision3 500T, warm amber memory, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render
```

### 23. S08　教她按和弦
```
close-up, a wrinkled old man's hand resting on top of silver robotic fingers with yellow fingertips, guiding them to press the strings of an angular yellow electric guitar with a silver gear-shaped hub in its body, a warm tungsten desk lamp from the side, an old cassette recorder blurred in the background, dust floating in the light, 85mm, warm amber memory, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 24. S09　商场演出：“别碰”
```
a small stage in a shopping mall atrium with a banner, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head sitting on a stool playing an angular yellow electric guitar with a silver gear-shaped hub in its body and singing, a crowd of children in front, a little girl reaching out to touch the robot's metal fingers while her mother pulls her back with a disapproving look, a 62-year-old Chinese engineer with grey buzz-cut hair, old metal-framed reading glasses and a worn brown cardigan standing at the back of the crowd with his smile frozen, soft overcast skylight, slightly overexposed warm memory, 35mm handheld, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 25. S10　人群外的乐手
```
a young Chinese street musician in his late twenties with messy hair, stubble and an old jacket with a black guitar case on his back standing still at the edge of a shopping mall crowd, holding a phone he just hung up, staring toward a distant stage, jaw tight, half backlit by a skylight, blurred people passing in the foreground, 85mm telephoto, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 26. S11　一排排举起的手机
```
from behind a dark audience, rows of raised smartphones glowing cold white, silhouettes of heads, far away on a small stage a tiny a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head singing under one spotlight, haze above the crowd, cold oppressive mood, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 27. H1　伦理听证会　**【已出】**
```
high angle from the top row of an old wooden tiered lecture hall like a historic anatomy theatre, rows of people in dark suits rising in circles all looking down, at the very bottom in the center a small lone female humanoid robot with a mint-teal and yellow metal shell standing on an empty floor under one cold white overhead light, a large screen on the wall glowing red with voting results, an elderly expert speaking at a podium above her, oppressive silence, dust in the air, 24mm lens, 35mm film still, Kodak Vision3 500T, cold desaturated palette, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render
```

### 28. IV2　访谈：断电的时候，很黑
```
documentary interview medium shot of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head in a worn armchair in a pitch black studio, head slightly lowered, metal hands resting on her knees, a single warm floor lamp beside her, her blue ring eyes dimmed, an interviewer's shoulder blurred in the foreground, 50mm, quiet and heavy, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 29. S13　AI 广告下卖唱
```
a subway passage, a huge glowing white billboard reading AI MUSIC with a cold digital singer face, directly beneath it a young Chinese street musician in his late twenties with messy hair, stubble and an old jacket sitting on the floor playing guitar with an empty guitar case, commuters rushing past in motion blur, cold white billboard light making his face pale, wet floor reflecting the screen, 28mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 30. S14　钥匙在冰箱里
```
late night in a small old kitchen, shot from inside an open refrigerator, a 62-year-old Chinese engineer with grey buzz-cut hair, old metal-framed reading glasses and a worn brown cardigan holding a bunch of keys he just found inside the fridge, frozen in confusion and unease, cold fridge light from below on his face, the rest of the kitchen pitch black, rain on the window, 35mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 31. S15　手背上的字
```
macro close-up of the back of an old wrinkled hand with age spots, words handwritten in blue ballpoint pen on the skin, warm desk lamp light raking across the skin texture, dark background, 100mm macro, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 32. S16　他们为什么怕我
```
late night lab lit only by one warm desk lamp, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head sitting on the edge of a workbench, a 62-year-old Chinese engineer with grey buzz-cut hair, old metal-framed reading glasses and a worn brown cardigan sitting hunched on an old chair across from her placing a yellow-wrapped throat lozenge into her open metal palm, the lamp between them, both outer sides in darkness, rain on the window, 40mm anamorphic, side view, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

---

## 1:33–2:31 抵制、告别

### 33. S18　资产处置通知
```
close-up of an office printer slowly pushing out an A4 notice with a red official stamp in the corner, cold fluorescent light, grey rainy window behind, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 34. S19　篷布下的光熄灭
```
an empty old warehouse, a human-shaped figure completely covered by a grey tarp with an asset number tag, among rows of scrapped machines, a faint blue glow leaking from under the tarp, one cold shaft of light from a high window full of floating dust, roof leaking drops of water, 35mm, Tarkovsky-like stillness, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 35. S20　手电光
```
night in a dark warehouse, a 62-year-old Chinese engineer with grey buzz-cut hair, old metal-framed reading glasses and a worn brown cardigan seen from behind holding a flashlight, pulling a grey tarp off a human-shaped figure, revealing the head of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, her blue ring eyes flickering on, the flashlight beam visible in the dust, 35mm handheld, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 36. S21　雨中的铁轨
```
extreme wide shot, early morning drizzle and thick fog, a single railway track stretching into the mist toward a small distant station, an old man dragging a worn suitcase and a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing an oversized worn brown wool coat walking side by side away from the camera half a step apart, telegraph poles fading into the fog, cold grey-blue light, 85mm telephoto, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 200 --no cartoon, anime, 3d render, plastic toy
```

### 37. H3　按货物托运
```
close-up of a printed notice on a station wall soaked by rain, water running down it, an old wrinkled hand gripping the handle of a worn suitcase in the blurred foreground, cold overcast light, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 38. S22a　天冷，穿上　**【已出】**
```
rainy day at a small rural Chinese train station, an old dark green passenger train waiting at the platform, an elderly Chinese man with grey hair and reading glasses taking off his worn brown wool coat and putting it over the shoulders of a female humanoid robot with a mint-teal and lemon-yellow metal shell and a silver robotic face, gently fixing the collar like a father, she carries a yellow guitar case on her back, rain falling from the edge of the platform canopy like a curtain, steam between the train wheels, cold overcast light, warm light from inside the train carriage on his face, 50mm handheld, 35mm film still, Kodak Vision3 500T, quiet heartbreak, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render
```

### 39. S22b　远去的列车　**【已出】**
```
from behind, a female humanoid robot in an oversized worn brown wool coat standing alone on a wet rainy train platform, one metal hand slowly raised, an old green train pulling away, an old man's palm pressed against the fogged train window, wind lifting dead leaves and the hem of her coat, steam drifting across the tracks, grey overcast sky, cold desaturated palette, 40mm anamorphic, 35mm film still, Kodak Vision3 500T, loneliness, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render
```

### 40. S23　一滴雨
```
medium profile shot of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing an oversized worn brown wool coat standing on a rainy train platform looking toward where the train left, a single raindrop sliding down the seam of her silver metal face, grey sky rim light, blurred empty tracks behind, 85mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 41. S24a　站了七个小时·首帧
```
extreme wide locked-off shot of an empty rural train platform in late morning drizzle, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing an oversized worn brown wool coat standing alone in the middle looking down the tracks, a round platform clock on a pillar showing eleven o'clock, cold grey light, wet ground, 24mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 42. S24b　站了七个小时·尾帧
```
the exact same extreme wide locked-off shot of an empty rural train platform at dusk, the rain has stopped, a thin line of dark orange light in the clouds, platform lights just turned on, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing an oversized worn brown wool coat still standing in the same spot with a long shadow, the round clock on the pillar showing six o'clock, 24mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 43. IV3　访谈：站台太安静了
```
documentary interview extreme close-up of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, her blue ring eyes slowly looking up, warm floor lamp light on brushed metal, pitch black background, a faint reflection of the lamp in her eyes, 100mm, tender and quiet, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 44. PF3　黄昏的空站台 ★　**【已出】**
```
dusk after rain at an empty rural train platform, a female humanoid robot with a silver robotic face and glowing blue ring eyes, wearing an oversized worn brown wool coat, sitting alone on a bench playing a yellow electric guitar and singing for the first time, head turned toward the empty tracks where the train left, a thin line of dark orange light breaking through the clouds on the horizon, platform lights just turned on cold white, wet ground reflecting the sky, light mist, 40mm anamorphic, 35mm film still, Kodak Vision3 500T, melancholic, grounded realism --ar 239:100 --v 8.1 --style raw --s 200 --no cartoon, anime, 3d render
```

---

## 无音乐章节：为电活着

### 45. L01　戴上假发
```
in a filthy public restroom at night, the reflection in a cracked mirror of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing an oversized worn brown wool coat pulling a cheap black wig onto her metal head, the wig caught crooked on the yellow fin, a flickering sickly green fluorescent tube overhead, mouldy tiles, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 46. H2　禁止入内
```
rainy night, seen from inside an old noodle shop through a fogged glass door, warm yellow light and steaming bowls in the blurred foreground, outside under the dripping awning a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing a crooked cheap black wig and an oversized worn brown wool coat, her shell dirty, dented and chipped standing to shelter from the rain, a heavy shop owner in a greasy apron pushing the door open and waving her away, cold cyan night outside, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 47. L02　什么活都干，只要电
```
early morning drizzle at a roadside day-labor market in China, a row of migrant workers squatting and standing with cardboard signs, all exhaling white breath, at the end of the line a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing a crooked cheap black wig and an oversized worn brown wool coat, her shell dirty, dented and chipped holding up a cardboard sign, a van driver glancing at her through a rolled-down window, cold grey light, 35mm handheld, documentary style, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 48. L03　拆解厂
```
night shift at an electronic waste dismantling plant, a conveyor belt piled with scrapped robot parts, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing a crooked cheap black wig and an oversized worn brown wool coat, her shell dirty, dented and chipped standing at the line holding a broken robot head of her own model, its blue ring eye still faintly glowing, gently pressing her metal fingers over its eye, a thin expressionless Chinese man in his thirties wearing black-framed glasses with no lenses and a grey work jacket across the belt looking up at her, harsh white fluorescent light, welding sparks, dust and smoke, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 49. L04　暴雨里的电塔
```
thunderstorm at night, extreme wide low angle, a huge high-voltage transmission tower in a field, a tiny figure of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing a crooked cheap black wig and an oversized worn brown wool coat, her shell dirty, dented and chipped climbing halfway up with her coat whipping in the wind, a lightning bolt illuminating the whole tower, far below a few workers in raincoats huddled beside a utility truck, 24mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 200 --no cartoon, anime, 3d render, plastic toy
```

### 50. L05　冷库　**【已出】**
```
inside a minus 25 degree industrial cold storage warehouse, rows of frozen meat hanging on racks, Chinese workers in thick padded coats carrying boxes and exhaling clouds of white breath, a female humanoid robot with a mint-teal and yellow metal shell and silver robotic face, wearing a cheap crooked black wig and an oversized brown coat, carrying a heavy box past them with no breath at all, frost on the shelves, cold mist flowing on the floor, harsh cold white ceiling lights and deep blue shadows, handheld 35mm, documentary film still, Kodak Vision3 500T, grounded realism --ar 239:100 --v 8.1 --style raw --s 120 --no cartoon, anime, 3d render
```

### 51. L06　黑电　**【已出】**
```
rainy night in a narrow Chinese urban village alley, a chaotic tangle of electrical wires overhead dripping with rain, a bald middle-aged man with a gold chain and a cigarette counting cash under a plastic awning lit by one bare tungsten bulb, a female humanoid robot with a silver robotic face, crooked black wig and soaked oversized brown coat sitting against a wet wall with a power cable plugged into the back of her neck, her blue ring eyes slowly lighting up, puddles reflecting warm bulb light and cold cyan night, laundry hanging in the foreground, 40mm, 35mm film still, Kodak Vision3 500T, gritty, grounded realism, in the style of a Chinese neo-noir film --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render
```

### 52. L07　解压馆
```
seen through a wire-mesh glass window in a door, a small room lit by a single red work light, the floor covered in broken glass and dented sheet metal, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing a crooked cheap black wig and an oversized worn brown wool coat, her shell dirty, dented and chipped standing alone in the center with fresh dents in her shell, slowly crouching to pick up a small broken piece of her own teal shell, cold white corridor light leaking in, 35mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 53. IV4　访谈：我想让他们以为我是人
```
documentary interview two-shot from the side, a Chinese female interviewer in her early forties with short bob hair and a black suit and a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head sitting in armchairs facing each other in a pitch black studio, a single floor lamp between them, the robot speaking with her head slightly turned away, the interviewer listening still, lots of black negative space, 40mm anamorphic, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 54. L08　夜总会包厢 ★　**【已出】**
```
a seedy private karaoke room in a Chinese nightclub, purple and red lights, thick cigarette smoke, a low table crowded with baijiu bottles and fruit plates, two drunk middle-aged businessmen with open collars and gold watches laughing on a velvet sofa, in the center of the room a female humanoid robot with a segmented silver robotic face and glowing blue ring eyes, mint-teal and yellow metal shell, a crooked cheap black wig, holding a microphone and singing while liquor drips down her metal face, a cold silent young man with spiky black hair and a worn black leather jacket standing by the door, TV screen light flickering on her face, handheld 35mm from behind the sofa, film still, Kodak Vision3 500T, decadent and uncomfortable, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, nudity
```

### 55. M1　雨夜的摩托车　**【已出】**
```
late night heavy rain under an empty city overpass, a young Chinese man with spiky black hair and a worn black leather jacket riding an old modified motorcycle, a female humanoid robot with a silver robotic face and soaked oversized brown coat sitting behind him, neither speaking, faint steam rising from his shoulders in the cold rain, orange sodium streetlights sweeping across them one by one with cold cyan darkness in between, rain streaks glowing in the light, water spraying from the tires, side tracking shot, 40mm anamorphic, 35mm film still, Kodak Vision3 500T, lonely and tender, in the spirit of Fallen Angels but colder and more realistic --ar 239:100 --v 8.1 --style raw --s 200 --no cartoon, anime, 3d render
```

### 56. L09　幕布后的歌声 ★
```
backstage behind a black curtain in an underground nightclub, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing a crooked cheap black wig and an oversized worn brown wool coat, her shell dirty, dented and chipped singing into a microphone in the dark, a thin slit of colorful stage light cutting across her metal face, through the gap in the curtain a middle-aged male singer in a sequin suit lip-syncing on stage to a cheering crowd, stage smoke creeping under the curtain, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 200 --no cartoon, anime, 3d render, plastic toy
```

---

## 2:31–3:24 遇见与被看见

### 57. S25　地下通道 ★
```
low angle almost at floor level, a late night station underpass, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing a crooked cheap black wig and an oversized worn brown wool coat, her shell dirty, dented and chipped sitting against a tiled wall playing an angular yellow electric guitar with a silver gear-shaped hub in its body and singing with her head tilted back, a power cord running from her back to a newsstand socket, a guitar case with a few coins, legs of passers-by blurred in the foreground, a half-broken flickering cyan fluorescent tube, warm light from the newsstand on half of her face, wet floor reflections, 40mm anamorphic, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 200 --no cartoon, anime, 3d render, plastic toy
```

### 58. S26　我们也是
```
late night underpass, over the shoulder of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing a crooked cheap black wig and an oversized worn brown wool coat, her shell dirty, dented and chipped sitting against the wall with her eyes dark, a 23-year-old Chinese girl with a round face, a low ponytail and a faded blue denim jacket crouching in front of her pulling a thin black cable from inside her own sleeve cuff and plugging it into the back of the robot's neck, raindrops on the girl's eyelashes, the robot's blue ring eyes slowly lighting up and illuminating the girl's calm face, flickering fluorescent light, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 59. S27　没有镜片的眼镜
```
low angle in a late night underpass, three people standing side by side looking down at the camera: a 23-year-old Chinese girl with a round face, a low ponytail and a faded blue denim jacket in the middle, a young Chinese man with spiky black hair and a worn black leather jacket on the left with hands in his jacket pockets looking away, a thin expressionless Chinese man in his thirties wearing black-framed glasses with no lenses and a grey work jacket on the right, cold fluorescent backlight from above, faces half in shadow, 24mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 60. S28　她摘下了假发
```
a cramped urban village rental room, a string of warm small bulbs on the wall, more than a dozen unopened takeout boxes stacked neatly on top of the fridge, reflection in an old mirror of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing an oversized worn brown wool coat taking off her cheap black wig and revealing her whole metal head, behind her a 23-year-old Chinese girl with a round face, a low ponytail and a faded blue denim jacket, a young Chinese man with spiky black hair and a worn black leather jacket and a thin expressionless Chinese man in his thirties wearing black-framed glasses with no lenses and a grey work jacket watching in silence, warm bulb light and cold rainy window light splitting her face, 40mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 61. S29　雨夜天台 ★　**【已出】**
```
rainy night on the rooftop of a dense Chinese urban village, a female humanoid robot with no wig, segmented silver robotic face and glowing blue ring eyes, mint-teal and yellow metal shell with dents and scratches, wearing an old brown wool coat, standing in heavy rain singing with her head tilted back while playing a yellow electric guitar, rain streaming down her metal face like tears, a young man in a black leather jacket beside her holding a closed umbrella, a girl behind them filming with a phone, orange sodium light rising from the alley below, cold cyan fog over the city, backlit rain, 40mm anamorphic, 35mm film still, Kodak Vision3 500T, cathartic, grounded realism --ar 239:100 --v 8.1 --style raw --s 250 --no cartoon, anime, 3d render
```

### 62. IV5　访谈：唱歌的就不是我了
```
documentary interview close-up of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, her shell covered in old dents, scratches and repainted patches in an armchair, looking straight ahead with calm resolve, warm floor lamp light, a soft cold rim light behind her head, pitch black background, 85mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 63. S32a　亮起的窗·首帧
```
rainy night, telephoto wide shot of an old dense residential block with hundreds of windows, only a few windows lit, cold blue night, lights softly blooming in the rain mist, 85mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 64. S32b　亮起的窗·尾帧
```
the exact same telephoto shot of an old dense residential block on a rainy night, now most of the hundreds of windows glowing warm yellow and a few glowing with blue phone light, lights blooming in the rain mist, 85mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 65. PF2　她的手和琴弦 ★
```
close-up of scratched silver robotic fingers pressing chords on an angular yellow electric guitar with a silver gear-shaped hub in its body while the other hand strums hard, the gear hub at the bottom of the frame, strings vibrating in a warm top light, pitch black background, 85mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 66. PF4　全场静止·仰拍 ★　**【已出】**
```
extreme low angle from the edge of a stage, a female humanoid robot in a mint-teal and lemon-yellow metal shell singing her highest note with a yellow electric guitar, silver robotic face lifted toward a single spotlight, behind and above her the silhouettes of a frozen TV crew, a lighting technician standing still on a tall ladder, camera operators and stagehands all staring at her, thick haze glowing around the top light, backlit silhouettes, 24mm lens, 35mm anamorphic film still, Kodak Vision3 500T, awe and silence, grounded realism --ar 239:100 --v 8.1 --style raw --s 200 --no cartoon, anime, 3d render
```

---

## 3:24–4:00 与结尾

### 67. S30　最后几句 ★
```
close-up of a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, her shell covered in old dents, scratches and repainted patches sitting in an armchair singing the last lines with an angular yellow electric guitar with a silver gear-shaped hub in its body, head slowly lowering, fingers slowing on the strings, top light splitting her face into light and shadow, cold blue rim light behind, two blurred crew shoulders in the foreground, 85mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 68. S31　侧台的阿凯
```
in the darkness at the side of a studio set, a young Chinese man with spiky black hair and a worn black leather jacket standing in front with a 23-year-old Chinese girl with a round face, a low ponytail and a faded blue denim jacket and a thin expressionless Chinese man in his thirties wearing black-framed glasses with no lenses and a grey work jacket behind him, all watching the stage, warm stage light only touching the edges of their faces, the young man slowly pulling off one fingerless leather glove, 85mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 69. S33　冬夜，他认不出她了　**【已出】**
```
winter night in an old house in a small northern Chinese town, heavy snow outside the frosted window, a very old frail Chinese man with white hair and metal-framed reading glasses sitting in a worn armchair under a blanket, his daughter in her thirties crouching beside him holding out a glowing phone, he looks at the screen with confused eyes, one warm tungsten lamp as the only light inside, cold blue snow light from the window, framed through a doorway, 40mm, 35mm film still, Kodak Vision3 500T, quiet and devastating, grounded realism, in the mood of Black Coal Thin Ice --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render
```

### 70. S34　手指在打拍子
```
close-up of an old wrinkled hand with age spots resting on a worn wooden armrest, two fingers lifted mid-tap, the faint glow of a phone screen on the skin, warm lamp light and cold blue snow light from a window mixing, 100mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 71. S35　春天，她来了
```
spring after rain at a small northern Chinese railway station, pink and white peach blossoms along the platform, an old green train stopped, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, wearing an oversized worn brown wool coat stepping down from the train with a guitar case on her back, behind her a 23-year-old Chinese girl with a round face, a low ponytail and a faded blue denim jacket, a young Chinese man with spiky black hair and a worn black leather jacket and a thin expressionless Chinese man in his thirties wearing black-framed glasses with no lenses and a grey work jacket pushing a power case, soft diffused sunlight, the first warm saturated colors of the film, petals stuck to the wet platform, 40mm anamorphic, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 200 --no cartoon, anime, 3d render, plastic toy
```

### 72. S36　第一个鼓掌的人
```
from behind a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, her shell covered in old dents, scratches and repainted patches sitting in an armchair with a guitar, her back to camera in the foreground, looking out at a dark studio where a Chinese lighting technician in his fifties with grey hair, stubble and a dark work vest on a ladder is the first to start clapping with red eyes and the crew below still frozen, the stage light forming a halo behind her head, haze, 50mm, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 73. S37　你的悲伤是真的吗（划掉“设备”）
```
documentary interview two-shot in a pitch black studio, a female humanoid robot with a glossy mint-teal and lemon-yellow painted metal shell, a segmented brushed-silver robotic face with teal lips, glowing blue ring-shaped LED eyes, silver turbine ears and a yellow fin on one side of her head, her shell covered in old dents, scratches and repainted patches with a guitar on the left, a Chinese female interviewer in her early forties with short bob hair and a black suit on the right holding a pen over a white name card on the small table between them, crossing out a word on it, a single floor lamp between them, quiet resolution, 40mm anamorphic, 35mm anamorphic film still, Kodak Vision3 500T, low-key motivated lighting, deep shadows, muted color, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render, plastic toy
```

### 74. S38　长椅上　**【已出】**
```
extreme wide shot, spring at a small rural train station after rain, peach blossoms falling, a very old white-haired Chinese man and a female humanoid robot with a mint-teal and yellow metal shell and silver robotic face sitting side by side on a weathered wooden bench, half a step apart, tiny in the frame, empty railway tracks stretching into soft mist, gentle diffused sunlight, the first warm colors of the film, lots of negative space, 35mm film still, Kodak Vision3 500T, tender and quiet, grounded realism --ar 239:100 --v 8.1 --style raw --s 150 --no cartoon, anime, 3d render
```

---

## 小技巧

- **想要更多变化**：末尾加 `--chaos 15`。
- **ALPHA 变成真人**：在 `--no` 后面加 `human skin, human face`。
- **画面太精致、像广告**：把 `--s` 调到 50–100。
- **想要更有氛围**：`--s` 调到 200–300，或者正文加 `heavy haze, volumetric light`。
- **同一个场景前后统一**：先选定一张满意的图，后面同场景的镜头用它当风格参考 `--sref`（只参考风格，不锁人物）。