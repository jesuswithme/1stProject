# 아바타 배경 제거 + 몸통/머리/턱 레이어 분리
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
im=Image.open('assets/avatar_src.png').convert('RGB'); W,H=im.size
work=im.filter(ImageFilter.GaussianBlur(1.5)).copy()
rects=[(290,100,810,710),(360,640,770,1180),(290,1150,820,1320)]
def inside(x,y): return any(a<=x<=c and b<=y<=d for a,b,c,d in rects)
MAG=(255,0,255)
seeds=[(x,y) for y in range(3,H,18) for x in range(3,W,18) if not inside(x,y)]+[(567,1102),(565,1085)]
for s in seeds:
    if work.getpixel(s)!=MAG: ImageDraw.floodfill(work,s,MAG,thresh=14)
a=np.array(work); bg=(a[:,:,0]==255)&(a[:,:,1]==0)&(a[:,:,2]==255)
m=Image.fromarray(((~bg)*255).astype(np.uint8))
d=ImageDraw.Draw(m); cx,rx=555.5,251
d.ellipse((cx-rx,1160,cx+rx,1264),fill=255); d.rectangle((cx-rx,1212,cx+rx,1262),fill=255); d.ellipse((cx-rx,1210,cx+rx,1314),fill=255)
m=m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(3))
ImageDraw.floodfill(m,(555,400),128); m=m.point(lambda v:255 if v==128 else 0)
inv=m.copy(); ImageDraw.floodfill(inv,(0,0),77)
# 다리 사이 틈(배경)은 구멍 메우기에서 제외
hole=inv.point(lambda v:255 if v==0 else 0)
gap=Image.new('L',(W,H),0); ImageDraw.floodfill_img=None
m=inv.point(lambda v:0 if v==77 else 255)
gm=np.array(m); gh=np.array(hole)>0
# 다리 사이 구멍(라벨링 대신 해당 좌표의 구멍만 제거)
tmp=Image.fromarray((gh*255).astype(np.uint8)); ImageDraw.floodfill(tmp,(567,1102),128) if tmp.getpixel((567,1102))==255 else None
gm[np.array(tmp)==128]=0; m=Image.fromarray(gm)
m=m.filter(ImageFilter.GaussianBlur(1.3))
full=im.copy(); full.putalpha(m)
X0,Y0=297,102; X1,Y1=827,1323
full=full.crop((X0,Y0,X1,Y1)); w,h=full.size
full.save('assets/avatar.png')
def band(y0,y1,f0,f1):
    # y0~y1 영역 불투명, f0/f1 폭으로 위/아래 페더
    g=np.zeros(h,np.float32); ys=np.arange(h)
    g=np.clip((ys-(y0-f0))/max(f0,1),0,1)*np.clip(((y1+f1)-ys)/max(f1,1),0,1)
    return g
A=np.array(full).astype(np.float32)
def save(name,g2d):
    B=A.copy(); B[:,:,3]*=g2d; Image.fromarray(B.astype(np.uint8)).save('assets/'+name)
ones=np.ones(w)
waist=945-Y0; neck=700-Y0
save('av_lower.png',np.outer(band(waist-30,h+50,1,1),ones))
save('av_torso.png',np.outer(band(neck-120,waist,1,22),ones))
save('av_head.png',np.outer(band(-50,neck-40,1,30),ones))
# 턱(아랫입술~턱) 레이어
jm=Image.new('L',(w,h),0); dj=ImageDraw.Draw(jm)
lip=[(500,582),(520,585),(560,587),(600,584),(630,578),(652,570)]
poly=[(x-X0,y-Y0) for x,y in lip]+[(x-X0,y-Y0) for x,y in [(690,600),(700,640),(660,690),(560,705),(460,690),(415,640),(425,595)]]
dj.polygon(poly,fill=255)
jm=jm.filter(ImageFilter.GaussianBlur(5))
# 입술선은 선명하게
sharp=Image.new('L',(w,h),0); ds=ImageDraw.Draw(sharp)
ds.polygon([(x-X0,y-Y0) for x,y in lip]+[(652-X0,600-Y0),(500-X0,605-Y0)],fill=255)
jm=Image.fromarray(np.maximum(np.array(jm),np.array(sharp)))
J=A.copy(); J[:,:,3]*=np.array(jm)/255.0
Image.fromarray(J.astype(np.uint8)).save('assets/av_jaw.png')
print(w,h,'waist',waist,'neck',neck,'lipY',585-Y0,'lipX',575-X0)
