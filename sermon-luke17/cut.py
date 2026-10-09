"""설교 음성에서 핵심 구간을 잘라 clips/*.wav 로 저장 (src/sermon.m4a 필요, git 제외)"""
import json, subprocess, sys
import numpy as np
SR = 48000
CUTS = [  # (id, 시작, 끝) — 원본 설교 기준 초
    ('c01', 204.55, 217.85), ('c02', 262.22, 270.65), ('c03', 340.65, 352.6), ('c04', 392.75, 398.05),
    ('c05', 407.55, 428.4), ('c06', 610.75, 624.65), ('c07', 659.0, 673.7), ('c09', 938.75, 946.6), ('c10', 978.25, 983.3), ('c11', 1012.25, 1025.8), ('c12', 1031.62, 1038.0),
    ('c13', 1056.6, 1077.9), ('c14', 1299.9, 1305.55), ('c16', 1315.45, 1318.65), ('c15', 1331.3, 1346.8),
]
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'src/sermon.m4a', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
fr = int(0.01 * SR)
rms = np.sqrt(np.convolve(x ** 2, np.ones(fr) / fr, 'same'))
def quiet(t, w=0.2):
    i0, i1 = int((t - w) * SR), int((t + w) * SR)
    return (i0 + int(np.argmin(rms[i0:i1]))) / SR
out = {}
for cid, a, b in CUTS:
    a2, b2 = quiet(a), quiet(b)
    seg = x[int(a2 * SR):int(b2 * SR)].copy()
    n = len(seg); f1, f2 = int(0.03 * SR), int(0.08 * SR)
    seg[:f1] *= np.linspace(0, 1, f1); seg[-f2:] *= np.linspace(1, 0, f2)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f64le', '-ar', str(SR), '-ac', '1', '-i', '-', f'clips/{cid}.wav'], input=seg.tobytes(), check=True)
    out[cid] = [round(a2, 3), round(b2, 3)]
    print(cid, out[cid], round(b2 - a2, 2))
json.dump(out, open('clips/cuts.json', 'w'))
print('total', round(sum(b - a for a, b in out.values()), 1))
