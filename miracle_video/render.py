import sys,asyncio,subprocess,time,base64,os
from playwright.async_api import async_playwright
FPS=30
async def main(i0,i1,out):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",args=["--allow-file-access-from-files"]); pg=await b.new_page(viewport={"width":1920,"height":1080})
        await pg.goto("file://"+os.path.abspath("index.html"));await pg.evaluate("document.fonts.ready");await pg.wait_for_timeout(800)
        ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","image2pipe","-framerate",str(FPS),"-c:v","mjpeg","-i","-","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
        cdp=await pg.context.new_cdp_session(pg); t0=time.time()
        for f in range(i0,i1):
            await pg.evaluate(f"setTime({f/FPS})")
            r=await cdp.send("Page.captureScreenshot",{"format":"jpeg","quality":92})
            ff.stdin.write(base64.b64decode(r["data"]))
            if f%150==0: print(out,f,round(time.time()-t0,1),flush=True)
        ff.stdin.close();ff.wait();await b.close();print("DONE",out,flush=True)
asyncio.run(main(int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]))
