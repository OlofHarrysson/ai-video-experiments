import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill,renderMedia,openBrowser} from '@remotion/renderer';
import {mkdir,copyFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
const root=resolve('../../../comfyui/projects/watermelon-scene');
const out=resolve(root,'references/assets');await mkdir(out,{recursive:true});await mkdir(resolve('public/scene'),{recursive:true});
await copyFile(resolve(root,'runs/stills/background/output-0.png'),resolve('public/scene/background.png'));
const serveUrl=await bundle({entryPoint:resolve('src/scene.tsx')});const browser=await openBrowser('chrome');
const frames=[0,13,27,40,53,67,80];
try{
 for(const kind of ['guide','mask','background','layout']){
  const composition=await selectComposition({serveUrl,id:`Scene-${kind}`,puppeteerInstance:browser});
  for(const [i,frame] of frames.entries())await renderStill({serveUrl,composition,frame,output:resolve(out,`${kind}-${i}.png`),imageFormat:'png',puppeteerInstance:browser});
  if(kind!=='layout')await renderMedia({serveUrl,composition,codec:'h264',outputLocation:resolve(out,`${kind}.mp4`),crf:10,puppeteerInstance:browser});
 }
 await writeFile(resolve(out,'manifest.json'),JSON.stringify({width:1024,height:1024,fps:16,durationFrames:81,frames:frames.map((frame,i)=>({index:i,frame,cx:250+520*frame/80,cy:650,radius:130}))},null,2));
}finally{await browser.close({silent:true});}
