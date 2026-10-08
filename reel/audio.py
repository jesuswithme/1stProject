import numpy as np, wave
SR=48000; D=15.0; N=int(SR*D); t=np.arange(N)/SR; rs=np.random.default_rng(3)
L=np.zeros(N); R=np.zeros(N)
def add(sig,start,gain=1.0,pan=0.0):
    i=int(start*SR); n=min(len(sig),N-i)
    if n<=0: return
    L[i:i+n]+=sig[:n]*gain*np.sqrt((1-pan)/2)*1.414; R[i:i+n]+=sig[:n]*gain*np.sqrt((1+pan)/2)*1.414
def band(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
def sweepnoise(dur,f0,f1,q=.5):
    n=int(dur*SR); x=rs.standard_normal(n); out=np.zeros(n); seg=2048
    for s in range(0,n,seg//2):
        c=f0*(f1/f0)**(s/n); w=x[s:s+seg]*np.hanning(len(x[s:s+seg]))
        out[s:s+len(w)]+=band(w,c*(1-q),c*(1+q))
    return out/ (np.abs(out).max()+1e-9)
HITS=[(0.15,.25),(1.6,1),(3.0,.8),(4.2,1),(4.5,.9),(4.8,1.1),(5.4,.6),(6.6,.7),(8.35,1.4),(9.4,.6)]+[(11.0+i*.15,.55) for i in range(8)]+[(12.2,1.5)]
# pad: D minor until 12.2, then D major
def tone(fr,dur,det=.0): 
    tt=np.arange(int(dur*SR))/SR; return np.sin(2*np.pi*fr*(1+det)*tt)+.3*np.sin(2*np.pi*fr*2*(1+det)*tt)+.12*np.sin(2*np.pi*fr*3*tt)
mi=[73.42,110,146.83,174.61,220,293.66]; ma=[73.42,110,146.83,185.0,220,293.66,369.99,440]
d1=12.2; pe=np.minimum(1,np.arange(int(d1*SR))/SR/2.5)*(.5+.5*np.arange(int(d1*SR))/SR/d1)
for k,fr in enumerate(mi):
    add(tone(fr,d1,.0015)*pe*(.035 if fr>200 else .05),0,1,-.4); add(tone(fr,d1,-.0015)*pe*(.035 if fr>200 else .05),0,1,.4)
d2=2.8; tt=np.arange(int(d2*SR))/SR; pe2=np.exp(-tt*.5)*np.minimum(1,tt/.05)*np.minimum(1,(D-12.2-tt)/.6).clip(0)
for fr in ma:
    add(tone(fr,d2,.002)*pe2*.06,12.2,1,-.5); add(tone(fr,d2,-.002)*pe2*.06,12.2,1,.5)
# shimmer bells in finale
for k,fr in enumerate([587.33,739.99,880,1174.66,1479.98,1760]):
    st=12.45+k*.13; tt=np.arange(int((D-st)*SR))/SR
    b=(np.sin(2*np.pi*fr*tt)+.4*np.sin(2*np.pi*fr*2.76*tt)*np.exp(-tt*6))*np.exp(-tt*1.6)*(1+.2*np.sin(2*np.pi*5*tt))
    add(b*.05,st,1,(-1)**k*.6)
# heartbeat-ish clock ticks (the last hours)
for tk in np.arange(0.3,11.0,0.5):
    n=int(.04*SR); tt=np.arange(n)/SR; x=(np.sin(2*np.pi*3200*tt)*.5+band(rs.standard_normal(n),2000,9000))*np.exp(-tt*140)
    add(x*.10*(0.6+0.4*tk/11),tk,1,.35 if int(tk*2)%2 else -.35)
# impacts
for ht,s in HITS:
    n=int(1.6*SR); tt=np.arange(n)/SR
    f=38+90*np.exp(-tt*18); ph=2*np.cumsum(np.pi*f)/SR
    sub=np.sin(ph)*np.exp(-tt*(3.2 if s>1 else 5))
    nz=band(rs.standard_normal(n),40,2500 if s<1 else 6000)*np.exp(-tt*14)*.6
    cl=band(rs.standard_normal(n),3000,12000)*np.exp(-tt*60)*.4
    add((sub+nz+cl)*.32*s,ht)
# whooshes before cuts + risers
for ct in [1.6,3.0,4.2,5.4,6.6,9.4,11.0]:
    w=sweepnoise(.35,500,5000,.35)*np.hanning(int(.35*SR))**.7; add(w*.10,ct-.33,1,-.6); add(w[::-1]*.05,ct-.05,1,.6)
for a,b in [(7.3,8.35),(10.2,11.0),(11.3,12.2)]:
    w=sweepnoise(b-a,200,7000,.4); n=len(w); w*=(np.arange(n)/n)**2.2; add(w*.22,a)
    tt=np.arange(n)/SR; add(np.sin(2*np.pi*np.cumsum(220*2**(2*tt/(b-a)))/SR)*(np.arange(n)/n)**3*.05,a)
# reverb
ir_n=int(2.4*SR); ir=rs.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR*2.6); ir[:int(.02*SR)]=0; ir/=np.sqrt((ir**2).sum())
def conv(x): 
    m=len(x)+ir_n; F=1<<(m-1).bit_length(); return np.fft.irfft(np.fft.rfft(x,F)*np.fft.rfft(ir,F),F)[:len(x)]
L2=L+.35*conv(L); R2=R+.35*conv(np.roll(R,240))
st=np.stack([L2,R2],1); st=np.tanh(st/np.abs(st).max()*1.6); st/=np.abs(st).max(); st*=.89
fo=np.minimum(1,(D-t)/.5).clip(0)[:,None]; st*=fo
with wave.open('audio.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
print('ok')
