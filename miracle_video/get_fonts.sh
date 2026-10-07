#!/bin/bash
# 한글 폰트(Google Fonts, OFL) 받기
cd "$(dirname "$0")"; mkdir -p fonts; cd fonts
B=https://raw.githubusercontent.com/google/fonts/main/ofl
curl -fsSL -o GowunBatang-Bold.ttf $B/gowunbatang/GowunBatang-Bold.ttf
curl -fsSL -o GowunBatang-Regular.ttf $B/gowunbatang/GowunBatang-Regular.ttf
curl -fsSL -o NotoSansKR.ttf "$B/notosanskr/NotoSansKR%5Bwght%5D.ttf"
curl -fsSL -o NotoSerifKR.ttf "$B/notoserifkr/NotoSerifKR%5Bwght%5D.ttf"
