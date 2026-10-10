import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.join(root,process.argv[2]||'output-motion-v001');
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const browser=await chromium.launch();
try{
 const page=await browser.newPage({viewport:{width:1200,height:850}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(root,'index.html')).href);await page.waitForFunction(()=>window.ready);
 const initial=await page.locator('#seek').inputValue();await page.locator('#play').click();await page.waitForTimeout(500);await page.locator('#play').click();const plays=await page.locator('#seek').inputValue()!==initial;
 await page.locator('[data-scene="1"]').click();const scene=await page.locator('#seek').inputValue()==='96';
 await page.locator('#seek').fill('216');await page.locator('#seek').dispatchEvent('input');const seeks=(await page.locator('#time').textContent()).includes('KEEP UP');
 await page.screenshot({path:path.join(out,'review-ui.png')});await page.setViewportSize({width:390,height:844});const mobile=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth);await page.screenshot({path:path.join(out,'review-mobile.png')});
 const video=await browser.newPage();await video.goto(pathToFileURL(path.join(out,'three-identities.mp4')).href);
 const playback=await video.evaluate(async()=>{const v=document.querySelector('video');v.muted=true;v.currentTime=0;await v.play();await new Promise((resolve,reject)=>{v.addEventListener('ended',resolve,{once:true});v.addEventListener('error',()=>reject(Error('Playback failed')),{once:true});setTimeout(()=>reject(Error('Playback timed out')),20000)});return {ended:v.ended,duration:v.duration,width:v.videoWidth,height:v.videoHeight};});
 const report={plays,scene,seeks,mobile,errors,playback,passed:plays&&scene&&seeks&&mobile&&!errors.length&&playback.ended};fs.writeFileSync(path.join(out,'screen-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(!report.passed)process.exitCode=1;
}finally{await browser.close();}
