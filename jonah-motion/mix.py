"""요나 모션그래픽 오디오: 대사 배치 + 합성 BGM/효과음 + 더킹 → jonah_audio.wav, timeline.js"""
import json
import subprocess
from pathlib import Path

import numpy as np

SR = 44100
DUR = 40.0
HERE = Path(__file__).parent
rng = np.random.default_rng(7)
N = int(SR * DUR)
t = np.arange(N) / SR

# 대사 배치 (시작 시각, 파일, 화자, 자막)
LINES = [
    (3.0, '0_narr.mp3', 'narr', '욥바 항구. 요나가 다시스행 배를 바라본다.'),
    (8.2, '1_f.mp3', 'f', '요나님, 하나님께서 니느웨로 가라고 하셨다면서요?'),
    (12.0, '2_j.mp3', 'j', '그 악한 도시에 가서 말씀을 전하라고?|난 가고 싶지 않소.'),
    (17.3, '3_f.mp3', 'f', '그래서 반대 방향인 다시스로 가시려는 건가요?'),
    (20.8, '4_j.mp3', 'j', '그렇소. 지금은 그저… 멀리 떠나고 싶소.'),
    (25.8, '5_f.mp3', 'f', '하지만 바다 끝까지 가도|하나님을 피할 수는 없잖아요.'),
    (31.8, '6_j.mp3', 'j', '…배가 떠나는군. 난 가겠소.'),
]


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def lowpass(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (1 / np.sqrt(1 + (f / hi) ** 4)) * (1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4))
    return np.fft.irfft(X, len(x))


def seg_env(a, b, att=0.5, rel=0.5):
    """a~b 구간 사다리꼴 엔벨로프"""
    return np.clip((t - a) / att, 0, 1) * np.clip((b - t) / rel, 0, 1)


def place(dst, sig, start):
    i = int(start * SR)
    j = min(len(dst), i + len(sig))
    if i < len(dst):
        dst[i:j] += sig[:j - i]


# ---------- 대사 ----------
voice = np.zeros(N)
speaker = np.zeros(N, dtype=np.int8)  # 0 없음, 1 여, 2 요나, 3 나레이션
subs = []
for start, fn, who, text in LINES:
    v = load(HERE / 'voice' / fn)
    place(voice, v * (0.9 if who == 'narr' else 1.0), start)
    i0, i1 = int(start * SR), int(start * SR) + len(v)
    speaker[i0:i1] = {'f': 1, 'j': 2, 'narr': 3}[who]
    subs.append({'start': start, 'end': start + len(v) / SR + 0.25, 'who': who, 'text': text})

# ---------- 음악 ----------
def note(freq, a, b, amp, att=1.2, rel=1.5, harm=8, detune=0.004):
    """디튠된 톱니파 패드 음 (배음 제한으로 부드럽게)"""
    e = seg_env(a, b, att, rel)
    idx = e > 0
    out = np.zeros(N)
    tt = t[idx]
    for d in (-detune, 0, detune):
        f = freq * (1 + d)
        for h in range(1, harm + 1):
            out[idx] += np.sin(2 * np.pi * f * h * tt + h * 0.7) / h
    return out * e * amp / 3


A2, C3, E3, F2, A1, D3, F3, A3, Bb2, D2, E2, Gs2, B2, F3s = 110, 130.81, 164.81, 87.31, 55, 146.83, 174.61, 220, 116.54, 73.42, 82.41, 103.83, 123.47, 185
CHORDS = [  # (시작, 끝, 음들, 세기)
    (0.0, 8.4, [A1, A2, C3, E3], 0.05),
    (8.0, 12.4, [A1, A2, C3, E3], 0.06),
    (12.0, 15.6, [F2, A2, C3], 0.07),
    (15.2, 17.6, [Bb2 / 2, Bb2, D3, F3], 0.075),
    (17.2, 21.0, [D2, D3, F3, A3], 0.065),
    (20.6, 26.0, [A1, A2, C3, E3], 0.06),
    (25.6, 28.0, [Bb2 / 2, Bb2, D3, F3], 0.085),
    (27.6, 31.8, [E2, Gs2, B2, E3], 0.09),
    (31.6, 35.0, [A1, A2, C3, E3], 0.06),
    (34.6, 37.4, [F2, A2, C3], 0.07),
    (37.0, 40.0, [A1, A2, E3], 0.07),
]
music = np.zeros(N)
for a, b, notes, amp in CHORDS:
    for f in notes:
        music += note(f, a, b, amp)
music = lowpass(music, 1400)

# 저음 드론 + 트레몰로
drone = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 55.3 * t) + 0.3 * np.sin(2 * np.pi * 27.5 * t))
intensity = np.interp(t, [0, 8, 25, 29, 31.8, 34, 40], [0.5, 0.6, 0.8, 1.0, 0.5, 0.7, 0.4])
music += drone * 0.06 * intensity * (0.8 + 0.2 * np.sin(2 * np.pi * 0.25 * t))

# 스타카토 오스티나토 (8분음 → 클라이맥스에서 16분음)
def pluck(freq, start, amp, dec=0.12):
    n = int(0.35 * SR)
    tt = np.arange(n) / SR
    s = (np.sin(2 * np.pi * freq * tt) + 0.4 * np.sin(2 * np.pi * freq * 2 * tt) + 0.2 * np.sin(2 * np.pi * freq * 3 * tt))
    place(music, s * np.exp(-tt / dec) * amp, start)

beat = 60 / 100
pattern = [A2, A2, C3, A2, A2, Bb2, A2, Gs2]
k = 0
x = 12.0
while x < 29.5:
    step = beat / 2 if x < 25.8 else beat / 4
    amp = 0.05 if x < 25.8 else 0.07 + 0.04 * (x - 25.8) / 3.7
    pluck(pattern[k % len(pattern)], x, amp)
    x += step
    k += 1
x = 34.2
while x < 38.5:
    pluck(pattern[k % len(pattern)], x, 0.035 * (38.5 - x) / 4.3)
    x += beat / 2
    k += 1

# 심장 박동
def heartbeat(start, amp):
    for off, a in ((0, 1.0), (0.22, 0.7)):
        n = int(0.25 * SR)
        tt = np.arange(n) / SR
        s = np.sin(2 * np.pi * (60 - 25 * tt / 0.25) * tt) * np.exp(-tt / 0.07)
        place(music, s * amp * a, start + off)

for s0, s1, bpm, amp in ((0.3, 8.0, 66, 0.12), (25.8, 29.6, 84, 0.16), (29.6, 31.8, 92, 0.32), (34.0, 39.0, 70, 0.12)):
    x = s0
    while x < s1:
        heartbeat(x, amp)
        x += 60 / bpm

# 임팩트(쿵)
def boom(start, amp):
    n = int(2.0 * SR)
    tt = np.arange(n) / SR
    f = 30 + 60 * np.exp(-tt / 0.15)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.6)
    s += lowpass(rng.standard_normal(n), 300) * np.exp(-tt / 0.08) * 0.5
    place(music, s * amp, start)

for s0, amp in ((0.6, 0.55), (12.0, 0.35), (15.3, 0.3), (25.8, 0.35), (28.65, 0.6), (37.0, 0.5)):
    boom(s0, amp)

# 라이저 (27.4 → 28.65)
r = seg_env(27.4, 28.7, 1.2, 0.05)
music += bandpass(rng.standard_normal(N), 800, 6000) * r * 0.05 * np.clip((t - 27.4) / 1.25, 0, 1) ** 2
music += np.sin(2 * np.pi * np.cumsum(np.interp(t, [27.4, 28.65], [200, 900])) / SR) * r * 0.03

# ---------- 효과음 ----------
sfx = np.zeros(N)
# 파도: 저역 노이즈를 느린 주기로 변조
waves = lowpass(rng.standard_normal(N), 500)
waves /= np.abs(waves).max()
sfx += waves * (0.35 + 0.25 * np.sin(2 * np.pi * t / 6.5) ** 2) * np.interp(t, [0, 3, 8, 26, 30, 34, 40], [0.0, 0.5, 0.3, 0.45, 0.6, 0.55, 0.4]) * 0.35
# 바람
wind = bandpass(rng.standard_normal(N), 300, 1500)
wind /= np.abs(wind).max()
sfx += wind * (0.5 + 0.5 * np.sin(2 * np.pi * t / 9 + 1)) * np.interp(t, [0, 3, 25, 29, 40], [0, 0.12, 0.15, 0.3, 0.25])
# 빗소리 (25.8~)
rain = bandpass(rng.standard_normal(N), 3000, 12000)
rain /= np.abs(rain).max()
sfx += rain * seg_env(25.6, 40, 2.5, 2.0) * 0.06
# 천둥
for s0, amp, ln in ((0.6, 0.5, 3.5), (15.3, 0.25, 2.5), (28.65, 0.6, 4.0), (37.0, 0.55, 3.0)):
    n = int(ln * SR)
    tt = np.arange(n) / SR
    th = lowpass(rng.standard_normal(n), 180) * (np.exp(-tt / (ln * 0.3)) * (1 - np.exp(-tt / 0.05)))
    th *= 1 + 0.6 * np.sin(2 * np.pi * 3 * tt) ** 2
    place(sfx, th / np.abs(th).max() * amp, s0)
# 갈매기
for s0 in (3.6, 5.1, 6.4):
    n = int(0.45 * SR)
    tt = np.arange(n) / SR
    f = 1800 + 900 * np.sin(np.pi * tt / 0.45) - 600 * tt
    g = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.45) ** 2
    place(sfx, g * 0.05, s0)
# 뱃고동 (29.9~31.5)
hn = seg_env(29.9, 31.6, 0.25, 0.6)
vib = 1 + 0.004 * np.sin(2 * np.pi * 5 * t)
horn = sum(np.sin(2 * np.pi * 98 * h * vib * t) / h ** 1.2 for h in range(1, 10))
horn += 0.6 * sum(np.sin(2 * np.pi * 146.8 * h * vib * t) / h ** 1.2 for h in range(1, 7))
sfx += lowpass(horn * hn, 900) * 0.12

# ---------- 믹스 & 더킹 ----------
vact = (speaker > 0).astype(float)
k = int(0.25 * SR)
duck = np.convolve(vact, np.ones(k) / k, mode='same')
bed = (music + sfx) * (1 - 0.72 * duck)
mix = voice * 1.6 + bed
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix *= 0.89 / np.abs(mix).max()
# 끝 페이드
mix *= np.clip((DUR - t) / 1.5, 0, 1)
stereo = np.stack([mix, mix], axis=1)
pcm = (stereo * 32767).astype('<i2').tobytes()
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', str(HERE / 'jonah_audio.wav')], input=pcm, check=True)

# ---------- 화면용 타임라인 (30fps 음성 크기, 화자) ----------
FPS = 30
fr = int(DUR * FPS)
env, who = [], []
for i in range(fr):
    a, b = int(i / FPS * SR), int((i + 1) / FPS * SR)
    env.append(round(float(np.sqrt(np.mean(voice[a:b] ** 2))) * 6, 3))
    seg = speaker[a:b]
    who.append(int(np.bincount(seg, minlength=4)[1:].argmax() + 1) if seg.any() else 0)
(HERE / 'timeline.js').write_text('window.TL = ' + json.dumps({'dur': DUR, 'env': env, 'who': who, 'subs': subs}, ensure_ascii=False) + ';\n', encoding='utf-8')
m = speaker > 0
print("voice rms dB", 20*np.log10(np.sqrt(np.mean(voice[m]**2))), "bed under voice dB", 20*np.log10(np.sqrt(np.mean(bed[m]**2))), "bed elsewhere dB", 20*np.log10(np.sqrt(np.mean(bed[~m]**2))))
print("ok", DUR)
