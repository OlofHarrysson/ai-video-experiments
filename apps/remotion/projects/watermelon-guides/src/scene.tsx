import React from 'react';
import {AbsoluteFill,Composition,Img,registerRoot,staticFile,useCurrentFrame} from 'remotion';
const N=1024;
export const scenePosition=(frame:number)=>({cx:250+520*Math.min(80,Math.max(0,frame))/80,cy:650,r:130});
function Scene({kind}:{kind:'guide'|'mask'|'background'|'layout'}){
 const {cx,cy,r}=scenePosition(useCurrentFrame());
 return <AbsoluteFill style={{background:kind==='mask'?'black':'#ddd'}}>
  {(kind==='guide'||kind==='background')&&<Img src={staticFile('scene/background.png')} style={{width:N,height:N}}/>}
  <svg width={N} height={N} viewBox={`0 0 ${N} ${N}`} style={{position:'absolute'}}>
   {kind==='layout'&&<><rect width={N} height={420} fill="#e7e0d7"/><path d="M0 420H1024V1024H0Z" fill="#b78b54"/><rect x={30} y={30} width={140} height={260} fill="#d7e8f1"/></>}
   {(kind==='guide'||kind==='layout')&&<circle cx={cx} cy={cy} r={r} fill="#559530"/>}
   {kind==='mask'&&<><circle cx={cx} cy={cy} r={r+15} fill="white"/><ellipse cx={cx+45} cy={cy+r} rx={180} ry={45} fill="white"/></>}
  </svg>
 </AbsoluteFill>;
}
const Root=()=> <>{(['guide','mask','background','layout'] as const).map(kind=><Composition key={kind} id={`Scene-${kind}`} component={Scene} defaultProps={{kind}} durationInFrames={81} fps={16} width={N} height={N}/>)}</>;
registerRoot(Root);
