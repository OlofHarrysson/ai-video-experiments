import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const here=path.dirname(fileURLToPath(import.meta.url)),out=path.join(here,process.argv[2]||'output-proof');
if(fs.existsSync(out))throw Error('Output exists; use a new checkpoint.');fs.mkdirSync(out,{recursive:true});
const files=['../../node_modules/clipper-lib/clipper.js','../image-to-code-v006/vector-fields.js','geometry.js','highlights.js','art.js'];
const browser=await chromium.launch();
try{
 const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.setContent('<canvas width="1600" height="1000"></canvas>');
 for(const f of files)await page.addScriptTag({content:fs.readFileSync(path.join(here,f),'utf8')});
 const list=[];
 for(const id of ['script','machine','tuscan','liquid'])for(const flat of [true,false]){
  const start=Date.now();const png=await page.evaluate(({id,flat})=>{const c=document.querySelector('canvas');LetteringArt.card(c,id,.25,{flat});return c.toDataURL().split(',')[1]},{id,flat});
  const name=id+(flat?'-flat':'');fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(png,'base64'));list.push({name,png});console.log(name,Date.now()-start+'ms');
 }
 const sheet=await page.evaluate(async list=>{const c=document.createElement('canvas');c.width=1600;c.height=1050;const g=c.getContext('2d');g.fillStyle='#111';g.fillRect(0,0,c.width,c.height);for(let i=0;i<list.length;i++){const img=new Image();img.src='data:image/png;base64,'+list[i].png;await img.decode();const x=Math.floor(i/2)%2*800,y=Math.floor(i/4)*525; if(i%2)g.drawImage(img,x,y,800,500);}return c.toDataURL().split(',')[1]},list);
 fs.writeFileSync(path.join(out,'material-sheet.png'),Buffer.from(sheet,'base64'));
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({errors,segments:await page.evaluate(()=>Object.fromEntries(Object.entries(LetteringArt.shapes).map(([k,v])=>[k,v.segmentCount])))},null,2));
 const source=path.join(out,'source');fs.mkdirSync(source);for(const f of files.slice(2))fs.copyFileSync(path.join(here,f),path.join(source,path.basename(f)));
 if(errors.length)throw Error(errors.join('\n'));
}finally{await browser.close();}
