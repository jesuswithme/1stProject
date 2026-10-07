#!/bin/bash
# 오디오 받기 → 믹스 → 영상과 합치기 → 유튜브용 최종본
set -e; cd "$(dirname "$0")"
bash fetch_audio.sh
python3 mix.py
ffmpeg -y -v error -i video_silent.mp4 -i mix.m4a -map 0:v -map 1:a -c:v copy -c:a copy -shortest -movflags +faststart "하루가_더해지는_기적_master.mp4"
ffmpeg -y -v error -i "하루가_더해지는_기적_master.mp4" -c:v libx264 -preset slow -b:v 1700k -pass 1 -an -f null /dev/null
ffmpeg -y -v error -i "하루가_더해지는_기적_master.mp4" -c:v libx264 -preset slow -b:v 1700k -pass 2 -c:a aac -b:a 160k -movflags +faststart "하루가_더해지는_기적.mp4"
ls -la *.mp4
