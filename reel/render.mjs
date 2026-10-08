import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { spawn } from 'child_process';
const [,, mode, arg] = process.argv;
const browser = await chromium.launch({ args: ['--disable-web-security'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('console', m => console.log('page:', m.text())); page.on('pageerror', e => console.log('ERR', e.message));
await page.goto('http://127.0.0.1:8765/' + (process.env.PAGE||'reel.html'));
console.log('pts', await page.evaluate(() => window.ready));
const grab = async t => Buffer.from((await page.evaluate(t => { render(t); return document.getElementById('c').toDataURL('image/jpeg', .96); }, t)).split(',')[1], 'base64');
if (mode === 'stills') {
  const fs = await import('fs');
  for (const t of arg.split(',').map(Number)) fs.writeFileSync(`still_${t.toFixed(2)}.jpg`, await grab(t));
} else {
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '60', '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', process.env.OUT||'video.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  const NF = +(process.env.FRAMES||900); for (let f = 0; f < NF; f++) { const b = await grab(f / 60); if (!ff.stdin.write(b)) await new Promise(r => ff.stdin.once('drain', r)); if (f % 100 === 0) console.log('frame', f, ((Date.now() - t0) / 1000).toFixed(1) + 's'); }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await browser.close();
