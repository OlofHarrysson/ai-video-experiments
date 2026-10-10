/* A repeatable phrase of held print configurations, with a readable word as anchor.
   Durations are frames at 30 fps; three shorter accents interrupt the half-second grid. */
window.PrintMotion = (() => {
  const zero={top:0,bottom:0,topSt:0,bottomSt:0,reg:0,fan:0,checker:0};
  const phrases=[
    [15,5,{top:.85}],[12,3,{top:-.65}],[18,6,{top:.5,topSt:.25}],[15,3,{}],
    [15,6,{bottom:.8}],[18,4,{bottom:-.6}],[12,6,{bottom:.35,bottomSt:.6}],[15,3,{}],
    [10,3,{reg:.9,fan:1,checker:1}],[10,3,{topSt:.24,fan:2,checker:2}],
    [20,5,{bottomSt:-.3,fan:3,checker:3}],[20,3,{reg:-.8,fan:4,checker:4}],
    [15,4,{top:.85,bottom:-.65,fan:5,checker:4}],
    [15,6,{top:-.4,bottom:.3,fan:6,checker:3}],
    [15,8,{top:.15,bottom:-.15,fan:6,checker:2}],[15,5,{}],
  ];
  function sample(frame){
    let f=((frame%240)+240)%240,i=0;
    while(f>=phrases[i][0]){f-=phrases[i][0];i++;}
    const [duration,travel,values]=phrases[i],prev={...zero,...phrases[(i+15)%16][2]},next={...zero,...values};
    const t=Math.min(1,f/travel),e=1-Math.pow(1-t,3),pose={};
    for(const key of Object.keys(zero))pose[key]=prev[key]+(next[key]-prev[key])*e;
    // Motifs step like successive ink impressions; their forms do not smear through rotation.
    pose.fan=Math.round(pose.fan);pose.checker=Math.round(pose.checker);
    return {...pose,phrase:i,localFrame:f,duration};
  }
  return {sample,phrases};
})();
