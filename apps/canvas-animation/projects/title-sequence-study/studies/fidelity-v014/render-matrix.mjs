import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.resolve(process.argv[2]);
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const records=JSON.parse(fs.readFileSync(path.join(out,'manifest.json'))),browser=await chromium.launch();
try{
 const page=await browser.newPage();await page.setContent('<canvas></canvas>');
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const r of records){
  const data=JSON.parse(fs.readFileSync(path.join(out,r.key+'.json')));
  for(const scale of [1,3]){
   const b64=await page.evaluate(({data,scale})=>{
    const c=document.createElement('canvas');c.width=data.width*scale;c.height=data.height*scale;const g=c.getContext('2d');g.scale(scale,scale);g.fillStyle='black';g.fillRect(0,0,data.width,data.height);
    g.scale(1/(data.coordinateScale||1),1/(data.coordinateScale||1));for(const p of data.paths){const t=p.transform.match(/[-\d.]+/g)||[0,0];g.save();g.translate(+t[0],+t[1]);g.fillStyle=p.fill;g.fill(new Path2D(p.d));g.restore();}
    const dest=document.createElement('canvas');dest.width=data.width;dest.height=data.height;const q=dest.getContext('2d');q.imageSmoothingQuality='high';q.drawImage(c,0,0,dest.width,dest.height);return dest.toDataURL().split(',')[1];
   },{data,scale});fs.writeFileSync(path.join(out,r.key+`-ss${scale}.png`),Buffer.from(b64,'base64'));
  }
 }
 // Baseline is cropped from the full v013 proof, so small crop context cannot favor it.
 for(const id of ['billions','keep-up']){
  const box=records.find(r=>r.identity===id).crop,base=path.join(root,`../identity-motion-v013/output-proof-${id==='keep-up'?'keep':id}-v003/vector.png`);
  const image=fs.readFileSync(base).toString('base64');
  const b64=await page.evaluate(async({image,box})=>{const im=new Image();im.src='data:image/png;base64,'+image;await im.decode();const c=document.createElement('canvas');c.width=box[2]-box[0];c.height=box[3]-box[1];c.getContext('2d').drawImage(im,...box.slice(0,2),c.width,c.height,0,0,c.width,c.height);return c.toDataURL().split(',')[1]},{image,box});
  fs.writeFileSync(path.join(out,id+'-baseline.png'),Buffer.from(b64,'base64'));
 }
 if(errors.length)throw Error(errors.join('\n'));console.log('Rendered crop matrix, 1x and 3x.');
}finally{await browser.close();}
