# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Four Krea stills comparing verbal and masked material placement."""
import argparse
import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from run_krea import KreaGraph, MODEL_MANIFEST
from run_baseline import PROJECT, collect, request, ui_workflow, validate, write_json

EXPORT = PROJECT / 'exports/krea-coral-v001'
MASK_NAME = 'krea-coral-band.png'
SCENE = ('A single monumental sculpted human face seen straight from the front, centred and filling almost the entire square picture. '
         'The forehead begins near the top edge and the chin ends near the bottom edge. Both eyes, the nose and the mouth form one coherent, recognizable face. '
         'A dark teal background surrounds the head. Warm directional light from the upper left reveals the sculpted volume. '
         'A richly detailed painterly fantasy illustration with subtle brushwork and unified lighting. ')
STONE = ('Weathered ivory limestone forms the face, with fine cracks and carved contours. Exposed stone remains visible on both sides of the coral band. ')
CORAL = ('Luminous orange and peach coral grows directly from the facial surface, with intricate branching coral, tiny polyps and soft amber glow. '
         'The coral follows and reveals the underlying facial anatomy and integrates naturally into the stone. ')
SHAPE = ('The coral occupies only one broad continuous S-shaped band from the centre of the forehead to the centre of the chin. '
         'The band curves toward the viewer\'s right across the upper forehead and above the right eye, returns across the bridge of the nose, '
         'curves toward the viewer\'s left across the lower cheek, and returns to the centre of the chin. '
         'The band is approximately one sixth of the picture width, with gently softened irregular edges. ')
COMPLETE = SCENE + STONE + CORAL + SHAPE


def make_mask():
    EXPORT.mkdir(parents=True, exist_ok=True)
    mask = Image.new('L', (1024, 1024), 0)
    draw = ImageDraw.Draw(mask)
    points = [(round(512 + 150 * math.sin(2 * math.pi * (y-160)/704)), y) for y in range(160, 865)]
    for x, y in points:
        draw.ellipse((x-85, y-85, x+85, y+85), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(12))
    path = EXPORT / MASK_NAME
    if path.exists():
        assert Image.open(path).tobytes() == mask.tobytes(), 'Preserve an existing mask'
    else:
        mask.save(path)
    write_json(EXPORT / 'design.json', {'size':[1024,1024], 'stroke_width':170, 'blur_radius':12,
        'curve':'x=512+150*sin(2*pi*(y-160)/704), y=160..864', 'prompts':{
            'complete':COMPLETE, 'coral':SCENE+CORAL+SHAPE, 'stone':SCENE+STONE},
        'mask_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    return path


class CoralGraph(KreaGraph):
    def __init__(self, prefix, seed):
        super().__init__(prefix, seed)
        self.nodes[self.complete[0]]['inputs']['text'] = COMPLETE

    def build_pair(self):
        empty = self.empty()
        self.snapshot(self.sample(empty, self.complete, self.seed), 'complete')
        loaded = self.add('LoadImage', image=MASK_NAME)
        mask = self.add('ImageToMask', image=loaded, channel='red')
        inverse = self.add('InvertMask', mask=mask)
        regional = self.add('ConditioningSetAreaStrength', conditioning=self.complete, strength=0.25)
        for prompt, area in ((SCENE+CORAL+SHAPE, mask), (SCENE+STONE, inverse)):
            local = self.add('ConditioningSetMask', conditioning=self.text(prompt), mask=area,
                             set_cond_area='default', strength=1.0)
            regional = self.add('ConditioningCombine', conditioning_1=regional, conditioning_2=local)
        self.snapshot(self.sample(empty, regional, self.seed), 'regional')
        return self.nodes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['mask', 'run', 'collect'])
    parser.add_argument('--deployment', type=Path)
    parser.add_argument('--seed', type=int, choices=[21001,21101], default=21001)
    parser.add_argument('--folder', type=Path)
    args = parser.parse_args()
    mask = make_mask()
    if args.action == 'mask':
        print(mask); return
    if not args.deployment: parser.error('--deployment is required')
    deployment = json.loads(args.deployment.read_text())
    if deployment.get('status') == 'deleted': raise RuntimeError('Deployment is closed')
    if args.action == 'collect': collect(args.folder, deployment); return
    subprocess.run(['scp', '-i', deployment['ssh_identity'], '-P', str(deployment['ssh_port']), str(mask),
                    'root@'+deployment['ssh_host']+':/workspace/runpod-slim/ComfyUI/input/'+MASK_NAME], check=True)
    remote = subprocess.check_output(['ssh','-i',deployment['ssh_identity'],'-p',str(deployment['ssh_port']),
        'root@'+deployment['ssh_host'],'sha256sum /workspace/runpod-slim/ComfyUI/input/'+MASK_NAME], text=True)
    assert remote.split()[0] == hashlib.sha256(mask.read_bytes()).hexdigest()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    label = f'{stamp}-krea-coral-seed{args.seed}'
    folder = PROJECT/'runs'/label; folder.mkdir(parents=True)
    sources = {}
    for source in (Path(__file__), Path(__file__).with_name('run_krea.py'), Path(__file__).with_name('run_baseline.py')):
        (folder/source.name).write_bytes(source.read_bytes())
        sources[source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
    (folder/MASK_NAME).write_bytes(mask.read_bytes())
    (folder/'design.json').write_bytes((EXPORT/'design.json').read_bytes())
    graph = CoralGraph('krea-coral/'+label, args.seed).build_pair()
    schema = request(deployment['base_url'], '/object_info'); validate(graph, schema)
    ui = ui_workflow(graph, schema)
    write_json(folder/'workflow.api.json', graph); write_json(folder/'workflow.json', ui)
    write_json(folder/'node-schemas.json', {n['class_type']:schema[n['class_type']] for n in graph.values()})
    write_json(folder/'system-stats.json', request(deployment['base_url'], '/system_stats'))
    receipt = {'pod_id':deployment['pod_id'], 'variant':'krea-coral', 'seed':args.seed,
        'source_hashes':sources, 'mask_sha256':hashlib.sha256(mask.read_bytes()).hexdigest(),
        'models':[a for a in json.loads(MODEL_MANIFEST.read_text()) if a['repo']=='Comfy-Org/Krea-2'],
        'submitted_at':datetime.now(timezone.utc).isoformat()}
    write_json(folder/'submission.json', receipt)
    try:
        response = request(deployment['base_url'], '/prompt', {'prompt':graph,'client_id':label,
                         'extra_data':{'extra_pnginfo':{'workflow':ui}}})
    except Exception as error:
        write_json(folder/'submission-error.json', {'error':str(error),'action':'Inspect queue/history before resubmission'})
        raise
    write_json(folder/'submit-response.json', response)
    if not response.get('prompt_id') or response.get('node_errors'): raise RuntimeError(response)
    receipt['prompt_id'] = response['prompt_id']; write_json(folder/'submission.json', receipt)
    print(json.dumps({'submitted':receipt['prompt_id'],'folder':str(folder)}), flush=True)
    collect(folder, deployment)


if __name__ == '__main__': main()
