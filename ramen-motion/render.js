// 사용법: node render.js            -> ramen_motion.mp4 생성
//        node render.js --stills 2,5,9  -> 지정 시각 PNG 미리보기
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30, DUR = 19.584;
const dir = __dirname;
const audio = path.join(dir, 'narration.m4a');
const out = path.join(dir, 'ramen_motion.mp4');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(dir, 'scene.html'));
  const grab = async t => {
    const url = await page.evaluate(t => { renderFrame(t); return document.getElementById('c').toDataURL('image/png'); }, t);
    return Buffer.from(url.split(',')[1], 'base64');
  };

  const si = process.argv.indexOf('--stills');
  if (si > 0) {
    fs.mkdirSync(path.join(dir, 'stills'), { recursive: true });
    for (const t of process.argv[si + 1].split(',').map(Number)) fs.writeFileSync(path.join(dir, 'stills', `t${t}.png`), await grab(t));
    await browser.close(); return;
  }

  const frames = Math.ceil(DUR * FPS);
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-i', audio,
    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-r', String(FPS), '-c:a', 'aac', '-b:a', '192k', '-t', String(DUR), '-movflags', '+faststart', out], { stdio: ['pipe', 'ignore', 'inherit'] });
  for (let i = 0; i < frames; i++) {
    const buf = await grab(i / FPS);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('done', out);
})();
