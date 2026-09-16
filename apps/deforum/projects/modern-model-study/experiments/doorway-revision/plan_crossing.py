"""Aim through the opening measured in the completed approach painting."""
import copy
import numpy as np
from PIL import Image
from run import lab
from deforum_lab.image.warps import mapping, warp_at_time
from deforum_lab.media.sheets import sheet

CASE='d2-through-the-door'
parent=lab.OUT/'d1-doorway-approach'
c=copy.deepcopy(lab.read(parent/'config.json'))
c.update(case=CASE,duration=26.5,prefix_root=str(parent.relative_to(lab.APP)),prefix_through=468,painting_frames=list(range(0,636,12)))
start,end=19.5,25.5
point=np.array([870/1024,475/1024]);target=np.array([.75,.5])
base=c['phrases']
future=mapping(mapping(point,start,base,True),end,base)
scale=8.5
push=dict(start=19.25,duration=6.25,zoom=scale-1,turn=0,travel=[0,0],center=point.tolist())
pan=dict(start=19.5,duration=6,zoom=0,turn=0,travel=[0,0],center=point.tolist())
phrases=base+[push,pan]
origin=mapping(mapping(point,start,phrases,True),end,phrases)
pan['travel']=(target-origin).tolist()
assert np.allclose(mapping(mapping(point,start,phrases,True),end,phrases),target)
# A separate lateral reveal begins before forward movement finishes.
phrases += [dict(start=24.5,duration=4,zoom=0,turn=0,travel=[-.12,.025],center=[.75,.5])]
c['phrases']=phrases
style=' A luminous surrealist oil painting, dimensional carved ivory and polished golden instruments, deep emerald foliage, warm sunbeams, rich shadows and crisp reflected details. Readable near and far forms.'
events=[
 (20,'entering-the-arch','A tall open ivory doorway fills most of the view. Its straight pale jambs frame a sunlit emerald forest with a monumental golden harp standing among the trees. Curving golden railway rails cross the near threshold and continue into the forest. The crimson wall is confined to the outer sides. The scene inside the doorway has deep layered foliage and warm sunlight.'),
 (21.5,'crossing-the-threshold','The view passes through a huge open ivory arch into a sunlit forest of giant golden musical instruments. Pale doorway pillars are cropped at the extreme sides. A golden harp grows into a branching tree on the right, its fine vertical strings catching sunlight. A railway curves from the foreground toward a bright clearing beyond the harp. Deep jade leaves and open golden sky fill the passage.'),
 (23,'inside-the-music-forest','An expansive sunlit emerald forest of monumental golden musical instruments. Huge harp-shaped trees stand at different distances, their curved golden trunks and fine strings framing an open bright clearing. A slender railway curves along mossy roots through the clearing. A small vermilion steam train follows the distant curve. Golden sunlight streams between the jade leaves, with rich green shadow and open pale sky.'),
 (25,'the-golden-clearing','A broad golden clearing in an emerald forest. Monumental harp-shaped trees stand on either side, with delicate golden strings stretched between their branching trunks. A tiny red steam train travels along a curving golden railway across the mossy middle distance. Tall jade canopies open onto pale gold sky. The nearest harp trunk is at the right edge, leaving a spacious view into the sunlit glade.'),
]
c['prompt_schedule'] += [dict(at=t,name=n,prompt=p+style) for t,n,p in events]
values=[.56,.60,.64,.68,.72,.74,.76,.74,.70,.66,.60,.54,.46]
c['noise_schedule'] += [dict(at=20+i*.5,noise=n) for i,n in enumerate(values)]
c['seeds_by_frame']={str(f):c['seed']+1000+f for f in c['painting_frames'][1:]}
lab.save(lab.HERE/'configs'/f'{CASE}.json',c)
rgb=lab.pixels(parent/'anchors/0468.png');times=[19.5,20.5,21.5,23,24.5,25.5]
tiles=[(Image.fromarray(warp_at_time(rgb,start,t,phrases)),f'Warp only | source {t:g}s') for t in times]
sheet([tiles[i:i+2] for i in range(0,6,2)],lab.OUT/'review/crossing-motion.jpg',size=(576,384))
lab.save(lab.HERE/'crossing-framing.json',dict(source_frame=468,source_point=point.tolist(),target_point=target.tolist(),push=push,pan=pan,path=[dict(seconds=t,point=mapping(mapping(point,start,phrases,True),t,phrases).tolist()) for t in times],scope='Fixed-image forecast, including later lateral reveal; painting review decides the next passage.'))
print(CASE)
