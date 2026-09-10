# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Matched complete-prompt, regional, and native-tail Krea stills."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from run_baseline import Graph, PROJECT, collect, request, ui_workflow, validate, write_json

ROBOT = "A single small red tin robot stands on the grass, its entire body visible, with articulated metal arms and legs."
TREE = "A single blue glass tree is rooted in the grass, with a translucent trunk and a branching canopy made of blue glass that catches the sunlight."
SETTING = "An open grassy meadow stretches toward distant mountains beneath a golden sky. Warm sunlight from the upper left illuminates the scene. A painterly fantasy illustration with visible brushwork, coherent perspective and natural contact shadows on the shared grassy ground."
GLOBAL = ROBOT + " The robot stands on the left. " + TREE + " The tree stands on the right, separated from the robot by open grass. " + SETTING
TAIL = 3
MODEL_MANIFEST = PROJECT.parents[2]/'deforum/serverless/modern-models.json'


class KreaGraph(Graph):
    def __init__(self, prefix, seed):
        self.nodes, self.prefix, self.seed = {}, prefix, seed
        self.model = self.add('UNETLoader', unet_name='krea2_turbo_fp8_scaled.safetensors', weight_dtype='default')
        self.clip = self.add('CLIPLoader', clip_name='qwen3vl_4b_fp8_scaled.safetensors', type='krea2', device='default')
        self.vae = self.add('VAELoader', vae_name='qwen_image_vae.safetensors')
        self.complete = self.text(GLOBAL)
        self.negative = self.add('ConditioningZeroOut', conditioning=self.complete)

    def sample(self, latent, positive, seed):
        return self.add('KSampler', model=self.model, positive=positive, negative=self.negative,
                        latent_image=latent, seed=seed, steps=8, cfg=1.0,
                        sampler_name='euler', scheduler='simple', denoise=1.0)

    def snapshot(self, latent, label):
        self.save(self.decode(latent), label)
        self.add('SaveLatent', samples=latent, filename_prefix=f'{self.prefix}/{label}')

    def build_comparison(self, positioned=False):
        empty = self.empty()
        control = self.sample(empty, self.complete, self.seed)
        self.snapshot(control, 'complete')
        regional = self.add('ConditioningSetAreaStrength', conditioning=self.text(SETTING), strength=0.25)
        subjects = (ROBOT, TREE)
        if positioned:
            subjects = (ROBOT+' The robot stands on the left.', TREE+' The tree stands on the right.')
        for text, rectangle in zip(subjects, ((64,384,384,512),(576,384,384,512))):
            local = self.add('ConditioningSetMask', conditioning=self.text(text+' '+SETTING),
                             mask=self.mask(rectangle, soft=True), set_cond_area='default', strength=1.0)
            regional = self.add('ConditioningCombine', conditioning_1=regional, conditioning_2=local)
        source = self.sample(empty, regional, self.seed)
        self.snapshot(source, 'regional')
        sigmas = self.add('BasicScheduler', model=self.model, scheduler='simple', steps=8, denoise=1.0)
        split = self.add('SplitSigmas', sigmas=sigmas, step=8-TAIL)
        sampler = self.add('KSamplerSelect', sampler_name='euler')
        refined = self.add('SamplerCustom', model=self.model, add_noise=True, noise_seed=self.seed+3,
                           cfg=1.0, positive=self.complete, negative=self.negative,
                           sampler=sampler, sigmas=[split[0],1], latent_image=source)
        self.snapshot(refined, 'refined')
        return self.nodes


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['run','collect'])
    p.add_argument('--deployment', type=Path, required=True)
    p.add_argument('--seed', type=int, choices=[21001,21101], default=21001)
    p.add_argument('--folder', type=Path)
    p.add_argument('--positioned', action='store_true', help='Add left/right descriptions to the regional prompts')
    args = p.parse_args()
    d = json.loads(args.deployment.read_text())
    if d.get('status') == 'deleted':
        raise RuntimeError('Deployment is closed')
    if args.action == 'collect':
        collect(args.folder, d)
        return
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    label = f'{stamp}-krea'+('-positioned' if args.positioned else '')+f'-seed{args.seed}'
    folder = PROJECT/'runs'/label
    folder.mkdir(parents=True)
    (folder/'runner.py').write_bytes(Path(__file__).read_bytes())
    graph = KreaGraph('regional-krea/'+label, args.seed).build_comparison(args.positioned)
    schema = request(d['base_url'], '/object_info')
    validate(graph, schema)
    ui = ui_workflow(graph, schema)
    write_json(folder/'workflow.api.json', graph)
    write_json(folder/'workflow.json', ui)
    write_json(folder/'node-schemas.json', {n['class_type']:schema[n['class_type']] for n in graph.values()})
    write_json(folder/'system-stats.json', request(d['base_url'], '/system_stats'))
    models = [a for a in json.loads(MODEL_MANIFEST.read_text()) if a['repo']=='Comfy-Org/Krea-2']
    assert len(models)==3
    receipt = {'pod_id':d['pod_id'], 'variant':'krea-comparison', 'seed':args.seed,
               'refinement_seed':args.seed+3, 'tail_intervals':TAIL, 'models':models,
               'positioned_regional_prompts':args.positioned,
               'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'submitted_at':datetime.now(timezone.utc).isoformat()}
    write_json(folder/'submission.json', receipt)
    try:
        response = request(d['base_url'], '/prompt', {'prompt':graph, 'client_id':label,
                           'extra_data':{'extra_pnginfo':{'workflow':ui}}})
    except Exception as error:
        write_json(folder/'submission-error.json', {'error':str(error), 'action':'Inspect queue/history before any resubmission'})
        raise
    write_json(folder/'submit-response.json', response)
    if not response.get('prompt_id') or response.get('node_errors'):
        raise RuntimeError(response)
    receipt['prompt_id'] = response['prompt_id']
    write_json(folder/'submission.json', receipt)
    print(json.dumps({'submitted':receipt['prompt_id'], 'folder':str(folder)}), flush=True)
    collect(folder, d)


if __name__ == '__main__':
    main()
