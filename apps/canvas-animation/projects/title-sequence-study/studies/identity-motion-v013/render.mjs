import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.join(root,process.argv[2]||'output-motion-v001');
if(fs.existsSync(out))throw Error('Choose a new output checkpoint');fs.mkdirSync(out,{recursive:true});
const run=(cmd,args)=>{const r=spawnSync(cmd,args,{encoding:'utf8',maxBuffer:10e6});if(r.status!==0)throw Error(r.stderr);return r.stdout;};
const hash=b=>createHash('sha256').update(b).digest('hex');
const browser=await chromium.launch();
try{
 const page=await browser.newPage(),errors=[],network=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url());});
 await page.goto(pathToFileURL(path.join(root,'index.html')).href);await page.waitForFunction(()=>window.ready);
 const frame=async n=>Buffer.from(await page.evaluate(n=>{renderFrame(n);return document.querySelector('canvas').toDataURL().split(',')[1];},n),'base64');
 const a=await frame(24);await frame(219);const deterministic=hash(a)===hash(await frame(24));
 const hashes=[];
 for(let i=0;i<288;i++){const bytes=await frame(i);hashes.push(hash(bytes));fs.writeFileSync(path.join(out,`frame-${String(i).padStart(4,'0')}.png`),bytes);if(i%48===0)console.log(`Rendered ${i}/288`);}
 const movie=path.join(out,'three-identities.mp4');
 run('ffmpeg',['-v','error','-framerate','24','-i',path.join(out,'frame-%04d.png'),'-c:v','libx264','-crf','15','-pix_fmt','yuv420p','-movflags','+faststart',movie]);
 const media=JSON.parse(run('ffprobe',['-v','quiet','-show_streams','-show_format','-of','json',movie]));run('ffmpeg',['-v','error','-i',movie,'-f','null','-']);
 for(const [i,id]of ['billions','next','keep-up'].entries())run('ffmpeg',['-v','error','-i',movie,'-ss',String(i*4),'-t','4','-an','-c:v','libx264','-crf','15','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,id+'.mp4')]);
 const selected=[0,6,15,24,39,44,65,84,96,102,111,120,132,136,147,172,192,200,216,226,248,256,268,282];
 async function sheet(name,frames){
  const imgs=frames.map(n=>({n,png:fs.readFileSync(path.join(out,`frame-${String(n).padStart(4,'0')}.png`)).toString('base64')}));
  const result=await page.evaluate(async imgs=>{const c=document.createElement('canvas');c.width=1600;c.height=Math.ceil(imgs.length/4)*250;const g=c.getContext('2d');g.fillStyle='#171719';g.fillRect(0,0,c.width,c.height);for(let i=0;i<imgs.length;i++){const im=new Image();im.src='data:image/png;base64,'+imgs[i].png;await im.decode();const x=i%4*400,y=Math.floor(i/4)*250;g.drawImage(im,x,y,400,225);g.font='12px sans-serif';g.fillStyle='#fff';g.fillText('frame '+imgs[i].n,x+8,y+243);}return c.toDataURL().split(',')[1];},imgs);
  fs.writeFileSync(path.join(out,name),Buffer.from(result,'base64'));
 }
 await sheet('contact.png',selected);
 await sheet('next-event.png',Array.from({length:12},(_,i)=>130+i));
 await sheet('billions-event.png',Array.from({length:12},(_,i)=>i));
 await sheet('keep-event.png',Array.from({length:12},(_,i)=>244+i));
 run('ffmpeg',['-v','error','-i',movie,'-vf','fps=2,scale=400:225,tile=4x6','-frames:v','1',path.join(out,'encoded-contact.png')]);
 const report={passed:deterministic&&!errors.length&&!network.length&&media.streams.every(s=>s.codec_type!=='audio'),width:1600,height:900,fps:24,frames:288,duration:12,silent:media.streams.every(s=>s.codec_type!=='audio'),fullDecode:true,deterministic,errors,network,uniqueFrames:new Set(hashes).size,uniqueFramesPerStudy:[0,96,192].map(n=>new Set(hashes.slice(n,n+96)).size),media,sourceHashes:{}};
 for(const name of ['art.js','build.mjs','assets/provenance.json'])report.sourceHashes[name]=hash(fs.readFileSync(path.join(root,name)));
 fs.mkdirSync(path.join(out,'source'));fs.copyFileSync(path.join(root,'art.js'),path.join(out,'source/art.js'));fs.copyFileSync(path.join(root,'index.html'),path.join(out,'source/index.html'));
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({out,passed:report.passed,uniqueFrames:report.uniqueFrames,uniqueFramesPerStudy:report.uniqueFramesPerStudy}));if(!report.passed)process.exitCode=1;
}finally{await browser.close();}
