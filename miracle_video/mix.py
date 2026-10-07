import json,subprocess,numpy as np
SR=48000
def load(fn):
    raw=subprocess.check_output(["ffmpeg","-v","0","-i",fn,"-f","f32le","-ac","2","-ar",str(SR),"-"])
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
def fit(a,n):  # loop music if shorter than needed
    if len(a)>=n: return a[:n]
    return np.concatenate([a]*(n//len(a)+1))[:n]
TL=json.load(open("tl.json")); END=TL[-1]["end"]; N=int(END*SR)+SR
voice=np.zeros((N,2),np.float32); speech=np.zeros(N,np.float32)
for s in TL:
    for l in s["lines"]:
        a=load(l["file"]); i=int(l["t"]*SR); a=a[:N-i]; voice[i:i+len(a)]+=a; speech[i:i+len(a)]=1
def ma(x,k):
    c=np.cumsum(np.concatenate([[0],x])); h=k//2
    i0=np.clip(np.arange(len(x))-h,0,len(x)); i1=np.clip(np.arange(len(x))+h,0,len(x))
    return (c[i1]-c[i0])/k
k=int(0.4*SR); m=ma(ma(speech,k),k); gain=0.85-0.55*np.clip(m*1.6,0,1)
miracle=[s for s in TL if s["id"]=="miracle"][0]["start"]
X=miracle-1.2; XF=4.0   # 5연 '깨달음' 직전 BGM 전환
n1=int((X+XF)*SR); b1=fit(load("bgm1.mp3"),n1); t=np.arange(n1)/SR; b1*=np.clip((X+XF-t)/XF,0,1)[:,None]
bgm=np.zeros((N,2),np.float32); bgm[:n1]+=b1
i2=int(X*SR); b2=fit(load("bgm2.mp3"),N-i2); t2=np.arange(N-i2)/SR; b2*=np.clip(t2/XF,0,1)[:,None]; bgm[i2:]+=b2
tt=np.arange(N)/SR; bgm*=(gain*np.clip(tt/2.0,0,1)*np.clip((END-0.3-tt)/4.0,0,1))[:,None]
voice*=0.17/np.sqrt(np.mean(voice[speech>0]**2))
out=voice+bgm*0.62; pk=np.abs(out).max()
if pk>0.97: out*=0.97/pk
out=out[:int(END*SR)]
subprocess.run(["ffmpeg","-y","-v","error","-f","f32le","-ar",str(SR),"-ac","2","-i","-","-af","loudnorm=I=-15:TP=-1.5:LRA=11","-ar","48000","-c:a","aac","-b:a","192k","mix.m4a"],input=out.tobytes(),check=True)
print("mix ok",END)
