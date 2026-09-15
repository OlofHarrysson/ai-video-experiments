"""Choose the last push from a measured doorway in the actual I4 painting."""
import numpy as np
from PIL import Image
from branch import freeze
from run import lab
from deforum_lab.image.warps import mapping, warp_at_time
from deforum_lab.media.sheets import sheet

base=lab.read(lab.HERE/'configs/i4-through-the-clock.json')
lab.save(lab.OUT/'i4-through-the-clock/config.json',base)
start,end=23.0,31.5
point=np.array([635/1024,867/1024])
target=np.array([.75,.55])
phrases=base['phrases']
future=mapping(mapping(point,start,phrases,True),end,phrases)
scale=4.2
travel=target-(point+(future-point)*scale)
phrases=phrases+[dict(start=start,duration=end-start,zoom=scale-1,turn=0,
                      travel=travel.tolist(),center=point.tolist(),radius=4)]
landed=mapping(mapping(point,start,phrases,True),end,phrases)
assert np.allclose(landed,target)
style=' A luminous surrealist oil painting, dimensional ivory whales, turquoise ocean, warm golden light, crisp engraved highlights and deep teal shadows. Spacious readable forms.'
stages=[
 (23.5,'through-the-window','An open red-rimmed window onto a turquoise sea at golden dawn. Graceful ivory whales float above the water inside. The red clock rim is receding outside the edges as the ocean opens into a broad landscape. A small red train follows a thin ivory bridge along the left horizon.'),
 (26,'the-open-dream','A wide open turquoise ocean at golden dawn. A large ivory whale floats near the right foreground, with a calm dark eye and deep sculptural shading. Two smaller whales float farther away above the sea. A tiny red train follows a thin ivory bridge at the distant left horizon. Broad pale gold sky and a round sun, waves reflecting luminous gold. Only a small curved red fragment remains at the far left edge.'),
 (29,'morning','Three ivory whales float freely over an immense turquoise ocean beneath a golden sunrise. The nearest whale has a calm dark eye, engraved ivory shading and a small warm light on its back. A delicate red train crosses a distant ivory bridge at the left horizon. Wide pale gold sky, deep turquoise water, spacious graceful composition and clear silhouettes.'),
]
values=[.60,.66,.72,.76,.74,.68,.72,.78,.76,.68,.62,.56,.50,.46,.42,.36,.30]
freeze('i4-through-the-clock','i5-the-open-dream',552,32,
       [dict(at=t,name=n,prompt=p+style) for t,n,p in stages],
       [dict(at=23.5+i*.5,noise=n) for i,n in enumerate(values)],phrases)
lab.save(lab.HERE/'doorway-framing.json',dict(source_frame=552,source_point=point.tolist(),
         target_point=target.tolist(),end_time=end,zoom=scale-1,travel=travel.tolist(),
         predicted_endpoint=landed.tolist(),scope='Geometric prediction on one fixed painting; repainting can move the subject.'))
source=lab.APP/'work/storytelling-session/i4-source-0552.png'
if source.exists():
    rgb=lab.pixels(source)
    tiles=[(Image.fromarray(warp_at_time(rgb,start,t,phrases)),f'Warp only | source {t:g}s') for t in [23,25,27,29,30.5,31.5]]
    sheet([tiles[i:i+2] for i in range(0,len(tiles),2)],lab.OUT/'review/doorway-framing.jpg',size=(576,384))
