import fs from 'node:fs/promises';

// Compare identical poses and timing; only motion interpolation differs.
const out='assets/dense-nuzzle/composition';
await fs.mkdir(out,{recursive:true});
for(const [source,target] of [['assets/gsap.min.js','gsap.min.js'],['renders/dense-nuzzle-drawings.mp4','drawings.mp4'],['renders/dense-nuzzle-60fps.mp4','smooth.mp4']])await fs.copyFile(source,`${out}/${target}`);
const html=`<!doctype html><html><head><meta charset="utf-8"><title>Dense nuzzle comparison</title><script src="gsap.min.js"></script><style>
*{box-sizing:border-box;margin:0}html,body,#film{width:1920px;height:1080px;overflow:hidden;background:#f1eadb}#film{position:relative;font-family:Arial,sans-serif;color:#23382d}h1{position:absolute;top:70px;width:1920px;text-align:center;font-size:48px;font-weight:500}.panel{position:absolute;top:270px;width:960px;height:540px;overflow:hidden}.left{left:0}.right{left:960px}video{width:960px;height:540px;object-fit:contain}.label{position:absolute;top:185px;width:960px;text-align:center;font-size:34px;font-weight:600}.caption{position:absolute;top:865px;width:1920px;text-align:center;font-size:30px;line-height:1.3}.divider{position:absolute;left:958px;top:270px;width:4px;height:540px;background:#f1eadb}
</style></head><body><div id="film" data-composition-id="dense-nuzzle" data-width="1920" data-height="1080" data-duration="4"><h1>The nuzzle · motion test</h1><div class="label left">Generated poses · 6 changes/sec</div><div class="label right">RIFE in-betweens · 60 fps</div><div class="panel left"><video id="raw" class="clip" src="drawings.mp4" data-start="0" data-duration="4" data-track-index="1" muted playsinline width="960" height="540"></video></div><div class="panel right"><video id="smooth" class="clip" src="smooth.mp4" data-start="0" data-duration="4" data-track-index="2" muted playsinline width="960" height="540"></video></div><div class="divider"></div><div class="caption">Same 12 source drawings · same two-second action</div><div class="caption" style="top:915px">Right side adds 99 inferred frames between the drawings</div></div><script>
const tl=gsap.timeline({paused:true});tl.to({t:0},{t:4,duration:4,ease:'none'});window.__timelines=window.__timelines||{};window.__timelines['dense-nuzzle']=tl;
</script></body></html>`;
await fs.writeFile(`${out}/index.html`,html);
await fs.writeFile(`${out}/hyperframes.json`,JSON.stringify({authoringSkill:'general-video'}));
console.log('Built four-second comparison with explicit generated/interpolated labels.');
