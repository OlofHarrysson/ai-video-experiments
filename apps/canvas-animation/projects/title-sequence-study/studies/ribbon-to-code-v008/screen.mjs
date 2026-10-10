import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const here=path.dirname(fileURLToPath(import.meta.url)),selected=path.join(here,process.argv[2]||'output-delivery'),out=path.join(here,process.argv[3]||'output-screen-delivery');
if(fs.existsSync(out))throw new Error('Screening output exists; preserve the earlier evidence.');fs.mkdirSync(out);
const decode=spawnSync('ffmpeg',['-v','error','-i',path.join(selected,'wild-hours-ribbons.mp4'),'-vf',"select='between(n,15,23)+between(n,180,188)+eq(n,0)+eq(n,239)'",'-fps_mode','vfr',path.join(out,'decoded-%02d.png')],{encoding:'utf8'});if(decode.status!==0)throw new Error(decode.stderr);
const browser=await chromium.launch();
try{
 const page=await browser.newPage({viewport:{width:1400,height:1050}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const files=fs.readdirSync(out).filter(f=>f.endsWith('.png')).sort();
 await page.setContent('<body></body>');
 const times=[0,...Array.from({length:9},(_,i)=>(15+i)/30),...Array.from({length:9},(_,i)=>(180+i)/30),239/30];
 for(const [name,indices]of [['early-twist',Array.from({length:9},(_,i)=>i+1)],['late-twist',Array.from({length:9},(_,i)=>i+10)],['loop',[19,0]]]){
  const data=indices.map(i=>({time:times[i],src:'data:image/png;base64,'+fs.readFileSync(path.join(out,files[i])).toString('base64')}));
  const sheet=await page.evaluate(async data=>{const c=document.createElement('canvas');c.width=1536;c.height=Math.ceil(data.length/3)*370;const g=c.getContext('2d');g.fillStyle='#191b16';g.fillRect(0,0,c.width,c.height);for(let i=0;i<data.length;i++){const img=new Image();img.src=data[i].src;await img.decode();const x=i%3*512,y=Math.floor(i/3)*370;g.drawImage(img,x,y,512,341.333);g.fillStyle='#ffffff';g.font='16px sans-serif';g.fillText(data[i].time.toFixed(3)+' s',x+8,y+360);}return c.toDataURL().split(',')[1]},data);fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(sheet,'base64'));
 }
 await page.goto(pathToFileURL(path.join(here,'review.html')).href);await page.evaluate(src=>{document.querySelector('video').src=src;},pathToFileURL(path.join(selected,'wild-hours-ribbons.mp4')).href);await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0)&&document.querySelector('video').readyState>=1);
 await page.screenshot({path:path.join(out,'review.png'),fullPage:true});
 const video=await page.evaluate(async()=>{const v=document.querySelector('video');await v.play();return {duration:v.duration,width:v.videoWidth,height:v.videoHeight}});await page.waitForFunction(()=>document.querySelector('video').currentTime>.5);video.playbackAdvanced=true;await page.evaluate(()=>document.querySelector('video').pause());
 await page.getByRole('link',{name:'Edit the design'}).click();await page.waitForFunction(()=>window.ready);const editorLoads=true;
 const report={errors,decodedFrames:files.length,video,editorLoads};report.passed=!errors.length&&files.length===20&&video.duration===8&&video.width===1536&&video.height===1024;
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(report);if(!report.passed)process.exitCode=1;
}finally{await browser.close()}
