"""Enter the visible meadow gap instead of panning into the remaining wall."""
import copy
import numpy as np
from PIL import Image
from run import lab
from deforum_lab.image.warps import mapping, warp_at_time
from deforum_lab.media.sheets import sheet

parent=lab.OUT/'d4-the-open-glade';case='d5-beyond-the-threshold'
c=copy.deepcopy(lab.read(parent/'config.json'))
c.update(case=case,duration=30,prefix_root=str(parent.relative_to(lab.APP)),prefix_through=576,painting_frames=list(range(0,720,12)))
start,end=24,29.5
point=np.array([738/1024,586/1024]);target=np.array([.75,.57])
push=dict(start=23.75,duration=5.75,zoom=5,turn=0,travel=[0,0],center=point.tolist())
pan=dict(start=24,duration=5.5,zoom=0,turn=0,travel=[0,0],center=point.tolist())
drift=dict(kind='cruise',start=24,velocity=[-.004,.002],log_zoom_rate=.012,center=target.tolist())
phrases=[push,pan,drift]
origin=mapping(mapping(point,start,phrases,True),end,phrases)
# The final cruise scales translations, so solve its exact two-axis response.
columns=[]
for axis in range(2):
    pan['travel']=[0,0];pan['travel'][axis]=1
    columns.append(mapping(mapping(point,start,phrases,True),end,phrases)-origin)
pan['travel']=np.linalg.solve(np.stack(columns,axis=1),target-origin).tolist()
assert np.allclose(mapping(mapping(point,start,phrases,True),end,phrases),target)
c['phrases']=phrases
style=' A richly detailed surrealist oil painting, luminous green moss, delicate blue flowers, deep dimensional shadows, polished red enamel, warm sunlight and crisp reflected highlights. A spacious landscape with readable shapes at different distances.'
events=[
 (24.5,'through-the-visible-gap','A little red steam train travels along a curving railway through a sunlit green meadow. The view is entering the open space around the train. A golden harp and a dark tree arch are cropped at the far left edge, while the meadow fills the center and right. Tiny blue flowers dot the moss beside the tracks. Tall slender trees stand far away beneath a warm pale sky.'),
 (26,'the-meadow-opens','A red steam locomotive with a short line of red carriages travels on curving rails across a vast sunlit emerald meadow. The train is the clear focal point near the lower center, with soft white steam above it. Blue wildflowers and moss fill the foreground. A few distant golden harp-shaped trees mark the rolling hills on the horizon. Broad open green ground and luminous sky surround the train.'),
 (28,'the-journey-continues','A polished vermilion steam train travels through a luminous green valley, its curved golden rails winding into the distance. Moss and tiny blue flowers border the railway. Distant slender trees have delicate golden harp-shaped branches, beneath warm clouds and a pale golden sky. The red locomotive and its small carriages remain distinct, with deep shadows and warm highlights. The view remains open around the train.'),
]
c['prompt_schedule']=[e for e in c['prompt_schedule'] if e['at']<=24]+[dict(at=t,name=n,prompt=p+style) for t,n,p in events]
values=[.56,.58,.60,.62,.64,.64,.60,.56,.50,.44,.36]
c['noise_schedule']=[e for e in c['noise_schedule'] if e['at']<=24]+[dict(at=24.5+i*.5,noise=n) for i,n in enumerate(values)]
c['seeds_by_frame']={str(f):c['seed']+1000+f for f in c['painting_frames'][1:]}
lab.save(lab.HERE/'configs'/f'{case}.json',c)
rgb=lab.pixels(parent/'anchors/0576.png');times=[24,25,26,27.5,28.5,29.5]
tiles=[(Image.fromarray(warp_at_time(rgb,start,t,phrases)),f'Warp only | source {t:g}s') for t in times]
sheet([tiles[i:i+2] for i in range(0,6,2)],lab.OUT/'review/clearance-motion.jpg',size=(576,384))
lab.save(lab.HERE/'clearance-framing.json',dict(source_frame=576,source_point=point.tolist(),target_point=target.tolist(),phrases=phrases,path=[dict(seconds=t,point=mapping(mapping(point,start,phrases,True),t,phrases).tolist()) for t in times],scope='Measured open gap between harp/tree on left and red wall on right; fixed-painting geometric preview.'))
print(case)
