import numpy as np, wave, json
SR=48000; D=30.0; N=int(SR*D); t=np.arange(N)/SR; rs=np.random.default_rng(21)
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
        c=f0*(f1/f0)**(s/n); w=x[s:s+seg]*np.hanning(len(x[s:s+seg])); out[s:s+len(w)]+=band(w,c*(1-q),c*(1+q))
    return out/(np.abs(out).max()+1e-9)
HITS=json.load(open('hits5.json'))['hits']
C={'D5':[73.42,110,146.83,220],'Dm':[73.42,146.83,220,293.66,349.23],'Bb':[58.27,116.54,174.61,233.08,293.66],'F':[87.31,174.61,261.63,349.23,440],
   'C':[65.41,130.81,196,261.63,329.63,392],'Gm':[98,146.83,196,233.08,293.66],'A':[110,164.81,220,277.18,329.63],
   'D':[73.42,146.83,220,293.66,369.99,440,587.33,739.99]}
PROG=[(0,2.6,'D5',.6),(2.6,4.0,'Dm',1),(4.0,5.0,'Bb',1),(5.0,6.0,'F',1.2),(6.0,6.8,'C',1),(6.8,7.6,'F',1.1),(7.6,8.0,'Dm',.9),(8.0,9.2,'Gm',1.1),(9.2,9.8,'A',1.2),
      (9.8,12.1,'Dm',1.0),(12.4,13.0,'Bb',1),(13.0,13.6,'C',1),(13.6,14.2,'F',1.1),(14.2,14.8,'C',1),(14.8,16.25,'Dm',.7),(16.7,17.4,'D',1.2),
      (17.4,18.2,'Bb',1),(18.2,18.9,'F',1),(18.9,19.6,'C',1.1),(19.6,20.25,'Dm',1),(20.25,20.9,'Bb',1.1),(20.9,21.4,'F',1.2),(21.4,21.8,'C',1.1),
      (21.8,22.3,'Gm',1),(22.3,22.8,'Dm',1),(22.8,23.6,'Bb',1),(23.6,24.3,'C',1),(24.3,25.0,'A',1.1),(25.0,26.1,'Dm',.9),(26.1,26.8,'Bb',1.1),(26.8,27.4,'A',1.2),(27.4,30.0,'D',1.3)]
for a,b,ch,g in PROG:
    n=int((b-a+.5)*SR); tt=np.arange(n)/SR; e=np.minimum(1,tt/.25)*np.clip((b-a+.5-tt)/.5,0,1)
    if a==27.4: e=np.minimum(1,tt/.4)*np.exp(-tt*.15)*np.clip((D-a-tt)/.8,0,1)
    for fr in C[ch]:
        for det,pan in [(.0016,-.45),(-.0016,.45)]:
            w=np.sin(2*np.pi*fr*(1+det)*tt)+.28*np.sin(2*np.pi*fr*2*(1+det)*tt)+.1*np.sin(2*np.pi*fr*3*tt)
            add(w*e*(.024 if fr>200 else .036)*g,a,1,pan)
def bells(st,frs,gap=.11,g=.05):
    for k,fr in enumerate(frs):
        s=st+k*gap; tt=np.arange(int(min(3.5,D-s)*SR))/SR
        add((np.sin(2*np.pi*fr*tt)+.4*np.sin(2*np.pi*fr*2.76*tt)*np.exp(-tt*6))*np.exp(-tt*1.6)*g,s,1,(-1)**k*.6)
bells(1.3,[587.33,880,1174.66],.09,.035); bells(5.25,[698.46,880,1046.5,1396.9]); bells(16.7,[587.33,739.99,880,1174.66]); bells(20.95,[698.46,880,1046.5])
bells(27.6,[587.33,739.99,880,1174.66,1479.98,1760],.13,.05)
# fire crackle
for k in range(140):
    st=8.0+rs.random()*1.8; n=int(.012*SR); tt=np.arange(n)/SR; add(band(rs.standard_normal(n),1500,9000)*np.exp(-tt*500)*(.15+.2*rs.random()),st,1,rs.random()-.5)
n=int(1.9*SR); tt=np.arange(n)/SR; add(band(rs.standard_normal(n),60,500)*np.minimum(1,tt/.3)*np.clip((1.9-tt)/.3,0,1)*.12,7.95)
# riot: crowd roar + chant stabs
n=int(2.4*SR); tt=np.arange(n)/SR; add(band(rs.standard_normal(n),200,2000)*np.minimum(1,tt/.2)*np.clip((2.3-tt)/.15,0,1)*.16,9.8)
for b in np.arange(10.1,12.05,.3):
    n=int(.25*SR); tt=np.arange(n)/SR; saw=sum(np.sin(2*np.pi*146.83*h*tt)/h for h in range(1,8))+sum(np.sin(2*np.pi*220*h*tt)/h for h in range(1,6))
    add(saw*np.exp(-tt*9)*.05,b); add(band(rs.standard_normal(n),300,3000)*np.exp(-tt*12)*.12,b)
# flatline + heartbeat
n=int(.45*SR); tt=np.arange(n)/SR; add(np.sin(2*np.pi*1000*tt)*.03*np.minimum(1,tt/.01),16.27)
for hb in [16.7,16.95]:
    n=int(.3*SR); tt=np.arange(n)/SR; add(np.sin(2*np.pi*(50+40*np.exp(-tt*25))*tt)*np.exp(-tt*14)*.5,hb); add(np.sin(2*np.pi*1000*tt[:int(.08*SR)])*.03,hb)
# lamp-room clock ticks
for tk in np.arange(14.9,16.0,.25):
    n=int(.03*SR); tt=np.arange(n)/SR; add(band(rs.standard_normal(n),2000,8000)*np.exp(-tt*150)*.06,tk,1,.3)
# fall whoosh
w=sweepnoise(.45,300,4000,.4)*np.linspace(0,1,int(.45*SR))**2; add(w*.25,15.8)
def drum(g):
    n=int(.35*SR); tt=np.arange(n)/SR; f=55+60*np.exp(-tt*30); return (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*9)+band(rs.standard_normal(n),80,900)*np.exp(-tt*35)*.3)*g
def shaker(g):
    n=int(.08*SR); tt=np.arange(n)/SR; return band(rs.standard_normal(n),5000,14000)*np.exp(-tt*55)*g
for lo,hi in [(2.6,7.6),(12.4,14.8),(17.4,19.6),(22.8,25.0)]:
    for b in np.arange(lo,hi,0.5):
        r=min(1,(b-2.6)/3); acc=1.3 if int(round(b*2))%4==0 else 1
        add(drum(.22*r*acc),b); add(shaker(.06*r),b+.25,1,.5 if int(b*2)%2 else -.5)
# accelerating footsteps on the running track
tk=19.65; gap=.32
while tk<20.6: add(drum(.14),tk); tk+=gap; gap=max(.1,gap*.85)
for b in [25.05,25.55,26.1]: add(drum(.28),b)
for a,b in [(12.95,13.25),(14.45,14.75),(17.6,19.2),(23.0,24.25)]:
    n=int((b-a+.5)*SR); x=band(rs.standard_normal(n),150,1800); e=np.sin(np.pi*np.arange(n)/n)**2; add(x*e*.05,a,1,-.3)
for ht,s in HITS:
    n=int(1.6*SR); tt=np.arange(n)/SR; hard=16.2<ht<16.3
    f=38+(140 if hard else 90)*np.exp(-tt*18); sub=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*(3.2 if s>1 else 5))
    nz=band(rs.standard_normal(n),40,2500 if s<1 else 6000)*np.exp(-tt*(20 if hard else 14))*(.9 if hard else .6)
    cl=band(rs.standard_normal(n),2500,12000)*np.exp(-tt*60)*(.6 if hard else .4)
    add((sub+nz+cl)*.32*s,ht)
for ct in [2.6,5.0,7.6,9.8,12.4,14.8,17.4,19.6,22.8,25.0]:
    w=sweepnoise(.35,500,5000,.35)*np.hanning(int(.35*SR))**.7; add(w*.10,ct-.33,1,-.6)
for a,b in [(1.9,2.6),(4.7,5.25),(7.5,8.0),(9.3,9.8),(26.7,27.4)]:
    w=sweepnoise(b-a,200,7000,.4); n=len(w); w*=(np.arange(n)/n)**2.2; add(w*.2,a)
    tt=np.arange(n)/SR; add(np.sin(2*np.pi*np.cumsum(240*2**(2*tt/(b-a)))/SR)*(np.arange(n)/n)**3*.045,a)
ir_n=int(2.4*SR); ir=rs.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR*2.6); ir[:int(.02*SR)]=0; ir/=np.sqrt((ir**2).sum())
def conv(x):
    m=len(x)+ir_n; F=1<<(m-1).bit_length(); return np.fft.irfft(np.fft.rfft(x,F)*np.fft.rfft(ir,F),F)[:len(x)]
L2=L+.33*conv(L); R2=R+.33*conv(np.roll(R,240))
st=np.stack([L2,R2],1); st=np.tanh(st/np.abs(st).max()*1.6); st/=np.abs(st).max(); st*=.89
st*=np.clip((D-t)/.6,0,1)[:,None]
with wave.open('audio5.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
print('ok')
