import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const b = await chromium.launch(); const p = await b.newPage();
await p.goto('http://127.0.0.1:8765/reel3.html'); await p.evaluate(() => window.ready);
console.log(JSON.stringify(await p.evaluate(() => ({ hits: window.HITS, segs: window.SEGS })))); await b.close();
