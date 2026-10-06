#!/usr/bin/env bash
# Audio (a sung line, vocal only) -> jaw curve -> rendered motion-reference clips of the ALPHA head rig.
#   ./make_ref.sh <vocal.wav> <name> [syllables.csv] [yaw_steps_json]
# Output: out/<name>_w_34.mp4 (main reference), _w_front, _w_mouth, _p_34 (painted), _preview_with_audio.mp4
set -euo pipefail
cd "$(dirname "$0")"
AUD=$(realpath "$1"); NAME=$2; SYL=${3:-}; YAW=${4:-}
export NODE_PATH=$(npm root -g)
python3 jaw_curve.py "$AUD" ${SYL:+--syllables "$SYL"} --out "out/${NAME}_curve.json"
rm -rf "frames/$NAME"
for v in 34 front mouth; do node render.cjs --curve "out/${NAME}_curve.json" --view $v --mode white --out "frames/$NAME/w_$v" ${YAW:+--yaw "$YAW"} >/dev/null & done
node render.cjs --curve "out/${NAME}_curve.json" --view 34 --mode paint --out "frames/$NAME/p_34" ${YAW:+--yaw "$YAW"} >/dev/null
wait
for d in w_34 w_front w_mouth p_34; do
  ffmpeg -v error -y -framerate 24 -i "frames/$NAME/$d/f%04d.png" -c:v libx264 -crf 16 -pix_fmt yuv420p "out/${NAME}_$d.mp4"
done
ffmpeg -v error -y -i "out/${NAME}_w_34.mp4" -i "$AUD" -map 0:v -map 1:a -c:v copy -c:a aac -shortest "out/${NAME}_preview_with_audio.mp4"
echo "done: out/${NAME}_*.mp4"
