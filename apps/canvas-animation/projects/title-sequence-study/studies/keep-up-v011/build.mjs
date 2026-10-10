import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const here=path.dirname(fileURLToPath(import.meta.url));
const opentype=createRequire(path.join(here,'../../package.json'))('opentype.js');
const readFont=name=>{const b=fs.readFileSync(path.join(here,'../../fonts/',name));return opentype.parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));};
const fonts={anton:readFont('Anton-Regular.ttf'),race:readFont('RacingSansOne-Regular.ttf')};
const copy={ai:['AI','race'],everything:['EVERYTHING JUST CHANGED','anton'],again:['AGAIN','race'],
 funding:['OPENAI / FUNDING ANNOUNCED / MAR 2025','anton'],more:['MORE','anton'],faster:['FASTER','race'],next:['NEXT','anton'],
 'am-i':['AM I','anton'],already:['ALREADY','anton'],behind:['BEHIND?','anton'],subtitle:['A FILM ABOUT ARTIFICIAL INTELLIGENCE','anton']};
const outlines=Object.fromEntries(Object.entries(copy).map(([id,[text,font]])=>{
 const p=fonts[font].getPath(text,0,0,1000),b=p.getBoundingBox();return [id,{text,d:p.toPathData(3),bounds:[b.x1,b.y1,b.x2-b.x1,b.y2-b.y1]}];
}));
fs.writeFileSync(path.join(here,'outlines.json'),JSON.stringify(outlines));
const assets=JSON.parse(fs.readFileSync(path.join(here,'vectors-v003/assets.json'),'utf8'));
const runtime=fs.readFileSync(path.join(here,'../../../../tools/lettering/runtime.js'),'utf8');
const art=fs.readFileSync(path.join(here,'art.js'),'utf8');
const scripts=runtime+'\nwindow.LetteringData='+JSON.stringify(assets)+';\nwindow.TypeOutlines='+JSON.stringify(outlines)+';\n'+art;
const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>KEEP UP — storyboard</title>
<style>*{box-sizing:border-box}body{margin:0;padding:24px;background:#171719;color:#eee;font:16px system-ui}main{max-width:1440px;margin:auto}h1{font-size:24px;margin:0 0 8px}p{color:#c2bfc4;line-height:1.5;max-width:85ch}nav{display:flex;flex-wrap:wrap;gap:12px;margin:18px 0}button,select{font:inherit;color:inherit;background:#27272b;border:1px solid #666;border-radius:4px;padding:9px}canvas{width:100%;height:auto;display:block;background:#08080b}a{color:#cabaff}details{margin-top:24px}#error{color:#ff8f84}</style>
<main><h1>KEEP UP</h1><p>A proposed silent intro about AI progress, money and the pressure to keep up. Six storyboard frames; motion has not been built.</p>
<nav><button id="prev">Previous</button><select id="frame" aria-label="Storyboard frame"></select><button id="next">Next</button></nav>
<canvas id="art" width="1600" height="900"></canvas><p id="description"></p><p id="error" role="status"></p>
<details><summary>Artwork and sources</summary><p>Three generated monochrome lettering plates, converted to editable vectors. Film frames draw only paths. Simple supporting copy uses Anton and Racing Sans One outlines from the project's existing licensed fonts.</p><p><a href="output-inspection-v003/inspect.html">Compare source artwork with vectors and inspect word groups</a> · <a href="BRIEF.md">Read the proposed sequence</a> · <a href="TOOLING.md">Tooling decisions</a> · <a href="prompts.json">Generation prompts</a></p><p>The money frame refers to <a href="https://openai.com/index/march-funding-updates/">OpenAI's funding announcement of 31 March 2025</a>. It is a dated example, not a current valuation or spending total.</p></details></main>
<script>${scripts}\nconst selector=document.querySelector('#frame');KeepUpArt.descriptions.forEach(f=>selector.add(new Option(f.label,f.id)));function show(id){KeepUpArt.draw(document.querySelector('#art'),id);selector.value=id;const d=KeepUpArt.descriptions.find(f=>f.id===id);document.querySelector('#description').textContent=d.time+' — '+d.motion;}
function step(n){const all=KeepUpArt.descriptions,i=all.findIndex(f=>f.id===selector.value);show(all[(i+n+all.length)%all.length].id);}
selector.onchange=()=>show(selector.value);document.querySelector('#prev').onclick=()=>step(-1);document.querySelector('#next').onclick=()=>step(1);
try{show('title');window.ready=true;}catch(e){document.querySelector('#error').textContent=e.message;throw e;}</script></html>`;
fs.writeFileSync(path.join(here,'index.html'),html);
console.log('Built vector-only storyboard preview');
