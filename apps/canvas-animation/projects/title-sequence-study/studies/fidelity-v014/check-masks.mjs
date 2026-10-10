import fs from 'node:fs';import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';import {createRequire} from 'node:module';
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.resolve(process.argv[2]);fs.mkdirSync(out,{recursive:true});
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const browser=await chromium.launch();
try{
 const page=await browser.newPage();await page.goto(pathToFileURL(path.join(root,'index.html')).href);await page.waitForFunction(()=>window.ready);
 await page.evaluate(()=>{const c=document.querySelector('canvas');c.width=1672;c.height=941});
 for(const [i,id] of ['billions','keep'].entries())for(const feather of [0,3])for(const time of [0,.5,1,1.5,2,2.5,3]){
  const png=await page.evaluate(({i,id,feather,time})=>{drawFrame(i*96);renderer.setMasks(artworkData[id].masks,id,{feather});renderer.draw(time);return document.querySelector('canvas').toDataURL().split(',')[1]}, {i,id,feather,time});
  fs.writeFileSync(path.join(out,`${id}-f${feather}-${time}.png`),Buffer.from(png,'base64'));
 }
 console.log(out);
}finally{await browser.close()}
