import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const here=path.dirname(fileURLToPath(import.meta.url));
const out=path.join(here,process.argv[2]||'output-01'),movie=process.argv.includes('--motion');
if(fs.existsSync(out))throw new Error('Choose a new output directory; checkpoints are preserved.');
fs.mkdirSync(out,{recursive:true});
const hash=data=>createHash('sha256').update(data).digest('hex');
const browser=await chromium.launch();
try{
 const page=await browser.newPage({viewport:{width:1500,height:1100}}),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
 // Independent renderer has no reference file, fonts, network or image elements.
 await page.setContent('<canvas id="art" width="1536" height="1024"></canvas>');
 for(const f of ['geometry.js','art.js'])await page.addScriptTag({content:fs.readFileSync(path.join(here,f),'utf8')});
 async function frame(n,options={}){return Buffer.from(await page.evaluate(({n,options})=>{const state=RibbonArt.draw(document.querySelector('canvas'),n,options);if(state.error)throw new Error('WebGL error: '+state.error);return document.querySelector('canvas').toDataURL().split(',')[1]}, {n,options}),'base64');}
 const hero=await frame(0),clean=await frame(0,{flat:true});
 fs.writeFileSync(path.join(out,'hero.png'),hero);fs.writeFileSync(path.join(out,'clean.png'),clean);
 const checks={loop:hash(hero)===hash(await frame(240)),deterministic:hash(await frame(38))===hash(await frame(38)),materialChanges:hash(hero)!==hash(clean),zeroIntensity:hash(hero)===hash(await frame(38,{intensity:0})),motionChanges:hash(hero)!==hash(await frame(2)),networkRequests:requests.length};
 checks.customStrengthLoop=hash(await frame(0,{intensity:.55}))===hash(await frame(240,{intensity:.55}));
 const timings=await page.evaluate(()=>{const samples=[];for(let i=0;i<30;i++){const t=performance.now();RibbonArt.draw(document.querySelector('canvas'),i);document.querySelector('canvas').getContext('webgl2').finish();samples.push(performance.now()-t)}return samples;});
 const sampleFrames=[0,7,20,44,64,81,104,124,146,167,186,222];
 for(const n of sampleFrames)fs.writeFileSync(path.join(out,`sample-${n}.png`),await frame(n));
 const sheet=await page.evaluate(frames=>{const c=document.createElement('canvas');c.width=1536;c.height=4*365;const g=c.getContext('2d'),tile=document.createElement('canvas');tile.width=1536;tile.height=1024;g.fillStyle='#20221b';g.fillRect(0,0,c.width,c.height);frames.forEach((n,i)=>{const x=i%3*512,y=Math.floor(i/3)*365;RibbonArt.draw(tile,n);g.drawImage(tile,x,y,512,256*4/3);g.fillStyle='#ffffff';g.font='14px sans-serif';g.fillText((n/30).toFixed(2)+' s',x+12,y+19);});return c.toDataURL().split(',')[1]},sampleFrames);
 fs.writeFileSync(path.join(out,'contact.png'),Buffer.from(sheet,'base64'));
 if(movie){
  for(let n=0;n<240;n++){fs.writeFileSync(path.join(out,`frame-${String(n).padStart(4,'0')}.png`),await frame(n));if(n%30===0)console.log(`Rendered ${n}/240`);}
  const run=args=>{const r=spawnSync(args[0],args.slice(1),{encoding:'utf8'});if(r.status!==0)throw new Error(r.stderr);return r.stdout;};
  run(['ffmpeg','-hide_banner','-loglevel','error','-framerate','30','-i',path.join(out,'frame-%04d.png'),'-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,'wild-hours-ribbons.mp4')]);
  checks.video=JSON.parse(run(['ffprobe','-v','quiet','-show_streams','-show_format','-of','json',path.join(out,'wild-hours-ribbons.mp4')]));
  run(['ffmpeg','-v','error','-i',path.join(out,'wild-hours-ribbons.mp4'),'-f','null','-']);
  checks.fullDecode=true;
 }
 await page.goto(pathToFileURL(path.join(here,'index.html')).href);await page.waitForFunction(()=>window.ready);
 await page.locator('#compare').click();await page.screenshot({path:path.join(out,'comparison.png'),fullPage:true});
 await page.locator('#phase').fill('43');await page.locator('#phase').dispatchEvent('input');await page.locator('#play').click();await page.waitForFunction(()=>document.querySelector('#phase').value!=='43');await page.locator('#play').click();checks.playbackAdvanced=await page.locator('#phase').inputValue()!=='43';
 await page.locator('summary').click();await page.locator('#texture').uncheck();await page.locator('#isolate').selectOption('W');
 const downloadPromise=page.waitForEvent('download');await page.locator('#save').click();await(await downloadPromise).saveAs(path.join(out,'export-W.png'));
 const svgPromise=page.waitForEvent('download');await page.locator('#svg').click();await(await svgPromise).saveAs(path.join(out,'letter-outlines.svg'));
 checks.svg=await page.evaluate(svg=>{const d=new DOMParser().parseFromString(svg,'image/svg+xml');return {valid:!d.querySelector('parsererror'),paths:d.querySelectorAll('path').length,images:d.querySelectorAll('image').length}},fs.readFileSync(path.join(out,'letter-outlines.svg'),'utf8'));
 await page.setViewportSize({width:390,height:844});checks.noOverflow=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth);
 const source=path.join(out,'source');fs.mkdirSync(source);const hashes={};for(const f of ['geometry.js','art.js','viewer.js','index.html','render.mjs']){const b=fs.readFileSync(path.join(here,f));fs.writeFileSync(path.join(source,f),b);hashes[f]=hash(b);}
 const report={checks,errors,renderMilliseconds:timings,sourceHashes:hashes,referenceHash:hash(fs.readFileSync(path.join(here,'reference/ribbon-reference-01.png'))),chromium:browser.version()};
 report.passed=checks.loop&&checks.customStrengthLoop&&checks.deterministic&&checks.materialChanges&&checks.zeroIntensity&&checks.motionChanges&&checks.networkRequests===0&&checks.playbackAdvanced&&checks.noOverflow&&checks.svg.valid&&checks.svg.paths===17&&checks.svg.images===0&&!errors.length;
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({passed:report.passed,errors,checks:{...checks,video:movie?'probed':null},meanRenderMs:timings.reduce((a,b)=>a+b,0)/timings.length,out},null,2));if(!report.passed)process.exitCode=1;
}finally{await browser.close();}
