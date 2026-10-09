import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const here=path.dirname(fileURLToPath(import.meta.url));
const browser=await chromium.launch();
try{
  const page=await browser.newPage(),errors=[],requests=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
  await page.setContent('<body><canvas id="art" width="1536" height="1024"></canvas></body>');
  for(const f of ['../../node_modules/clipper-lib/clipper.js','vector-fields.js'])await page.addScriptTag({path:path.join(here,f)});
  const fields=await page.evaluate(()=>{
    const tests=[];
    for(const density of [1,2]){
      const shape={d:'M0 0 L60 0 L60 60 L0 60Z M20 20 L20 40 L40 40 L40 20Z'};
      const contours=VectorFields.contours(shape,0),box=[-10,-10,80,80],f=VectorFields.field(contours.face,box,density);
      let maxError=0,wrongSign=0;
      function edgeDistance(x,y,a,b){const dx=b[0]-a[0],dy=b[1]-a[1],t=Math.max(0,Math.min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));return Math.hypot(x-a[0]-dx*t,y-a[1]-dy*t)}
      for(let j=0;j<80*density;j++)for(let i=0;i<80*density;i++){
        const x=-10+(i+.5)/density,y=-10+(j+.5)/density,inside=x>0&&x<60&&y>0&&y<60&&!(x>20&&x<40&&y>20&&y<40);
        let distance=Infinity;for(const poly of contours.face)for(let k=0;k<poly.length;k++)distance=Math.min(distance,edgeDistance(x,y,poly[k],poly[(k+1)%poly.length]));
        const expected=distance*(inside?1:-1),actual=f.distance[j*80*density+i];maxError=Math.max(maxError,Math.abs(expected-actual));if((actual>0)!==inside)wrongSign++;
      }
      tests.push({density,maxError,wrongSign,passed:maxError<.0001&&wrongSign===0});
    }
    return tests;
  });
  for(const f of ['geometry.js','details.js','facets.js','renderer.js'])await page.addScriptTag({path:path.join(here,f)});
  const hashes={};
  for(const [name,frame,options]of [['first',0,{}],['middle',72,{}],['repeat',0,{}],['loop',144,{}],['noDepth',0,{depth:0}],['silver',0,{palette:1}],['flat',0,{flat:true}],['isolated',0,{glyph:'W'}],['preview',48,{quality:.5}],['restored',0,{}]]){
    const pixels=await page.evaluate(({frame,options})=>{WildRenderer.draw(document.querySelector('#art'),frame,options);return document.querySelector('#art').toDataURL().split(',')[1]},{frame,options});
    hashes[name]=createHash('sha256').update(Buffer.from(pixels,'base64')).digest('hex');
  }
  const report={fields,hashes,deterministic:hashes.first===hashes.repeat&&hashes.first===hashes.restored,exactLoop:hashes.first===hashes.loop,controlsChangePixels:['middle','noDepth','silver','flat','isolated'].every(k=>hashes[k]!==hashes.first),networkRequests:requests,errors};
  report.passed=fields.every(t=>t.passed)&&report.deterministic&&report.exactLoop&&report.controlsChangePixels&&requests.length===0&&errors.length===0;
  const out=path.join(here,process.argv[2]||'output-validation');fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));if(!report.passed)process.exitCode=1;
}finally{await browser.close()}
