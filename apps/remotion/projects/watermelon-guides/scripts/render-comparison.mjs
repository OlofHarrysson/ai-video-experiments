import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill,renderMedia,openBrowser} from '@remotion/renderer';
import {mkdir,copyFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
const lab=resolve('../../../comfyui/projects/spatial-control-lab');
const out=resolve('renders/v001');
await mkdir(out,{recursive:true});
const sources=[];
for(let i=0;i<7;i++){
 const files={guide:resolve(out,`guide-${i}.png`),independent:resolve(lab,`runs/round3/sunburst-independent-motion${i}/output-0.png`),reference:resolve(lab,`runs/round3/sunburst-reference-motion${i}/output-0.png`),inpaint:resolve(lab,`runs/round3/${17+i}-qwen21-inpaint-motion${i}-43/output.png`)};
 for(const [key,path] of Object.entries(files)){await mkdir(resolve('public',key),{recursive:true});await copyFile(path,resolve('public',key,`${i}.png`));sources.push({index:i,panel:key,source:path});}
}
const serveUrl=await bundle({entryPoint:resolve('src/index.tsx')});
const browser=await openBrowser('chrome');
try{
 const composition=await selectComposition({serveUrl,id:'WatermelonComparison',puppeteerInstance:browser});
 await renderMedia({serveUrl,composition,codec:'h264',outputLocation:resolve(out,'comparison.mp4'),crf:18,puppeteerInstance:browser});
 for(const frame of [0,12,24,36,48,60,72])await renderStill({serveUrl,composition,frame,output:resolve(out,`comparison-${frame}.png`),imageFormat:'png',puppeteerInstance:browser});
 await writeFile(resolve(out,'comparison-manifest.json'),JSON.stringify({fps:24,generatedFps:2,durationFrames:84,interpolated:false,sources},null,2));
}finally{await browser.close({silent:true});}
