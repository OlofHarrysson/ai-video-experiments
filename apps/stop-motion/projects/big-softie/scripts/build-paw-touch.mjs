import fs from 'node:fs/promises';
const out='assets/paw-touch/composition';
await fs.mkdir(out,{recursive:true});
await fs.copyFile('assets/gsap.min.js',`${out}/gsap.min.js`);
await fs.copyFile('assets/paw-touch/paw-touch-master.mp4',`${out}/scene.mp4`);
await fs.writeFile(`${out}/index.html`,`<!doctype html>
<html><head><meta charset="utf-8"><title>Big Softie · a gentle touch</title><script src="gsap.min.js"></script>
<style>*{margin:0;box-sizing:border-box}html,body,#film{width:1920px;height:1080px;overflow:hidden;background:#7a8055}#film{position:relative}#scene{position:absolute;inset:0;width:1920px;height:1080px;object-fit:contain}</style></head>
<body><div id="film" data-composition-id="paw-touch" data-width="1920" data-height="1080" data-duration="4"><video id="scene" class="clip" src="scene.mp4" data-start="0" data-duration="4" data-track-index="0" muted playsinline width="1920" height="1080"></video></div>
<script>const tl=gsap.timeline({paused:true});tl.to({t:0},{t:4,duration:4,ease:'none'});window.__timelines=window.__timelines||{};window.__timelines['paw-touch']=tl;</script></body></html>`);
await fs.writeFile(`${out}/hyperframes.json`,JSON.stringify({authoringSkill:'general-video'}));
console.log('Built the four-second clean composition.');
