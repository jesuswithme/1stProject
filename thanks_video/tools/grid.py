import sys
from PIL import Image
fs=sys.argv[2:]; cols=2; w,h=960,540
g=Image.new('RGB',(w*cols,h*((len(fs)+cols-1)//cols)),'black')
for i,f in enumerate(fs): g.paste(Image.open(f).resize((w,h)),((i%cols)*w,(i//cols)*h))
g.save(sys.argv[1],quality=85)
