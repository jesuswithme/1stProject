import json, subprocess, numpy as np
SR = 48000
D = json.load(open("tl.json")); TL = D["L"]; SFX = D["SFX"]; END = SFX["END"]
N = int(END * SR) + SR
rng = np.random.default_rng(7)

def load(fn, af=None, mono=False):
    cmd = ["ffmpeg", "-v", "0", "-i", fn]
    if af: cmd += ["-af", af]
    cmd += ["-f", "f32le", "-ac", "1" if mono else "2", "-ar", str(SR), "-"]
    x = np.frombuffer(subprocess.check_output(cmd), np.float32).copy()
    return x if mono else x.reshape(-1, 2)

def place(buf, x, t, g=1.0):
    i = int(t * SR)
    if x.ndim == 1: x = np.stack([x, x], 1)
    n = min(len(x), len(buf) - i)
    if n > 0: buf[i:i + n] += x[:n] * g

def fftconv(x, ir):
    n = len(x) + len(ir) - 1; m = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:n]

def bandpass(x, lo, hi):
    m = len(x); X = np.fft.rfft(x); f = np.fft.rfftfreq(m, 1 / SR)
    w = np.ones_like(f)
    if lo: w *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: w *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * w, m)

def ir(dur, decay, seed):
    r = np.random.default_rng(seed); t = np.arange(int(dur * SR)) / SR
    return r.standard_normal(len(t)) * np.exp(-t / decay)

def reverb(x, dur=1.6, decay=0.45, wet=0.3):
    out = np.zeros((len(x) + int(dur * SR), 2), np.float32)
    for c in range(2):
        h = ir(dur, decay, 10 + c); h = bandpass(h, 120, 5000); h /= np.sqrt((h ** 2).sum())
        src = x[:, c] if x.ndim == 2 else x
        out[:len(src), c] += src * (1 - wet)
        y = fftconv(src, h)[:len(out)]; out[:len(y), c] += y * wet
    return out

def env(n, a, r):
    e = np.ones(n); na = int(a * SR); nr = int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] = np.minimum(e[-nr:], np.linspace(1, 0, nr))
    return e

# ---------------- voice ----------------
voice = np.zeros((N, 2), np.float32); speech = np.zeros(N, np.float32)
for k, v in TL.items():
    if k == "p": continue
    a = load(f"tts/{k}.mp3")
    a *= 0.16 / np.sqrt(np.mean(a ** 2) + 1e-9)
    place(voice, a, v["t"]); i = int(v["t"] * SR); speech[i:i + len(a)] = 1
# light room on narration (subtle)
voice = reverb(voice, 1.2, 0.25, 0.10)[:N]

# prayer: several generations together, stretched to same length
pr = np.zeros((int(5 * SR), 2), np.float32)
srcs = [("tts/p1.mp3", -0.35), ("tts/p2.mp3", 0.3), ("tts/p3.mp3", 0.15), ("tts/p4.mp3", -0.1), ("amb/a7.mp3", 0.45)]
target = 3.0
for j, (fn, pan) in enumerate(srcs):
    d = float(subprocess.check_output(["ffprobe", "-v", "0", "-show_entries", "format=duration", "-of", "csv=p=0", fn]))
    a = load(fn, f"silenceremove=start_periods=1:start_threshold=-45dB,atempo={d/target:.4f}", mono=True)
    a *= 0.12 / np.sqrt(np.mean(a ** 2) + 1e-9)
    st = np.stack([a * (1 - pan) ** .5, a * (1 + pan) ** .5], 1) / 1.2
    o = int((0.03 * j) * SR); pr[o:o + len(st)] += st[:len(pr) - o]
pr = reverb(pr, 2.4, 0.6, 0.35)
place(voice, pr, TL["p"]["t"], 1.15); i = int(TL["p"]["t"] * SR); speech[i:i + int(3.2 * SR)] = 1

# ---------------- SFX ----------------
sfx = np.zeros((N, 2), np.float32)
def knock(strength=1.0, seed=0):
    r = np.random.default_rng(seed); t = np.arange(int(0.7 * SR)) / SR; s = np.zeros_like(t)
    for f, tau, a in [(150, .06, 1.0), (285, .04, .7), (470, .028, .55), (760, .018, .4), (1180, .011, .3), (1900, .006, .2)]:
        f *= 1 + r.uniform(-.04, .04); s += a * np.sin(2 * np.pi * f * t + r.uniform(0, 6)) * np.exp(-t / tau)
    click = r.standard_normal(len(t)) * np.exp(-t / .0035); click = bandpass(click, 800, 7000)
    thump = np.sin(2 * np.pi * 72 * t) * np.exp(-t / .045) * .6
    x = (s * .5 + click * 1.4 + thump) * strength
    return x / np.abs(x).max() * strength
for j, k in enumerate(SFX["knock"]):
    sola = 55 <= k < 90
    x = knock(1.0, j)
    x = reverb(np.stack([x, x], 1), 2.2 if not sola else 2.8, .5 if not sola else .7, .18 if not sola else .3)
    place(sfx, x, k, 0.6 if sola else 1.15)

# odometer ticks 101.9 - 104.4
for i in range(4):
    a0, a1 = 101.9 + i * .18, 103.6 + i * .18
    for n in range(10):
        tt = a0 + (a1 - a0) * (np.arcsin(2 * n / 10 - 1) / np.pi + .5)
        tk = rng.standard_normal(int(.012 * SR)) * np.exp(-np.arange(int(.012 * SR)) / SR / .002)
        place(sfx, bandpass(tk, 2000, 9000), tt, .05)
# 2026 chime
t = np.arange(int(4 * SR)) / SR
ch = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in [(523.25, .5, 1.6), (784, .35, 1.2), (1046.5, .25, .9), (1568, .12, .6)]) * env(len(t), .005, .5)
place(sfx, reverb(np.stack([ch, ch], 1), 3, .9, .4), 104.25, .09)

def whoosh(dur, lo, hi, seed, peak=.6):
    r = np.random.default_rng(seed); n = int(dur * SR); x = r.standard_normal(n)
    x = bandpass(x, lo, hi); e = np.sin(np.pi * np.clip(np.arange(n) / n / peak, 0, 1) * .5) ** 2 * np.clip((n - np.arange(n)) / (n * (1 - peak)), 0, 1)
    return x * e / (np.abs(x).max() + 1e-9)
place(sfx, np.stack([whoosh(1.4, 300, 3000, 1), whoosh(1.4, 300, 3000, 2)], 1), 156.5, .06)   # card
place(sfx, np.stack([whoosh(1.2, 400, 4000, 3), whoosh(1.2, 400, 4000, 4)], 1), 200.5, .04)   # card hand-off
sw = whoosh(2.5, 150, 2500, 5, .8); place(sfx, reverb(np.stack([sw, sw], 1), 2, .6, .4), 169.3, .05)  # ivory reveal swell
# pen scribble
for k in range(26):
    tt = 164.2 + k * .17 + rng.uniform(0, .05); n = int(.12 * SR)
    sc = bandpass(rng.standard_normal(n), 2500, 8000) * np.hanning(n); place(sfx, sc, tt, .012)

# door: latch + creak + air
lt = knock(1, 99)[:int(.15 * SR)]; place(sfx, bandpass(lt, 1500, 8000), 214.45, .18)
dur = 4.0; n = int(dur * SR); tt = np.arange(n) / SR; cr = np.zeros(n)
rate = 18 + 40 * np.sin(np.pi * tt / dur) + 6 * np.sin(2 * np.pi * .7 * tt)
ph = np.cumsum(rate) / SR; pulses = np.where(np.diff(np.floor(ph), prepend=0) > 0)[0]
for p in pulses:
    m = min(int(.03 * SR), n - p); f0 = 520 + 260 * np.sin(p / n * 3.1)
    cr[p:p + m] += np.sin(2 * np.pi * f0 * np.arange(m) / SR) * np.exp(-np.arange(m) / SR / .006) * rng.uniform(.5, 1)
cr = bandpass(cr, 300, 3500) * env(n, .3, 1.2); cr /= np.abs(cr).max()
place(sfx, reverb(np.stack([cr, cr], 1), 2.5, .6, .35), 214.7, .16)
air = np.stack([whoosh(8, 80, 1800, 7, .75), whoosh(8, 80, 1800, 8, .75)], 1)
place(sfx, reverb(air, 3, .9, .5), 215.2, .10)
# shimmer of light
t = np.arange(int(9 * SR)) / SR
sh = sum(np.sin(2 * np.pi * f * t + i) * (.5 + .5 * np.sin(2 * np.pi * (.3 + .1 * i) * t)) for i, f in enumerate([1318.5, 1567.98, 1975.5, 2637])) * env(len(t), 3, 4)
place(sfx, reverb(np.stack([sh, sh], 1), 3, 1.2, .6), 217.0, .012)
# breath before the prayer
br = bandpass(rng.standard_normal(int(1.3 * SR)), 300, 2500) * np.sin(np.linspace(0, np.pi, int(1.3 * SR))) ** 2
place(sfx, br, 238.6, .025)

# ---------------- chaos ambience 0-30 ----------------
amb = np.zeros((int(31 * SR), 2), np.float32)
tt = np.arange(len(amb)) / SR
grow = np.clip(tt / 27, 0, 1) ** 1.3 * .85 + .15 * np.clip(tt / 2, 0, 1)
rum = bandpass(rng.standard_normal(len(amb)), 30, 260); rum /= np.abs(rum).max()
hiss = bandpass(rng.standard_normal(len(amb)), 400, 1800); hiss /= np.abs(hiss).max()
amb[:, 0] += rum * .35 + hiss * .05; amb[:, 1] += np.roll(rum, 9000) * .35 + np.roll(hiss, 7000) * .05
clips = [load(f"amb/a{i}.mp3", "highpass=f=180,lowpass=f=4200") for i in range(7)]
t0 = 0.8; k = 0; pans = [-.7, .6, -.3, .8, -.8, .2, .5]
while t0 < 29.5:
    c = clips[k % 7]; c = c * (0.09 / np.sqrt(np.mean(c ** 2) + 1e-9)); pan = pans[k % 7] * rng.uniform(.6, 1)
    st = np.stack([c[:, 0] * (1 - pan) ** .5, c[:, 1] * (1 + pan) ** .5], 1)
    place(amb, st, t0, rng.uniform(.5, 1.0) * (0.6 if k % 7 == 6 else 1))
    t0 += max(.35, 2.0 - t0 * .06) * rng.uniform(.6, 1.2); k += 1
# faint prayer murmur
place(amb, load("amb/a7.mp3"), 24.2, .5)
# phone pings
for pt in [3.4, 9.6, 17.8, 25.1, 27.6]:
    n = int(.25 * SR); x = np.arange(n) / SR
    pg = (np.sin(2 * np.pi * 1760 * x) * np.exp(-x / .05) + np.sin(2 * np.pi * 2350 * (x - .09)) * np.exp(-np.clip(x - .09, 0, 9) / .05) * (x > .09))
    place(amb, pg, pt, .035)
amb = reverb(amb, 1.8, .5, .35)[:len(amb)]
amb *= grow[:, None]
# drone (minimal music)
dr = (np.sin(2 * np.pi * 55 * tt) + .6 * np.sin(2 * np.pi * 82.41 * tt) + .3 * np.sin(2 * np.pi * 110.3 * tt)) * (.6 + .4 * np.sin(2 * np.pi * .13 * tt))
amb += (dr * .05 * np.clip(tt / 6, 0, 1))[:, None]
# duck ambience under the three questions, then hard cut at 30.0
sp = speech[:len(amb)]
k_ = int(.3 * SR); sm = np.convolve(sp[::100], np.ones(k_ // 100) / (k_ // 100), "same").repeat(100)[:len(amb)]
amb *= (1 - .55 * np.clip(sm * 1.5, 0, 1))[:, None]
cut = int(30.0 * SR); amb[cut:] = 0; amb[cut - int(.015 * SR):cut] *= np.linspace(1, 0, int(.015 * SR))[:, None]
sfx[:len(amb)] += amb * 0.62
# room tone after the cut
rt = bandpass(rng.standard_normal(N), 60, 1200) * 0.0025
rmask = np.zeros(N); rmask[int(30.25 * SR):int(55.5 * SR)] = 1
rmask = np.convolve(rmask[::100], np.ones(200) / 200, "same").repeat(100)[:N]
sfx += (rt * rmask)[:, None]

# ---------------- music ----------------
b1 = load("bgm1.mp3"); b2 = load("bgm2.mp3")
mus = np.zeros((N, 2), np.float32)
s1, e1 = 55.4, 131.0
seg = b1[:int((e1 - s1) * SR)].copy(); n = len(seg); ti = np.arange(n) / SR
seg *= (np.clip(ti / 1.5, 0, 1) * np.clip((e1 - s1 - ti) / 5.0, 0, 1))[:, None]
place(mus, seg, s1)
OFF = 84.0; s2 = 126.5
seg = b2[int(OFF * SR):].copy(); ti = np.arange(len(seg)) / SR
seg *= np.clip(ti / 4.5, 0, 1)[:, None]; place(mus, seg, s2)
# section gains
tt = np.arange(N) / SR
def ramp(a, b, va, vb): return va + (vb - va) * np.clip((tt - a) / (b - a), 0, 1)
g = np.ones(N)
g *= np.where(tt < 90, 0.85, 1.0)                     # solas: lighter rhythm bed
g *= np.where((tt > 129) & (tt < 171), ramp(129, 131, 1, .5) * ramp(169, 171.5, 1, 2), 1)  # discern lowered
g *= np.where((tt > 208) & (tt < 216.5), ramp(208, 212.2, 1, .12) * ramp(214.6, 216.5, 1, 6), 1)  # dip for final knock
g *= ramp(244.5, 248.8, 1, 0)
# ducking under speech
k = int(.35 * SR) // 100
m = speech[::100]; m = np.convolve(np.convolve(m, np.ones(k) / k, "same"), np.ones(k) / k, "same").repeat(100)[:N]
duck = 1 - .62 * np.clip(m * 1.6, 0, 1)
mus *= (g * duck)[:, None] * 0.55

out = voice + sfx + mus
out = out[:int(END * SR)]
pk = np.abs(out).max(); print("peak", pk)
if pk > .97: out *= .97 / pk
import re
raw = out.astype(np.float32).tobytes()
meas = subprocess.run(["ffmpeg", "-v", "info", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "ebur128", "-f", "null", "-"], input=raw, capture_output=True).stderr.decode()
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", meas)[-1]); gain = -16.0 - I; print("measured I", I, "gain", gain)
y = out * (10 ** (gain / 20)); LIM = 0.80; B = 48
nb = len(y) // B + 1; yp = np.pad(np.abs(y).max(1), (0, nb * B - len(y))).reshape(nb, B).max(1)
gb = np.minimum(1, LIM / np.maximum(yp, 1e-9))
la = 6; gmin = np.array([gb[max(0, i - 2):i + la].min() for i in range(nb)])
rel = np.exp(-1 / 80.0); gs = np.empty(nb); cur = 1.0
for i in range(nb):
    cur = gmin[i] if gmin[i] < cur else cur * rel + gmin[i] * (1 - rel); gs[i] = cur
gsamp = np.interp(np.arange(len(y)), np.arange(nb) * B + B / 2, gs)
y = (y * gsamp[:, None]).astype(np.float32); print("limited blocks", int((gs < .999).sum()), "max", np.abs(y).max())
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "aac", "-b:a", "256k", "mix.m4a"], input=y.tobytes(), check=True)
# also stems summary
for name, x in [("voice", voice), ("sfx", sfx), ("music", mus)]:
    print(name, "rms dB", round(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9), 1))
