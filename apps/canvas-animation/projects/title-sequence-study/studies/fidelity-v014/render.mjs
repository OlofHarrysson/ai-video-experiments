import fs from 'node:fs';import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';import {createRequire} from 'node:module';import {createHash} from 'node:crypto';import {spawnSync} from 'node:child_process';
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.resolve(process.argv[2]);if(fs.existsSync(out))throw Error('Choose a new output directory');fs.mkdirSync(out,{recursive:true});
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const run=(cmd,args)=>{const r=spawnSync(cmd,args,{encoding:'utf8',maxBuffer:10e6});if(r.status!==0)throw Error(r.stderr);return r.stdout;};const hash=b=>createHash('sha256').update(b).digest('hex');
const browser=await chromium.launch();
try{
 const page=await browser.newPage(),errors=[],network=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url());});await page.goto(pathToFileURL(path.join(root,'index.html')).href);await page.waitForFunction(()=>window.ready);
 const frame=async(n,still=false)=>Buffer.from(await page.evaluate(({n,still})=>{drawFrame(n,still);const source=document.querySelector('canvas');if(still)return source.toDataURL().split(',')[1];const c=Object.assign(document.createElement('canvas'),{width:1600,height:900}),g=c.getContext('2d');g.imageSmoothingEnabled=true;g.imageSmoothingQuality='high';g.drawImage(source,0,0,1600,900);return c.toDataURL().split(',')[1]},{n,still}),'base64');
 for(const [i,id] of ['billions','keep'].entries()){
  await page.evaluate(()=>{const c=document.querySelector('canvas');c.width=1672;c.height=941;});fs.writeFileSync(path.join(out,id+'-unlit.png'),await frame(i*96,true));
 }
 await page.evaluate(()=>{const c=document.querySelector('canvas');c.width=3200;c.height=1800;});
 const first=await frame(25);await frame(180);const deterministic=hash(first)===hash(await frame(25));
 const benchmark=await page.evaluate(()=>{const results={};for(const n of [0,96]){drawFrame(n);const samples=[];for(let i=0;i<24;i++){const t=performance.now();drawFrame(n+i);renderer.gl.finish();samples.push(performance.now()-t);}results[n===0?'billions':'keep']={medianMs:samples.sort((a,b)=>a-b)[12],maxMs:Math.max(...samples)};}return results;});
 const hashes=[];for(let n=0;n<192;n++){const b=await frame(n);hashes.push(hash(b));fs.writeFileSync(path.join(out,`frame-${String(n).padStart(4,'0')}.png`),b);if(n%48===0)console.log('Rendered '+n+'/192');}
 const movie=path.join(out,'clean-lettering.mp4');run('ffmpeg',['-v','error','-framerate','24','-i',path.join(out,'frame-%04d.png'),'-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',movie]);
 const media=JSON.parse(run('ffprobe',['-v','quiet','-show_streams','-show_format','-of','json',movie]));run('ffmpeg',['-v','error','-i',movie,'-f','null','-']);
 run('ffmpeg',['-v','error','-i',movie,'-vf','fps=2,scale=400:225,tile=4x4','-frames:v','1',path.join(out,'encoded-contact.png')]);
 for(const [name,start] of [['billions',24],['keep',120]])run('ffmpeg',['-v','error','-framerate','24','-start_number',String(start),'-i',path.join(out,'frame-%04d.png'),'-vf','scale=400:225,tile=4x3','-frames:v','1',path.join(out,name+'-event.png')]);
 const report={passed:deterministic&&!errors.length&&!network.length&&media.streams.every(s=>s.codec_type!=='audio'),deterministic,errors,network,width:1600,height:900,supersample:2,frames:192,fps:24,duration:8,silent:media.streams.every(s=>s.codec_type!=='audio'),fullDecode:true,uniqueFrames:new Set(hashes).size,benchmark,media,sourceHashes:{}};
 fs.mkdirSync(path.join(out,'source'));for(const f of ['surface-runtime.js','build.mjs','../../../../tools/artwork/mask-texture.js']){const b=fs.readFileSync(path.join(root,f));report.sourceHashes[f]=hash(b);fs.writeFileSync(path.join(out,'source',path.basename(f)),b);}fs.copyFileSync(path.join(root,'index.html'),path.join(out,'source/index.html'));
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({out,passed:report.passed,uniqueFrames:report.uniqueFrames,benchmark}));if(!report.passed)process.exitCode=1;
}finally{await browser.close();}
