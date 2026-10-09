import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const here=path.dirname(fileURLToPath(import.meta.url)),out=path.join(here,process.argv[2]||'output-first');
if(fs.existsSync(out))throw new Error('Output exists; choose a new checkpoint.');fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch();try{const page=await browser.newPage({viewport:{width:1600,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.join(here,'index.html')).href);await page.waitForFunction(()=>window.ready);
for(const [name,options]of [['enamel',{}],['flat',{flat:true}],['blue',{palette:1}],['W',{glyph:'W'}]]){const data=await page.evaluate(options=>{WildRenderer.draw(document.querySelector('#art'),0,options);return document.querySelector('#art').toDataURL().split(',')[1]},options);fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(data,'base64'))}
await page.evaluate(()=>{document.querySelector('#mode').value='enamel';document.querySelector('#mode').dispatchEvent(new Event('change'))});await page.screenshot({path:path.join(out,'comparison.png'),fullPage:true});
await page.evaluate(src=>{document.querySelector('img').src=src},'data:image/png;base64,'+fs.readFileSync(path.join(here,'output/wild-hours-reference-01.png')).toString('base64'));
await page.waitForFunction(()=>document.querySelector('img').complete&&document.querySelector('img').naturalWidth>0);
for(const [name,crop]of [['W-head',[0,10,420,340]],['W-join',[340,100,280,500]],['serifs',[700,170,400,400]],['Hours',[190,560,1190,425]]]){
 const data=await page.evaluate(({crop})=>{const [x,y,w,h]=crop,c=document.createElement('canvas');c.width=w*2;c.height=h;const g=c.getContext('2d');g.drawImage(document.querySelector('img'),x,y,w,h,0,0,w,h);g.drawImage(document.querySelector('#art'),x,y,w,h,w,0,w,h);return c.toDataURL().split(',')[1]},{crop});fs.writeFileSync(path.join(out,name+'-compare.png'),Buffer.from(data,'base64'));
}
const overlay=await page.evaluate(()=>{const c=document.createElement('canvas');c.width=1536;c.height=1024;const g=c.getContext('2d');g.drawImage(document.querySelector('img'),0,0);g.strokeStyle='#00ffe4';g.lineWidth=1.5;for(const shape of WildGeometry)g.stroke(new Path2D(shape.d));return c.toDataURL().split(',')[1]});fs.writeFileSync(path.join(out,'outline-overlay.png'),Buffer.from(overlay,'base64'));
const source=path.join(out,'source');fs.mkdirSync(source);for(const f of ['geometry.js','details.js','renderer.js','index.html','render.mjs'])fs.copyFileSync(path.join(here,f),path.join(source,f));
fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({errors,shapes:await page.evaluate(()=>WildRenderer.shapes)},null,2));if(errors.length)throw new Error(errors.join('\n'));console.log(out);
}finally{await browser.close()}
