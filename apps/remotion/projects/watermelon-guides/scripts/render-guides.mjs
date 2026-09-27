import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill,renderMedia,openBrowser} from '@remotion/renderer';
import {mkdir,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
const out=resolve('renders/v001');await mkdir(out,{recursive:true});
const serveUrl=await bundle({entryPoint:resolve('src/index.tsx')});
const browser=await openBrowser('chrome');
try{
 const composition=await selectComposition({serveUrl,id:'WatermelonGuide',puppeteerInstance:browser});
 const frames=[0,12,24,36,48,60,72];const manifest=[];
 for(const [i,frame] of frames.entries()){
  const output=resolve(out,`guide-${i}.png`);
  await renderStill({serveUrl,composition,frame,output,imageFormat:'png',puppeteerInstance:browser});
  manifest.push({index:i,frame,cx:256+512*frame/72,cy:512,radius:180,output});
 }
 await renderMedia({serveUrl,composition,codec:'h264',outputLocation:resolve(out,'guide-motion.mp4'),crf:18,puppeteerInstance:browser});
 await writeFile(resolve(out,'manifest.json'),JSON.stringify({remotion:'4.0.529',fps:24,width:1024,height:1024,frames:manifest},null,2));
}finally{await browser.close({silent:true});}
