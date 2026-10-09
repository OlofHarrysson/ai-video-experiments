// Compare the numerical distance helper against an independent brute-force oracle.
import fs from 'node:fs';import vm from 'node:vm';
const context={window:{}};vm.runInNewContext(fs.readFileSync(new URL('surface.js',import.meta.url),'utf8'),context);
const distance=context.window.TypeSurface.euclideanDistance;
const cases=[];for(let k=0;k<18;k++){const w=7+k%5,h=8+k%4,mask=[];for(let y=0;y<h;y++)for(let x=0;x<w;x++)mask.push(x>0&&x<w-1&&y>0&&y<h-1&&(k===0||((x*17+y*31+k*13)%11)>k%5));cases.push({w,h,mask})}
let points=0,maxError=0;
for(const{w,h,mask}of cases){const got=distance(Float32Array.from(mask,v=>v?1e5:0),w,h);for(let y=0;y<h;y++)for(let x=0;x<w;x++){let expected=Infinity;for(let py=0;py<h;py++)for(let px=0;px<w;px++)if(!mask[py*w+px])expected=Math.min(expected,Math.hypot(x-px,y-py));const error=Math.abs(got[y*w+x]-expected);maxError=Math.max(maxError,error);if(error>1e-5)throw new Error(`Distance error at ${x},${y}: ${got[y*w+x]} != ${expected}`);points++}}
console.log(JSON.stringify({cases:cases.length,points,maxError,passed:true}));
