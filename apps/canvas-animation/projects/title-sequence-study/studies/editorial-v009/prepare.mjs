import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const here=path.dirname(fileURLToPath(import.meta.url));
const require=createRequire(new URL('../../package.json',import.meta.url));
const opentype=require('opentype.js');
const fonts={condensed:'../../fonts/Anton-Regular.ttf',wide:'../../fonts/Audiowide-Regular.ttf',serif:'../../fonts/CormorantGaramond-Italic.ttf',slab:'../../fonts/AlfaSlabOne-Regular.ttf',race:'../../fonts/RacingSansOne-Regular.ttf',gothic:'../typography-v001/fonts/UnifrakturCook-Bold.ttf'};
const words=['MAKE','IT','MOVE','Make','it','Move','Make it','make it move','M','O','V','E'];
const outlines={};
for(const [id,file]of Object.entries(fonts)){
 const bytes=fs.readFileSync(path.resolve(here,file)); const font=opentype.parse(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength));outlines[id]={};
 for(const word of words){const p=font.getPath(word,0,0,1000),b=p.getBoundingBox();outlines[id][word]={d:p.toPathData(3),x:b.x1,y:b.y1,w:b.x2-b.x1,h:b.y2-b.y1};}
}
fs.writeFileSync(path.join(here,'outlines.js'),'window.LetterOutlines = '+JSON.stringify(outlines)+';\n');
console.log('Prepared vector outlines from six existing licensed local font files.');
