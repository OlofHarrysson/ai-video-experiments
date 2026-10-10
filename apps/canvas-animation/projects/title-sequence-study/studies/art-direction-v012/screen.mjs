import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const here=path.dirname(fileURLToPath(import.meta.url));
const {chromium}=createRequire(path.join(here,'../../../../../../.agents/skills/animate/package.json'))('playwright');
const out=path.join(here,process.argv[2]||'output-review-v001');if(fs.existsSync(out))throw Error('Use a fresh output directory');fs.mkdirSync(out);
const browser=await chromium.launch();
try{
 const page=await browser.newPage({viewport:{width:1400,height:1060}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(here,'index.html')).href);
 for(const id of ['billions','next','keep-up']){await page.click(`[data-id="${id}"]`);await page.waitForFunction(()=>document.querySelector('#target').complete&&document.querySelector('#target').naturalWidth>0);}
 await page.screenshot({path:path.join(out,'desktop.png')});
 await page.click('[data-id="vector"]');const frame=page.frames().find(f=>f.url().endsWith('/next.html'));await frame.waitForFunction(()=>window.ready);
 const vectorReady=await frame.evaluate(()=>document.querySelector('canvas').width>1000);
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(out,'mobile.png')});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 const images=['billions','next','keep-up'].map(id=>({id,png:fs.readFileSync(path.join(here,'reference',id+'.png')).toString('base64')}));
 const sheet=await page.evaluate(async images=>{const c=document.createElement('canvas');c.width=2400;c.height=510;const g=c.getContext('2d');g.fillStyle='#171719';g.fillRect(0,0,c.width,c.height);for(const [i,a]of images.entries()){const img=new Image();img.src='data:image/png;base64,'+a.png;await img.decode();g.drawImage(img,i*800,0,800,450);g.fillStyle='white';g.font='21px sans-serif';g.fillText(a.id.toUpperCase()+' · generated target',i*800+18,487);}return c.toDataURL().split(',')[1]},images);
 fs.writeFileSync(path.join(out,'directions.png'),Buffer.from(sheet,'base64'));
 const report={passed:!errors.length&&!overflow&&vectorReady,errors,overflow,vectorReady,generatedTargetsLoaded:3};fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(!report.passed)throw Error('Review failed');
}finally{await browser.close();}
