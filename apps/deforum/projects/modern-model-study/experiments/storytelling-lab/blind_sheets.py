"""Neutral chronological sheets for a reviewer who has not read the plot."""
import argparse
from PIL import Image
from deforum_lab.media.sheets import sheet
from run import lab

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('case');p.add_argument('label');p.add_argument('frames',type=int,nargs='+')
    a=p.parse_args()
    for offset in range(0,len(a.frames),6):
        tiles=[]
        for f in a.frames[offset:offset+6]:
            with Image.open(lab.OUT/a.case/f'anchors/{f:04d}.png') as im:
                tiles.append((im.convert('RGB'),f'{a.label} | {f/36:.2f} seconds'))
        sheet([tiles[i:i+2] for i in range(0,len(tiles),2)],
              lab.APP/f'work/storytelling-session/blind-review/{a.label}-{offset//6+1}.jpg',
              size=(576,384))
