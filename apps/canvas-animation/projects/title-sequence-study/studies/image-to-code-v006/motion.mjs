import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const here=path.dirname(fileURLToPath(import.meta.url)),out=path.join(here,process.argv[2]||'output-motion-01');
if(fs.existsSync(out))throw new Error('Choose a new output directory.');fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch();
try{
  const page=await browser.newPage(),errors=[],loadedSources={};page.on('pageerror',e=>errors.push(e.message));
  await page.setContent('<body><canvas id="art" width="1536" height="1024"></canvas></body>');
  for(const f of ['../../node_modules/clipper-lib/clipper.js','geometry.js','details.js','facets.js','vector-fields.js','renderer.js']){loadedSources[f]=fs.readFileSync(path.join(here,f),'utf8');await page.addScriptTag({content:loadedSources[f]});}
  for(let frame=0;frame<144;frame++){
    const data=await page.evaluate(frame=>{WildRenderer.draw(document.querySelector('#art'),frame);return document.querySelector('#art').toDataURL().split(',')[1]},frame);
    fs.writeFileSync(path.join(out,`frame-${String(frame).padStart(4,'0')}.png`),Buffer.from(data,'base64'));
    if(frame%24===0)console.log(`Rendered ${frame}/144`);
  }
  if(errors.length)throw new Error(errors.join('\n'));
  const encode=spawnSync('ffmpeg',['-hide_banner','-loglevel','error','-framerate','24','-i',path.join(out,'frame-%04d.png'),'-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,'wild-hours-material-loop.mp4')],{encoding:'utf8'});if(encode.status!==0)throw new Error(encode.stderr);
  const probe=spawnSync('ffprobe',['-v','quiet','-show_streams','-show_format','-of','json',path.join(out,'wild-hours-material-loop.mp4')],{encoding:'utf8'});if(probe.status!==0)throw new Error(probe.stderr);
  const source=path.join(out,'source');fs.mkdirSync(source);const hashes={};for(const f of ['geometry.js','details.js','facets.js','vector-fields.js','renderer.js','motion.mjs']){const content=loadedSources[f]||fs.readFileSync(path.join(here,f),'utf8');fs.writeFileSync(path.join(source,f),content);hashes[f]=createHash('sha256').update(content).digest('hex')}
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({frames:144,fps:24,width:1536,height:1024,errors,sourceHashes:hashes,probe:JSON.parse(probe.stdout)},null,2));console.log(out);
}finally{await browser.close()}
