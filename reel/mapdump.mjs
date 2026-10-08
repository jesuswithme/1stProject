import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
const b = await chromium.launch(); const p = await b.newPage();
await p.goto('http://127.0.0.1:8765/' + process.env.PAGE); await p.evaluate(() => window.ready);
const d = await p.evaluate(() => { const c = document.createElement('canvas'); c.width = 1400; c.height = Math.round(1400 * mapC.height / mapC.width); c.getContext('2d').drawImage(mapC, 0, 0, c.width, c.height); return c.toDataURL('image/jpeg', .9); });
fs.writeFileSync('map.jpg', Buffer.from(d.split(',')[1], 'base64')); await b.close();
