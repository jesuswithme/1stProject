#!/bin/bash
# TopView 나레이션(충신유치원 나레이션) 17줄 + BGM 2곡 다운로드
set -e; cd "$(dirname "$0")"; mkdir -p tts
python3 - <<'PY'
import json,subprocess
S=json.load(open("lines_src.json"))
for i,(_,_,code) in enumerate(S):
    subprocess.run(["curl","-fsSL","--retry","3","-o",f"tts/{i:02d}.mp3",f"https://api.topview.ai/s/{code}"],check=True)
PY
curl -fsSL --retry 3 -o bgm1.mp3 https://api.topview.ai/s/R7PF4eHy
curl -fsSL --retry 3 -o bgm2.mp3 https://api.topview.ai/s/rghKMKIM
echo "audio ok"
