import sys
from PIL import Image
fs=sys.argv[2:];out=sys.argv[1];cols=2;rows=(len(fs)+1)//2
G=Image.new('RGB',(960*cols,540*rows+0),(40,40,40))
for i,f in enumerate(fs):
    im=Image.open(f).resize((956,538));G.paste(im,((i%cols)*960+2,(i//cols)*540+1))
G.save(out,quality=85)
