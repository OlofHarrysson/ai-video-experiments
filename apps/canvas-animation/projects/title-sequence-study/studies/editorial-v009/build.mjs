import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const scripts=['outlines.js','art.js','edit.js','viewer.js'].map(f=>fs.readFileSync(path.join(here,f),'utf8')).join('\n');
const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Make it Move — silent edit</title>
<style>*{box-sizing:border-box}body{background:#141416;color:#efeee9;font:16px system-ui;margin:0;padding:24px}main{max-width:1280px;margin:auto}h1{font-size:22px;font-weight:600}p{color:#b8b5b2;line-height:1.5}canvas{display:block;width:100%;height:auto;background:#060609}nav{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:18px 0}button,select{font:inherit;padding:9px 14px;border:1px solid #555;background:#242427;color:#eee;border-radius:4px}button{cursor:pointer}input{flex:1;min-width:160px;accent-color:#ff7074}a{color:#d7c8ff}output{font-variant-numeric:tabular-nums;min-width:80px}details{margin-top:24px}summary{cursor:pointer}#error{color:#ffa39f}</style>
<main><h1>Make it Move</h1><p>Twelve seconds of silent typography. Eight selected compositions, one recurring phrase.</p><canvas id="art" width="1600" height="900"></canvas>
<nav><button id="play">Play</button><input id="seek" aria-label="Frame" type="range" min="0" max="287" value="0"><output id="time">0.00 s</output><button id="save">Save frame</button></nav><div id="error" role="status"></div>
<p><a href="review.html">Watch the rendered film</a></p><details><summary>Explore the design studies</summary><nav><select id="card" aria-label="Design"><option value="">Edited sequence</option></select></nav><p id="description"></p><p><a href="README.md">Selection and screening notes</a></p></details></main><script>${scripts}</script></html>`;
fs.writeFileSync(path.join(here,'index.html'),html);
console.log('Built self-contained index.html');
