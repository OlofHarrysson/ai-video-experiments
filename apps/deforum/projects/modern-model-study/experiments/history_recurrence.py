"""Matched recurrent painting probe: fresh/gentle noise x latest/history latent."""
import argparse
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image
import ten_dollar as base
import correlated_noise as previous

OUT=Path(__file__).resolve().parents[1]/'exports/history-recurrence-v001'
CASES={'fresh':(0.,False),'gentle':(.995,False),
       'history-fresh':(0.,True),'history-gentle':(.995,True)}
SEED=918273
CYCLES=15
INPUT=Path('/workspace/runpod-slim/ComfyUI/input/history-recurrence-v001')


def config(case):
    source=json.loads((previous.CONFIGS/'independent.json').read_text())
    rho,history=CASES[case]
    return {**source,'case':case,'correlation':rho,'use_history':history,
            'history_weights':[.7,.2,.1] if history else [1.],
            'history_representation':'VAE encodings of archived recent paintings; newest first'}


def graph(case,index):
    c=config(case);n=base.node
    g=base.repaint_graph(c['prompt'],SEED+index,c['sigmas'])
    inputs=dict(current=['24',0],use_history=c['use_history'],seed=SEED,index=index,
                correlation=c['correlation'],case=case)
    if c['use_history']:
        for age,key,loader,encoder in ((1,'older','26','27'),(2,'oldest','28','29')):
            if index>=age:
                g[loader]=n('LoadImage',image=f'history-recurrence-v001/{case}/{index-age:04d}.png')
                g[encoder]=n('VAEEncode',pixels=[loader,0],vae=['3',0])
                inputs[key]=[encoder,0]
    g['44']=n('DeforumHistorySource',**inputs)
    g['45']=n('CFGGuider',model=['1',0],positive=['4',0],negative=['5',0],cfg=1.)
    g['9']=n('SamplerCustomAdvanced',noise=['44',1],guider=['45',0],sampler=['42',0],
              sigmas=['43',0],latent_image=['44',0])
    g['11']['inputs']['filename_prefix']='history-recurrence-v001/'+case+'/painting'
    return g


def prepare():
    source=base.APP/previous.SOURCE
    for case in CASES:
        root=OUT/case;root.mkdir(parents=True,exist_ok=True)
        base.save(root/'config.json',config(case))
        dest=root/'anchors/0000.png';dest.parent.mkdir(exist_ok=True)
        if dest.exists():assert base.sha(dest)==base.sha(source)
        else:shutil.copy2(source,dest)


def render(case,count):
    root=OUT/case
    (INPUT/case).mkdir(parents=True,exist_ok=True)
    for index in range(count):
        source=root/f'anchors/{index*6:04d}.png'
        target=root/f'anchors/{(index+1)*6:04d}.png'
        staged=INPUT/case/f'{index:04d}.png'
        if staged.exists():assert base.sha(staged)==base.sha(source)
        else:shutil.copy2(source,staged)
        g=graph(case,index)
        history=[root/f'anchors/{(index-age)*6:04d}.png' for age in range(min(index+1,3) if CASES[case][1] else 1)]
        row={'index':index,'frame':(index+1)*6,'seconds':(index+1)/4,
             'history_sha256':[base.sha(p) for p in history],
             'parent_sha256':base.sha(source),'correlation':CASES[case][0]}
        receipt=root/f'anchor-{(index+1)*6:04d}.json'
        if receipt.exists():
            recorded=json.loads(receipt.read_text());run=OUT/recorded['run']
            assert all(recorded[k]==v for k,v in row.items())
            assert json.loads((run/'workflow.api.json').read_text())==g
            assert recorded['output_sha256']==base.sha(target)==base.sha(run/'frames/0000.png')
            continue
        run=base.submit_once(f'memory-{case.replace("-", "")}-{index:04d}',g,source,row)
        if target.exists():assert base.sha(target)==base.sha(run/'frames/0000.png')
        else:shutil.copy2(run/'frames/0000.png',target)
        base.save(root/f'anchor-{(index+1)*6:04d}.json',{**row,'run':str(run.relative_to(OUT)),
                   'output_sha256':base.sha(target)})
        print(f'{case}: {index+1}/{count}',flush=True)


def parity():
    images=[]
    for case in CASES:
        render(case,1)
        images.append(np.asarray(Image.open(OUT/case/'anchors/0006.png')))
    historical=np.asarray(Image.open(previous.OUT/'independent/anchors/0006.png'))
    assert all(np.array_equal(images[0],im) for im in images[1:]),'First paintings differ across cases'
    assert np.array_equal(images[0],historical),'Historical first repaint differs: investigate before continuing'
    base.save(OUT/'parity.json',{'all_four_identical':True,'historical_pixel_identical':True})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','parity','render'])
    p.add_argument('--deployment',type=Path);p.add_argument('--case',choices=CASES)
    args=p.parse_args();base.OUT=OUT
    if args.deployment:base.pod_client.DEPLOYMENT=args.deployment
    if args.stage=='prepare':prepare()
    elif args.stage=='parity':parity()
    else:
        assert json.loads((OUT/'parity.json').read_text())['all_four_identical']
        for case in ([args.case] if args.case else CASES):render(case,CYCLES)
