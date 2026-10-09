# 제작 소스 (재렌더링용)

- `tpl.html` — 모션그래픽 본체. `window.setTime(t)`로 각 프레임을 결정론적으로 그립니다(CSS 애니메이션 없음).
- `timeline.py` → `tl.json` — 나레이션 줄별 시작 시각(문서 시간 배분 기준)과 효과음 시각.
- `build.py` — `tpl.html` + `tl.json` → `index.html`
- `snap.js 12.5 40 ...` — 특정 시각 스크린샷(`snaps/`), `grid.py` — 썸네일 합치기
- `render.js 시작프레임 끝프레임 out.mp4` — Playwright Chromium 프레임 캡처 → ffmpeg H.264 (30fps)
- `mix.py` — 나레이션·합성 효과음(망치·문·군중·드론)·BGM 2곡 믹스, 더킹, −16 LUFS 정규화, 룩어헤드 리미터 → `mix.m4a`
- 음성: `tts/`(나레이션·기도문, TopView TTS), `amb/`(도입부 군중 음성), `bgm1.mp3`·`bgm2.mp3`(TopView AI Music)
- 폰트: 라틴 Gloock 등(OFL). 한글은 시스템의 WenQuanYi Zen Hei를 사용합니다.

```bash
python3 timeline.py && python3 build.py
mkdir -p snaps && node snap.js 10 40 100
node render.js 0 2500 part1.mp4 & node render.js 2500 5000 part2.mp4 & node render.js 5000 7500 part3.mp4 & wait
python3 mix.py
printf "file part1.mp4\nfile part2.mp4\nfile part3.mp4\n" > list.txt
ffmpeg -f concat -safe 0 -i list.txt -i mix.m4a -map 0:v -map 1:a -c:v libx264 -crf 18 -preset slow -c:a copy -movflags +faststart master.mp4
```
