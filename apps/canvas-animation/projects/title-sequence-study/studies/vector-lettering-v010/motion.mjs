import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const here=path.dirname(fileURLToPath(import.meta.url)),out=path.join(here,process.argv[2]||'output-motion-01');
const WIDTH=1600,HEIGHT=900;
if(fs.existsSync(out))throw Error('Output exists; choose a new checkpoint.');fs.mkdirSync(out,{recursive:true});
const files=['../../node_modules/clipper-lib/clipper.js','../image-to-code-v006/vector-fields.js','geometry.js','highlights.js','art.js','edit.js'];
const run=(bin,args)=>{const r=spawnSync(bin,args,{encoding:'utf8'});if(r.status!==0)throw Error(r.stderr);return r.stdout};
const hash=b=>createHash('sha256').update(b).digest('hex');
const browser=await chromium.launch();
try{
 const page=await browser.newPage(),errors=[],requests=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
 await page.setContent(`<canvas width="${WIDTH}" height="${HEIGHT}"></canvas>`);
 for(const f of files)await page.addScriptTag({content:fs.readFileSync(path.join(here,f),'utf8')});
 const {frames,fps,shots}=await page.evaluate(()=>({frames:LetteringEdit.frames,fps:LetteringEdit.fps,shots:LetteringEdit.shots}));
 for(const id of ['script','tuscan','liquid'])await page.evaluate(id=>LetteringArt.prepare(id),id);
 async function frame(n){return Buffer.from(await page.evaluate(n=>{const c=document.querySelector('canvas');LetteringEdit.draw(c,n);return c.toDataURL().split(',')[1]},n),'base64')}
 const a=await frame(76);await frame(219);const deterministic=hash(a)===hash(await frame(76));const loop=hash(await frame(0))===hash(await frame(frames));
 const hashes=[];for(let n=0;n<frames;n++){const b=await frame(n);fs.writeFileSync(path.join(out,`frame-${String(n).padStart(4,'0')}.png`),b);hashes.push(hash(b));if(n%48===0)console.log(`Rendered ${n}/${frames}`);}
 const film=path.join(out,'wild-hours.mp4');run('ffmpeg',['-hide_banner','-loglevel','error','-framerate',String(fps),'-i',path.join(out,'frame-%04d.png'),'-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',film]);
 const media=JSON.parse(run('ffprobe',['-v','quiet','-show_streams','-show_format','-of','json',film]));run('ffmpeg',['-v','error','-i',film,'-f','null','-']);
 async function sheet(name,items,cols=4){const data=await page.evaluate(async({items,cols})=>{const c=document.createElement('canvas'),cell=400;c.width=cols*cell;c.height=Math.ceil(items.length/cols)*250;const g=c.getContext('2d');g.fillStyle='#171719';g.fillRect(0,0,c.width,c.height);for(let i=0;i<items.length;i++){const im=new Image();im.src='data:image/png;base64,'+items[i].png;await im.decode();const x=i%cols*cell,y=Math.floor(i/cols)*250;g.drawImage(im,x,y,400,225);g.fillStyle='#ddd';g.font='12px sans-serif';g.fillText(items[i].label,x+8,y+242);}return c.toDataURL().split(',')[1]},{items,cols});fs.writeFileSync(path.join(out,name),Buffer.from(data,'base64'));}
 const item=(n,label)=>({png:fs.readFileSync(path.join(out,`frame-${String(n).padStart(4,'0')}.png`)).toString('base64'),label});
 await sheet('edit-contact.png',shots.map(s=>item(s.start+Math.floor(s.frames/2),`${(s.start/fps).toFixed(2)} s / ${s.label}`)));
 for(const [label,event]of [['assembly','assemble'],['contours','flow'],['registration','register']]){
  const shot=shots.find(s=>s.event===event);
  await sheet('motion-'+label+'.png',Array.from({length:Math.min(12,shot.frames)},(_,i)=>item(shot.start+i,`frame ${shot.start+i}`)));
 }
 const report={width:WIDTH,height:HEIGHT,frames,fps,duration:frames/fps,deterministic,loop,errors,requests,uniqueFrames:new Set(hashes).size,silent:media.streams.every(s=>s.codec_type!=='audio'),fullDecode:true,media,shots,sourceHashes:{}};
 fs.mkdirSync(path.join(out,'source'));for(const f of files){const b=fs.readFileSync(path.join(here,f));const name=path.basename(f);fs.writeFileSync(path.join(out,'source',name),b);report.sourceHashes[name]=hash(b);}
 report.passed=deterministic&&loop&&!errors.length&&!requests.length&&report.silent;
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({out,passed:report.passed,frames,uniqueFrames:report.uniqueFrames},null,2));if(!report.passed)process.exitCode=1;
}finally{await browser.close();}
