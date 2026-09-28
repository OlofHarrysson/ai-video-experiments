import {bundle} from '@remotion/bundler';
import {selectComposition,renderMedia,renderStill,openBrowser} from '@remotion/renderer';
import {mkdir,copyFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
const root=resolve('../../../comfyui/projects/watermelon-scene');const assets=resolve('public/scene-review');await mkdir(assets,{recursive:true});
for(let i=0;i<7;i++)await copyFile(resolve(root,`runs/stills/sunburst-guide-${i}/output-0.png`),resolve(assets,`still-${i}.png`));
for(const [src,dst] of [['references/assets/guide.mp4','guide.mp4'],['runs/video/ltx-guide-three-anchors/output.mp4','ltx.mp4'],['runs/video/h3-guide-reference-24fps/output.mp4','h3.mp4']])await copyFile(resolve(root,src),resolve(assets,dst));
const serveUrl=await bundle({entryPoint:resolve('src/scene-comparison.tsx')});const browser=await openBrowser('chrome');const out=resolve(root,'exports/video');await mkdir(out,{recursive:true});
try{const composition=await selectComposition({serveUrl,id:'SceneComparison',puppeteerInstance:browser});await renderMedia({serveUrl,composition,codec:'h264',crf:18,outputLocation:resolve(out,'comparison.mp4'),puppeteerInstance:browser});await renderStill({serveUrl,composition,frame:60,output:resolve(out,'comparison-preview.png'),puppeteerInstance:browser});await writeFile(resolve(out,'comparison-manifest.json'),JSON.stringify({fps:24,frames:122,stills:'Seven independent generated images held using nearest authored source time; no interpolation',nativeVideos:'Original timing, muted; display cropped to 122/24 seconds',sources:['guide.mp4','stills','ltx.mp4','h3.mp4']},null,2));}finally{await browser.close({silent:true});}
