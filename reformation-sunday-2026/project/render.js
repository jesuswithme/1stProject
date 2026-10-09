const {chromium}=require('/opt/node22/lib/node_modules/playwright');const {spawn}=require('child_process');
const [i0,i1,out]=[+process.argv[2],+process.argv[3],process.argv[4]];const FPS=30;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1920,height:1080}});
await pg.goto('file://'+process.cwd()+'/index.html');await pg.waitForTimeout(1000);
const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',''+FPS,'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',out]);
const cdp=await pg.context().newCDPSession(pg);const t0=Date.now();
for(let f=i0;f<i1;f++){await pg.evaluate(`setTime(${f/FPS})`);const r=await cdp.send('Page.captureScreenshot',{format:'jpeg',quality:93});
 const buf=Buffer.from(r.data,'base64');if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
 if(f%300==0)console.log(out,f,((Date.now()-t0)/1000).toFixed(0)+'s');}
ff.stdin.end();await new Promise(r=>ff.on('close',r));console.log('DONE',out,((Date.now()-t0)/1000).toFixed(0));await b.close()})();
