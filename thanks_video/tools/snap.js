// 사용법: node tools/snap.js t1 t2 ...  → snaps/snap_<t>.jpg
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1920,height:1080}});
const errs=[];pg.on('pageerror',e=>errs.push(String(e)));pg.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await pg.goto('file://'+path.resolve('index.html'));await pg.waitForTimeout(800);
fs.mkdirSync('snaps',{recursive:true});
for(const t of process.argv.slice(2)){await pg.evaluate(`setTime(${t})`);await pg.screenshot({path:`snaps/snap_${t}.jpg`,type:'jpeg',quality:80})}
console.log(errs.slice(0,5),await pg.evaluate('TOTAL'));await b.close()})();
