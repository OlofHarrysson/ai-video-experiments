import fs from 'node:fs/promises';
import sharp from 'sharp';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
const ROOT='assets/paw-touch';
const source=`${ROOT}/rife-full/frames`,out=`${ROOT}/finished-frames`;
const W=1280,H=720,FPS=60;
const HOLD_BEFORE=30,HOLD_AFTER=90;
const PAW={left:718,top:494,width:144,height:140};
const EYES={left:638,top:312,width:98,height:55};
await fs.mkdir(out,{recursive:true});
const get=async p=>sharp(p).removeAlpha().raw().toBuffer();
const base=await get(`${ROOT}/rife-input/000000.png`);
const isAllowed=(x,y)=>[PAW,EYES].some(r=>x>=r.left&&x<r.left+r.width&&y>=r.top&&y<r.top+r.height);
const fixed=[];for(let y=0;y<H;y++)for(let x=0;x<W;x++)if(!isAllowed(x,y))fixed.push((y*W+x)*3);
const files=(await fs.readdir(source)).filter(f=>/^[0-9]+\.png$/.test(f)).sort();
if(files.length!==120)throw new Error('Expected the complete 120-frame RIFE sequence.');
const rows=[];
for(let i=0;i<files.length;i++){
 const raw=await get(`${source}/${files[i]}`),dst=Buffer.from(base);
 for(const r of [PAW,EYES])for(let y=r.top;y<r.top+r.height;y++)raw.copy(dst,(y*W+r.left)*3,(y*W+r.left)*3,(y*W+r.left+r.width)*3);
 for(const k of fixed)for(let c=0;c<3;c++)if(dst[k+c]!==base[k+c])throw new Error(`Static pixel changed at frame ${i}`);
 const path=`${out}/${String(i).padStart(4,'0')}.png`;await sharp(dst,{raw:{width:W,height:H,channels:3}}).png().toFile(path);
 rows.push({index:i,sha256:createHash('sha256').update(dst).digest('hex')});
}
// Encode the finished pixels, then let HyperFrames own final composition rendering.
execFileSync('ffmpeg',['-v','error','-framerate',String(FPS),'-i',`${out}/%04d.png`,'-vf',`tpad=start_duration=${HOLD_BEFORE/FPS}:stop_duration=${HOLD_AFTER/FPS}:start_mode=clone:stop_mode=clone`,'-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',`${ROOT}/paw-touch-master.mp4`,'-y']);
await fs.writeFile(`${ROOT}/finish-manifest.json`,JSON.stringify({fps:FPS,width:W,height:H,sourceFrames:120,holdBeforeFrames:HOLD_BEFORE,holdAfterFrames:HOLD_AFTER,deliveryFrames:240,durationSeconds:4,allowedRegions:{paw:PAW,eyes:EYES},verifiedFixedPixelsPerFrame:fixed.length,uniqueFinishedMotionFrames:new Set(rows.map(r=>r.sha256)).size,frames:rows},null,2));
console.log('Finished 120 frames; verified',fixed.length,'fixed pixels in every frame.');
