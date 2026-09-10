# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Eight Krea stills: two subject layouts, two seeds, two conditioning methods."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from run_krea import KreaGraph, MODEL_MANIFEST, SETTING
from run_baseline import PROJECT, collect, request, ui_workflow, validate, write_json

SUBJECTS = {
    'red': 'One red tin robot holds a single flower in one hand.',
    'blue': 'One blue tin robot holds a single open umbrella by its handle.',
    'yellow': 'One yellow tin robot holds a single flag on a pole.',
}
SLOTS = {
    'large': {'box': [32,448,384,512], 'position': 'in the lower-left foreground',
              'height': 40, 'size': 'large'},
    'medium': {'box': [624,384,352,384], 'position': 'on the right in the middle distance',
               'height': 25, 'size': 'medium-sized'},
    'small': {'box': [448,288,160,224], 'position': 'near the upper centre in the far distance',
              'height': 12, 'size': 'small'},
}
LAYOUTS = {
    'A': {'red':'large','blue':'medium','yellow':'small'},
    'B': {'red':'medium','blue':'small','yellow':'large'},
}
SPACING = 'Open grass separates the robots. Each robot holds its own prop. Every robot is fully visible, including its head and both feet.'
EXPORT = PROJECT/'exports/krea-layouts-v001'


def prompts(layout):
    result = {}
    for color, slot_name in LAYOUTS[layout].items():
        slot = SLOTS[slot_name]
        result[color] = (SUBJECTS[color] + f' This {slot["size"]} robot stands {slot["position"]}. '
                         f'Its body from head to feet is approximately {slot["height"]} percent of the picture height. '
                         'Its entire body and held prop are visible, with its feet on the grass.')
    return result


class LayoutGraph(KreaGraph):
    def __init__(self, prefix, seed, layout):
        super().__init__(prefix, seed)
        self.layout = layout
        self.subject_prompts = prompts(layout)
        self.nodes[self.complete[0]]['inputs']['text'] = ' '.join(self.subject_prompts.values())+' '+SPACING+' '+SETTING

    def build_pair(self):
        empty = self.empty()
        self.snapshot(self.sample(empty,self.complete,self.seed),'complete')
        regional = self.add('ConditioningSetAreaStrength',conditioning=self.text(SETTING),strength=0.25)
        for color, slot_name in LAYOUTS[self.layout].items():
            local = self.add('ConditioningSetMask',
                             conditioning=self.text(self.subject_prompts[color]+' '+SPACING+' '+SETTING),
                             mask=self.mask(SLOTS[slot_name]['box'],soft=True),
                             set_cond_area='default',strength=1.0)
            regional = self.add('ConditioningCombine',conditioning_1=regional,conditioning_2=local)
        self.snapshot(self.sample(empty,regional,self.seed),'regional')
        return self.nodes


def targets():
    EXPORT.mkdir(parents=True,exist_ok=True)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',27)
    small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
    colors={'red':'#ef6969','blue':'#67abff','yellow':'#e8ce64'}
    records={}
    for layout in LAYOUTS:
        im=Image.new('RGB',(1024,1024),'#18202a'); draw=ImageDraw.Draw(im)
        draw.text((32,24),f'Layout {layout} · subject and prop regions',font=font,fill='white')
        draw.text((32,70),'Boxes guide the regional sampler; they are not hard object boundaries.',font=small,fill='#c4cdd6')
        draw.text((32,110),'Robot body heights: large 40% · medium 25% · small 12%',font=small,fill='#c4cdd6')
        records[layout]={'subject_prompts':prompts(layout),'regions':{}}
        for color,slot_name in LAYOUTS[layout].items():
            s=SLOTS[slot_name];x,y,w,h=s['box']
            draw.rectangle((x,y,x+w-1,y+h-1),outline=colors[color],width=4)
            draw.text((x+9,y+10),color.upper(),font=small,fill=colors[color])
            draw.text((x+9,y+39),slot_name,font=small,fill='white')
            records[layout]['regions'][color]=s
        im.save(EXPORT/f'target-{layout}.png')
    write_json(EXPORT/'targets.json',records)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['run','collect','targets'])
    p.add_argument('--deployment',type=Path)
    p.add_argument('--layout',choices=LAYOUTS,default='A')
    p.add_argument('--seed',type=int,choices=[21001,21101],default=21001)
    p.add_argument('--folder',type=Path)
    args=p.parse_args()
    if args.action=='targets':
        targets();return
    if args.deployment is None: p.error('--deployment is required')
    d=json.loads(args.deployment.read_text())
    if d.get('status')=='deleted': raise RuntimeError('Deployment is closed')
    if args.action=='collect':
        collect(args.folder,d);return
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    label=f'{stamp}-krea-layout-{args.layout}-seed{args.seed}'
    folder=PROJECT/'runs'/label;folder.mkdir(parents=True)
    sources={}
    for source in (Path(__file__),Path(__file__).with_name('run_krea.py'),Path(__file__).with_name('run_baseline.py')):
        (folder/source.name).write_bytes(source.read_bytes())
        sources[source.name]=hashlib.sha256(source.read_bytes()).hexdigest()
    graph=LayoutGraph('krea-layouts/'+label,args.seed,args.layout).build_pair()
    schema=request(d['base_url'],'/object_info');validate(graph,schema)
    ui=ui_workflow(graph,schema)
    write_json(folder/'workflow.api.json',graph);write_json(folder/'workflow.json',ui)
    write_json(folder/'node-schemas.json',{n['class_type']:schema[n['class_type']] for n in graph.values()})
    write_json(folder/'system-stats.json',request(d['base_url'],'/system_stats'))
    receipt={'pod_id':d['pod_id'],'variant':'krea-layouts','layout':args.layout,'seed':args.seed,
             'subject_prompts':prompts(args.layout),'slots':SLOTS,'assignments':LAYOUTS[args.layout],
             'source_hashes':sources,'models':[a for a in json.loads(MODEL_MANIFEST.read_text()) if a['repo']=='Comfy-Org/Krea-2'],
             'submitted_at':datetime.now(timezone.utc).isoformat()}
    write_json(folder/'submission.json',receipt)
    try:
        response=request(d['base_url'],'/prompt',{'prompt':graph,'client_id':label,'extra_data':{'extra_pnginfo':{'workflow':ui}}})
    except Exception as error:
        write_json(folder/'submission-error.json',{'error':str(error),'action':'Inspect queue/history before any resubmission'})
        raise
    write_json(folder/'submit-response.json',response)
    if not response.get('prompt_id') or response.get('node_errors'): raise RuntimeError(response)
    receipt['prompt_id']=response['prompt_id'];write_json(folder/'submission.json',receipt)
    print(json.dumps({'submitted':receipt['prompt_id'],'folder':str(folder)}),flush=True)
    collect(folder,d)


if __name__=='__main__': main()
