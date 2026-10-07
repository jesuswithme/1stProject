# 하루가 더해지는 기적 (송은영) — 모션그래픽 영상

1920×1080 · 30fps · 약 1분 58초. 시 7연을 7개 장면(겨울·숨결·고백·물음·깨달음·하늘·사랑)으로 구성했고, 인트로와 아웃트로가 붙습니다.

- 나레이션: TopView `충신유치원 나레이션` 목소리, 17줄, 속도 0.9 (`lines_src.json`)
- BGM: TopView Music 2곡. 전반은 피아노와 현악의 애틋한 곡, 5연 '깨달음'부터 희망찬 오케스트라 곡으로 크로스페이드
- 자막: 하단 자막 박스와 장면별 키워드 타이포그래피

## 다시 만들기
```bash
./get_fonts.sh                   # 한글 폰트
python3 timeline.py && python3 build.py
python3 render.py 0 3549 video_silent.mp4   # 화면 (playwright + chromium)
./finish.sh                      # TopView 음성·BGM 받기 → 믹스 → 최종본 만들기
```
`finish.sh`를 실행하려면 네트워크에서 `api.topview.ai`와 `du9d8548ooqnc.cloudfront.net`에 접근할 수 있어야 합니다.
