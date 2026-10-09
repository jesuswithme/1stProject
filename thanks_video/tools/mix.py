# 나레이션 + BGM(더킹, 곡의 실제 엔딩으로 크로스페이드) + 전환 효과음 → mix.m4a
import json,subprocess,numpy as np
SR=48000
def load(fn,ch=2):
    raw=subprocess.check_output(["ffmpeg","-v","0","-i",fn,"-f","f32le","-ac",str(ch),"-ar",str(SR),"-"])
    return np.frombuffer(raw,np.float32).reshape(-1,ch).copy()
TL=json.load(open("tl.json")); END=TL["total"]; N=int(END*SR)
voice=np.zeros((N,2),np.float32); speech=np.zeros(N,np.float32)
for s in TL["scenes"]:
    a=load(s["file"]); i=int(s["t"]*SR); n=min(len(a),N-i); voice[i:i+n]+=a[:n]; speech[i:i+n]=1
def ma(x,k):
    c=np.cumsum(np.concatenate([[0],x])); h=k//2; idx=np.arange(len(x))
    return (c[np.clip(idx+h,0,len(x))]-c[np.clip(idx-h,0,len(x))])/k
k=int(0.35*SR); m=ma(ma(speech,k),k); gain=0.9-0.6*np.clip(m*1.6,0,1)
song=load("assets/bgm.mp3"); L=len(song)/SR
X=21.0; XF=2.5; OFF=L-1.6-END     # 곡 끝(잔향 직전)이 영상 끝에 오도록
tt=np.arange(N)/SR
b1=song[:N].copy()*np.clip((X+XF-tt)/XF,0,1)[:,None]
j=(tt+OFF)*SR; j=np.clip(j.astype(int),0,len(song)-1)
b2=song[j]*np.clip((tt-X)/XF,0,1)[:,None]
bgm=(b1+b2)*(gain*np.clip(tt/1.2,0,1)*np.clip((END-tt)/1.2,0,1))[:,None]
# 효과음
sfx=np.zeros((N,2),np.float32); rng=np.random.default_rng(7)
def whoosh(t0,d=0.7,amp=0.10):
    n=int(d*SR); w=rng.standard_normal(n).astype(np.float32)
    w=np.convolve(w,np.ones(24)/24,'same'); env=np.sin(np.pi*np.linspace(0,1,n))**2
    i=int((t0-d/2)*SR); sfx[i:i+n]+=(w*env*amp)[:,None]
def chime(t0,fs=(1318.5,1975.5,2637),amp=0.06,d=2.4):
    n=int(d*SR); x=np.arange(n)/SR; w=sum(np.sin(2*np.pi*f*x)*np.exp(-x*(2.2+q)) for q,f in enumerate(fs))
    i=int(t0*SR); n=min(n,N-i); sfx[i:i+n]+=(w[:n]*amp)[:,None]
for t in [4.8,8.8,13.4,17.8,22.6]: whoosh(t)
chime(2.6,amp=.035); chime(9.6,(1046.5,1568,2093),.03); chime(22.8,amp=.05); chime(26.55,(1568,2093,2637),.035)
voice*=0.17/np.sqrt(np.mean(voice[speech>0]**2))
out=voice+bgm*0.55+sfx; pk=np.abs(out).max()
if pk>0.97: out*=0.97/pk
subprocess.run(["ffmpeg","-y","-v","error","-f","f32le","-ar",str(SR),"-ac","2","-i","-","-af","loudnorm=I=-15:TP=-1.5:LRA=11","-ar","48000","-c:a","aac","-b:a","192k","mix.m4a"],input=out.astype(np.float32).tobytes(),check=True)
print("ok",END,OFF)
