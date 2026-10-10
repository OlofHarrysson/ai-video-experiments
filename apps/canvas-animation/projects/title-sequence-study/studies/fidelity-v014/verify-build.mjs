import fs from 'node:fs';import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';import {createRequire} from 'node:module';import {createHash} from 'node:crypto';
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.resolve(process.argv[2]);fs.mkdirSync(out,{recursive:true});
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright'),hash=b=>createHash('sha256').update(b).digest('hex');
const browser=await chromium.launch(),report={};
try{
 for(const [file,baseline,mesh]of [['index.html','output-motion-v004',false],['mesh.html','output-motion-v001',true]]){
  const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.join(root,file)).href);await page.waitForFunction(()=>window.ready);
  const checks={},neutralDeltas={};
  for(const [i,id]of ['billions','keep'].entries()){
   const encoded=await page.evaluate(i=>{const c=document.querySelector('canvas');c.width=1672;c.height=941;drawFrame(i*96,true);return c.toDataURL().split(',')[1]},i),png=Buffer.from(encoded,'base64');
   fs.writeFileSync(path.join(out,(mesh?'mesh-':'hybrid-')+id+'.png'),png);
   const prior=fs.readFileSync(path.join(root,baseline,id+'-unlit.png'));checks[id]=hash(png)===hash(prior);
   if(mesh){
    const delta=await page.evaluate(async({before,after})=>{const pixels=async(encoded)=>{const im=new Image();im.src='data:image/png;base64,'+encoded;await im.decode();const c=Object.assign(document.createElement('canvas'),{width:im.width,height:im.height}),g=c.getContext('2d');g.drawImage(im,0,0);return g.getImageData(0,0,c.width,c.height).data};const a=await pixels(before),b=await pixels(after);let max=0,total=0,count=0;for(let i=0;i<a.length;i++){if(i%4===3)continue;const d=Math.abs(a[i]-b[i]);max=Math.max(max,d);total+=d;count++;}return {max,mae:total/count};},{before:prior.toString('base64'),after:png.toString('base64')});
    neutralDeltas[id]=delta;checks[id]=delta.max<=1;
   }
  }
  if(!mesh){
   const encoded=await page.evaluate(()=>{const c=document.querySelector('canvas');c.width=3200;c.height=1800;drawFrame(25);const copy=Object.assign(document.createElement('canvas'),{width:1600,height:900}),g=copy.getContext('2d');g.imageSmoothingQuality='high';g.drawImage(c,0,0,1600,900);return copy.toDataURL().split(',')[1]});
   checks.selectedFrame=hash(Buffer.from(encoded,'base64'))===hash(fs.readFileSync(path.join(root,baseline,'frame-0025.png')));
  }
  report[file]={checks,neutralDeltas,comparisonNote:mesh?'Neutral shader now bypasses a gamma round trip; permit at most one RGB code value versus the frozen earlier mesh.':'Exact PNG identity required.',errors,sha256:hash(fs.readFileSync(path.join(root,file))),passed:Object.values(checks).every(Boolean)&&!errors.length};await page.close();
 }
 fs.writeFileSync(path.join(out,'build-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(Object.values(report).some(x=>!x.passed))process.exitCode=1;
}finally{await browser.close()}
