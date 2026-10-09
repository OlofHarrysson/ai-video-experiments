import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const here=path.dirname(fileURLToPath(import.meta.url));
const targets=[
  {file:'output-delivery-showcase/showcase.mp4',frames:610,height:720,duration:25.4166666667},
  {file:'output-release-library/catalogue.mp4',frames:816,height:768,duration:34},
  {file:'output-review-layouts/composition-catalogue.mp4',frames:336,height:768,duration:14},
  {file:'output-native-review/native-motion.mp4',frames:384,height:768,duration:16},
];
function run(command,args){const result=spawnSync(command,args,{encoding:'utf8',maxBuffer:8*1024*1024});if(result.status!==0)throw new Error(result.stderr||command+' failed');return result.stdout}
const artifacts=[];
for(const target of targets){
  const file=path.join(here,target.file);
  const data=JSON.parse(run('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',file]));
  const v=data.streams.find(s=>s.codec_type==='video');
  if(data.streams.some(s=>s.codec_type==='audio'))throw new Error('Unexpected audio');
  if(!v||v.width!==1280||v.height!==target.height||v.r_frame_rate!=='24/1'||Number(v.nb_read_frames)!==target.frames||Math.abs(Number(data.format.duration)-target.duration)>.01)throw new Error('Export mismatch: '+target.file);
  artifacts.push({...target,width:v.width,fps:24,audio:false,sha256:createHash('sha256').update(fs.readFileSync(file)).digest('hex'),sourceSnapshot:path.dirname(target.file)+'/source/'});
}
const timeline=JSON.parse(fs.readFileSync(path.join(here,'output-delivery-showcase/timeline.json'),'utf8'));
const stats=run('ffmpeg',['-v','error','-i',path.join(here,targets[0].file),'-vf','signalstats,metadata=mode=print:key=lavfi.signalstats.YMAX:file=-','-an','-f','null','-']);
const peaks=[...stats.matchAll(/lavfi\.signalstats\.YMAX=(\d+)/g)].map(m=>Number(m[1]));
if(peaks.length!==timeline.frames)throw new Error('Incomplete decoded frame stats');
let blackFrames=0;
for(let f=0;f<peaks.length;f++){
  const shot=timeline.shots.find(s=>f>=s.start&&f<s.end),black=peaks[f]<=20;
  if(black!==!shot.id)throw new Error(`Unexpected ${black?'black':'non-black'} frame ${f}`);
  if(black)blackFrames++;
}
const native=JSON.parse(fs.readFileSync(path.join(here,'output-release-inspection/report.json'),'utf8'));
const result={created:new Date().toISOString(),artifacts,validation:{allFramesDecoded:true,showcaseBlackFrames:blackFrames,blackFramesMatchTimeline:true,constructionStates:68,compositionStates:28,nativeChangeSamples:native.families.reduce((n,f)=>n+f.states.filter(s=>s.nativeChange).length,0),nativeSampleFrames:[0,11],browserErrors:native.errors}};
fs.writeFileSync(path.join(here,'release.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
