"""2026 종교개혁주일 오프닝 영상 오디오: 내레이션 배치 + 합성 음악/효과음 → audio.wav, timeline.js, subtitles.srt"""
import json
import subprocess
from pathlib import Path

import numpy as np

SR = 44100
DUR = 240.0
HERE = Path(__file__).parent
V = HERE / 'voice'
rng = np.random.default_rng(1517)
N = int(SR * DUR)
t = np.arange(N) / SR

# ---------- 내레이션 타임라인 (id, 시작, 화면 문구) ----------
NARR = [
    ('c1', 14.5, '세상은 빠르게 변하고 있습니다.'),
    ('c2', 19.5, '교회는 무엇을 붙들어야 합니까?'),
    ('c3', 24.0, '무엇은 다시 개혁되어야 합니까?'),
    ('k1', 37.0, '1517'),
    ('k2', 40.0, '한 사람이 문을 두드렸다.'),
    ('k3', 44.5, '교회를 무너뜨리기 위해서가 아니라'),
    ('k4', 48.5, '교회를 깨우기 위해서였다.'),
    ('s1', 56.1, 'SOLA GRATIA|오직 은혜|우리는 성취가 아니라 은혜로 살아간다.'),
    ('s2', 63.1, 'SOLA FIDE|오직 믿음|우리는 힘이 아니라 하나님을 신뢰한다.'),
    ('s3', 71.6, 'SOLA SCRIPTURA|오직 성경|수많은 목소리 가운데 말씀을 다시 듣는다.'),
    ('s4', 80.4, 'SOLUS CHRISTUS|오직 그리스도|우리의 중심에는 그리스도가 계신다.'),
    ('s5', 88.8, 'SOLI DEO GLORIA|오직 하나님께 영광|우리의 이름이 아니라 하나님의 영광을 구한다.'),
    ('r1', 104.5, '그러나 종교개혁은 1517년에 끝났을까요?'),
    ('r2', 109.8, '아닙니다.'),
    ('r3', 112.5, 'ECCLESIA REFORMATA, SEMPER REFORMANDA'),
    ('r4', 118.0, '개혁된 교회는 계속 개혁되어야 한다.'),
    ('d1', 129.0, '나의 삶에서?'),
    ('d2', 132.5, '우리 가정에서?'),
    ('d3', 136.0, '우리 교회에서?'),
    ('d4', 139.5, '우리 공동체에서?'),
    ('d5', 143.0, '우리 시대와 세계에서?'),
    ('d6', 148.0, '우리 시대의 95개조'),
    ('d7', 152.5, '오늘 우리가 다시 붙여야 할 한 문장은 무엇입니까?'),
    ('f1', 165.0, '믿는 것을 고백하고'),
    ('f2', 169.0, '고백한 것을 실천하고'),
    ('f3', 173.0, '실천한 것이 우리를 형성하며'),
    ('f4', 177.5, '형성된 삶을 다음 세대에 전수한다.'),
    ('e1', 209.5, '개혁은 아직 끝나지 않았습니다.'),
    ('e2', 214.0, '성령께서 오늘도 교회를 다시 형성하고 계십니다.'),
    ('e3', 222.5, '고백에서 삶으로.|교회에서 가정으로.|우리에게서 다음 세대로.'),
    ('p', 231.0, '주여, 우리를 다시 개혁하소서.'),
]
KNOCKS = [31.0, 34.0, 36.0, 55.5, 62.5, 71.0, 79.8, 88.2, 200.5]  # 망치 (마지막은 엔딩)
DOOR_OPEN = 201.6


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def fft_filter(x, lo=None, hi=None, order=2):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if hi: g *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    if lo: g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(X * g, len(x))


def seg(a, b, att=1.0, rel=1.0):
    return np.clip((t - a) / att, 0, 1) * np.clip((b - t) / rel, 0, 1)


def place(dst, sig, start, pan=0.0):
    i = int(start * SR)
    j = min(dst.shape[0], i + len(sig))
    if i >= dst.shape[0]: return
    s = sig[:j - i]
    dst[i:j, 0] += s * np.sqrt(0.5 * (1 - pan))
    dst[i:j, 1] += s * np.sqrt(0.5 * (1 + pan))


def mono(x):
    return np.stack([x, x], axis=1) * np.sqrt(0.5)


# ---------- 내레이션 ----------
voice = np.zeros((N, 2))
active = np.zeros(N)
lines = []
for nid, start, text in NARR:
    if nid == 'p':  # 여러 세대의 한 목소리
        clips = [load(V / f'p{i}.mp3') for i in range(1, 5)]
        L = max(len(c) for c in clips)
        for i, (c, off, pan) in enumerate(zip(clips, (0, 0.05, 0.09, 0.03), (-0.3, 0.3, -0.1, 0.15))):
            place(voice, c * 0.62, start + off, pan)
        dur = L / SR + 0.1
    else:
        c = load(V / f'{nid}.mp3')
        place(voice, c, start)
        dur = len(c) / SR
    active[int(start * SR):int((start + dur) * SR)] = 1
    lines.append({'id': nid, 'start': start, 'end': round(start + dur, 3), 'text': text})

# ---------- 효과음 ----------
sfx = np.zeros((N, 2))

# 혼란: 여러 언어의 웅성거림 (내레이션 클립을 겹쳐 흐릿하게)
babble = np.zeros((N, 2))
for fn, st, pan, g in [('b_en', 2.0, -0.6, 0.5), ('b_fr', 4.4, 0.6, 0.45), ('b_ko1', 6.0, -0.2, 0.5), ('b_pt', 7.8, 0.4, 0.45),
                       ('b_ko2', 9.4, 0.7, 0.4), ('b_it', 10.6, -0.7, 0.45), ('b_ko3', 12.2, 0.1, 0.45), ('b_en', 13.8, 0.5, 0.3),
                       ('b_ko1', 15.4, -0.5, 0.28), ('b_fr', 17.6, 0.3, 0.25), ('b_pt', 20.5, -0.4, 0.22), ('b_ko3', 22.8, 0.6, 0.2)]:
    place(babble, load(V / f'{fn}.mp3') * g, st, pan)
for ch in range(2):
    babble[:, ch] = fft_filter(babble[:, ch], lo=180, hi=4200)
# 군중 소음 & 거리 소리
crowd = fft_filter(rng.standard_normal(N), lo=250, hi=2500)
crowd *= 1 + 0.6 * fft_filter(rng.standard_normal(N), hi=4)
crowd /= np.abs(crowd).max()
street = fft_filter(rng.standard_normal(N), hi=220)
street /= np.abs(street).max()
chaos_env = np.clip((t - 0.8) / 6, 0, 1) * np.clip((29.6 - t) / 0.08, 0, 1) * np.interp(t, [0, 12, 14, 27, 30], [1, 1, 0.75, 0.6, 0.6])
sfx += babble * chaos_env[:, None]
sfx += mono((crowd * 0.07 + street * 0.12) * chaos_env)
for st in (5.5, 12.8, 21.0):  # 지나가는 차
    n = int(3 * SR); tt = np.arange(n) / SR
    car = fft_filter(rng.standard_normal(n), lo=80, hi=900) * np.sin(np.pi * tt / 3) ** 2
    pan = np.linspace(-0.8, 0.8, n)
    seg_ = car / np.abs(car).max() * 0.08
    i = int(st * SR); sfx[i:i + n, 0] += seg_ * np.sqrt(0.5 * (1 - pan)); sfx[i:i + n, 1] += seg_ * np.sqrt(0.5 * (1 + pan))


# 망치: 오래된 나무 문을 치는 건조한 소리 (모달 합성)
def knock(amp=1.0):
    n = int(0.6 * SR); tt = np.arange(n) / SR
    modes = [(120, 0.09, 1.0), (205, 0.07, 0.8), (390, 0.05, 0.55), (640, 0.035, 0.4), (1020, 0.022, 0.25), (1730, 0.012, 0.15)]
    s = sum(a * np.sin(2 * np.pi * f * tt + rng.random() * 6) * np.exp(-tt / d) for f, d, a in modes)
    click = fft_filter(rng.standard_normal(n), lo=600, hi=6000) * np.exp(-tt / 0.004)
    thud = np.sin(2 * np.pi * (70 - 20 * tt) * tt) * np.exp(-tt / 0.05)
    out = s * 0.5 + click * 0.6 + thud * 0.6
    # 짧은 공간 울림 (예배당 느낌의 약한 잔향)
    rev = np.zeros(n)
    for dl, g in ((0.031, 0.28), (0.047, 0.22), (0.073, 0.16), (0.109, 0.1)):
        k = int(dl * SR); rev[k:] += out[:n - k] * g
    return (out + rev) / np.abs(out + rev).max() * amp

for i, st in enumerate(KNOCKS):
    place(sfx, knock(0.95 if i < 3 or i == len(KNOCKS) - 1 else 0.7), st)

# 문 열리는 소리 (삐걱임 + 나무 울림)
n = int(5.0 * SR); tt = np.arange(n) / SR
f = 420 + 160 * np.sin(2 * np.pi * 0.35 * tt) + 40 * fft_filter(rng.standard_normal(n), hi=12) / 0.05
f = np.clip(f, 250, 900)
creak = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (0.5 + 0.5 * np.abs(fft_filter(rng.standard_normal(n), hi=30)) * 8)
creak = fft_filter(creak, lo=300, hi=2500) * np.sin(np.pi * np.clip(tt / 4.5, 0, 1)) ** 1.5
groan = fft_filter(rng.standard_normal(n), lo=40, hi=200) * np.exp(-tt / 2)
door = creak / np.abs(creak).max() * 0.12 + groan / np.abs(groan).max() * 0.12
place(sfx, door, DOOR_OPEN)
# 긴 호흡 + 빛 (문 너머)
n = int(4 * SR); tt = np.arange(n) / SR
breath = fft_filter(rng.standard_normal(n), lo=300, hi=3000) * np.sin(np.pi * tt / 4) ** 2
place(sfx, breath / np.abs(breath).max() * 0.06, 203.5)

# ---------- 음악 ----------
music = np.zeros(N)


def pad(freq, a, b, amp, att=2.5, rel=3.0, harm=6, det=0.003):
    e = seg(a, b, att, rel); idx = e > 0; tt = t[idx]; out = np.zeros(N)
    for d in (-det, 0, det):
        for h in range(1, harm + 1):
            out[idx] += np.sin(2 * np.pi * freq * (1 + d) * h * tt + h) / h ** 1.6
    return out * e * amp / 3


def piano(freq, start, amp, dur=3.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = np.zeros(n)
    for h in range(1, 9):
        fh = freq * h * np.sqrt(1 + 0.0004 * h * h)
        s += np.sin(2 * np.pi * fh * tt) * np.exp(-tt * (1.2 + h * 0.9)) / h ** 1.3
    s *= np.clip(tt / 0.004, 0, 1)
    i = int(start * SR); j = min(N, i + n)
    music[i:j] += s[:j - i] * amp


NOTE = {n: 440 * 2 ** ((i - 9) / 12) for i, n in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])}
def hz(name, octv): return NOTE[name] * 2 ** (octv - 4)

CH = {'D': [('D', 3), ('A', 3), ('D', 4), ('F#', 4)], 'Bm': [('B', 2), ('F#', 3), ('B', 3), ('D', 4)], 'G': [('G', 2), ('D', 3), ('G', 3), ('B', 3)],
      'A': [('A', 2), ('E', 3), ('A', 3), ('C#', 4)], 'Em': [('E', 3), ('B', 3), ('E', 4), ('G', 4)], 'Dsus': [('D', 3), ('A', 3), ('D', 4), ('E', 4)]}


def progression(seq, start, bar, amp, arp=None, arp_amp=0.0, arp_div=4):
    x = start
    for c in seq:
        for fn, o in CH[c]:
            music[:] += pad(hz(fn, o), x - 0.3, x + bar + 0.6, amp, att=1.5, rel=1.8)
        if arp:
            notes = [hz(fn, o + 1) for fn, o in CH[c]]
            for k in range(arp_div):
                piano(notes[arp[k % len(arp)]], x + k * bar / arp_div, arp_amp)
        x += bar
    return x

# 0–30 혼란: 불안정한 저음 클러스터
for f0 in (hz('D', 2), hz('D#', 2), hz('A', 2)):
    music += pad(f0, 1.0, 29.6, 0.035, att=8, rel=0.05)
# 30–55 침묵 (망치만)
# 55–100 고백: 약한 리듬 + 따뜻한 화성
progression(['D', 'Bm', 'G', 'A'] * 3, 55.5, 3.75, 0.03, arp=[0, 2, 1, 3], arp_amp=0.035)
for k in range(int((100 - 56) / 1.0)):  # 부드러운 맥박
    st = 56 + k * 1.0
    n = int(0.3 * SR); tt = np.arange(n) / SR
    i = int(st * SR); music[i:i + n] += np.sin(2 * np.pi * 55 * tt) * np.exp(-tt / 0.08) * 0.05 * (1 if k % 2 == 0 else 0.5)
# 100–128 개혁: 현재적인 질감 (8분음 펠트 피아노)
progression(['Bm', 'G', 'D', 'A', 'Bm', 'G', 'D', 'A'], 100.5, 3.5, 0.032, arp=[0, 1, 2, 3, 2, 1, 2, 3], arp_amp=0.04, arp_div=8)
# 128–162 분별: 낮게, 질문 사이 여백
music += pad(hz('D', 3), 127.5, 162.5, 0.03, att=3, rel=3) + pad(hz('A', 3), 127.5, 162.5, 0.02, att=3, rel=3)
for st, nm in ((130.9, ('F#', 5)), (134.2, ('E', 5)), (137.4, ('D', 5)), (141.4, ('B', 4)), (145.2, ('A', 4)), (151.0, ('D', 5)), (157.5, ('A', 4))):
    piano(hz(*nm), st, 0.05, 4)
# 162–198 형성: 따뜻하고 넓게
progression(['D', 'A', 'Bm', 'G', 'D', 'A', 'G', 'A', 'D'], 162.0, 4.0, 0.034, arp=[0, 2, 3, 2, 1, 2, 3, 2], arp_amp=0.04, arp_div=8)
# 198–207 정적 → 문
music += pad(hz('D', 3), 198, 207.5, 0.018, att=1, rel=2)
# 207–238 엔딩: 넓은 D장조, 폭발 없이
progression(['Dsus', 'D', 'G', 'D', 'Bm', 'G', 'A', 'D'], 207.0, 3.8, 0.034, arp=[0, 2, 3, 2], arp_amp=0.03, arp_div=4)
shim = sum(np.sin(2 * np.pi * hz(n, o) * t) for n, o in (('D', 6), ('A', 6), ('F#', 6))) * seg(204, 238, 4, 6) * 0.006
music += shim
music = fft_filter(music, hi=6000)

# ---------- 믹스 ----------
k = int(0.35 * SR)
duck = np.convolve(active, np.ones(k) / k, mode='same')
bed_m = music * (1 - 0.55 * duck)
mix = voice * 1.25 + mono(bed_m) * 1.6 + sfx * (1 - 0.35 * duck)[:, None]
mix = np.tanh(mix * 1.05) / np.tanh(1.05)
mix *= 0.89 / np.abs(mix).max()
mix *= np.clip((DUR - 1.0 - t) / 2.5, 0, 1)[:, None]  # 마지막 검은 화면은 무음
pcm = (mix * 32767).astype('<i2').tobytes()
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', str(HERE / 'audio.wav')], input=pcm, check=True)

m = active > 0
vr = 20 * np.log10(np.sqrt(np.mean((voice[m] * 1.25) ** 2)))
br = 20 * np.log10(np.sqrt(np.mean((mono(bed_m)[m] * 1.6 + sfx[m] * 0.65) ** 2)))
print(f'voice {vr:.1f} dB / bed under voice {br:.1f} dB')

(HERE / 'timeline.js').write_text('window.TL = ' + json.dumps({'dur': DUR, 'lines': lines, 'knocks': KNOCKS, 'doorOpen': DOOR_OPEN}, ensure_ascii=False) + ';\n', encoding='utf-8')


def ts(s):
    ms = int(round(s * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'

srt = []
for i, l in enumerate(lines, 1):
    srt.append(f"{i}\n{ts(l['start'])} --> {ts(l['end'] + 0.3)}\n{l['text'].replace('|', chr(10))}\n")
(HERE / 'subtitles.srt').write_text('\n'.join(srt), encoding='utf-8')
print('ok')
