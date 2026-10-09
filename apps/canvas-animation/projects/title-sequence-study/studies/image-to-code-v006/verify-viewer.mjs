import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const {chromium}=createRequire(new URL('../../../../../../.agents/skills/animate/package.json',import.meta.url))('playwright');
const here=path.dirname(fileURLToPath(import.meta.url)),out=path.join(here,process.argv[2]||'output-viewer-check');if(fs.existsSync(out))throw new Error('Choose a new output path.');fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch();
try{
 const page=await browser.newPage({viewport:{width:1600,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.join(here,'index.html')).href);await page.waitForFunction(()=>window.ready,{},{timeout:120000});
 await page.screenshot({path:path.join(out,'comparison.png'),fullPage:true});
 await page.getByRole('button',{name:'Reference on'}).click();await page.locator('#mode').selectOption('blue');await page.screenshot({path:path.join(out,'silver.png'),fullPage:true});
 await page.locator('summary').click();await page.locator('#depth').fill('0');await page.locator('#depth').dispatchEvent('input');await page.locator('#glyph').selectOption('W');
 const svgDownload=page.waitForEvent('download');await page.getByRole('button',{name:'Save SVG paths'}).click();const svg=await svgDownload;await svg.saveAs(path.join(out,'isolated-W.svg'));
 const pngDownload=page.waitForEvent('download');await page.getByRole('button',{name:'Save PNG',exact:true}).click();const png=await pngDownload;await png.saveAs(path.join(out,'isolated-W.png'));
 const svgCheck=await page.evaluate(svg=>{const doc=new DOMParser().parseFromString(svg,'image/svg+xml');return {valid:!doc.querySelector('parsererror'),paths:doc.querySelectorAll('path').length,ids:[...doc.querySelectorAll('g')].map(g=>g.id),images:doc.querySelectorAll('image').length}},fs.readFileSync(path.join(out,'isolated-W.svg'),'utf8'));
 await page.locator('#glyph').selectOption('');await page.locator('#mode').selectOption('enamel');await page.locator('#depth').fill('34');await page.locator('#depth').dispatchEvent('input');await page.locator('#phase').fill('51');await page.locator('#phase').dispatchEvent('input');
 const before=await page.locator('#phase').inputValue();await page.getByRole('button',{name:'Play light'}).click();await page.waitForFunction(()=>document.querySelector('#phase').value!=='51',{},{timeout:30000});await page.getByRole('button',{name:'Pause',exact:true}).click();const after=await page.locator('#phase').inputValue();
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
 const noOverflow=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth);
 const timings=await page.evaluate(()=>{const values={full:[],preview:[]};for(const [name,quality]of [['full',2],['preview',.5]])for(let i=0;i<4;i++){const start=performance.now();WildRenderer.draw(document.querySelector('#art'),i*12,{quality});values[name].push(performance.now()-start)}return values});
 const report={errors,svgCheck,playbackAdvanced:before!==after,noOverflow,renderMilliseconds:timings};report.passed=errors.length===0&&svgCheck.valid&&svgCheck.paths===1&&svgCheck.ids[0]==='W'&&svgCheck.images===0&&report.playbackAdvanced&&noOverflow;fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(report);if(!report.passed)process.exitCode=1;
}finally{await browser.close()}
