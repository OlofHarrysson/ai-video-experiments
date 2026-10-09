/* Fixed art direction variants. Placement changes between cards, never a camera pan. */
window.TypeCompositions=(()=>{
  const W=1280,H=720,make=()=>TypeLibrary.canvas(),cards=[];
  function layer(g,id,word,state,frame,{x=640,y=360,scale=1,angle=0,alpha=1}={}){
    const c=make();TypeLibrary.render(id,word,state,frame,c,{transparent:true});g.save();g.translate(x,y);g.rotate(angle);g.scale(scale,scale);g.globalAlpha=alpha;g.drawImage(c,-640,-360);g.restore();
  }
  function fit(g,word,box,font,fill,stroke=null,width=1){g.save();g.font=`${font==='Cormorant'?'700 ':''}200px ${font}`;const m=g.measureText(word),w=m.actualBoundingBoxLeft+m.actualBoundingBoxRight,h=m.actualBoundingBoxAscent+m.actualBoundingBoxDescent;g.translate(box[0],box[1]);g.scale(box[2]/w,box[3]/h);g.lineJoin='round';if(stroke){g.strokeStyle=stroke;g.lineWidth=width;g.strokeText(word,m.actualBoundingBoxLeft,m.actualBoundingBoxAscent)}if(fill){g.fillStyle=fill;g.fillText(word,m.actualBoundingBoxLeft,m.actualBoundingBoxAscent)}g.restore()}
  function add(id,name,draw){cards.push({id,name,draw})}
  add('breakout','Depth / broken frame',(g,s,f)=>layer(g,'depth','ECHO',s,f,{x:470,y:382,scale:1.86}));
  add('whisper','Mercury / tiny signal',(g,s,f)=>layer(g,'chrome','RUSH',s,f,{x:640,y:362,scale:.27}));
  add('monument','Giant glyph / razor caption',(g,s,f)=>{
    fit(g,'R',[-92,-145,1120,1050],'RubikMono',['#4f2277','#a72737','#d74425','#2f5488'][s]);
    layer(g,'wire','RAPTURE',s,f,{x:790,y:450,scale:.85});
  });
  add('triplicate','Wild / three exposures',(g,s,f)=>{
    for(let i=0;i<3;i++)layer(g,'tube','Wild',(s+i)%4,f,{x:640+(i-1)*54,y:197+i*207,scale:.7,angle:-.09});
  });
  add('interlock','Wild hours / script and serif',(g,s,f)=>{
    g.save();g.translate(640,360);g.rotate(-.09);g.translate(-640,-360);
    // The serif sits behind the original drawn upper word and its long exit curl.
    const shade=['#f5c57f','#c9edcd','#d6c2ea','#91dbdb'][s];
    for(let i=13;i>0;i--)fit(g,'Hours',[284+i*.6,371+i*.6,885,211],'Cormorant','#432840','#432840',5);
    fit(g,'Hours',[284,371,885,211],'Cormorant',shade,'#08070d',11);fit(g,'Hours',[284,371,885,211],'Cormorant',shade,shade,2);
    layer(g,s===1?'ribbon':'tube','Wild',s,f,{x:557,y:248,scale:.91});
    g.restore();
  });
  add('nightwall','Sign wall / competing scales',(g,s,f)=>{
    // Lamp ribbons create an environment, with gaps reserved for the hero lettering.
    for(let col=0;col<16;col++)for(let row=0;row<18;row++){
      const x=40+col*81,y=18+row*42;if(x>200&&x<1000&&y>190&&y<560)continue;
      const lit=(col+row+Math.floor(f/3))%5!==0;g.save();g.translate(x+Math.sin(row*.6)*10,y);g.rotate(Math.PI/4);g.fillStyle=lit?'#eac180':'#422b2b';g.fillRect(-2.5,-2.5,5,5);g.restore();
    }
    layer(g,'marquee','DYNAMO',(s+1)%4,f,{x:1050,y:116,scale:.36,angle:.15});
    layer(g,'palace','After Hours',(s+1)%4,f,{x:174,y:114,scale:.35,angle:-.2});
    layer(g,'wire','VELOCITY',1,f,{x:995,y:623,scale:.5,angle:-.2});
    // A low, broad hero crosses the smaller signs; its black jacket supplies separation.
    layer(g,'tube','Wild',s,f,{x:652,y:440,scale:.98,angle:-.075});
    layer(g,'pinboard','PULSE',s===1?1:2,f,{x:177,y:620,scale:.3});
  });
  add('signature','Wild / compound brush sign',(g,s,f)=>{g.save();g.translate(15,25);g.rotate(-.04);DrawnLettering.signature(g,s,f);g.restore()});
  function render(id,state,frame,target,{label=false}={}){
    const card=typeof id==='number'?cards[id]:cards.find(x=>x.id===id);if(!card)throw new Error('Unknown composition');const g=target.getContext('2d');g.fillStyle='#030305';g.fillRect(0,0,target.width,target.height);card.draw(g,state%4,frame);
    if(label){g.fillStyle='#17171b';g.fillRect(0,720,1280,48);g.font='17px system-ui';g.fillStyle='#eee';g.fillText(card.name,22,751)}
  }
  return {cards,render};
})();
