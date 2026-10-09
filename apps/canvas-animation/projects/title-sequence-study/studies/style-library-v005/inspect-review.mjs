import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const here=path.dirname(fileURLToPath(import.meta.url));
const out=path.join(here,process.env.OUTPUT||'output-review-inspection');
if(fs.existsSync(out))throw new Error('Preserve existing inspection');
fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch();
try {
  const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(pathToFileURL(path.join(here,'index.html')).href);
  await page.waitForFunction(()=>window.libraryReady||window.libraryLoadError);
  if(await page.evaluate(()=>window.libraryLoadError))throw new Error('Font loading failed');
  for(let sheet=0;sheet<2;sheet++){
    const png=await page.evaluate(sheet=>{
      const count=Math.min(4,TypeCompositions.cards.length-sheet*4),c=document.createElement('canvas');c.width=1920;c.height=count*292;
      const g=c.getContext('2d');g.fillStyle='#17171b';g.fillRect(0,0,c.width,c.height);
      for(let row=0;row<count;row++)for(let s=0;s<4;s++){
        const i=sheet*4+row,p=TypeLibrary.canvas();TypeCompositions.render(i,s,0,p);
        g.drawImage(p,s*480,row*292,480,270);g.fillStyle='#eee';g.font='13px system-ui';g.fillText(TypeCompositions.cards[i].name+' / '+(s+1),s*480+10,row*292+286);
      }
      return c.toDataURL().split(',')[1];
    },sheet);
    fs.writeFileSync(path.join(out,`composition-states-${sheet+1}.png`),Buffer.from(png,'base64'));
  }
  await page.goto(pathToFileURL(path.join(here,'review.html')).href);
  const expected=[25.4166666667,34,14,16],videos=[];
  for(let i=0;i<expected.length;i++){
    await page.locator('button[data-src]').nth(i).click();
    await page.waitForFunction(()=>document.querySelector('video').readyState>=2||document.querySelector('video').error);
    const data=await page.locator('video').evaluate(v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,error:v.error?.message||null}));
    if(data.error||Math.abs(data.duration-expected[i])>.03||data.width!==1280)throw new Error('Video metadata mismatch: '+JSON.stringify(data));
    await page.locator('video').evaluate(async v=>{v.currentTime=1;await new Promise(resolve=>v.addEventListener('seeked',resolve,{once:true}));await v.play()});
    await page.waitForTimeout(250);
    await page.locator('video').evaluate(v=>v.pause());
    videos.push(data);
  }
  await page.locator('button[data-src]').first().click();
  await page.waitForFunction(()=>document.querySelector('video').readyState>=2);
  await page.locator('video').evaluate(async v=>{v.currentTime=8.5;await new Promise(resolve=>v.addEventListener('seeked',resolve,{once:true}))});
  await page.screenshot({path:path.join(out,'review-desktop.png')});
  await page.setViewportSize({width:800,height:700});await page.screenshot({path:path.join(out,'review-small.png')});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw new Error('Review page overflows horizontally');
  if(errors.length)throw new Error(errors.join('\n'));
  const images=await page.locator('img').evaluateAll(imgs=>imgs.map(i=>({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0})));
  if(images.some(i=>!i.loaded))throw new Error('Shortlist image missing');
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({videos,images,errors,decodedPlayback:true},null,2));
  console.log({out,videos});
} finally {await browser.close()}
