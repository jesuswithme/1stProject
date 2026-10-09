import json,subprocess,numpy as np
SR=48000; FPS=30
LINES=["오늘 아침도 성도님들의 따뜻한 사랑을 받았습니다.",
"정성껏 준비해 주신 맛있는 아침 식사!",
"한 끼의 음식에 담긴 사랑과 섬김이 참 감사합니다.",
"성도님들 덕분에 오늘도 든든하고 행복합니다.",
"성도님들의 귀한 섬김을 기억하며, 진심으로 감사드립니다.",
"하나님께서 그 사랑을 축복하시기를 바랍니다."]
# 장면: (id, start, end, 나레이션 시작)
SC=[("morning",0.0,4.8,0.9),("care",4.8,8.8,5.2),("thanks",8.8,13.4,9.3),
    ("together",13.4,17.8,13.8),("bow",17.8,22.6,18.1),("verse",22.6,29.8,23.3)]
def load(fn):
    raw=subprocess.check_output(["ffmpeg","-v","0","-i",fn,"-f","f32le","-ac","1","-ar",str(SR),"-"])
    return np.frombuffer(raw,np.float32)
TOTAL=SC[-1][2]; N=int(round(TOTAL*FPS))
amp=np.zeros(N+2)
tl=[]
for i,(sid,s,e,t) in enumerate(SC):
    a=load(f"tts/t{i}.wav"); d=len(a)/SR
    assert t+d<=e, (sid,t+d,e)
    hop=SR//FPS
    for k in range(int(d*FPS)):
        r=np.sqrt(np.mean(a[k*hop:(k+1)*hop]**2)); amp[int(round(t*FPS))+k]=r
    tl.append({"id":sid,"start":s,"end":e,"t":round(t,3),"e":round(t+d,3),"text":LINES[i],"file":f"tts/t{i}.wav"})
amp=amp/np.percentile(amp[amp>0],95); amp=np.clip(amp,0,1)
amp=np.convolve(amp,[0.25,0.5,0.25],'same')
json.dump({"scenes":tl,"total":TOTAL,"amp":[round(float(x),3) for x in amp]},open("tl.json","w"),ensure_ascii=False)
for s in tl: print(s["id"],s["start"],s["end"],s["t"],s["e"])
