import numpy as np, wave, json
SR=48000; D=30.0; N=int(SR*D); t=np.arange(N)/SR; rs=np.random.default_rng(12)
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
HITS=json.load(open('hits4.json'))['hits']
C={'A5':[110,164.81,220,329.63],'Am':[110,164.81,220,261.63,329.63],'Dm':[73.42,146.83,220,293.66,349.23],'F':[87.31,174.61,261.63,349.23,440],
   'G':[98,146.83,196,246.94,293.66,392],'C':[65.41,130.81,196,261.63,329.63,392],'E':[82.41,123.47,164.81,207.65,246.94,329.63],
   'A':[110,164.81,220,277.18,329.63,440,554.37,659.25]}
PROG=[(0,2.6,'A5',.6),(2.6,3.2,'Am',1),(3.2,4.6,'Dm',1.1),(4.6,6.25,'Am',1),(6.25,7.0,'F',1.1),(7.0,8.35,'Dm',1),(8.35,9.4,'E',1.2),
      (9.4,10.3,'F',1),(10.3,11.6,'G',1.2),(11.6,12.3,'C',1.1),(12.3,13.0,'G',1.2),(13.0,13.8,'Am',1),(13.8,14.55,'F',1),(14.55,15.4,'Am',.6),
      (15.4,16.1,'E',1.3),(16.1,17.0,'A',1.2),(17.0,18.0,'Dm',1),(18.0,19.2,'F',1),(19.2,20.45,'Am',1),(20.45,22.0,'E',1.1),(22.0,22.7,'C',1),
      (22.7,23.15,'F',1.1),(23.15,24.6,'G',1.2),(24.6,25.8,'F',1),(25.8,26.5,'G',1.1),(26.5,27.0,'E',1.2),(27.0,30.0,'A',1.3)]
for a,b,ch,g in PROG:
    n=int((b-a+.5)*SR); tt=np.arange(n)/SR; e=np.minimum(1,tt/.25)*np.clip((b-a+.5-tt)/.5,0,1)
    if a==27.0: e=np.minimum(1,tt/.4)*np.exp(-tt*.15)*np.clip((D-a-tt)/.8,0,1)
    for fr in C[ch]:
        for det,pan in [(.0016,-.45),(-.0016,.45)]:
            w=np.sin(2*np.pi*fr*(1+det)*tt)+.28*np.sin(2*np.pi*fr*2*(1+det)*tt)+.1*np.sin(2*np.pi*fr*3*tt)
            add(w*e*(.024 if fr>200 else .036)*g,a,1,pan)
def bells(st,frs,gap=.11,g=.05):
    for k,fr in enumerate(frs):
        s=st+k*gap; tt=np.arange(int(min(3.5,D-s)*SR))/SR
        add((np.sin(2*np.pi*fr*tt)+.4*np.sin(2*np.pi*fr*2.76*tt)*np.exp(-tt*6))*np.exp(-tt*1.6)*g,s,1,(-1)**k*.6)
bells(1.3,[880,1318.5,1760],.09,.035); bells(10.3,[783.99,987.77,1174.66,1567.98]); bells(12.3,[783.99,1174.66,1567.98],.12,.05)
bells(16.1,[880,1108.7,1318.5,1760]); bells(23.15,[783.99,987.77,1174.66]); bells(27.2,[880,1108.7,1318.5,1760,2217.5,2637],.13,.05)
# hymn hummed in the prison (16:25)
for k,(fr,d) in enumerate([(440,.18),(523.25,.18),(587.33,.18),(659.25,.3)]):
    st=14.6+sum(x[1] for x in [(0,.18),(0,.18),(0,.18),(0,.3)][:k]); tt=np.arange(int((d+.3)*SR))/SR
    add((np.sin(2*np.pi*fr*tt)+.2*np.sin(2*np.pi*fr*2*tt))*np.minimum(1,tt/.05)*np.exp(-tt*2.2)*.05,st,1,.2)
# earthquake rumble
n=int(1.0*SR); tt=np.arange(n)/SR; add(band(rs.standard_normal(n),20,140)*np.exp(-tt*2.6)*np.minimum(1,tt/.02)*.9,15.4)
def drum(g):
    n=int(.35*SR); tt=np.arange(n)/SR; f=55+60*np.exp(-tt*30); return (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*9)+band(rs.standard_normal(n),80,900)*np.exp(-tt*35)*.3)*g
def shaker(g):
    n=int(.08*SR); tt=np.arange(n)/SR; return band(rs.standard_normal(n),5000,14000)*np.exp(-tt*55)*g
for b in np.arange(2.6,27.0,0.5):
    if 14.5<=b<16.1 or 9.4<=b<10.3: continue
    r=min(1,(b-2.6)/3); acc=1.3 if int(round(b*2))%4==0 else 1
    add(drum(.22*r*acc),b); add(shaker(.06*r),b+.25,1,.5 if int(b*2)%2 else -.5)
    if b>=24.6: add(shaker(.05),b+.125,1,-.4); add(shaker(.05),b+.375,1,.4)
for a,b in [(11.85,12.85),(18.55,19.15),(24.8,26.0)]:
    n=int((b-a+.5)*SR); x=band(rs.standard_normal(n),150,1800); e=np.sin(np.pi*np.arange(n)/n)**2; add(x*e*.06,a,1,-.3)
for ht,s in HITS:
    n=int(1.6*SR); tt=np.arange(n)/SR; hard=15.3<ht<15.8 or 8.3<ht<8.4
    f=38+(140 if hard else 90)*np.exp(-tt*18); sub=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*(3.2 if s>1 else 5))
    nz=band(rs.standard_normal(n),40,2500 if s<1 else 6000)*np.exp(-tt*(20 if hard else 14))*(.9 if hard else .6)
    cl=band(rs.standard_normal(n),2500,12000)*np.exp(-tt*60)*(.6 if hard else .4)
    add((sub+nz+cl)*.32*s,ht)
for ct in [2.6,4.6,7.0,9.4,11.6,13.8,17.0,19.2,22.0,24.6]:
    w=sweepnoise(.35,500,5000,.35)*np.hanning(int(.35*SR))**.7; add(w*.10,ct-.33,1,-.6)
for a,b in [(1.9,2.6),(9.8,10.3),(11.9,12.3),(15.0,15.4),(19.95,20.45),(26.3,27.0)]:
    w=sweepnoise(b-a,200,7000,.4); n=len(w); w*=(np.arange(n)/n)**2.2; add(w*.2,a)
    tt=np.arange(n)/SR; add(np.sin(2*np.pi*np.cumsum(240*2**(2*tt/(b-a)))/SR)*(np.arange(n)/n)**3*.045,a)
ir_n=int(2.4*SR); ir=rs.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR*2.6); ir[:int(.02*SR)]=0; ir/=np.sqrt((ir**2).sum())
def conv(x):
    m=len(x)+ir_n; F=1<<(m-1).bit_length(); return np.fft.irfft(np.fft.rfft(x,F)*np.fft.rfft(ir,F),F)[:len(x)]
L2=L+.33*conv(L); R2=R+.33*conv(np.roll(R,240))
st=np.stack([L2,R2],1); st=np.tanh(st/np.abs(st).max()*1.6); st/=np.abs(st).max(); st*=.89
st*=np.clip((D-t)/.6,0,1)[:,None]
with wave.open('audio4.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
print('ok')
