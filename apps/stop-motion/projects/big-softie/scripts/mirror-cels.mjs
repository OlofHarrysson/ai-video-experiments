import sharp from 'sharp';import fs from 'node:fs/promises';
const m=JSON.parse(await fs.readFile('assets/cels/manifest.json'));
for (const [k,v] of Object.entries(m))if(k.includes('-run-')&&!k.endsWith('-left')){await sharp('assets/cels/'+k+'.png').flop().toFile('assets/cels/'+k+'-left.png');m[k+'-left']={...v,mirroredFrom:k};}
await fs.writeFile('assets/cels/manifest.json',JSON.stringify(m,null,2));
