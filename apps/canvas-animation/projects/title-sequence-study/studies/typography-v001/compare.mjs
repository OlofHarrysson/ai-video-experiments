// Generates comparison sheets containing reference pixels, exclusively in ignored references/.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const require=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url));
const {chromium}=require('playwright');
const here=path.dirname(fileURLToPath(import.meta.url)),project=path.resolve(here,'../..');
const map=JSON.parse(fs.readFileSync(path.join(here,'reference-map.json'),'utf8'));
const out=path.join(project,'references/inspection/typography-v001-comparisons');fs.mkdirSync(out,{recursive:true});
const rows=map.map(row=>{
 const folder=path.join(project,'references/inspection',row.inspection,'v001'),meta=JSON.parse(fs.readFileSync(path.join(folder,'review.json'),'utf8')),frame=meta.frames[row.frame];
 return {...row,time:frame.time_seconds,sourceFrame:frame.frame_number,ref:fs.readFileSync(path.join(folder,frame.file)).toString('base64'),ours:fs.readFileSync(path.join(here,'output',String(row.id).padStart(2,'0')+'.png')).toString('base64')};
});
const b=await chromium.launch();
try{
 const page=await b.newPage();
 for(let k=0;k<3;k++){
   const png=await page.evaluate(async rows=>{
     const c=document.createElement('canvas');c.width=1280;c.height=rows.length*322;const g=c.getContext('2d');g.fillStyle='#151515';g.fillRect(0,0,c.width,c.height);
     for(const [i,r]of rows.entries()){
       const y=i*322;
       for(const [x,data]of [[0,r.ref],[640,r.ours]]){const im=new Image();im.src='data:image/png;base64,'+data;await im.decode();g.drawImage(im,x,y+42,640,272)}
       g.fillStyle='#ddd';g.font='15px system-ui';const mm=Math.floor(r.time/60),ss=(r.time%60).toFixed(3).padStart(6,'0');
       g.fillText(`Reference ${mm}:${ss} · ${r.family}`,14,y+26);g.fillText(`Study ${String(r.id).padStart(2,'0')} · original lettering`,654,y+26);
     }return c.toDataURL('image/png').split(',')[1];
   },rows.slice(k*4,k*4+4));
   fs.writeFileSync(path.join(out,`comparison-${k+1}.png`),Buffer.from(png,'base64'));
 }
 fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(rows.map(({ref,ours,...rest})=>rest),null,2)+'\n');console.log(out);
}finally{await b.close()}
