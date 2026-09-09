import fs from 'node:fs/promises';
import sharp from 'sharp';
const ROOT='assets/paw-touch';
const SIZE={width:1280,height:720};
const ADULT={left:55,top:158,width:1003,height:565};
const PUPPY={left:708,top:293,width:360,height:360};
const sequence=[0,6,7,2,8,3,9,4,10,11,5];
const input=`${ROOT}/rife-input`;
await fs.mkdir(input,{recursive:true});
const park=await sharp('assets/source/park.png').resize(SIZE).toBuffer();
const adult=await sharp(`${ROOT}/cels/adult.png`).resize(ADULT.width,ADULT.height).toBuffer();
// Accept only the two eyelid patches from the generated blink.
const {data:base,info}=await sharp(`${ROOT}/cels/adult.png`).ensureAlpha().raw().toBuffer({resolveWithObject:true});
const blink=await sharp(`${ROOT}/source/adult-blink.png`).resize(info.width,info.height).ensureAlpha().raw().toBuffer();
const mask=await sharp(Buffer.from(`<svg width="1672" height="941"><ellipse cx="1020" cy="300" rx="39" ry="23" fill="white"/><ellipse cx="1099" cy="299" rx="15" ry="25" fill="white"/></svg>`)).ensureAlpha().blur(3).raw().toBuffer();
const closed=Buffer.from(base);for(let k=0;k<base.length;k+=4){const m=mask[k+3]/255;for(let c=0;c<3;c++)closed[k+c]=Math.round(base[k+c]*(1-m)+blink[k+c]*m);}
await sharp(closed,{raw:info}).png().toFile(`${ROOT}/cels/adult-closed.png`);
const adultClosed=await sharp(closed,{raw:info}).resize(ADULT.width,ADULT.height).png().toBuffer();
for(let i=0;i<=sequence.length;i++){
 const pose=sequence[Math.min(i,sequence.length-1)];
 const pup=await sharp(`${ROOT}/cels/locked-${pose}.png`).resize(PUPPY.width,PUPPY.height).toBuffer();
 await sharp(park).composite([{input:i===sequence.length?adultClosed:adult,left:ADULT.left,top:ADULT.top},{input:pup,left:PUPPY.left,top:PUPPY.top}]).removeAlpha().png().toFile(`${input}/${String(i).padStart(6,'0')}.png`);
}
await fs.writeFile(`${ROOT}/staging.json`,JSON.stringify({size:SIZE,adult:ADULT,puppy:PUPPY,sequence:[...sequence,'5 + adult closed eyelids'],sourceFps:6,multiplier:10,outputFps:60,holdBeforeSeconds:.5,holdAfterSeconds:1.5},null,2));
const tiles=[];for(const [n,i]of[0,3,5,7,10,11].entries()){tiles.push({input:await sharp(`${input}/${String(i).padStart(6,'0')}.png`).resize(640,360).toBuffer(),left:n%2*640,top:Math.floor(n/2)*390});tiles.push({input:Buffer.from(`<svg width="640" height="30"><text x="12" y="22" font-size="18" font-family="Arial">Anchor ${i}</text></svg>`),left:n%2*640,top:Math.floor(n/2)*390+360});}
await sharp({create:{width:1280,height:1170,channels:3,background:'#eae4d7'}}).composite(tiles).png().toFile('review/paw-touch/staged-anchors.png');
console.log('Staged 12 anchors including the adult eyelid response.');
