import fs from 'node:fs';import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';import {createRequire} from 'node:module';
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.resolve(process.argv[2]),{chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const browser=await chromium.launch();try{
 const page=await browser.newPage({viewport:{width:1200,height:850}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.join(root,'index.html')).href);await page.waitForFunction(()=>window.ready);
 await page.locator('#play').click();await page.waitForFunction(()=>window.currentFrame===143);const completes=(await page.locator('#play').textContent())==='Replay';
 await page.locator('#seek').fill('50');await page.locator('#seek').dispatchEvent('input');const seeks=await page.evaluate(()=>currentFrame===50);
 const anchors=[];for(const f of [34,64,128]){await page.locator(`[data-frame="${f}"]`).click();anchors.push(await page.evaluate(f=>currentFrame===f,f))}
 await page.screenshot({path:path.join(out,'player.png')});await page.setViewportSize({width:390,height:844});const mobile=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth);
 const video=await browser.newPage();await video.goto(pathToFileURL(path.join(out,'three-identities.mp4')).href);
 const playback=await video.evaluate(async()=>{const v=document.querySelector('video');v.muted=true;await v.play();await new Promise((resolve,reject)=>{v.addEventListener('ended',resolve,{once:true});v.addEventListener('error',()=>reject(Error('Video error')),{once:true});setTimeout(()=>reject(Error('Playback timeout')),12000)});return{ended:v.ended,duration:v.duration,width:v.videoWidth,height:v.videoHeight}});
 const report={completes,seeks,anchors,mobile,errors,playback,passed:completes&&seeks&&anchors.every(Boolean)&&mobile&&!errors.length&&playback.ended};fs.writeFileSync(path.join(out,'screen-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(!report.passed)process.exitCode=1;
}finally{await browser.close()}
