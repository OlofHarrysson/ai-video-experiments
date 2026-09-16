"""Rewind before the crowded ending; make space beyond the doorway."""
import copy
import numpy as np
from PIL import Image
from run import lab
from deforum_lab.image.warps import warp_at_time
from deforum_lab.media.sheets import sheet

parent=lab.OUT/'d2-through-the-door';case='d4-the-open-glade'
c=copy.deepcopy(lab.read(parent/'config.json'))
c.update(case=case,duration=29,prefix_root=str(parent.relative_to(lab.APP)),prefix_through=528,painting_frames=list(range(0,696,12)))
# Reanchor the new local path at the saved painting. Previous paintings and
# their interpolated prefix are preserved; only future relative warps change.
c['phrases']=[
 dict(kind='cruise',start=22,velocity=[-.025,-.006],log_zoom_rate=.10,roll_rate=0,center=[.96,.62]),
 dict(start=21.75,duration=3.75,zoom=0,turn=0,travel=[-.22,-.12],center=[.75,.5]),
 dict(start=24,duration=5,zoom=0,turn=-5,travel=[0,0],center=[.8,.55],radius=6),
]
style=' An exquisitely detailed surrealist oil painting, dimensional sculptural forms, emerald moss and jade foliage, luminous golden light, rich deep shadows, sharp highlights and delicate engraved textures. A broad cinematic landscape with open space and clearly separated near and far forms.'
events=[
 (22.5,'past-the-near-harp','Beyond an open stone arch lies a broad sunlit green meadow. A railway curves from the lower right into the distant clearing. The huge near harp is cropped almost entirely off the left edge, leaving the center and right as open mossy ground and golden sky. A small red steam train sits on the railway in the middle distance. Delicate harp-shaped trees stand far away along the edges of the meadow.'),
 (24,'the-open-glade','An expansive sunlit emerald meadow fills the view. A little red steam train travels on a golden railway winding across the open middle distance. The foreground is mossy ground with scattered tiny blue flowers. Only distant slender trees line the left and right edges, with delicate golden harp strings among their branches. Broad shafts of warm sunlight cross the open glade. The center is spacious, and the train is clearly visible against the green ground.'),
 (26,'a-new-world','A tiny red steam train follows a gently curving railway across a vast emerald valley beneath a luminous pale gold sky. Along the distant valley slopes, slender trees have elegant golden harp-shaped branches. The open foreground is moss, small blue flowers and winding golden tracks, with rich green shadows. Rounded hills and a warm sunlit clearing give a deep spacious view. No large object occupies the center.'),
]
c['prompt_schedule']=[e for e in c['prompt_schedule'] if e['at']<=22]+[dict(at=t,name=n,prompt=p+style) for t,n,p in events]
values=[.70,.76,.80,.80,.78,.72,.68,.64,.60,.56,.52,.48,.42]
c['noise_schedule']=[e for e in c['noise_schedule'] if e['at']<=22]+[dict(at=22.5+i*.5,noise=n) for i,n in enumerate(values)]
c['seeds_by_frame']={str(f):c['seed']+1000+f for f in c['painting_frames'][1:]}
lab.save(lab.HERE/'configs'/f'{case}.json',c)
rgb=lab.pixels(parent/'anchors/0528.png');times=[22,23,24,25.5,27,28.5]
tiles=[(Image.fromarray(warp_at_time(rgb,22,t,c['phrases'])),f'Warp only | source {t:g}s') for t in times]
sheet([tiles[i:i+2] for i in range(0,6,2)],lab.OUT/'review/open-glade-motion.jpg',size=(576,384))
print(case)
