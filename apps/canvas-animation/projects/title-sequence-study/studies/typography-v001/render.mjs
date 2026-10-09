// node studies/typography-v001/render.mjs [--motion]
// Uses the shared Animate Playwright installation. Outputs stay beside this study.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
const require = createRequire(new URL('../../../../../../.agents/skills/animate/package.json', import.meta.url));
const { chromium } = require('playwright');
const here=path.dirname(fileURLToPath(import.meta.url)), out=path.join(here,'output');
fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch();
try {
 const page=await b.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(here,'study.html')).href);
 await page.waitForFunction(()=>window.studyReady);
 const report=await page.evaluate(()=>{
   const {faces,identity}=window.TypographyStudy,c=document.createElement('canvas'),g=c.getContext('2d');
   return {identity,fonts:Object.fromEntries(Object.entries(faces).map(([k,f])=>{
     g.font=`100px "${f}", monospace`;const actual=g.measureText('Hamburgefonts0123').width;
     g.font='100px monospace';return [k,{family:f,distinctFromFallback:Math.abs(actual-g.measureText('Hamburgefonts0123').width)>1}];
   }))};
 });
 if(Object.values(report.fonts).some(f=>!f.distinctFromFallback))throw new Error('A required font resolves to fallback: '+JSON.stringify(report.fonts));
 const data=async(i,t)=>page.evaluate(([i,t])=>{const c=document.createElement('canvas');c.width=1280;c.height=544;TypographyStudy.render(i,t,c);return c.toDataURL('image/png').split(',')[1]},[i,t]);
 const sha=s=>createHash('sha256').update(Buffer.from(s,'base64')).digest('hex');
 report.frames=[];
 for(let i=0;i<report.identity.length;i++){
   const png=await data(i,0),moving=await data(i,.75),again=await data(i,0);
   if(sha(png)!==sha(again))throw new Error('Non-deterministic rendering: '+i);
   const file=`${String(i+1).padStart(2,'0')}.png`;fs.writeFileSync(path.join(out,file),Buffer.from(png,'base64'));
   report.frames.push({id:i+1,file,sha256:sha(png),deterministic:true,changesAt075:sha(png)!==sha(moving)});
 }
 // Gallery sheets are original artwork only, never reference pixels.
 for(const [name,ids,cols,cellW] of [
   ['all-identities',[0,1,2,3,4,5,6,7,8,9,10,11],3,480],
   ['shortlist',[0,1,4,10],2,640],
   ['geometric',[0,5,6,7],2,640],
   ['lettering',[2,3,4,11],2,640],
 ]){
   const png=await page.evaluate(({ids,cols,cellW})=>{
     const ch=cellW*544/1280,lh=42,c=document.createElement('canvas');c.width=cols*cellW;c.height=Math.ceil(ids.length/cols)*(ch+lh);
     const g=c.getContext('2d');g.fillStyle='#151515';g.fillRect(0,0,c.width,c.height);
     ids.forEach((id,n)=>{const tile=document.createElement('canvas');tile.width=1280;tile.height=544;TypographyStudy.render(id,0,tile);
       const x=n%cols*cellW,y=Math.floor(n/cols)*(ch+lh);g.drawImage(tile,x,y,cellW,ch);
       g.fillStyle='#eee';g.font='16px system-ui';g.fillText(TypographyStudy.identity[id][0]+'  '+TypographyStudy.identity[id][1],x+16,y+ch+27);
     });return c.toDataURL('image/png').split(',')[1];
   },{ids,cols,cellW});fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(png,'base64'));
 }
 await page.screenshot({path:path.join(out,'study-page.png'),fullPage:true});
 if(process.argv.includes('--motion')){
   const ids=[0,4,7,10],fps=24,seconds=3,frames=path.join(out,'motion-frames');fs.mkdirSync(frames,{recursive:true});
   for(let f=0;f<ids.length*seconds*fps;f++){
     const i=ids[Math.floor(f/(fps*seconds))],t=(f%(fps*seconds))/fps;
     fs.writeFileSync(path.join(frames,`f${String(f).padStart(4,'0')}.png`),Buffer.from(await data(i,t),'base64'));
   }
   const r=spawnSync('ffmpeg',['-v','error','-y','-framerate',String(fps),'-i',path.join(frames,'f%04d.png'),'-frames:v',String(ids.length*seconds*fps),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,'motion-proof.mp4')],{stdio:'inherit'});
   if(r.status!==0)throw new Error('Motion encoding failed');
   report.motion={ids:ids.map(i=>i+1),fps,duration:ids.length*seconds,audio:false};
 }
 if(errors.length)throw new Error(errors.join('\n'));
 fs.writeFileSync(path.join(out,'render-report.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({output:out,identities:report.frames.length,deterministic:report.frames.every(f=>f.deterministic),fonts:report.fonts,motion:report.motion},null,2));
} finally {await b.close()}
