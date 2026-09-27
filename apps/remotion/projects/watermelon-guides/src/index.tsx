import React from 'react';
import {Composition, registerRoot, useCurrentFrame, AbsoluteFill, Img, staticFile} from 'remotion';
export const position = (frame:number) => ({cx:256+512*Math.min(72,Math.max(0,frame))/72,cy:512,r:180});
function Guide(){
 const {cx,cy,r}=position(useCurrentFrame());
 return <AbsoluteFill><svg viewBox="0 0 1024 1024" width="1024" height="1024"><rect width="1024" height="1024" fill="#202428"/><circle cx={cx} cy={cy} r={r} fill="#559530"/></svg></AbsoluteFill>;
}
function Comparison(){
 const frame=useCurrentFrame();const i=Math.min(6,Math.floor(frame/12));
 const panels=[['guide','Remotion guide'],['independent','Sunburst · circle only'],['reference','Sunburst · circle + fixed reference'],['inpaint','Qwen 2.1 · mask, fixed seed']];
 return <AbsoluteFill style={{background:'#202428',color:'white',fontFamily:'Arial'}}>
  <div style={{height:64,padding:'14px 24px',boxSizing:'border-box',fontSize:22}}>Watermelon placement · seven generated frames, held at 2 fps</div>
  <div style={{display:'grid',gridTemplateColumns:'1fr 1fr'}}>{panels.map(([key,label])=><div key={key} style={{position:'relative',height:548}}><div style={{height:36,paddingLeft:20,fontSize:20}}>{label}</div><Img src={staticFile(`${key}/${i}.png`)} style={{width:512,height:512}}/></div>)}</div>
 </AbsoluteFill>;
}
const Root=()=> <><Composition id="WatermelonGuide" component={Guide} durationInFrames={73} fps={24} width={1024} height={1024}/><Composition id="WatermelonComparison" component={Comparison} durationInFrames={84} fps={24} width={1024} height={1160}/></>;
registerRoot(Root);
