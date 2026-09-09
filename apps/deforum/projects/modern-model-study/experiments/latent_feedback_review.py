"""Verify latent lineage and compare every cycle with preserved RGB feedback."""
import copy
import json
import subprocess
import numpy as np
from PIL import Image
import latent_feedback as p
from repaint_diagnosis_review import metrics, panel


def rgb(path):
    return np.asarray(Image.open(path).convert('RGB'))


def main():
    reference = rgb(p.d.SOURCE)
    records, checks = [], []
    for case in p.STRENGTHS:
        root = p.OUT/case
        manifest = json.loads((root/'manifest.json').read_text())
        run = p.d.a.PROJECT/manifest['run']
        g = p.graph(case)
        assert json.loads((run/'workflow.api.json').read_text()) == manifest['graph'] == g
        actual = json.loads((run/'workflow.executed.json').read_text())
        normalized = copy.deepcopy(actual)
        normalized['20']['inputs']['image'] = 'anchor.png'
        assert normalized == g
        hist = json.loads((run/'history.json').read_text())
        assert hist['status']['completed'] and hist['status']['status_str']=='success'
        assert p.d.a.sha(run/'anchor.png') == manifest['source_sha256'] == p.d.a.sha(p.d.SOURCE)
        assert sum(node['class_type']=='VAEEncode' for node in g.values()) == 1
        assert sum(node['class_type']=='KSampler' for node in g.values()) == 24
        for i in range(1,25):
            sampler=g[str(100+i)]['inputs']
            assert sampler['latent_image'] == (['24',0] if i==1 else [str(99+i),0])
            assert sampler['seed'] == p.d.opening.SEED+i
            expected=p.d.graph('repaint'+case[-3:],p.d.opening.SEED+i)['9']['inputs']
            a=copy.deepcopy(sampler);a['latent_image']=['24',0]
            assert a==expected
        for i in range(25):
            path=root/f'anchors/{i:04d}.png'
            assert p.d.a.sha(path)==manifest['outputs'][str(i)]
            if i:assert p.d.a.sha(path)==p.d.a.sha(run/f'frames/{i-1:04d}.png')
            im=rgb(path);assert im.shape==reference.shape
            old=p.d.OUT/f'repaint{case[-3:]}/anchors/{i:04d}.png'
            records.append({'case':case,'cycle':i,**metrics(im,reference),
                'mean_difference_from_rgb_feedback':float(np.abs(im.astype(float)-rgb(old).astype(float)).mean())})
            p.d.a.copy(path,root/f'frames/{i:04d}.png')
        first=records[-24]['mean_difference_from_rgb_feedback']
        checks.append({'case':case,'latent_links':24,'vae_encodes':1,
                       'first_cycle_mean_difference_from_rgb_control':first})
        if not (root/'preview.mp4').exists():p.d.a.editing.encode(root/'frames',root/'preview.mp4',fps=4)
    labels=['RGB feedback 0.10','Latent feedback 0.10','RGB feedback 0.30','Latent feedback 0.30']
    for i in range(25):
        paths=[p.d.OUT/f'repaint010/anchors/{i:04d}.png',p.OUT/f'latent010/anchors/{i:04d}.png',
               p.d.OUT/f'repaint030/anchors/{i:04d}.png',p.OUT/f'latent030/anchors/{i:04d}.png']
        im=panel(paths,labels,cycle=i)
        p.d.a.image(p.OUT/f'comparison/frames/{i:04d}.png',im)
        if i in [0,1,4,11,24]:
            p.d.a.image(p.OUT/f'review/cycle-{i:02d}.png',im)
            p.d.a.image(p.OUT/f'review/detail-{i:02d}.png',panel(paths,labels,cycle=i,crop=(240,100,1008,612)))
    target=p.OUT/'comparison/preview.mp4'
    if not target.exists():p.d.a.editing.encode(target.parent/'frames',target,fps=4)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(target)]))['streams'][0]
    assert probe['nb_frames']=='150' and probe['r_frame_rate']=='24/1'
    p.d.a.save(p.OUT/'verification.json',{'verified':True,'checks':checks,'saved_cycles':48,
        'no_motion':True,'decoded_images_never_feed_sampling':True})
    p.d.a.save(p.OUT/'diagnostics.json',{'meaning':'change and contrast metrics, not aesthetic scores','results':records})
    print(json.dumps(checks,indent=2))


if __name__=='__main__':main()
