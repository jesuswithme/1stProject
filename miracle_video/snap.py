import sys,asyncio,os
from playwright.async_api import async_playwright
from PIL import Image
async def main():
    ts=sys.argv[2:];out=sys.argv[1]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",args=["--allow-file-access-from-files"]); pg=await b.new_page(viewport={"width":1920,"height":1080})
        errs=[];pg.on("pageerror",lambda e:errs.append(str(e)));pg.on("console",lambda m:errs.append(m.text) if m.type=="error" else None)
        await pg.goto("file://"+os.path.abspath("index.html"));await pg.evaluate("document.fonts.ready");await pg.wait_for_timeout(600)
        ims=[]
        for t in ts:
            await pg.evaluate(f"setTime({t})");fn=f"snaps/s_{t}.jpg";await pg.screenshot(path=fn,type="jpeg",quality=80);ims.append(Image.open(fn).resize((960,540)))
        cols=2;rows=(len(ims)+1)//2;G=Image.new("RGB",(960*cols,540*rows))
        for i,im in enumerate(ims):G.paste(im,((i%cols)*960,(i//cols)*540))
        G.save(out,quality=82)
        print(errs[:5], await pg.evaluate("TOTAL"))
        await b.close()
asyncio.run(main())
