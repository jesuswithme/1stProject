"""2026 종교개혁주일 오프닝 영상 (v2, 3:30) 오디오
내레이션 배치 + 합성 음악/효과음(긴장감·개혁의 분위기) → audio.wav, timeline.js, subtitles.srt"""
import json
import subprocess
from pathlib import Path

import numpy as np

SR = 44100
DUR = 210.0
HERE = Path(__file__).parent
V = HERE / 'voice'
rng = np.random.default_rng(1517)
N = int(SR * DUR)
t = np.arange(N) / SR

# ---------- 구간과 내레이션 ----------
SEC = {'knock': 21.5, 'confess': 39.5, 'reform': 81.5, 'discern': 106.0, 'form': 132.0, 'end': 161.0}
NARR = [
    ('c1', 9.0, '세상은 빠르게 변하고 있습니다.'),
    ('c2', 12.6, '교회는 무엇을 붙들어야 합니까?'),
    ('c3', 16.0, '무엇은 다시 개혁되어야 합니까?'),
    ('k1', 26.7, '1517'),
    ('k2', 29.0, '한 사람이 문을 두드렸다.'),
    ('k3', 32.3, '교회를 무너뜨리기 위해서가 아니라'),
    ('k4', 35.6, '교회를 깨우기 위해서였다.'),
    ('s1', 40.4, 'SOLA GRATIA|오직 은혜|우리는 성취가 아니라 은혜로 살아간다.'),
    ('s2', 46.8, 'SOLA FIDE|오직 믿음|우리는 힘이 아니라 하나님을 신뢰한다.'),
    ('s3', 54.6, 'SOLA SCRIPTURA|오직 성경|수많은 목소리 가운데 말씀을 다시 듣는다.'),
    ('s4', 62.8, 'SOLUS CHRISTUS|오직 그리스도|우리의 중심에는 그리스도가 계신다.'),
    ('s5', 70.5, 'SOLI DEO GLORIA|오직 하나님께 영광|우리의 이름이 아니라 하나님의 영광을 구한다.'),
    ('r1', 85.5, '그러나 종교개혁은 1517년에 끝났을까요?'),
    ('r2', 90.0, '아닙니다.'),
    ('r3', 91.8, 'ECCLESIA REFORMATA, SEMPER REFORMANDA'),
    ('r4', 96.8, '개혁된 교회는 계속 개혁되어야 한다.'),
    ('d1', 107.0, '나의 삶에서?'),
    ('d2', 109.6, '우리 가정에서?'),
    ('d3', 112.0, '우리 교회에서?'),
    ('d4', 114.4, '우리 공동체에서?'),
    ('d5', 117.0, '우리 시대와 세계에서?'),
    ('d6', 120.5, '우리 시대의 95개조'),
    ('d7', 124.2, '오늘 우리가 다시 붙여야 할 한 문장은 무엇입니까?'),
    ('f1', 133.0, '믿는 것을 고백하고'),
    ('f2', 136.0, '고백한 것을 실천하고'),
    ('f3', 139.2, '실천한 것이 우리를 형성하며'),
    ('f4', 143.0, '형성된 삶을 다음 세대에 전수한다.'),
    ('e1', 171.0, '개혁은 아직 끝나지 않았습니다.'),
    ('e2', 175.0, '성령께서 오늘도 교회를 다시 형성하고 계십니다.'),
    ('e3', 183.0, '고백에서 삶으로.|교회에서 가정으로.|우리에게서 다음 세대로.'),
    ('p', 192.6, '주여, 우리를 다시 개혁하소서.'),
]
KNOCKS = [22.5, 24.5, 26.0, 40.0, 46.4, 54.2, 62.4, 70.1, 163.0]
HITS = [21.0, 26.0, 85.0, 90.0, 107.0, 120.5, 163.0, 168.0]  # 큰 임팩트 (화면 플래시와 맞춤)
DOOR_OPEN = 164.0
BELLS = [85.0, 168.0, 196.5]


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def filt(x, lo=None, hi=None, order=2):
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
    if i >= dst.shape[0]: return
    j = min(dst.shape[0], i + len(sig))
    s = sig[:j - i]
    if dst.ndim == 1 or s.ndim == 2:
        dst[i:j] += s
    else:
        dst[i:j, 0] += s * np.sqrt(0.5 * (1 - pan)); dst[i:j, 1] += s * np.sqrt(0.5 * (1 + pan))


def mono(x): return np.stack([x, x], axis=1) * np.sqrt(0.5)
def norm(x): return x / (np.abs(x).max() + 1e-9)


def reverb(x, sec=2.2, mix=0.3):
    """간단한 잔향 (지수 감쇠 노이즈와 FFT 합성곱)"""
    n = int(sec * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt / (sec / 5)); ir = filt(ir, hi=5000); ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[:len(x)]
    return x * (1 - mix) + y * mix


# ---------- 내레이션 ----------
voice = np.zeros((N, 2))
active = np.zeros(N)
lines = []
for nid, start, text in NARR:
    if nid == 'p':
        clips = [load(V / f'p{i}.mp3') for i in range(1, 5)]
        for c, off, pan in zip(clips, (0, 0.05, 0.09, 0.03), (-0.3, 0.3, -0.1, 0.15)):
            place(voice, c * 0.62, start + off, pan)
        dur = max(len(c) for c in clips) / SR + 0.1
    else:
        c = load(V / f'{nid}.mp3'); place(voice, c, start); dur = len(c) / SR
    active[int(start * SR):int((start + dur) * SR)] = 1
    lines.append({'id': nid, 'start': start, 'end': round(start + dur, 3), 'text': text})

music = np.zeros(N)
sfx = np.zeros((N, 2))

# ---------- 악기 ----------
NOTE = {n: 440 * 2 ** ((i - 9) / 12) for i, n in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])}
def hz(name, o): return NOTE[name] * 2 ** (o - 4)


def pad(freq, a, b, amp, att=2.0, rel=2.5, harm=6, det=0.003):
    e = seg(a, b, att, rel); idx = e > 0; tt = t[idx]; out = np.zeros(N)
    for d in (-det, 0, det):
        for h in range(1, harm + 1):
            out[idx] += np.sin(2 * np.pi * freq * (1 + d) * h * tt + h) / h ** 1.6
    return out * e * amp / 3


def choir(freq, a, b, amp, att=2.5, rel=2.5, vowel='ah'):
    """포먼트 합성 합창 ('아' 모음)"""
    F = {'ah': [(800, 80, 1.0), (1150, 90, 0.5), (2900, 120, 0.25)], 'oh': [(450, 70, 1.0), (800, 80, 0.4), (2830, 100, 0.15)]}[vowel]
    e = seg(a, b, att, rel); idx = e > 0; tt = t[idx]; out = np.zeros(N)
    for v in range(4):
        vib = 1 + 0.005 * np.sin(2 * np.pi * (5 + v * 0.3) * tt + v) + (v - 1.5) * 0.003
        ph = 2 * np.pi * freq * np.cumsum(vib) / SR
        for h in range(1, int(4000 / freq)):
            fh = freq * h
            g = sum(amp_ * np.exp(-((fh - fc) / bw) ** 2 / 2) for fc, bw, amp_ in F) + 0.02
            out[idx] += np.sin(h * ph) * g / np.sqrt(h)
    return out * e * amp / 4


def piano(freq, start, amp, dur=3.0):
    n = int(dur * SR); tt = np.arange(n) / SR; s = np.zeros(n)
    for h in range(1, 9):
        s += np.sin(2 * np.pi * freq * h * np.sqrt(1 + 0.0004 * h * h) * tt) * np.exp(-tt * (1.2 + h * 0.9)) / h ** 1.3
    place(music, s * np.clip(tt / 0.004, 0, 1) * amp, start)


def string_stab(freq, start, amp, dur=0.22):
    """스타카토 현 (긴장감 오스티나토)"""
    n = int(dur * SR); tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * freq * h * (1 + 0.002 * (h % 3 - 1)) * tt) / h for h in range(1, 10))
    env = np.clip(tt / 0.01, 0, 1) * np.exp(-tt / (dur * 0.45))
    place(music, filt(s * env, hi=3500) * amp, start)


def drum(start, amp, f0=60, dec=0.45):
    """팀파니/북 (낮고 묵직한 타격)"""
    n = int(1.5 * SR); tt = np.arange(n) / SR
    f = f0 * (1 + 0.6 * np.exp(-tt / 0.03))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / dec)
    s += filt(rng.standard_normal(n), lo=60, hi=900) * np.exp(-tt / 0.03) * 0.5
    place(music, s * amp, start)


def boom(start, amp):
    n = int(3.0 * SR); tt = np.arange(n) / SR
    f = 28 + 55 * np.exp(-tt / 0.18)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.9)
    s += filt(rng.standard_normal(n), hi=400) * np.exp(-tt / 0.12) * 0.5
    place(music, s * amp, start)


def riser(a, b, amp):
    e = np.clip((t - a) / (b - a), 0, 1) * (t < b)
    noise = filt(rng.standard_normal(N), lo=600, hi=9000)
    music[:] += norm(noise) * e ** 2.5 * amp
    music[:] += np.sin(2 * np.pi * np.cumsum(np.interp(t, [a, b], [180, 1400])) / SR) * e ** 2 * amp * 0.35


def bell(start, amp, f=hz('D', 3)):
    n = int(7 * SR); tt = np.arange(n) / SR
    partials = [(0.5, 1.0, 4.0), (1, 0.8, 3.0), (1.19, 0.5, 2.0), (1.5, 0.45, 1.8), (2.0, 0.35, 1.4), (2.52, 0.25, 1.0), (3.0, 0.18, 0.8), (4.07, 0.1, 0.5)]
    s = sum(a * np.sin(2 * np.pi * f * 2 * r * tt) * np.exp(-tt / d) for r, a, d in partials)
    place(sfx, reverb(s * np.clip(tt / 0.002, 0, 1), 3.0, 0.35) * amp, start)


def press_clack(start, amp):
    """인쇄기 기계음"""
    n = int(0.25 * SR); tt = np.arange(n) / SR
    s = filt(rng.standard_normal(n), lo=1200, hi=7000) * np.exp(-tt / 0.012) + np.sin(2 * np.pi * 140 * tt) * np.exp(-tt / 0.04) * 0.8
    place(sfx, s * amp, start, pan=rng.uniform(-0.4, 0.4))


def tick(start, amp):
    n = int(0.04 * SR); tt = np.arange(n) / SR
    place(sfx, filt(rng.standard_normal(n), lo=2500, hi=8000) * np.exp(-tt / 0.004) * amp, start, pan=0.2)


def heartbeat(start, amp):
    for off, a in ((0, 1.0), (0.22, 0.7)):
        n = int(0.25 * SR); tt = np.arange(n) / SR
        place(music, np.sin(2 * np.pi * (58 - 22 * tt / 0.25) * tt) * np.exp(-tt / 0.07) * amp * a, start + off)


def knock(amp=1.0):
    """오래된 나무 문을 치는 망치 소리 + 예배당 잔향"""
    n = int(2.5 * SR); tt = np.arange(n) / SR
    modes = [(120, 0.09, 1.0), (205, 0.07, 0.8), (390, 0.05, 0.55), (640, 0.035, 0.4), (1020, 0.022, 0.25), (1730, 0.012, 0.15)]
    s = sum(a * np.sin(2 * np.pi * f * tt + rng.random() * 6) * np.exp(-tt / d) for f, d, a in modes)
    click = filt(rng.standard_normal(n), lo=600, hi=6000) * np.exp(-tt / 0.004)
    thud = np.sin(2 * np.pi * (62 - 18 * tt) * tt) * np.exp(-tt / 0.09)
    out = s * 0.5 + click * 0.6 + thud * 0.9
    return norm(reverb(out, 2.4, 0.32)) * amp


# ---------- 0–21 혼란: 웅성거림 + 시계 + 오스티나토 → 하드 컷 ----------
babble = np.zeros((N, 2))
for fn, st, pan, g in [('b_en', 0.8, -0.6, 0.5), ('b_fr', 2.2, 0.6, 0.45), ('b_ko1', 3.2, -0.2, 0.5), ('b_pt', 4.4, 0.4, 0.45),
                       ('b_ko2', 5.4, 0.7, 0.4), ('b_it', 6.2, -0.7, 0.45), ('b_ko3', 7.0, 0.1, 0.45), ('b_en', 8.4, 0.5, 0.3),
                       ('b_ko1', 10.0, -0.5, 0.3), ('b_fr', 11.6, 0.3, 0.28), ('b_pt', 13.4, -0.4, 0.28), ('b_ko3', 15.0, 0.6, 0.25), ('b_it', 17.0, -0.3, 0.28), ('b_ko2', 18.6, 0.2, 0.3)]:
    place(babble, load(V / f'{fn}.mp3') * g, st, pan)
for ch in range(2): babble[:, ch] = filt(babble[:, ch], lo=180, hi=4200)
crowd = norm(filt(rng.standard_normal(N), lo=250, hi=2500) * (1 + 0.6 * filt(rng.standard_normal(N), hi=4)))
street = norm(filt(rng.standard_normal(N), hi=220))
chaos = np.clip(t / 2.0, 0, 1) * (t < 21.0) * np.interp(t, [0, 8, 9, 19, 21], [0.8, 1, 0.7, 0.9, 1.1])
sfx += babble * chaos[:, None] + mono((crowd * 0.08 + street * 0.12) * chaos)
x = 0.5
while x < 20.9:  # 빨라지는 초침
    tick(x, 0.25 + 0.2 * x / 21); x += np.interp(x, [0, 21], [0.75, 0.16])
for k in range(int(20.9 / 0.125)):  # 16분음 저음 맥박 (점점 커짐)
    st = 4.0 + k * 0.125
    if st > 20.9: break
    string_stab(hz('D', 2) if (k // 8) % 4 != 3 else hz('D#', 2), st, 0.045 * np.interp(st, [4, 21], [0.3, 1.0]), 0.12)
music += pad(hz('D', 2), 0.5, 21.0, 0.05, att=6, rel=0.02) + pad(hz('D#', 2), 6, 21.0, 0.04, att=6, rel=0.02) + pad(hz('A', 2), 10, 21.0, 0.035, att=5, rel=0.02)
riser(17.5, 21.0, 0.06)
boom(21.0, 0.0)  # 하드 컷 직후 정적

# ---------- 21.5–39.5 망치: 정적 속의 세 번 ----------
music += pad(hz('D', 1) * 2, 22.4, 39.8, 0.035, att=4, rel=2)  # 낮은 저음 깔림
for st, a in ((22.5, 0.5), (24.5, 0.6), (26.0, 0.9)):
    boom(st, a * 0.7)
choir_ = choir(hz('D', 3), 26.2, 39.5, 0.02, att=3, rel=2, vowel='oh') + choir(hz('A', 3), 26.2, 39.5, 0.015, att=3, rel=2, vowel='oh')
music += choir_
for k in range(14):  # 낮은 북 맥박 (k3~k4)
    drum(31.8 + k * 0.55, 0.08 + 0.01 * k, f0=55)
riser(37.4, 40.0, 0.05)

# ---------- 39.5–81.5 다섯 고백: 북 + 합창 + 현 오스티나토, 점점 고조 ----------
prog_ = [('D', 'Bm', 'G', 'A'), ('Bm', 'G', 'D', 'A'), ('D', 'Bm', 'G', 'A'), ('G', 'A', 'Bm', 'A'), ('G', 'A', 'D', 'D')]
CH = {'D': [('D', 3), ('A', 3), ('F#', 4)], 'Bm': [('B', 2), ('F#', 3), ('D', 4)], 'G': [('G', 2), ('D', 3), ('B', 3)], 'A': [('A', 2), ('E', 3), ('C#', 4)], 'Em': [('E', 3), ('B', 3), ('G', 4)]}
sola_starts = KNOCKS[3:8] + [81.0]
for i in range(5):
    a, b = sola_starts[i], sola_starts[i + 1]
    bar = (b - a) / 4
    inten = 0.6 + 0.1 * i
    for j, c in enumerate(prog_[i]):
        x0 = a + j * bar
        for nm, o in CH[c]:
            music += pad(hz(nm, o), x0 - 0.1, x0 + bar + 0.4, 0.028 * inten, att=0.6, rel=0.8)
        music += choir(hz(CH[c][0][0], CH[c][0][1] + 1), x0, x0 + bar + 0.3, 0.012 * inten, att=0.6, rel=0.6)
        root = hz(CH[c][0][0], 2)
        k = 0; y = x0
        while y < x0 + bar - 0.01:  # 8분음 현 스타카토
            string_stab(root * (2 if k % 4 == 2 else 1), y, 0.05 * inten, 0.18); y += bar / 8; k += 1
    for k in range(int((b - a) / 0.5)):  # 북
        drum(a + k * 0.5, (0.12 if k % 2 == 0 else 0.06) * inten, f0=52)
    boom(a, 0.45)
riser(78.5, 81.5, 0.07)

# ---------- 81.5–106 개혁: 인쇄기 + 종 + 합창, "아닙니다" 직전 정적 ----------
for k in range(int((85.0 - 81.6) / 0.17)):
    press_clack(81.6 + k * 0.17, 0.18 + 0.12 * k / 20)
bell(85.0, 0.5)
boom(85.0, 0.6)
for nm, o in (('B', 2), ('F#', 3), ('D', 4)):
    music += pad(hz(nm, o), 85.0, 89.3, 0.03, att=0.3, rel=0.2)
music += choir(hz('B', 3), 85.0, 89.3, 0.02, att=0.5, rel=0.2) + choir(hz('F#', 4), 85.0, 89.3, 0.012, att=0.5, rel=0.2)
heartbeat(86.0, 0.18); heartbeat(87.0, 0.2); heartbeat(88.0, 0.24)
boom(90.0, 0.7); drum(90.0, 0.3, f0=45)
# 표어: 장엄한 D장조 합창
for nm, o in (('D', 3), ('A', 3), ('F#', 4)):
    music += pad(hz(nm, o), 91.4, 106.0, 0.032, att=1.2, rel=2.5)
music += choir(hz('D', 4), 91.4, 106.0, 0.022, att=1.5, rel=2.5) + choir(hz('A', 3), 91.4, 106.0, 0.018, att=1.5, rel=2.5) + choir(hz('F#', 4), 96.5, 106.0, 0.012, att=1.5, rel=2.5)
for k in range(int((105.5 - 91.6) / 0.5)):
    drum(91.6 + k * 0.5, 0.09 if k % 2 == 0 else 0.045, f0=52)
    string_stab(hz('D', 2), 91.6 + k * 0.5, 0.04); string_stab(hz('D', 2), 91.85 + k * 0.5, 0.025)

# ---------- 106–132 분별: 긴장된 저음 + 질문마다 역방향 스웰과 타격 ----------
music += pad(hz('D', 2), 105.8, 131.5, 0.04, att=2, rel=3) + pad(hz('A', 2), 108, 131.5, 0.025, att=3, rel=3)
for nid in ('d1', 'd2', 'd3', 'd4', 'd5', 'd6'):
    st = dict((n, s) for n, s, _ in NARR)[nid]
    n = int(0.9 * SR); tt = np.arange(n) / SR
    swell = filt(rng.standard_normal(n), lo=400, hi=5000) * (tt / 0.9) ** 3
    place(music, swell * 0.05, st - 0.9)
    drum(st, 0.25, f0=48, dec=0.6)
x = 106.0
while x < 131:
    heartbeat(x, 0.1); x += 60 / 66
for st, nm in ((124.0, ('D', 5)), (126.5, ('A', 4)), (128.6, ('F#', 4))):
    piano(hz(*nm), st, 0.05, 4)

# ---------- 132–161 형성: 따뜻하고 힘있게 (피아노 오스티나토 + 합창 + 북) ----------
form_seq = ['D', 'A', 'Bm', 'G', 'D', 'A', 'G', 'A']
bar = 3.6
for j, c in enumerate(form_seq):
    x0 = 132.0 + j * bar
    for nm, o in CH[c]:
        music += pad(hz(nm, o), x0 - 0.2, x0 + bar + 0.4, 0.03, att=1.0, rel=1.2)
    notes = [hz(nm, o + 1) for nm, o in CH[c]]
    for k in range(8):
        piano(notes[[0, 1, 2, 1, 0, 2, 1, 2][k]], x0 + k * bar / 8, 0.04)
    if j >= 3:
        music += choir(hz(CH[c][0][0], CH[c][0][1] + 1), x0, x0 + bar + 0.3, 0.014, att=0.8, rel=0.8)
        for k in range(4): drum(x0 + k * bar / 4, 0.07 if k % 2 == 0 else 0.04, f0=55)
for nm, o in (('D', 3), ('A', 3), ('F#', 4)):
    music += pad(hz(nm, o), 160.6, 162.6, 0.03, att=0.5, rel=1.0)
riser(158.6, 163.0, 0.07)

# ---------- 161–210 엔딩: 마지막 망치 → 문이 열림(종·합창) → 고요한 마무리 ----------
boom(163.0, 0.8)
n = int(5.0 * SR); tt = np.arange(n) / SR
f = np.clip(420 + 160 * np.sin(2 * np.pi * 0.35 * tt) + 40 * filt(rng.standard_normal(n), hi=12) / 0.05, 250, 900)
creak = filt(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), lo=300, hi=2500) * np.sin(np.pi * np.clip(tt / 4.5, 0, 1)) ** 1.5
place(sfx, mono(norm(creak) * 0.1 + norm(filt(rng.standard_normal(n), lo=40, hi=200)) * np.exp(-tt / 2) * 0.12), DOOR_OPEN)
riser(165.0, 168.0, 0.06)
bell(168.0, 0.55); boom(168.0, 0.5)
for nm, o in (('D', 3), ('A', 3), ('D', 4), ('F#', 4)):
    music += pad(hz(nm, o), 168.0, 182.0, 0.03, att=0.4, rel=4)
music += choir(hz('D', 4), 168.0, 181.0, 0.022, att=0.5, rel=4) + choir(hz('A', 4), 168.0, 181.0, 0.014, att=0.5, rel=4) + choir(hz('F#', 4), 168.0, 181.0, 0.012, att=0.5, rel=4)
end_seq = ['G', 'D', 'Bm', 'G', 'A', 'D']
for j, c in enumerate(end_seq):
    x0 = 179.0 + j * 3.6
    for nm, o in CH[c]:
        music += pad(hz(nm, o), x0 - 0.3, x0 + 3.6 + 0.6, 0.028, att=1.2, rel=1.6)
    notes = [hz(nm, o + 1) for nm, o in CH[c]]
    for k in range(4): piano(notes[k % 3], x0 + k * 0.9, 0.035)
music += pad(hz('D', 3), 200.0, 207.0, 0.03, att=1, rel=4) + pad(hz('A', 3), 200.0, 207.0, 0.02, att=1, rel=4)
bell(196.5, 0.32)
music += sum(np.sin(2 * np.pi * hz(nm, o) * t) for nm, o in (('D', 6), ('A', 6), ('F#', 6))) * seg(166, 205, 3, 5) * 0.005

for k in KNOCKS:
    place(sfx, mono(knock(0.95 if k in (22.5, 24.5, 26.0, 163.0) else 0.8)), k)

music = filt(music, hi=7000)

# ---------- 믹스 ----------
k = int(0.35 * SR)
duck = np.convolve(active, np.ones(k) / k, mode='same')
bed_m = music * (1 - 0.5 * duck)
mix = voice * 1.25 + mono(bed_m) * 1.5 + sfx * (1 - 0.3 * duck)[:, None]
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix *= 0.9 / np.abs(mix).max()
mix *= np.clip((DUR - 2.5 - t) / 3.0, 0, 1)[:, None]
pcm = (mix * 32767).astype('<i2').tobytes()
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', str(HERE / 'audio.wav')], input=pcm, check=True)

m = active > 0
vr = 20 * np.log10(np.sqrt(np.mean((voice[m] * 1.25) ** 2)))
br = 20 * np.log10(np.sqrt(np.mean((mono(bed_m)[m] * 1.5 + sfx[m] * 0.7) ** 2)))
print(f'voice {vr:.1f} dB / bed under voice {br:.1f} dB')

(HERE / 'timeline.js').write_text('window.TL = ' + json.dumps({'dur': DUR, 'sec': SEC, 'lines': lines, 'knocks': KNOCKS, 'hits': HITS, 'bells': BELLS, 'doorOpen': DOOR_OPEN}, ensure_ascii=False) + ';\n', encoding='utf-8')


def ts(s):
    ms = int(round(s * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'

srt = [f"{i}\n{ts(l['start'])} --> {ts(l['end'] + 0.3)}\n{l['text'].replace('|', chr(10))}\n" for i, l in enumerate(lines, 1)]
(HERE / 'subtitles.srt').write_text('\n'.join(srt), encoding='utf-8')
print('ok')
