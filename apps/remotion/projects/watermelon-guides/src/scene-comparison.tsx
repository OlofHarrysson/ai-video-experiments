import React from 'react';
import {AbsoluteFill,Composition,Img,OffthreadVideo,registerRoot,staticFile,useCurrentFrame} from 'remotion';
const sourceFrames=[0,13,27,40,53,67,80];
function Comparison(){
 const frame=useCurrentFrame();const sourceFrame=frame*16/24;
 const index=sourceFrames.reduce((best,f,i)=>Math.abs(f-sourceFrame)<Math.abs(sourceFrames[best]-sourceFrame)?i:best,0);
 const panels=[['guide.mp4','Authored guide · exact circle path'],['stills','Sunburst · 7 independent images, held'],['ltx.mp4','LTX 2.3 · guide + 3 keyframe images'],['h3.mp4','H3 Max · guide + first scene image']];
 return <AbsoluteFill style={{background:'#202428',color:'white',fontFamily:'Arial'}}>
  <div style={{height:64,padding:'15px 22px',fontSize:24}}>Spatial control in a scene · watch position, rind and tabletop</div>
  <div style={{display:'grid',gridTemplateColumns:'1fr 1fr'}}>{panels.map(([file,title])=><div key={file} style={{height:552}}><div style={{height:40,paddingLeft:16,fontSize:20}}>{title}</div>{file==='stills'?<Img src={staticFile(`scene-review/still-${index}.png`)} style={{width:512,height:512}}/>:<OffthreadVideo src={staticFile(`scene-review/${file}`)} muted style={{width:512,height:512}}/>}</div>)}</div>
 </AbsoluteFill>;
}
function BackgroundLock(){
 const frame=useCurrentFrame();const sourceFrame=frame*16/24;
 const i=sourceFrames.reduce((best,f,index)=>Math.abs(f-sourceFrame)<Math.abs(sourceFrames[best]-sourceFrame)?index:best,0);
 const cx=250+520*sourceFrames[i]/80;
 return <AbsoluteFill><Img src={staticFile('scene/background.png')} style={{width:1024,height:1024}}/><svg width={1024} height={1024} style={{position:'absolute'}}><defs><filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation={5}/></filter><mask id="edit"><g filter="url(#soft)" fill="white"><circle cx={cx} cy={650} r={145}/><ellipse cx={cx+45} cy={780} rx={220} ry={70}/></g></mask></defs><image href={staticFile(`scene-review/still-${i}.png`)} width={1024} height={1024} mask="url(#edit)"/></svg></AbsoluteFill>;
}
registerRoot(()=> <><Composition id="SceneComparison" component={Comparison} durationInFrames={122} fps={24} width={1024} height={1168}/><Composition id="SceneBackgroundLock" component={BackgroundLock} durationInFrames={122} fps={24} width={1024} height={1024}/></>);
