import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import crypto from 'node:crypto';
const here=path.dirname(fileURLToPath(import.meta.url));
const {chromium}=createRequire(path.join(here,'../../../../.agents/skills/animate/package.json'))('playwright');
const [manifestArg,vectorArg,outArg]=process.argv.slice(2);
if(!outArg)throw Error('Usage: node inspect.mjs manifest.json vector-directory new-output-directory');
const manifest=path.resolve(manifestArg),vectors=path.resolve(vectorArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('Output exists; choose a fresh version.');
const config=JSON.parse(fs.readFileSync(manifest,'utf8'));
const record=JSON.parse(fs.readFileSync(path.join(vectors,'assets.json'),'utf8'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
if(sha(fs.readFileSync(manifest))!==record.manifestSha256)throw Error('Manifest changed since trace; retrace into a fresh directory');
const runtime=fs.readFileSync(path.join(here,'runtime.js'),'utf8');
const bundle=record.assets.map(a=>{
 const source=fs.readFileSync(path.resolve(path.dirname(manifest),a.source));
 if(sha(source)!==a.sourceSha256)throw Error(`Source changed: ${a.id}`);
 return {...a,sourceURI:'data:image/png;base64,'+source.toString('base64'),
  vectorURI:'data:image/svg+xml;base64,'+fs.readFileSync(path.join(vectors,a.id+'.svg')).toString('base64')};
});
const browser=await chromium.launch();
try{
 const page=await browser.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.setContent('<body></body>');await page.addScriptTag({content:runtime});
 const results=await page.evaluate(async bundle=>{
  const results=[];
  for(const raw of bundle){
   const asset=Lettering.prepare(raw),canvases=[];
   for(const uri of [raw.sourceURI,raw.vectorURI]){
    const image=new Image();image.src=uri;await image.decode();
    const c=document.createElement('canvas');c.width=raw.width;c.height=raw.height;
    const g=c.getContext('2d',{willReadFrequently:true});g.fillStyle='#000';g.fillRect(0,0,c.width,c.height);g.drawImage(image,0,0);
    canvases.push(g.getImageData(0,0,c.width,c.height).data);
   }
   let intersection=0,union=0,sourceCount=0,vectorCount=0;
   for(let i=0;i<canvases[0].length;i+=4){
    const luminance=(canvases[0][i]+canvases[0][i+1]+canvases[0][i+2])/3;
    const a=raw.foreground==='dark'?luminance<=raw.threshold:luminance>raw.threshold;
    const b=canvases[1][i]>127;
    if(a&&b)intersection++;if(a||b)union++;if(a)sourceCount++;if(b)vectorCount++;
   }
   const {sourceURI,vectorURI,...saved}=Lettering.serializable(asset);
   results.push({asset:saved,metrics:{iou:intersection/union,retainedForeground:intersection/sourceCount,
    extraForeground:(vectorCount-intersection)/vectorCount}});
  }
  // Meaningful guardrails: bad grouping must stop instead of silently losing/duplicating art.
  const base=bundle[0],checks={};
  for(const [name,groups] of Object.entries({
   duplicate:[{id:'a',region:[0,0,1,1]},{id:'b',region:[0,0,1,1]}],
   missing:[{id:'a',parts:[base.parts[0].id]}],
   unknown:[{id:'a',parts:['nonexistent']}]
  })) {try{Lettering.prepare({...base,groups});checks[name]=false;}catch{checks[name]=true;}}
  return {results,checks};
 },bundle);
 if(errors.length)throw Error(errors.join('\n'));
 fs.mkdirSync(out,{recursive:true});
 const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
 <title>Lettering inspection</title><style>body{margin:24px;background:#151515;color:#eee;font:16px system-ui}header{display:flex;gap:12px;align-items:center;flex-wrap:wrap}button,select{font:inherit;padding:8px;background:#292929;color:white;border:1px solid #777;border-radius:4px}canvas{display:block;width:100%;height:auto;max-height:75vh;object-fit:contain;margin-top:18px}p{line-height:1.5;max-width:85ch}#status{font-size:14px;color:#bbb}</style>
 <header><select id="asset" aria-label="Lettering asset"></select><select id="mode" aria-label="Inspection view"><option value="compare">Source / vector</option><option value="overlay">Overlay differences</option><option value="groups">Groups and pivots</option></select><select id="group" aria-label="Isolate group"></select></header>
 <p id="status"></p><canvas id="canvas"></canvas>
 <script>${runtime}\nconst raw=${JSON.stringify(bundle).replaceAll('<','\\u003c')};const metrics=${JSON.stringify(results.results.map(r=>r.metrics))};
 const shapes=raw.map(Lettering.prepare),images=[];const asset=document.querySelector('#asset'),mode=document.querySelector('#mode'),group=document.querySelector('#group');
 shapes.forEach((a,i)=>asset.add(new Option(a.text,i)));
 async function init(){for(const r of raw){const img=new Image();img.src=r.sourceURI;await img.decode();images.push(img);}updateGroups();draw();window.ready=true;}
 function updateGroups(){group.replaceChildren(new Option('All groups',''));shapes[asset.value].groups.forEach(g=>group.add(new Option(g.label,g.id)));}
 function draw(){const a=shapes[asset.value],c=document.querySelector('canvas');c.width=a.width*(mode.value==='compare'?2:1);c.height=a.height;const g=c.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,c.width,c.height);
 const selected=group.value?a.groups.find(x=>x.id===group.value):a;
 if(mode.value==='compare'){g.drawImage(images[asset.value],0,0);g.translate(a.width,0);g.fillStyle='white';g.fill(selected.path);}
 if(mode.value==='overlay'){g.globalAlpha=.55;g.drawImage(images[asset.value],0,0);g.globalCompositeOperation='screen';g.fillStyle='#00cda0';g.fill(selected.path);g.globalCompositeOperation='source-over';g.globalAlpha=1;}
 if(mode.value==='groups'){a.groups.filter(x=>!group.value||x.id===group.value).forEach((x,i)=>{g.fillStyle=['#e4ff65','#ee799d','#75caff','#f7b96e'][i%4];g.fill(x.path);const [l,t,w,h]=x.bounds;g.strokeStyle='white';g.lineWidth=2;g.strokeRect(l,t,w,h);g.beginPath();g.arc(...x.pivotPoint,10,0,Math.PI*2);g.stroke();g.font='24px sans-serif';g.fillText(x.label,l,t-10);});}
 const m=metrics[asset.value];document.querySelector('#status').textContent=a.text+' · '+a.parts.length+' paths · '+a.groups.length+' groups · mask overlap '+(100*m.iou).toFixed(2)+'%. Inspect corners, counters and detached details; overlap is not an aesthetic score.';}
 asset.onchange=()=>{updateGroups();draw();};mode.onchange=draw;group.onchange=draw;init().catch(e=>{document.querySelector('#status').textContent=e.message;console.error(e)});</script></html>`;
 fs.writeFileSync(path.join(out,'inspect.html'),html);
 await page.goto(pathToFileURL(path.join(out,'inspect.html')).href);await page.waitForFunction(()=>window.ready);
 await page.setViewportSize({width:1400,height:900});
 for(let i=0;i<bundle.length;i++){
  await page.selectOption('#asset',String(i));await page.selectOption('#mode','compare');
  await page.locator('canvas').screenshot({path:path.join(out,bundle[i].id+'-comparison.png')});
  await page.selectOption('#mode','groups');
  await page.locator('canvas').screenshot({path:path.join(out,bundle[i].id+'-groups.png')});
  for(const group of results.results[i].asset.groups){await page.selectOption('#group',group.id);}
  await page.selectOption('#group','');await page.selectOption('#mode','overlay');
 }
 await page.setViewportSize({width:390,height:800});
 const mobileOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 const report={passed:errors.length===0&&!mobileOverflow&&Object.values(results.checks).every(Boolean)&&results.results.every(r=>r.metrics.iou>.98),
  errors,mobileOverflow,guardChecks:results.checks,assets:results.results.map(r=>({id:r.asset.id,paths:r.asset.parts.length,groups:r.asset.groups,...r.metrics}))};
 fs.writeFileSync(path.join(out,'prepared.json'),JSON.stringify({schema:1,assets:results.results.map(r=>r.asset)},null,2));
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({passed:report.passed,checks:report.guardChecks,assets:report.assets.map(({groups,...a})=>({...a,groups:groups.map(g=>({id:g.id,parts:g.parts,bounds:g.bounds}))}))}));
 if(!report.passed)throw Error('Inspection failed; read report.json');
}finally{await browser.close();}
