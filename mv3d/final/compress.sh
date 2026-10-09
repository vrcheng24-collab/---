#!/bin/bash
# Copies of the master small enough to send (each < 30 MiB): a 720p preview of the whole film, and the 1080p film in 4 parts.
set -e
cd "$(dirname "$0")/../out/final"
M="ALPHA_远去的列车_final_1080p.mp4"; S=send; mkdir -p $S
enc() {  # in out ss dur vbitrate abitrate vf
  ffmpeg -v error -y -ss "$3" -t "$4" -i "$1" -vf "$7" -c:v libx264 -preset slow -b:v "$5" -tune grain -pass 1 -passlogfile "$2.log" -an -f mp4 /dev/null
  ffmpeg -v error -y -ss "$3" -t "$4" -i "$1" -vf "$7" -c:v libx264 -preset slow -b:v "$5" -tune grain -pass 2 -passlogfile "$2.log" -pix_fmt yuv420p \
    -c:a aac -b:a "$6" -movflags +faststart "$2"
  rm -f "$2.log"*
}
enc "$M" "$S/ALPHA_远去的列车_预览_720p.mp4" 0 245.46 820k 96k "scale=1280:720:flags=lanczos,hqdn3d=1.5:1.5:3:3"
P=(0 61.02 124.38 184.29 245.46)
for i in 0 1 2 3; do
  enc "$M" "$S/ALPHA_远去的列车_1080p_第$((i+1))段共4段.mp4" "${P[$i]}" "$(python3 -c "print(${P[$((i+1))]} - ${P[$i]})")" 3300k 160k "null"
done
R="ALPHA_动画参考_口型与头部通道.mp4"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$R")
enc "$R" "$S/ALPHA_动画参考_口型与头部通道.mp4" 0 "$D" "$(python3 -c "print(int(27*8*1024/$D - 170))")k" 128k "null"
ls -la $S
