import {bundle} from '@remotion/bundler';
import {selectComposition,renderMedia,renderStill,openBrowser} from '@remotion/renderer';
import {resolve} from 'node:path';
const out=resolve('../../../comfyui/projects/watermelon-scene/exports/video');
const serveUrl=await bundle({entryPoint:resolve('src/scene-comparison.tsx')});const browser=await openBrowser('chrome');
try{const composition=await selectComposition({serveUrl,id:'SceneBackgroundLock',puppeteerInstance:browser});await renderMedia({serveUrl,composition,codec:'h264',crf:18,outputLocation:resolve(out,'background-locked-stills.mp4'),puppeteerInstance:browser});await renderStill({serveUrl,composition,frame:60,output:resolve(out,'background-lock-preview.png'),puppeteerInstance:browser});}finally{await browser.close({silent:true});}
