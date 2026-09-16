"""Read selected paintings or finishing frames in bounded two-column pages."""
import argparse
from PIL import Image
from run import lab
from deforum_lab.media.sheets import sheet
p=argparse.ArgumentParser();p.add_argument('case');p.add_argument('--frames',nargs='+',type=int);p.add_argument('--folder',default='anchors');p.add_argument('--tag',default='paintings');a=p.parse_args()
root=lab.OUT/a.case;paths=sorted((root/a.folder).glob('*.png'))
frames=a.frames or [int(x.stem) for x in paths]
for offset in range(0,len(frames),6):
 tiles=[]
 for f in frames[offset:offset+6]:
  with Image.open(root/a.folder/f'{f:04d}.png') as im:tiles.append((im.convert('RGB'),f'{a.case} | {f/24:.3f}s | frame {f}'))
 rows=[tiles[i:i+2] for i in range(0,len(tiles),2)]
 out=lab.OUT/'review'/f'{a.case}-{a.tag}-{offset//6+1:02d}.jpg';sheet(rows,out,size=(576,384));print(out)
