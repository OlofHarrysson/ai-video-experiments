import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const root=path.dirname(fileURLToPath(import.meta.url));
if(!process.argv[2])throw Error('Supply a new output directory');
const out=path.resolve(process.argv[2]);if(fs.existsSync(out))throw Error('Output exists; preserve it and choose another');fs.mkdirSync(out,{recursive:true});
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const hash=b=>createHash('sha256').update(b).digest('hex');
const run=(cmd,args)=>{const r=spawnSync(cmd,args,{encoding:'utf8',maxBuffer:4e6});if(r.status!==0)throw Error(r.stderr);return r.stdout};
const browser=await chromium.launch();
try{
  const page=await browser.newPage(),errors=[],network=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
  await page.goto(pathToFileURL(path.join(root,'index.html')).href);await page.waitForFunction(()=>window.ready);
  const png=async(n,native=false)=>Buffer.from(await page.evaluate(({n,native})=>{
    const src=document.querySelector('canvas');src.width=native?1672:3200;src.height=native?941:1800;drawFrame(n);
    if(native)return src.toDataURL().split(',')[1];
    const c=Object.assign(document.createElement('canvas'),{width:1600,height:900}),g=c.getContext('2d');g.imageSmoothingQuality='high';g.drawImage(src,0,0,c.width,c.height);return c.toDataURL().split(',')[1];
  },{n,native}),'base64');
  for(const [name,n]of [['billions',34],['next',64],['keep',128]])fs.writeFileSync(path.join(out,`${name}-native.png`),await png(n,true));
  const first=await png(92);await png(130);const deterministic=hash(first)===hash(await png(92));
  const hashes=[];
  for(let n=0;n<144;n++){const b=await png(n);hashes.push(hash(b));fs.writeFileSync(path.join(out,`frame-${String(n).padStart(4,'0')}.png`),b)}
  const movie=path.join(out,'three-identities.mp4');
  run('ffmpeg',['-v','error','-framerate','24','-i',path.join(out,'frame-%04d.png'),'-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',movie]);
  run('ffmpeg',['-v','error','-i',movie,'-f','null','-']);
  const media=JSON.parse(run('ffprobe',['-v','quiet','-show_streams','-show_format','-of','json',movie]));
  // Inspect decoded delivery frames, with frame numbers burned into review sheets only.
  const decoded=path.join(out,'decoded');fs.mkdirSync(decoded);
  run('ffmpeg',['-v','error','-i',movie,'-start_number','0',path.join(decoded,'%04d.png')]);
  const sheet=async(name,frames)=>{
    const images=frames.map(n=>({n,src:'data:image/png;base64,'+fs.readFileSync(path.join(decoded,String(n).padStart(4,'0')+'.png')).toString('base64')}));
    const data=await page.evaluate(async images=>{
      const c=Object.assign(document.createElement('canvas'),{width:1600,height:250*Math.ceil(images.length/4)}),g=c.getContext('2d');g.fillStyle='#171717';g.fillRect(0,0,c.width,c.height);
      for(let i=0;i<images.length;i++){const im=new Image();im.src=images[i].src;await im.decode();const x=(i%4)*400,y=Math.floor(i/4)*250;g.drawImage(im,x,y,400,225);g.fillStyle='white';g.font='14px sans-serif';g.fillText('f'+images[i].n+' · '+(images[i].n/24).toFixed(3)+'s',x+8,y+243)}return c.toDataURL().split(',')[1];
    },images);fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(data,'base64'));
  };
  await sheet('overview',[0,8,18,34,44,51,60,68,80,90,99,112]);
  await sheet('join-billions-next',Array.from({length:16},(_,i)=>40+i));
  await sheet('join-next-keep',Array.from({length:16},(_,i)=>84+i));
  await sheet('keep-reveal',Array.from({length:16},(_,i)=>98+i));
  const sources=['build.mjs','motion.js','../billions-motion-v015/motion.js','../billions-motion-v015/rig.json','../../../../tools/artwork/split-plate.js','../fidelity-v014/assets/billions.png','../fidelity-v014/assets/keep.png','../identity-motion-v013/assets/next.json.gz'];
  const provenance=Object.fromEntries(sources.map(p=>[p,hash(fs.readFileSync(path.join(root,p)))]));
  fs.mkdirSync(path.join(out,'source'));fs.copyFileSync(path.join(root,'index.html'),path.join(out,'source/index.html'));
  for(const p of ['build.mjs','motion.js','render.mjs'])fs.copyFileSync(path.join(root,p),path.join(out,'source',p));
  const silent=media.streams.every(s=>s.codec_type!=='audio'),video=media.streams.find(s=>s.codec_type==='video');
  const passed=deterministic&&!errors.length&&!network.length&&silent&&+video.nb_frames===144&&video.width===1600&&video.height===900&&+media.format.duration===6;
  const report={passed,deterministic,errors,network,frames:144,fps:24,duration:6,silent,uniqueFrames:new Set(hashes).size,provenance,media};
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify({...report,media:undefined,provenance:undefined,out}));if(!passed)process.exitCode=1;
}finally{await browser.close()}
