"""충신교회 유치부 사랑나눔 파티 — 오디오(내레이션 + 현장음 + BGM) & 타임라인"""
import json
import subprocess
from pathlib import Path

import numpy as np

SR = 44100
VOICE_DIR = 'voice_custom'  # TopView 맞춤 음성: 충신유치원 나레이션
HERE = Path(__file__).parent
DUR = 126.0
N = int(DUR * SR)
t = np.arange(N) / SR

# (id, 시작, 자막)
NARR = [
    ('n01', 1.2, '오늘 충신교회 유치부에 아주 특별한 파티가 열렸어요.'),
    ('n02', 5.8, '이름하여, 사랑나눔 파티!'),
    ('n03', 10.3, '신나는 찬양으로 파티의 문을 활짝 열었어요.'),
    ('n04', 15.0, '아이들의 노랫소리가 예배실 가득 울려 퍼집니다.'),
    ('n05', 25.6, '목사님이 들려주신 십자가 이야기.'),
    ('n06', 28.4, '예수님이 우리를 얼마나 사랑하시는지, 귀를 쫑긋 세우고 들었어요.'),
    ('n07', 34.8, '두 손을 꼭 모으고, 하나님께 드리는 작은 기도.'),
    ('n08', 42.8, '반마다 선생님과 동그랗게 둘러앉아, 카드를 펼치며 오늘 배운 사랑을 함께 나눴어요.'),
    ('n09', 53.0, '정성 담아 준비한 예물을 하나님께 드리고,'),
    ('n10', 65.2, '할머니, 할아버지께 드릴 사랑의 간식도 한가득 담았어요.'),
    ('n11', 70.0, '받은 사랑을 이웃과 나누는 것, 그게 바로 오늘 파티의 주인공이었죠.'),
    ('n12', 78.6, '그리고 무대 위, 하얀 가운을 입은 아이들의 찬양!'),
    ('n13', 104.0, '작은 손으로 시작된 사랑이, 세상을 따뜻하게 물들입니다.'),
    ('n14', 116.6, '충신교회 유치부 사랑나눔 파티. 하나님의 사랑을 나누는 아이들로 자라 가요!'),
]
# 현장 영상 (id, 화면 시작, 길이, 프레임 폴더, 현장음 크기)
CLIPS = [('a', 9.6, 15.0, 'clips/a', 0.9), ('b', 52.2, 12.5, 'clips/b', 0.9), ('c', 78.5, 24.0, 'clips/c', 1.0)]
SCENES = [  # (시작, 끝, 이름)
    (0.0, 9.6, 'intro'), (9.6, 24.6, 'praise'), (24.6, 34.2, 'word'), (34.2, 42.2, 'prayer'), (42.2, 52.2, 'class'),
    (52.2, 64.7, 'offering'), (64.7, 78.5, 'sharing'), (78.5, 102.5, 'choir'), (102.5, 115.8, 'recap'), (115.8, 126.0, 'ending'),
]


def load(fn):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(fn), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def place(dst, sig, start):
    i = int(start * SR); j = min(len(dst), i + len(sig))
    if i < len(dst): dst[i:j] += sig[:j - i]


def ma(x, k):
    c = np.cumsum(np.concatenate([[0], x])); h = k // 2
    i0 = np.clip(np.arange(len(x)) - h, 0, len(x)); i1 = np.clip(np.arange(len(x)) + h, 0, len(x))
    return (c[i1] - c[i0]) / k


voice = np.zeros(N); speech = np.zeros(N); lines = []
for nid, st, text in NARR:
    v = load(HERE / VOICE_DIR / f'{nid}.mp3'); place(voice, v, st)
    speech[int(st * SR):int(st * SR) + len(v)] = 1
    lines.append({'id': nid, 't': st, 'e': round(st + len(v) / SR, 3), 'text': text})
voice *= 0.16 / np.sqrt(np.mean(voice[speech > 0] ** 2))

# 현장음: 화면이 보일 때 들리고, 내레이션 중에는 낮춤
live = np.zeros(N); live_on = np.zeros(N)
for cid, st, ln, _, g in CLIPS:
    a = load(HERE / 'clips' / f'{cid}.wav')[:int(ln * SR)]
    a *= 0.14 / np.sqrt(np.mean(a ** 2) + 1e-12)
    tt = np.arange(len(a)) / SR
    a *= np.clip(tt / 0.6, 0, 1) * np.clip((ln - tt) / 0.8, 0, 1) * g
    place(live, a, st); live_on[int(st * SR):int((st + ln) * SR)] = 1

k = int(0.35 * SR)
m = np.clip(ma(ma(speech, k), k) * 1.6, 0, 1)
live *= 1 - 0.7 * m

# BGM: 0–80초 앞부분 → 찬양대 영상에서는 거의 빠짐 → 마무리에서 곡 후반부로 다시
b = load(HERE / 'bgm.mp3'); b *= 0.12 / np.sqrt(np.mean(b ** 2))
bgm = np.zeros(N)
seg1 = b[:int(84 * SR)].copy(); tt = np.arange(len(seg1)) / SR
seg1 *= np.clip(tt / 1.0, 0, 1) * np.clip((84 - tt) / 4.0, 0, 1)
place(bgm, seg1, 0.0)
seg2 = b[int(62 * SR):].copy(); tt = np.arange(len(seg2)) / SR
seg2 *= np.clip(tt / 3.0, 0, 1)
place(bgm, seg2, 100.0)
lv = np.ones(N)
lv = np.where(live_on > 0, 0.45, lv)                       # 현장 영상 중에는 BGM 낮춤
lv = np.where((t > 34.2) & (t < 42.2), 0.6, lv)            # 기도: 부드럽게
lv = np.where((t > 80.5) & (t < 101.5), 0.06, lv)          # 찬양대: 아이들 노래가 주인공
lv = ma(lv, int(0.8 * SR))
bgm *= lv * (1 - 0.68 * m) * np.clip((DUR - 0.3 - t) / 3.5, 0, 1)

mix = voice + live + bgm * 0.8
pk = np.abs(mix).max()
if pk > 0.97: mix *= 0.97 / pk
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
sp = speech > 0
print(f'voice {db(voice[sp]):.1f} / bed under voice {db((live + bgm * 0.8)[sp]):.1f} dB')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11', '-ar', '48000', '-ac', '2', str(HERE / 'audio.wav')],
               input=mix.astype(np.float32).tobytes(), check=True)

(HERE / 'timeline.js').write_text('window.TL = ' + json.dumps({'dur': DUR, 'lines': lines, 'clips': [{'id': c[0], 't': c[1], 'len': c[2], 'dir': c[3]} for c in CLIPS],
                                                              'scenes': [{'t': s[0], 'e': s[1], 'id': s[2]} for s in SCENES]}, ensure_ascii=False) + ';\n', encoding='utf-8')


def ts(s):
    ms = int(round(s * 1000)); return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'

srt = [f"{i}\n{ts(l['t'])} --> {ts(l['e'] + 0.3)}\n{l['text']}\n" for i, l in enumerate(lines, 1)]
(HERE / 'subtitles.srt').write_text('\n'.join(srt), encoding='utf-8')
print('ok')
