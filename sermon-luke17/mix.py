"""범사에 그를 인정하라 (누가복음 17:11-19) — 설교 하이라이트: 목사님 음성 클립 + BGM 믹스 & 타임라인/자막
먼저 python3 cut.py 로 clips/*.wav 생성 (원본 설교 음성은 src/, git 제외)"""
import json
import subprocess
from pathlib import Path

import numpy as np

SR = 44100
FPS = 30
HERE = Path(__file__).parent
CUTS = json.loads((HERE / 'clips' / 'cuts.json').read_text())

# 자막: (원본 설교 기준 시작 초, 문장) — 자동 음성인식 결과를 듣고 다듬은 문장
SUBS = {
    'c01': [(204.4, '그때 에드워드 스펜서가 뭐라고 하냐면'), (206.8, '“내가 17명의 사람을 구조해 줬는데”'),
            (210.8, '“어느 누구도 나에게 와서 감사하다고 인사하지 않은 것이”'), (215.8, '“가장 기억에 남습니다.”')],
    'c02': [(262.35, '열 명의 나병 환자가 어떻게 합니까?'), (265.0, '큰 소리로 부르며'), (266.6, '“예수 선생님, 우리를 불쌍히 여기소서”라고 외쳐요.')],
    'c03': [(340.63, '그런데 예수님이 뭐라고 하십니까?'), (343.3, '“너희 몸을 제사장들에게 가서 보이라”'),
            (346.9, '그들은 이 말을 신뢰하고'), (349.2, '이 말씀을 의지하여 제사장들에게 나아가는 거예요.')],
    'c04': [(392.84, '가다 보니까 어떻게 됩니까?'), (395.9, '가다 보니까… 깨끗해집니다!')],
    'c05': [(407.74, '열 명 중에 누가 옵니까? 몇 명이 와요?'), (411.95, '한 사람. 한 사람만 돌아와서'), (413.95, '하나님께 영광을 돌리고'),
            (416.2, '예수께 엎드려 감사 인사하는 것입니다.'), (419.3, '그때 예수님께서 물어보시죠.'), (421.0, '“나머지 아홉은 어디 있느냐?”'),
            (423.2, '열 사람이 다 고침 받았을 텐데'), (425.3, '“나머지 아홉은 어디 있느냐?”')],
    'c06': [(610.75, '그런데 그 아홉 명의 환자들은'), (614.1, '예수님을 의사로 알고 돌아간 겁니다.'),
            (617.2, '그런데 예수님께서 그들에게 원하신 것은 무엇이냐?'), (620.45, '의사 예수가 아니라'), (621.85, '구원자 예수가 되기를 원했던 것입니다.')],
    'c07': [(658.9, '이 사마리아 사람은 예수님이 나의 나병을 고쳐 주시고'), (662.6, '치료해 주심을 통하여서 예수님에 대한 마음이 바뀌는 거예요.'),
            (666.4, '“당신은 이제 나의 왕이십니다.”'), (668.1, '“당신은 이제 나의 신이십니다.”'), (669.75, '“당신은 이제 나의 주인이십니다.”'), (672.0, '호칭이 바뀝니다.')],
    'c09': [(938.9, '여러분, 이 치유와 능력과 기적은'), (940.95, '다 손가락일 뿐이에요.'), (942.25, '그것은 예수님을 보여 주는 도구일 뿐입니다.')],
    'c10': [(978.2, '이 사람이 예수님께 감사할 수 있었던 것은'), (981.85, '인정했기 때문입니다.')],
    'c11': [(1012.15, '이것을 인정한 그 사람만'), (1015.1, '예수님께 감사하고 하나님께 영광을 돌릴 수 있는 거예요.'),
            (1018.6, '나의 작음을 알고 그분의 크심을 알 때'), (1021.35, '그것을 인정할 때'), (1022.9, '우리가 감사할 수 있게 되는 것입니다.')],
    'c12': [(1031.6, '(다 함께) “범사에 그를 인정하라”'), (1034.3, '“그리하면 네 길을 지도하시리라” 아멘.')],
    'c13': [(1056.6, '우리는 어떻게 하냐? 아홉 가지는 내가 한 거예요.'), (1058.85, '이건 내가 수고하고, 내가 노력하고, 내가 애쓴 거지.'),
            (1061.5, '하나만, 이건 하나님이 도와주신 거예요.'), (1063.9, '이건 하나님이 하신 거예요.'), (1065.3, '오늘 예수님께서 원하시는 것은'),
            (1067.0, '“내가 너희에게 모든 것을 다 주었는데'), (1069.0, '범사에 다 인정하고 감사해야지.”'),
            (1071.7, '아홉은 내가 한 거고, 아홉은 내 노력으로 한 거고'), (1074.65, '하나만 감사하지 말고'), (1076.0, '모든 것을 인정하는 거예요.')],
    'c14': [(1299.95, '여러분, 누가 하나님께 감사할 수 있습니까?'), (1301.7, '누가 예수님께 감사할 수 있습니까?'), (1303.45, '인정한 그 사람이 감사할 수 있는 것입니다.')],
    'c16': [(1315.5, '여러분, 감사의 시작은 인정입니다.')],
    'c15': [(1331.3, '여기 있는 우리는 다 구원받은 백성입니다.'), (1333.65, '우리가 살아갈 삶은 무엇이냐?'),
            (1335.25, '범사에 그를 인정하고 감사하는 삶을 살아야 합니다.'), (1339.3, '그럴 때에 하나님께서'), (1342.75, '우리의 삶을 영원히 지도해 주십니다.')],
}

# 진행 순서: ('pad', 초, 장면) = BGM만 / ('clip', id, 장면)
SEQ = [
    ('pad', 7.0, 'intro'),
    ('pad', 6.0, 'spencer'), ('clip', 'c01', 'spencer'),
    ('pad', 1.8, 'ten'), ('clip', 'c02', 'ten'), ('pad', 0.5, 'ten'), ('clip', 'c03', 'go'), ('pad', 0.5, 'go'), ('clip', 'c04', 'clean'),
    ('pad', 1.8, 'nine'), ('clip', 'c05', 'nine'),
    ('pad', 1.8, 'savior'), ('clip', 'c06', 'savior'), ('pad', 0.8, 'king'), ('clip', 'c07', 'king'),
    ('pad', 2.0, 'moon'), ('clip', 'c09', 'moon'),
    ('pad', 1.8, 'admit'), ('clip', 'c10', 'admit'), ('pad', 0.5, 'admit'), ('clip', 'c11', 'admit'), ('pad', 0.9, 'prov'), ('clip', 'c12', 'prov'),
    ('pad', 1.8, 'tiles'), ('clip', 'c13', 'tiles'),
    ('pad', 1.8, 'start'), ('clip', 'c14', 'start'), ('pad', 0.6, 'start'), ('clip', 'c16', 'start'), ('pad', 1.0, 'path'), ('clip', 'c15', 'path'),
    ('pad', 9.5, 'outro'),
]


def load(fn, af=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', str(fn)] + (['-af', af] if af else []) + ['-f', 'f32le', '-ac', '1', '-ar', str(SR), '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32).astype(np.float64)


def ma(x, k):
    c = np.cumsum(np.concatenate([[0], x])); h = k // 2
    i0 = np.clip(np.arange(len(x)) - h, 0, len(x)); i1 = np.clip(np.arange(len(x)) + h, 0, len(x))
    return (c[i1] - c[i0]) / k


# 1) 타임라인 배치
t = 0.0; clips = []; scenes = []; lines = []
for kind, v, sc in SEQ:
    if kind == 'pad':
        dur = v; cid = None
    else:
        cid = v; a, b = CUTS[cid]; dur = b - a
        for i, (st, text) in enumerate(SUBS[cid]):
            en = SUBS[cid][i + 1][0] if i + 1 < len(SUBS[cid]) else b
            lines.append({'t': round(t + max(0, st - a), 3), 'e': round(t + min(dur, en - a) - 0.05, 3), 'text': text, 'clip': cid})
        clips.append({'id': cid, 't': round(t, 3), 'e': round(t + dur, 3)})
    if scenes and scenes[-1]['id'] == sc: scenes[-1]['e'] = round(t + dur, 3)
    else: scenes.append({'id': sc, 't': round(t, 3), 'e': round(t + dur, 3)})
    t += dur
DUR = round(t, 2)
N = int(DUR * SR); tt = np.arange(N) / SR
print('duration', DUR)

# 2) 목사님 음성: 저역 정리 + 가벼운 압축, 클립마다 같은 크기로
voice = np.zeros(N); speech = np.zeros(N)
for c in clips:
    v = load(HERE / 'clips' / f"{c['id']}.wav", 'highpass=f=85,lowpass=f=11000,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=180:makeup=2')
    act = np.abs(v) > 0.02
    v *= 0.15 / np.sqrt(np.mean(v[act] ** 2) + 1e-12)
    i = int(c['t'] * SR); j = min(N, i + len(v))
    voice[i:j] += v[:j - i]; speech[i:j] = 1

# 3) BGM: 음성 아래로 덕킹, 인트로/챕터/아웃트로에서 올라옴
b = load(HERE / 'bgm.mp3'); b *= 0.13 / np.sqrt(np.mean(b ** 2))
bgm = np.zeros(N); bgm[:min(N, len(b))] = b[:N]
m = np.clip(ma(ma(speech, int(0.4 * SR)), int(0.4 * SR)) * 1.5, 0, 1)
bgm *= (1 - 0.8 * m) * np.clip(tt / 1.5, 0, 1) * np.clip((DUR - 0.2 - tt) / 5.0, 0, 1)

mix = voice + bgm
pk = np.abs(mix).max()
if pk > 0.97: mix *= 0.97 / pk
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
sp = speech > 0
print(f'voice {db(voice[sp]):.1f} / bgm under voice {db(bgm[sp]):.1f} / bgm alone {db(bgm[~sp]):.1f} dB')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11',
                '-ar', '48000', '-ac', '2', str(HERE / 'audio.wav')], input=mix.astype(np.float32).tobytes(), check=True)

# 4) 화면용 음성 크기(프레임별) — 음성 반응 그래픽
hop = SR // FPS
env = [round(float(np.sqrt(np.mean(voice[i:i + hop] ** 2))) / 0.15, 2) for i in range(0, N, hop)]
(HERE / 'timeline.js').write_text('window.TL = ' + json.dumps({'dur': DUR, 'scenes': scenes, 'clips': clips, 'lines': lines, 'env': env},
                                                             ensure_ascii=False) + ';\n', encoding='utf-8')


def ts(s):
    ms = int(round(s * 1000)); return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


srt = [f"{i}\n{ts(l['t'])} --> {ts(l['e'])}\n{l['text']}\n" for i, l in enumerate(lines, 1)]
(HERE / 'subtitles.srt').write_text('\n'.join(srt), encoding='utf-8')
for s in scenes: print(f"{s['id']:8s} {s['t']:7.2f} {s['e']:7.2f}")
