import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const here=path.dirname(fileURLToPath(import.meta.url));
const selected=path.join(here,process.argv[2]||'output-delivery');
const out=path.join(here,process.argv[3]||'output-screen');
if(fs.existsSync(out))throw Error('Choose a new screening output.');fs.mkdirSync(out,{recursive:true});
const run=(bin,args)=>{const r=spawnSync(bin,args,{encoding:'utf8'});if(r.status!==0)throw Error(r.stderr);return r.stdout;};
const film=path.join(selected,'make-it-move.mp4');
const frames=[...Array.from({length:9},(_,i)=>39+i),...Array.from({length:9},(_,i)=>165+i),...Array.from({length:5},(_,i)=>283+i),...Array.from({length:4},(_,i)=>i)];
for(const n of frames)run('ffmpeg',['-hide_banner','-loglevel','error','-i',film,'-vf',`select=eq(n\\,${n})`,'-frames:v','1',path.join(out,`decoded-${n}.png`)]);
const browser=await chromium.launch();
try{
 const page=await browser.newPage({viewport:{width:1440,height:1080}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(here,'review.html')).href);
 const sheets=[];
 for(let i=0;i<frames.length;i+=9){
  const group=frames.slice(i,i+9);
  const data=await page.evaluate(async items=>{const c=document.createElement('canvas');c.width=1600;c.height=3*325;const q=c.getContext('2d');q.fillStyle='#222';q.fillRect(0,0,c.width,c.height);
   for(let k=0;k<items.length;k++){const {src,frame}=items[k],img=new Image();img.src=src;await img.decode();const x=k%3*533,y=Math.floor(k/3)*325;q.drawImage(img,x,y,533,300);q.fillStyle='#fff';q.font='16px sans-serif';q.fillText(`${frame} / ${(frame/24).toFixed(3)} s`,x+10,y+319);}return c.toDataURL().split(',')[1];
  },group.map(frame=>({frame,src:'data:image/png;base64,'+fs.readFileSync(path.join(out,`decoded-${frame}.png`)).toString('base64')})));
  const name=`window-${i/9+1}.png`;fs.writeFileSync(path.join(out,name),Buffer.from(data,'base64'));sheets.push(name);
 }
 const checks={errors,decodedFrames:frames,sheets};
 await page.locator('video').evaluate((v,src)=>{v.src=src;v.load();},pathToFileURL(film).href);
 await page.waitForFunction(()=>document.querySelector('video').readyState>=2);
 checks.video=await page.locator('video').evaluate(v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight}));
 await page.locator('video').evaluate(async v=>{v.loop=false;v.muted=true;v.playbackRate=4;await v.play();});await page.waitForFunction(()=>document.querySelector('video').ended,{},{timeout:15000});checks.playedToEnd=true;
 await page.locator('video').evaluate(v=>{v.currentTime=.625;});await page.screenshot({path:path.join(out,'review.png'),fullPage:true});
 await page.goto(pathToFileURL(path.join(here,'index.html')).href);await page.waitForFunction(()=>window.ready);
 await page.locator('#seek').fill('86');await page.locator('#seek').dispatchEvent('input');await page.locator('#play').click();await page.waitForFunction(()=>Number(document.querySelector('#seek').value)>90);await page.locator('#play').click();checks.previewAdvances=true;
 await page.locator('summary').click();await page.locator('#card').selectOption('gothic');
 const download=page.waitForEvent('download');await page.locator('#save').click();await(await download).saveAs(path.join(out,'export-gothic.png'));checks.exportedPng=fs.statSync(path.join(out,'export-gothic.png')).size>10000;
 await page.setViewportSize({width:390,height:844});checks.noOverflow=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth);
 checks.passed=!errors.length&&checks.video.duration===12&&checks.video.width===1600&&checks.video.height===900&&checks.playedToEnd&&checks.previewAdvances&&checks.exportedPng&&checks.noOverflow;
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(checks,null,2));console.log(checks);if(!checks.passed)process.exitCode=1;
}finally{await browser.close();}
