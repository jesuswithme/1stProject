"""설아의 초록빛 나들이 — 내레이션(충신유치원 나레이션) + BGM 믹스 & 타임라인/자막"""
import json, subprocess
from pathlib import Path
import numpy as np

SR = 44100
HERE = Path(__file__).parent
DUR = 40.0
N = int(DUR * SR); t = np.arange(N) / SR
NARR = [
    ('n01', 0.9, '할아버지, 할머니와 함께 떠난 설아의 신나는 나들이!'),
    ('n02', 5.9, '반짝이는 양주 기산 저수지! 할아버지 손을 꼭 잡고 걸어요.'),
    ('n03', 12.0, '할머니 품에서 까르르! 송은영 원장 선생님과 함께라 더 즐거워요.'),
    ('n04', 19.1, '장흥 조각공원에서는 멋진 조각들 사이를 신나게 뛰어놀아요.'),
    ('n05', 25.2, '풀잎도 만져 보고, 그림도 구경하며, 자연 속에서 배우고 느껴요.'),
    ('n06', 32.2, '할아버지, 할머니와 함께여서 더 행복했던 설아의 하루!'),
]
SCENES = [(0.0, 5.2, 'intro'), (5.2, 11.4, 'res1'), (11.4, 17.6, 'res2'), (17.6, 24.6, 'park1'), (24.6, 31.6, 'park2'), (31.6, 40.0, 'finale')]

def load(fn):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(fn), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)

def ma(x, k):
    c = np.cumsum(np.concatenate([[0], x])); h = k // 2
    i0 = np.clip(np.arange(len(x)) - h, 0, len(x)); i1 = np.clip(np.arange(len(x)) + h, 0, len(x))
    return (c[i1] - c[i0]) / k

voice = np.zeros(N); speech = np.zeros(N); lines = []
for nid, st, text in NARR:
    v = load(HERE / 'voice' / f'{nid}.mp3'); i = int(st * SR); j = min(N, i + len(v))
    voice[i:j] += v[:j - i]; speech[i:j] = 1
    lines.append({'id': nid, 't': st, 'e': round(st + len(v) / SR, 3), 'text': text})
voice *= 0.16 / np.sqrt(np.mean(voice[speech > 0] ** 2))
b = load(HERE / 'bgm.mp3'); b *= 0.13 / np.sqrt(np.mean(b ** 2))
bgm = np.zeros(N); bgm[:min(N, len(b))] = b[:N]
m = np.clip(ma(ma(speech, int(0.3 * SR)), int(0.3 * SR)) * 1.6, 0, 1)
bgm *= (1 - 0.7 * m) * np.clip(t / 0.3, 0, 1) * np.clip((DUR - 0.1 - t) / 2.5, 0, 1)
mix = voice + bgm
pk = np.abs(mix).max()
if pk > 0.97: mix *= 0.97 / pk
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
print(f'voice {db(voice[speech > 0]):.1f} / bgm under voice {db(bgm[speech > 0]):.1f} dB')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-ac', '2', str(HERE / 'audio.wav')],
               input=mix.astype(np.float32).tobytes(), check=True)
(HERE / 'timeline.js').write_text('window.TL = ' + json.dumps({'dur': DUR, 'lines': lines, 'scenes': [{'t': s[0], 'e': s[1], 'id': s[2]} for s in SCENES]}, ensure_ascii=False) + ';\n', encoding='utf-8')
ts = lambda s: f'{int(s // 3600):02d}:{int(s // 60 % 60):02d}:{int(s % 60):02d},{int(round(s * 1000)) % 1000:03d}'
(HERE / 'subtitles.srt').write_text('\n'.join(f"{i}\n{ts(l['t'])} --> {ts(l['e'] + 0.3)}\n{l['text']}\n" for i, l in enumerate(lines, 1)), encoding='utf-8')
print('ok')
