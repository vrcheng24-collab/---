# Build sentence-level song map (from the lyrics embedded in the master) and cut lip-sync WAV slices.
# Times come from the master's embedded LRC tags: status = provisional_lrc until checked by ear.
import subprocess, csv, hashlib, os, re, json
MASTER = "/root/.claude/uploads/244b6930-24ca-5e89-bb8e-bcf0d6db12f0/1dd96bd4-_____.mp3"
OUT = os.path.dirname(os.path.abspath(__file__))
SR = 48000
sha = hashlib.sha256(open(MASTER, "rb").read()).hexdigest()
lrc = subprocess.run(["ffprobe","-v","error","-show_entries","format_tags=lyrics-Lyrics-eng","-of","default=nw=1:nk=1",MASTER],capture_output=True,text=True).stdout
rows = []
for m in re.finditer(r"\[(\d+):(\d+\.\d+)\](.*)", lrc):
    rows.append((int(m.group(1))*60+float(m.group(2)), m.group(3).strip()))
DUR = 240.456
# sentence table: each lyric line runs until the next tag (blank tags mark the end of a phrase)
lines = []
for i,(t,txt) in enumerate(rows):
    if not txt: continue
    nxt = rows[i+1][0] if i+1 < len(rows) else DUR
    lines.append((t, nxt, txt))
# decode once so sample 0 == playback start
full = os.path.join(OUT, "_master_decoded.wav")
v7full = os.path.join(os.path.dirname(os.path.dirname(OUT)), "v7", "audio", "_master_decoded.wav")
if not os.path.exists(full) and os.path.exists(v7full):
    import shutil; shutil.copy(v7full, full)
if not os.path.exists(full):
    subprocess.run(["ffmpeg","-v","error","-y","-i",MASTER,"-map","0:a","-ar",str(SR),"-c:a","pcm_s24le",full],check=True)
with open(os.path.join(OUT,"song_lines.csv"),"w",newline="",encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["line_id","section","song_in","song_out","source_in_sample","source_out_sample","lyrics","time_status","note"])
    sec = ["A1"]*4+["B1"]*4+["C1"]*4+["A2"]*4+["B2"]*4+["C2"]*4+["Outro"]*4
    for k,(a,b,txt) in enumerate(lines):
        w.writerow([f"L{k+1:02d}",sec[k],f"{a:.2f}",f"{b:.2f}",round(a*SR),round(b*SR),txt,"provisional_lrc","出点为下一句起点或段落空白标记，尾音与换气需听辨"])
# lip-sync segments: (segment_id, shot, line ids, note)
SEGS = [
 ("ALPHA_S02_01","S02_01/S02_02",[1],"演播室开口，近景；S02_01 取前段，S02_02 取后段"),
 ("ALPHA_PF1_01","PF1",[2],"仰拍中景，机器人式分段转头"),
 ("ALPHA_RG2_01","RG2",[8],"大特写，金属分片嘴唇，耳侧涡轮在长音上转"),
 ("ALPHA_RG3_01","RG3",[12],"大特写，虹膜光圈收缩，句尾手指伺服颤动"),
 ("ALPHA_PF3_01","PF3",[16],"站台侧脸，远，口型可选"),
 ("ALPHA_L08_01","L08_01",[19,20],"包间里唱，母带原声，不做 KTV 处理"),
 ("ALPHA_S25_01","S25",[21],"地下通道，唱完这句被拔插头"),
 ("ALPHA_S29_01","S29_01/S29_02",[23],"雨夜天台，两个镜头共用一段"),
 ("ALPHA_PF4_01","PF4",[24],"演播室仰拍，最高音"),
 ("ALPHA_S30_01","S30",[25],"演播室最后几句"),
]
HANDLE = 0.5
with open(os.path.join(OUT,"audio_segments.csv"),"w",newline="",encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["segment_id","shot_id","source_file","source_hash","source_in_sample","source_out_sample","song_in","song_out","mv_in","mv_out","effective_duration","handle_in","handle_out","trim_in","trim_out","lyrics","mouth_cues","mix_file","vocal_file","sample_rate","bit_depth","channels","alignment_status","review_notes"])
    for sid, shot, ids, note in SEGS:
        a = lines[ids[0]-1][0]; b = lines[ids[-1]-1][1]
        cut_a = max(0, a-HANDLE); cut_b = min(DUR, b+HANDLE)
        fn = f"{sid}_MIX_v001.wav"
        subprocess.run(["ffmpeg","-v","error","-y","-i",full,"-af",f"atrim=start_sample={round(cut_a*SR)}:end_sample={round(cut_b*SR)},asetpts=PTS-STARTPTS","-c:a","pcm_s24le",os.path.join(OUT,fn)],check=True)
        txt = " / ".join(lines[i-1][2] for i in ids)
        w.writerow([sid,shot,os.path.basename(MASTER),sha,round(a*SR),round(b*SR),f"{a:.2f}",f"{b:.2f}",f"{a+10:.2f}",f"{b+10:.2f}",f"{b-a:.2f}",f"{a-cut_a:.2f}",f"{cut_b-b:.2f}",f"{a-cut_a:.2f}",f"{a-cut_a+(b-a):.2f}",txt,"","{}".format(fn),"（无干净人声，未提供）",SR,24,2,"provisional_lrc",note+"；WAV 是从 128kbps MP3 解码的兼容派生文件，不代表音质提升"])
print(len(lines),"lines;",len(SEGS),"segments")
