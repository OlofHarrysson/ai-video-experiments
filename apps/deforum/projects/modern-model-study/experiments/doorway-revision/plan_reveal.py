"""Follow the red train around the obstructing harp in the actual crossing."""
import copy
import numpy as np
from PIL import Image
from run import lab
from deforum_lab.image.warps import mapping, warp_at_time
from deforum_lab.media.sheets import sheet

parent=lab.OUT/'d2-through-the-door';case='d3-the-music-beyond'
c=copy.deepcopy(lab.read(parent/'config.json'))
c.update(case=case,duration=32,prefix_root=str(parent.relative_to(lab.APP)),prefix_through=624,painting_frames=list(range(0,768,12)))
start,end=26,31.5
point=np.array([1350/1024,601/1024]);target=np.array([.77,.57])
clearance=dict(start=25.75,duration=2.75,zoom=.8,turn=0,travel=[0,0],center=[.88,.5])
pan=dict(start=27.25,duration=4.25,zoom=0,turn=0,travel=[0,0],center=[.75,.5])
bank=dict(start=27.5,duration=5,zoom=0,turn=-7,travel=[0,0],center=target.tolist(),radius=6)
release=dict(start=29.5,duration=5,zoom=-.12,turn=0,travel=[0,0],center=target.tolist())
phrases=c['phrases']+[clearance,pan,bank,release]
def predict():return mapping(mapping(point,start,phrases,True),end,phrases)
zero=predict();columns=[]
for axis in range(2):
    pan['travel']=[0,0];pan['travel'][axis]=1
    columns.append(predict()-zero)
pan['travel']=np.linalg.solve(np.stack(columns,axis=1),target-zero).tolist()
for _ in range(6):
    position=predict(); travel=np.array(pan['travel']); jacobian=[]
    if np.linalg.norm(target-position)<1e-9:break
    for axis in range(2):
        probe=travel.copy();probe[axis]+=1e-5;pan['travel']=probe.tolist()
        jacobian.append((predict()-position)/1e-5)
    pan['travel']=(travel+np.linalg.solve(np.stack(jacobian,axis=1),target-position)).tolist()
assert np.allclose(predict(),target)
c['phrases']=phrases
style=' A luminous surrealist oil painting, polished golden instruments and emerald foliage, deep dimensional shadows, warm shafts of sunlight and crisp engraved highlights. Spacious readable forms at different distances.'
events=[
 (26.5,'follow-the-red-train','A little vermilion red steam train follows a sweeping curved railway through an immense emerald forest of golden harps. The train sits right of center, clearly separated from the trees. The near giant harp is cropped along the far left edge as the view opens toward the railway on the right. Sunlit moss and golden roots surround the winding tracks. Smaller harp-shaped trees stand in the distance beneath an open golden sky.'),
 (28,'a-world-of-music','A red steam train crosses a bright mossy clearing among monumental golden harp-shaped trees. The locomotive is near the center, trailing a ribbon of pale steam toward the left. The railway curves from the lower foreground toward the distant right, passing between slender golden trunks and strings. Tall emerald canopies frame broad shafts of golden sunlight. Open space surrounds the red train and the winding tracks.'),
 (30,'the-new-journey','A little red steam train travels through a spacious golden glade in an emerald forest of enormous musical instruments. Golden harp trees stand at varied distances on either side of a curving railway, their strings glinting in sunlight. Moss-covered roots border the track. A graceful branch arches high above the train, and luminous pale sky opens between the distant canopies. The train remains the clear red focal point in the new landscape.'),
]
c['prompt_schedule'] += [dict(at=t,name=n,prompt=p+style) for t,n,p in events]
values=[.52,.58,.66,.70,.70,.64,.60,.56,.52,.48,.42]
c['noise_schedule'] += [dict(at=26.5+i*.5,noise=n) for i,n in enumerate(values)]
c['seeds_by_frame']={str(f):c['seed']+1000+f for f in c['painting_frames'][1:]}
lab.save(lab.HERE/'configs'/f'{case}.json',c)
rgb=lab.pixels(parent/'anchors/0624.png');times=[26,27,28,29,30.5,31.5]
tiles=[(Image.fromarray(warp_at_time(rgb,start,t,phrases)),f'Warp only | source {t:g}s') for t in times]
sheet([tiles[i:i+2] for i in range(0,6,2)],lab.OUT/'review/reveal-motion.jpg',size=(576,384))
lab.save(lab.HERE/'reveal-framing.json',dict(source_frame=624,source_point=point.tolist(),target_point=target.tolist(),clearance=clearance,pan=pan,bank=bank,release=release,path=[dict(seconds=t,point=mapping(mapping(point,start,phrases,True),t,phrases).tolist()) for t in times],scope='Fixed-image path; reflected right edge is exposed and needs inspection after repainting.'))
print(case)
