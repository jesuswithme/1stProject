import numpy as np, wave
SR=48000; D=15.0; N=int(SR*D); t=np.arange(N)/SR; rs=np.random.default_rng(5)
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
def tone(fr,dur,det=0.):
    tt=np.arange(int(dur*SR))/SR; return np.sin(2*np.pi*fr*(1+det)*tt)+.3*np.sin(2*np.pi*fr*2*(1+det)*tt)+.12*np.sin(2*np.pi*fr*3*tt)
HITS=[(0.1,.3),(1.5,1),(3.2,.8),(3.86,1.1),(4.6,.7),(5.6,.9),(7.0,.7),(7.55,1.1),(8.0,.6),(8.4,.9),(8.95,.7),(9.1,.8),(9.25,1),(9.4,1.2),(10.6,.6),(12.0,1.3),(13.12,.5)]
# pad E minor (silenced in the dark 9.45-9.9), E major at the door
mi=[82.41,123.47,164.81,196.0,246.94,329.63]; ma=[82.41,123.47,164.81,207.65,246.94,329.63,415.3,493.88]
d1=12.0; tt=np.arange(int(d1*SR))/SR
pe=np.minimum(1,tt/2.0)*(.5+.5*tt/d1)*(1-.95*np.exp(-((tt-9.75)/.35)**4*1.0))
for fr in mi:
    g=.032 if fr>200 else .048; add(tone(fr,d1,.0015)*pe*g,0,1,-.4); add(tone(fr,d1,-.0015)*pe*g,0,1,.4)
d2=3.0; tt=np.arange(int(d2*SR))/SR; pe2=np.minimum(1,tt/.4)*np.exp(-tt*.25)*np.clip((d2-tt)/.6,0,1)
for fr in ma: add(tone(fr,d2,.002)*pe2*.055,12.0,1,-.5); add(tone(fr,d2,-.002)*pe2*.055,12.0,1,.5)
for k,fr in enumerate([659.25,830.61,987.77,1318.5,1661.2,1975.5]):
    st=12.3+k*.12; tt=np.arange(int((D-st)*SR))/SR
    add((np.sin(2*np.pi*fr*tt)+.4*np.sin(2*np.pi*fr*2.76*tt)*np.exp(-tt*6))*np.exp(-tt*1.5)*.05,st,1,(-1)**k*.6)
# journey pulse: frame-drum on beats (120bpm), shaker on off-beats; drops out 9.4-10.6
def drum(g):
    n=int(.35*SR); tt=np.arange(n)/SR; f=55+60*np.exp(-tt*30); return (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*9)+band(rs.standard_normal(n),80,900)*np.exp(-tt*35)*.3)*g
def shaker(g):
    n=int(.08*SR); tt=np.arange(n)/SR; return band(rs.standard_normal(n),5000,14000)*np.exp(-tt*55)*g
for b in np.arange(1.5,12.0,0.5):
    if 9.4<=b<10.6: continue
    ramp=min(1,(b-1.5)/2)
    add(drum(.22*ramp*(1.3 if int(b*2)%4==0 else 1)),b); add(shaker(.06*ramp),b+.25,1,.5 if int(b*2)%2 else -.5)
# rise in the dark: soft swell 10.0-10.6
n=int(.7*SR); tt=np.arange(n)/SR
for fr in [164.81,246.94,329.63]: add(np.sin(2*np.pi*fr*tt)*(tt/.7)**2*.05,9.9)
# tinnitus after the stones
n=int(1.0*SR); tt=np.arange(n)/SR; add(np.sin(2*np.pi*3800*tt)*np.exp(-tt*2.5)*np.minimum(1,tt/.03)*.035,9.45)
# sea swells on voyages
for a,b in [(1.95,2.6),(4.65,5.05),(11.45,11.95)]:
    n=int((b-a+.4)*SR); x=band(rs.standard_normal(n),150,1800); e=np.sin(np.pi*np.arange(n)/n)**2; add(x*e*.06,a,1,-.3)
# impacts (stones are drier and harder)
for ht,s in HITS:
    n=int(1.6*SR); tt=np.arange(n)/SR; stone=8.9<ht<9.5
    f=38+(140 if stone else 90)*np.exp(-tt*18); sub=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*(3.2 if s>1 else 5))
    nz=band(rs.standard_normal(n),40,2500 if s<1 else 6000)*np.exp(-tt*(25 if stone else 14))*(.9 if stone else .6)
    cl=band(rs.standard_normal(n),2500,12000)*np.exp(-tt*60)*(.7 if stone else .4)
    add((sub+nz+cl)*.32*s,ht,1,(rs.random()-.5)*.6 if stone else 0)
# whooshes + risers
for ct in [1.5,3.2,4.6,5.6,7.0,8.0,10.6]:
    w=sweepnoise(.35,500,5000,.35)*np.hanning(int(.35*SR))**.7; add(w*.10,ct-.33,1,-.6)
for a,b in [(5.0,5.6),(7.15,7.55),(11.2,12.0)]:
    w=sweepnoise(b-a,200,7000,.4); n=len(w); w*=(np.arange(n)/n)**2.2; add(w*.22,a)
    tt=np.arange(n)/SR; add(np.sin(2*np.pi*np.cumsum(240*2**(2*tt/(b-a)))/SR)*(np.arange(n)/n)**3*.05,a)
ir_n=int(2.4*SR); ir=rs.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR*2.6); ir[:int(.02*SR)]=0; ir/=np.sqrt((ir**2).sum())
def conv(x):
    m=len(x)+ir_n; F=1<<(m-1).bit_length(); return np.fft.irfft(np.fft.rfft(x,F)*np.fft.rfft(ir,F),F)[:len(x)]
L2=L+.33*conv(L); R2=R+.33*conv(np.roll(R,240))
st=np.stack([L2,R2],1); st=np.tanh(st/np.abs(st).max()*1.6); st/=np.abs(st).max(); st*=.89
st*=np.clip((D-t)/.5,0,1)[:,None]
with wave.open('audio2.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
print('ok')
