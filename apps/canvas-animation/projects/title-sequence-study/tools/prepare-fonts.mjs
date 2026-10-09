import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import opentype from 'opentype.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const sources={anton:'fonts/Anton-Regular.ttf',gothic:'studies/typography-v001/fonts/UnifrakturCook-Bold.ttf'};
const fonts=Object.fromEntries(Object.entries(sources).map(([k,p])=>{const b=fs.readFileSync(path.join(root,p));return [k,opentype.parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength))]}));
// Flatten curves to points so each point can move independently during rendering.
function contours(commands){let out=[],line=[],p={x:0,y:0};for(const c of commands){
 if(c.type==='M'){if(line.length)out.push(line);line=[[c.x,c.y]];p=c;}
 else if(c.type==='Z'){if(line.length)out.push(line);line=[];}
 else {const a=p,n=c.type==='L'?Math.max(1,Math.ceil(Math.hypot(c.x-a.x,c.y-a.y)/8)):16;
 for(let i=1;i<=n;i++){const t=i/n,u=1-t;let x,y;
 if(c.type==='L'){x=a.x+(c.x-a.x)*t;y=a.y+(c.y-a.y)*t;}
 else if(c.type==='Q'){x=u*u*a.x+2*u*t*c.x1+t*t*c.x;y=u*u*a.y+2*u*t*c.y1+t*t*c.y;}
 else{x=u*u*u*a.x+3*u*u*t*c.x1+3*u*t*t*c.x2+t*t*t*c.x;y=u*u*u*a.y+3*u*u*t*c.y1+3*u*t*t*c.y2+t*t*t*c.y;}
 line.push([+x.toFixed(3),+y.toFixed(3)]);}p=c;}}
 if(line.length)out.push(line);return out;}
const specs={more:['anton','MORE'],signal:['anton','SIGNAL'],faster:['anton','FASTER'],everything:['anton','EVERYTHING'],overdrive:['gothic','Overdrive'],becoming:['gothic','Becoming']};
const data={};for(const [key,[face,word]] of Object.entries(specs)){
 const f=fonts[face],p=f.getPath(word,0,0,260),b=p.getBoundingBox();
 const scale=Math.min(1080/(b.x2-b.x1),290/(b.y2-b.y1));
 const shape=contours(p.commands).map(c=>c.map(([x,y])=>[(x-(b.x1+b.x2)/2)*scale,(y-(b.y1+b.y2)/2)*scale]));
 const letters=[];f.forEachGlyph(word,0,0,260,{},(glyph,x,y,size)=>{const p=glyph.getPath(x,y,size);letters.push(contours(p.commands).map(c=>c.map(([a,bY])=>[(a-(b.x1+b.x2)/2)*scale,(bY-(b.y1+b.y2)/2)*scale])))});
 data[key]={word,shape,letters};
}
fs.writeFileSync(path.join(root,'tools/font-data.js'),'window.MotionFonts='+JSON.stringify(data)+';\n');
console.log(JSON.stringify({words:Object.keys(data),fonts:Object.fromEntries(Object.entries(sources).map(([k,p])=>[k,{path:p,sha256:createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')}]))},null,2));
