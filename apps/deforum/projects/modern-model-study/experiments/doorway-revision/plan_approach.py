"""Center the observed doorway and approach it before choosing the crossing."""
import copy
import json
import numpy as np
from PIL import Image
from run import lab
from deforum_lab.image.warps import mapping, warp_at_time
from deforum_lab.media.sheets import sheet

PARENT = lab.OUT.parent / 'storytelling-lab-v001/i2-bridge-to-the-moon'
CASE = 'd1-doorway-approach'
START = 13.5
POINT = np.array([1107 / 1024, 426 / 1024])
TARGET = np.array([.75, .51])

config = copy.deepcopy(lab.read(PARENT / 'config.json'))
config.pop('opening', None)
config.update(case=CASE, duration=20, prefix_root=str(PARENT.relative_to(lab.APP)),
              prefix_through=324, painting_frames=list(range(0, 480, 12)))
# Each phrase has one job. The start just before the branch gives nonzero
# velocity at the first new repaint; the preserved prefix is never rerendered.
pan = dict(start=13, duration=3, zoom=0, turn=0, travel=[0, 0], center=[.75,.5])
push = dict(start=13.5, duration=7, zoom=4.5, turn=0, travel=[0,0], center=TARGET.tolist())
cruise = dict(kind='cruise', start=13, velocity=[.004,-.003], center=TARGET.tolist())
phrases = [cruise, pan, push]
def predict():
    return mapping(mapping(POINT, START, phrases, True), 16, phrases)
zero = predict()
columns=[]
for axis in range(2):
    pan['travel']=[0,0]; pan['travel'][axis]=1
    columns.append(predict()-zero)
pan['travel']=np.linalg.solve(np.stack(columns, axis=1), TARGET-zero).tolist()
assert np.allclose(predict(), TARGET)
config['phrases']=phrases
style=' A finely detailed surrealist oil painting, dimensional ivory architecture, crimson enamel, deep indigo shadows and luminous warm golden light. Crisp engraved details and spacious readable forms.'
stages=[
 (14,'the-doorway','A narrow ivory railway curves upward into a tall open amber doorway. The doorway has two straight carved stone jambs and a rounded top, with a small station window above it. A crimson moon surrounds the doorway. The railway leads directly into the bright opening. A little red steam train and the ivory whale-shaped bridge remain at the lower left. Warm daylight shines through the opening.'),
 (16,'approaching-the-opening','A large open arched doorway of carved ivory stone is centered in a deep crimson wall. Two railway tracks curve up from the lower edge and pass through the tall opening. The arch has two separate straight vertical jambs and a curved lintel. Through the opening is golden daylight, distant jade foliage and slender gold tree trunks. The red locomotive is small at the lower left edge. The near stone threshold is clearly visible.'),
 (18,'a-glimpse-beyond','A broad open ivory arch frames a sunlit jade forest beyond. Two golden railway rails enter the opening from the bottom center. The carved doorway has tall straight side pillars and a curved ivory top; the crimson surrounding wall is cropped at the outer edges. Inside the arch, distant trees have golden harp strings stretched between their branches, lit by shafts of warm sunlight. The forest remains beyond the stone threshold, with deep green shade between the golden trunks.'),
]
config['prompt_schedule']=[e for e in config['prompt_schedule'] if e['at']<=START]+[dict(at=t,name=n,prompt=p+style) for t,n,p in stages]
values=[.50,.54,.56,.58,.60,.62,.64,.66,.68,.68,.64,.58]
config['noise_schedule']=[e for e in config['noise_schedule'] if e['at']<=START]+[dict(at=14+i*.5,noise=n) for i,n in enumerate(values)]
config['seeds_by_frame']={str(f):config['seed']+1000+f for f in config['painting_frames'][1:]}
lab.save(lab.HERE/'configs'/f'{CASE}.json',config)
rgb=lab.pixels(PARENT/'anchors/0324.png')
times=[13.5,14.5,16,17,18,19.5]
tiles=[(Image.fromarray(warp_at_time(rgb,START,t,phrases)),f'Warp only | source {t:g}s') for t in times]
sheet([tiles[i:i+2] for i in range(0,6,2)],lab.OUT/'review/approach-motion.jpg',size=(576,384))
lab.save(lab.HERE/'approach-framing.json',dict(source_frame=324,source_point=POINT.tolist(),target_point=TARGET.tolist(),target_time=16,pan=pan,path=[dict(seconds=t,point=mapping(mapping(POINT,START,phrases,True),t,phrases).tolist()) for t in times],scope='Fixed-painting geometry; inspect generated doorway position before crossing.'))
print(json.dumps(dict(case=CASE,pan=pan['travel'],target=predict().tolist())))
