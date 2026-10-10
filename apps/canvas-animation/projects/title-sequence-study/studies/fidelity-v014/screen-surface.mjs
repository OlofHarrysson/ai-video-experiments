import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';
const root=path.dirname(fileURLToPath(import.meta.url));const [kind,meshDir,outArg]=process.argv.slice(2);const out=path.resolve(outArg);if(fs.existsSync(out))throw Error('Output exists');fs.mkdirSync(out,{recursive:true});
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const mesh=JSON.parse(fs.readFileSync(path.resolve(meshDir,'mesh.json'))),masks=JSON.parse(fs.readFileSync(path.join(root,`output-masks-${kind}-v001/masks.json`)));
const source=fs.readFileSync(path.join(root,`../art-direction-v012/reference/${kind==='keep'?'keep-up':kind}.png`)).toString('base64');
const browser=await chromium.launch();
try{
 const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.setContent(`<canvas width="${mesh.width}" height="${mesh.height}"></canvas>`);await page.addScriptTag({content:fs.readFileSync(path.join(root,'../../../../tools/artwork/mask-texture.js'),'utf8')});await page.addScriptTag({content:fs.readFileSync(path.join(root,'surface-runtime.js'),'utf8')});
 const stats=await page.evaluate(({mesh,masks,kind})=>{const start=performance.now();window.renderer=new SurfaceRenderer(document.querySelector('canvas'),mesh.width,mesh.height);renderer.setGeometry(mesh);renderer.setMasks(masks,kind);renderer.draw(0,{amount:0});return {prepareMs:performance.now()-start};},{mesh,masks,kind});
 const png=async(time,amount,extra={})=>Buffer.from(await page.evaluate(({time,amount,extra})=>{renderer.draw(time,{amount,...extra});return document.querySelector('canvas').toDataURL().split(',')[1]},{time,amount,extra}),'base64');
 fs.writeFileSync(path.join(out,'mesh.png'),await png(0,0));fs.writeFileSync(path.join(out,'masks.png'),await png(0,0,{maskView:true}));
 const hash=b=>createHash('sha256').update(b).digest('hex');const first=await png(1.25,1);await png(3.5,1);const deterministic=hash(first)===hash(await png(1.25,1));
 for(const time of [0,.5,1,1.5,2,2.5,3,3.5])fs.writeFileSync(path.join(out,`mesh-${time}.png`),await png(time,1));
 await page.evaluate(async source=>{const im=new Image();im.src='data:image/png;base64,'+source;await im.decode();renderer.setArtwork(im);},source);
 fs.writeFileSync(path.join(out,'hybrid.png'),await png(0,0));for(const time of [0,.5,1,1.5,2,2.5,3,3.5])fs.writeFileSync(path.join(out,`hybrid-${time}.png`),await png(time,1));
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({kind,meshDirectory:path.resolve(meshDir),meshSha256:hash(fs.readFileSync(path.resolve(meshDir,'mesh.json'))),runtimeSha256:hash(fs.readFileSync(path.join(root,'surface-runtime.js'))),deterministic,errors,...stats,passed:deterministic&&!errors.length},null,2));console.log(JSON.stringify({out,deterministic,errors,...stats}));
}finally{await browser.close();}
