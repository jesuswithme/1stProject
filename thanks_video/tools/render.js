// 사용법: node tools/render.js f0 f1 out.mp4  (30fps, setTime(f/30) 프레임 캡처 → ffmpeg)
const {chromium}=require('playwright');const path=require('path');const {spawn}=require('child_process');
(async()=>{const [f0,f1,out]=[+process.argv[2],+process.argv[3],process.argv[4]];
const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1920,height:1080}});
await pg.goto('file://'+path.resolve('index.html'));await pg.waitForTimeout(1000);
const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p','-r','30',out],{stdio:['pipe','inherit','inherit']});
const cdp=await pg.context().newCDPSession(pg);const t0=Date.now();
for(let f=f0;f<f1;f++){await pg.evaluate(`setTime(${f/30})`);
 const r=await cdp.send('Page.captureScreenshot',{format:'jpeg',quality:95});
 if(!ff.stdin.write(Buffer.from(r.data,'base64')))await new Promise(r=>ff.stdin.once('drain',r));
 if(f%150===0)console.log(out,f,((Date.now()-t0)/1000).toFixed(1));}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('done',out)})();
