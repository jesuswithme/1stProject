const {chromium}=require('/opt/node22/lib/node_modules/playwright');
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1920,height:1080}});
const errs=[];pg.on('pageerror',e=>errs.push(String(e)));pg.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
const t0=Date.now();await pg.goto('file://'+process.cwd()+'/index.html');await pg.waitForTimeout(800);console.log('load ms',Date.now()-t0);
for(const t of process.argv.slice(2)){await pg.evaluate(`setTime(${t})`);await pg.screenshot({path:`snaps/s_${t}.jpg`,type:'jpeg',quality:80})}
console.log(errs.slice(0,5));await b.close()})();
