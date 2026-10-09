// 사용법: node render.js                  -> sermon_luke17_master.mp4 (python3 cut.py, python3 mix.py 먼저 실행)
//        node render.js --stills 3,12,40 -> stills/t*.png 미리보기
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30, DUR = JSON.parse(fs.readFileSync(path.join(__dirname, "timeline.js"), "utf8").replace(/^window.TL = /, "").replace(/;\s*$/, "")).dur;
const dir = __dirname;

(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-web-security'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', e => console.error('pageerror', e.message));
  await page.goto('file://' + path.join(dir, 'scene.html'));
  await page.evaluate(() => window.ready);
  const grab = async t => {
    const url = await page.evaluate(async t => { await renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.93); }, t);
    return Buffer.from(url.split(',')[1], 'base64');
  };
  const si = process.argv.indexOf('--stills');
  if (si > 0) {
    fs.mkdirSync(path.join(dir, 'stills'), { recursive: true });
    for (const t of process.argv[si + 1].split(',').map(Number)) fs.writeFileSync(path.join(dir, 'stills', `t${t}.jpg`), await grab(t));
    await browser.close(); return;
  }
  const frames = Math.round(DUR * FPS);
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-i', path.join(dir, 'audio.wav'),
    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
    '-t', String(DUR), '-movflags', '+faststart', path.join(dir, 'sermon_luke17_master.mp4')], { stdio: ['pipe', 'ignore', 'inherit'] });
  for (let i = 0; i < frames; i++) {
    const buf = await grab(i / FPS);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 600 === 0) console.log('frame', i);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('done');
})();
