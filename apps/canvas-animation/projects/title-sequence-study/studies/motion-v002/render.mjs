import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const require=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url));
const {chromium}=require('playwright'),here=path.dirname(fileURLToPath(import.meta.url));
const out=path.join(here,process.env.MOTION_OUTPUT||'output');
if(fs.existsSync(out))throw new Error('Preserve the existing output first, or set MOTION_OUTPUT to a new directory name.');
fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch();
try{
 const page=await b.newPage({viewport:{width:1328,height:780}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(here,'index.html')).href);await page.waitForFunction(()=>window.motionReady);
 const report=await page.evaluate(()=>({names:MotionStudy.names,cuts:MotionStudy.cuts,duration:MotionStudy.duration}));
 const png=async(id,t,label=false)=>Buffer.from(await page.evaluate(({id,t,label})=>{const c=MotionKit.canvas();id===8?MotionStudy.montage(t,c):MotionStudy.render(id,t,c,{label});return c.toDataURL().split(',')[1]},{id,t,label}),'base64');
 const hash=b=>createHash('sha256').update(b).digest('hex');report.checks=[];
 for(let id=0;id<8;id++){
  const a=await png(id,.4),middle=await png(id,1.8);await png(id,3.5);const repeat=await png(id,.4);
  if(hash(a)!==hash(repeat))throw new Error('Seek determinism failed '+id);
  const delta=await page.evaluate(id=>{const frames=[.4,1.8].map(t=>{const c=MotionKit.canvas();MotionStudy.render(id,t,c);return c.getContext('2d').getImageData(0,0,1280,544).data});let n=0;for(let i=0;i<frames[0].length;i+=4)if(Math.abs(frames[0][i]-frames[1][i])+Math.abs(frames[0][i+1]-frames[1][i+1])+Math.abs(frames[0][i+2]-frames[1][i+2])>60)n++;return n/(1280*544)},id);
  if(delta<.035)throw new Error('Insufficient frame change '+id+': '+delta);
  report.checks.push({id:id+1,repeatable:true,changedPixelFraction:delta});
  fs.writeFileSync(path.join(out,`style-${id+1}.png`),middle);
 }
 // Actual gallery controls: select, scrub, play, pause and preserve paused pixels.
 await page.selectOption('#scene','4');await page.locator('#seek').fill('1.8');await page.locator('#seek').dispatchEvent('input');
 const before=await page.locator('#time').textContent();await page.click('#play');await page.waitForTimeout(180);await page.click('#play');
 const after=await page.locator('#time').textContent();if(before===after)throw new Error('Playback did not advance');
 const paused=await page.locator('#view').evaluate(c=>c.toDataURL());await page.waitForTimeout(100);if(paused!==await page.locator('#view').evaluate(c=>c.toDataURL()))throw new Error('Pause did not hold');
 report.controls='select, scrub, play and pause passed';
 const sheet=async(name,entries,cols=4)=>{const bytes=await page.evaluate(({entries,cols})=>{const w=400,h=170,labelH=30,c=document.createElement('canvas');c.width=cols*w;c.height=Math.ceil(entries.length/cols)*(h+labelH);const g=c.getContext('2d');g.fillStyle='#161616';g.fillRect(0,0,c.width,c.height);entries.forEach(({id,t},i)=>{const tile=MotionKit.canvas();id===8?MotionStudy.montage(t,tile):MotionStudy.render(id,t,tile);const x=i%cols*w,y=Math.floor(i/cols)*(h+labelH);g.drawImage(tile,x,y,w,h);g.fillStyle='#eee';g.font='14px system-ui';g.fillText((id===8?'Edit':(id+1)+' '+MotionStudy.names[id])+' · '+t.toFixed(2)+'s',x+10,y+h+21)});return c.toDataURL().split(',')[1]},{entries,cols});fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(bytes,'base64'))};
 await sheet('motion-overview',report.names.map((_,id)=>({id,t:1.8})),2);
 await sheet('motion-phases',report.names.flatMap((_,id)=>[.25,.9,1.8,2.8].map(t=>({id,t}))));
 await sheet('edit-overview',[.5,2,4.5,6.5,8.5,9.5,10.5,11.5,12.25,13.25,15.1,16.6].filter(t=>t<report.duration).map(t=>({id:8,t})));
 await sheet('cut-window',Array.from({length:8},(_,i)=>({id:8,t:12-4/24+i/24})));
 if(!process.argv.includes('--stills')){
  for(const mode of ['catalogue','escalation']){const dir=path.join(out,mode+'-frames');fs.mkdirSync(dir);const fps=24,duration=mode==='catalogue'?32:report.duration,count=Math.round(duration*fps);
   for(let f=0;f<count;f++){const t=f/fps,id=mode==='catalogue'?Math.floor(t/4):8,local=id===8?t:(t%4)*3.7/4;fs.writeFileSync(path.join(dir,`f${String(f).padStart(4,'0')}.png`),await png(id,local,mode==='catalogue'));if(f%192===0)console.log(mode+' '+f+'/'+count)}
   const r=spawnSync('ffmpeg',['-v','error','-y','-framerate',String(fps),'-i',path.join(dir,'f%04d.png'),'-frames:v',String(count),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,mode+'.mp4')],{stdio:'inherit'});if(r.status!==0)throw new Error('ffmpeg failed');
  }
 }
 if(errors.length)throw new Error(errors.join('\n'));fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({out,checks:report.checks,controls:report.controls,duration:report.duration}));
}finally{await b.close()}
