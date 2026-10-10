import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import crypto from 'node:crypto';
const here=path.dirname(fileURLToPath(import.meta.url));
const {chromium}=createRequire(path.join(here,'../../../../../../.agents/skills/animate/package.json'))('playwright');
const out=path.join(here,process.argv[2]||'output-board-v001');
if(fs.existsSync(out))throw Error('Choose a new output directory');fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch();
try{
 const page=await browser.newPage({viewport:{width:1440,height:1060}}),errors=[],network=[];
 page.on('pageerror',e=>errors.push(e.message));await page.route(/^https?:/,r=>{network.push(r.request().url());r.abort()});
 await page.goto(pathToFileURL(path.join(here,'index.html')).href);await page.waitForFunction(()=>window.ready);
 const descriptions=await page.evaluate(()=>KeepUpArt.descriptions),frames=[];
 for(const frame of descriptions){
  await page.selectOption('#frame',frame.id);
  const png=await page.evaluate(()=>document.querySelector('canvas').toDataURL().split(',')[1]);
  fs.writeFileSync(path.join(out,frame.id+'.png'),Buffer.from(png,'base64'));frames.push({...frame,png});
 }
 const board=await page.evaluate(async frames=>{
  const c=document.createElement('canvas');c.width=2400;c.height=1020;const g=c.getContext('2d');g.fillStyle='#1b1b1e';g.fillRect(0,0,c.width,c.height);
  for(let i=0;i<frames.length;i++){const img=new Image();img.src='data:image/png;base64,'+frames[i].png;await img.decode();const x=(i%3)*800,y=Math.floor(i/3)*510;g.drawImage(img,x,y,800,450);g.fillStyle='#eee';g.font='20px sans-serif';g.fillText(frames[i].label+'  /  '+frames[i].time,x+20,y+485);}
  return c.toDataURL().split(',')[1];
 },frames);
 fs.writeFileSync(path.join(out,'storyboard.png'),Buffer.from(board,'base64'));
 const first=await page.evaluate(()=>{show('title');return document.querySelector('canvas').toDataURL()});
 const second=await page.evaluate(()=>{show('money');show('title');return document.querySelector('canvas').toDataURL()});
 await page.click('#next');const next=await page.inputValue('#frame');await page.click('#prev');const previous=await page.inputValue('#frame');
 await page.screenshot({path:path.join(out,'desktop.png')});
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(out,'mobile.png')});
 const mobileOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 const html=fs.readFileSync(path.join(here,'index.html'),'utf8');
 const noRasterRuntime=!/data:image|<img|new Image|drawImage/.test(html);
 const source=path.join(out,'source');fs.mkdirSync(source);for(const file of ['art.js','build.mjs','screen.mjs','lettering.json','index.html'])fs.copyFileSync(path.join(here,file),path.join(source,file));
 const report={passed:errors.length===0&&network.length===0&&first===second&&!mobileOverflow&&noRasterRuntime&&next==='opening'&&previous==='title',
  errors,network,deterministic:first===second,mobileOverflow,noRasterRuntime,controls:{next,previous},frames:frames.length,
  indexSha256:crypto.createHash('sha256').update(html).digest('hex'),notes:'Static frames and proposed timings only; animation and continuous rhythm not evaluated.'};
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(!report.passed)throw Error('Screening failed');
}finally{await browser.close();}
