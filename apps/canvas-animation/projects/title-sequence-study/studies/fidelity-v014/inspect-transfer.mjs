import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const here=path.dirname(fileURLToPath(import.meta.url));
const {chromium}=createRequire(path.join(here,'../../../../../../.agents/skills/animate/package.json'))('playwright');
const [input,source,output]=process.argv.slice(2);
if(!output)throw Error('Usage: inspect-transfer.mjs vector-folder reference.png new-output-folder');
const out=path.resolve(output);if(fs.existsSync(out))throw Error('Output exists');fs.mkdirSync(out);
const data=JSON.parse(fs.readFileSync(path.resolve(input,'geometry.json'),'utf8'));
const js=`const asset=${JSON.stringify(data)};const paths=asset.paths.map(p=>{const path=new Path2D();const t=p.transform.match(/[-\\d.]+/g)||[0,0];path.addPath(new Path2D(p.d),new DOMMatrix().translate(Number(t[0]),Number(t[1])));return {...p,path};});
 function render(){const c=document.querySelector('canvas'),g=c.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,c.width,c.height);g.save();g.scale(1/(asset.coordinateScale||1),1/(asset.coordinateScale||1));for(const p of paths){g.fillStyle=p.fill;g.fill(p.path);}g.restore();}render();window.ready=true;`;
fs.writeFileSync(path.join(out,'vector.html'),`<!doctype html><html><meta charset="utf-8"><style>body{margin:0;background:black}canvas{width:100%;height:auto;display:block}</style><canvas width="${data.width}" height="${data.height}"></canvas><script>${js}</script></html>`);
const browser=await chromium.launch();
try{
 const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(out,'vector.html')).href);await page.waitForFunction(()=>window.ready);
 const result=await page.evaluate(()=>{const start=performance.now();render();const first=document.querySelector('canvas').toDataURL();render();return {png:first.split(',')[1],deterministic:first===document.querySelector('canvas').toDataURL(),twoDrawsMs:performance.now()-start};});
 fs.writeFileSync(path.join(out,'vector.png'),Buffer.from(result.png,'base64'));
 const original=fs.readFileSync(path.resolve(source)).toString('base64');
 const compare=await page.evaluate(async ({original,vector})=>{
  const c=document.createElement('canvas');c.width=2400;c.height=730;const g=c.getContext('2d');g.fillStyle='#17171b';g.fillRect(0,0,c.width,c.height);
  for(const [i,png]of [original,vector].entries()){const img=new Image();img.src='data:image/png;base64,'+png;await img.decode();g.drawImage(img,i*1200,0,1200,675);g.fillStyle='white';g.font='24px sans-serif';g.fillText(i?'Canvas drawing from traced vector paths':'Generated target',i*1200+24,711);}
  return c.toDataURL().split(',')[1];
 },{original,vector:result.png});
 fs.writeFileSync(path.join(out,'comparison.png'),Buffer.from(compare,'base64'));
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({passed:!errors.length&&result.deterministic,errors,deterministic:result.deterministic,paths:data.paths.length,twoDrawsWithPNGExportMs:result.twoDrawsMs,noRasterInVectorPage:true},null,2));
 console.log(JSON.stringify({paths:data.paths.length,errors,deterministic:result.deterministic,twoDrawsWithPNGExportMs:result.twoDrawsMs}));
}finally{await browser.close();}
