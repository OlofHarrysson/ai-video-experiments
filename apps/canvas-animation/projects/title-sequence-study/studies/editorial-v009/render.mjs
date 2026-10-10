import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const here=path.dirname(fileURLToPath(import.meta.url));
const out=path.join(here,process.argv[2]||'output-candidates');
const movie=process.argv.includes('--motion');
if(fs.existsSync(out))throw Error('Output exists; choose a new checkpoint.');
fs.mkdirSync(out,{recursive:true});
const run=(bin,args)=>{const r=spawnSync(bin,args,{encoding:'utf8'});if(r.status!==0)throw Error(r.stderr);return r.stdout;};
const hash=x=>createHash('sha256').update(x).digest('hex');
const browser=await chromium.launch();
try{
 const page=await browser.newPage(),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
 await page.setContent('<canvas width="1600" height="900"></canvas>');
 for(const f of ['outlines.js','art.js',...(movie?['edit.js']:[])])await page.addScriptTag({content:fs.readFileSync(path.join(here,f),'utf8')});
 const names=await page.evaluate(()=>Editorial.cards.map(c=>({id:c.id,name:c.name})));
 async function png(id,p=.5){return Buffer.from(await page.evaluate(({id,p})=>{Editorial.card(document.querySelector('canvas'),id,p);return document.querySelector('canvas').toDataURL().split(',')[1];},{id,p}),'base64');}
 for(const c of names)fs.writeFileSync(path.join(out,c.id+'.png'),await png(c.id));
 async function sheetFromImages(items,cols=4){
  return Buffer.from(await page.evaluate(async ({items,cols})=>{
   const c=document.createElement('canvas');c.width=1600;c.height=Math.ceil(items.length/cols)*255;const q=c.getContext('2d');q.fillStyle='#202025';q.fillRect(0,0,c.width,c.height);
   for(let i=0;i<items.length;i++){const img=new Image();img.src='data:image/png;base64,'+items[i].png;await img.decode();const x=i%cols*400,y=Math.floor(i/cols)*255;q.drawImage(img,x,y,400,225);q.fillStyle='#eee';q.font='14px sans-serif';q.fillText(items[i].name,x+10,y+246);}
   return c.toDataURL().split(',')[1];
  },{items,cols}),'base64');
 }
 const sheet=await sheetFromImages(names.map(c=>({name:c.name,png:fs.readFileSync(path.join(out,c.id+'.png')).toString('base64')})));
 fs.writeFileSync(path.join(out,'candidates.png'),sheet);
 const checks={candidateCount:names.length,errors,networkRequests:requests.length};
 if(movie){
  const coverage=[];
  const getFrame=async n=>{
   const r=await page.evaluate(n=>{
    const c=document.querySelector('canvas');Editorial.draw(c,n);const pixels=c.getContext('2d').getImageData(0,0,1600,900).data;let visible=0,total=0;
    for(let i=0;i<pixels.length;i+=64){total++;if(Math.max(pixels[i],pixels[i+1],pixels[i+2])>90)visible++;}
    return {png:c.toDataURL().split(',')[1],coverage:visible/total};
   },n);coverage[n]=r.coverage;return Buffer.from(r.png,'base64');
  };
  const a=await getFrame(23);await getFrame(179);checks.deterministic=hash(a)===hash(await getFrame(23));checks.loop=hash(await getFrame(0))===hash(await getFrame(288));
  checks.timeline=await page.evaluate(()=>EditShots);checks.frameCount=checks.timeline.reduce((s,c)=>s+c.frames,0);
  checks.distinctCompositions=new Set(checks.timeline.map(s=>s.id)).size;
  const frameHashes=[];
  for(let n=0;n<288;n++){const b=await getFrame(n);fs.writeFileSync(path.join(out,`frame-${String(n).padStart(4,'0')}.png`),b);frameHashes.push(hash(b));if(n%48===0)console.log(`Rendered ${n}/288`);}
  checks.uniqueFrames=new Set(frameHashes).size;
  const film=path.join(out,'make-it-move.mp4');
  run('ffmpeg',['-hide_banner','-loglevel','error','-framerate','24','-i',path.join(out,'frame-%04d.png'),'-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',film]);
  checks.video=JSON.parse(run('ffprobe',['-v','quiet','-show_streams','-show_format','-of','json',film]));
  run('ffmpeg',['-v','error','-i',film,'-f','null','-']);checks.fullDecode=true;checks.silent=checks.video.streams.every(s=>s.codec_type!=='audio');
  const samples=await page.evaluate(()=>{let start=0;return EditShots.map(s=>{const x=start+Math.floor(s.frames/2);start+=s.frames;return x;});});
  const editSheet=await sheetFromImages(samples.map(f=>({name:(f/24).toFixed(3)+' s',png:fs.readFileSync(path.join(out,`frame-${String(f).padStart(4,'0')}.png`)).toString('base64')})));
  fs.writeFileSync(path.join(out,'edit-contact.png'),editSheet);
  checks.frameCoverage=coverage.slice(0,288);checks.noBlankFrames=checks.frameCoverage.every(v=>v>.001);

 }
 const source=path.join(out,'source');fs.mkdirSync(source);checks.sourceHashes={};
 for(const f of ['outlines.js','prepare.mjs','art.js','render.mjs',...(movie?['edit.js','index.html']:[])]){const b=fs.readFileSync(path.join(here,f));fs.writeFileSync(path.join(source,f),b);checks.sourceHashes[f]=hash(b);}
 checks.passed=!errors.length&&requests.length===0&&names.length===20&&(!movie||(checks.deterministic&&checks.loop&&checks.frameCount===288&&checks.fullDecode&&checks.silent&&checks.noBlankFrames));
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(checks,null,2));console.log(JSON.stringify({out,passed:checks.passed,errors,uniqueFrames:checks.uniqueFrames},null,2));if(!checks.passed)process.exitCode=1;
}finally{await browser.close();}
