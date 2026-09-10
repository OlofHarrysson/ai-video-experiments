"""Review prompt-directed morphs with the accepted opening and finishing unchanged."""
import argparse
import copy
import json
from types import SimpleNamespace
import numpy as np
from PIL import Image
import owl_transition as study
import starting_noise_review as shared

a, t = study.a, study.t
shared.REFERENCE=study.BASELINE/'rife-raw/manifest.json'
shared.t=SimpleNamespace(**{**vars(t),'coordinates_at_time':study.coordinates_at_time,'warp_at_time':study.warp_at_time})


def check():
    clock=study.timing();assert (clock.fps,clock.cadence,clock.count,clock.start)==(24,24,336,72)
    for second in range(1,14):
        seed=t.SEED+12+second
        left=study.graph('oracle',seed);right=study.graph('owl',seed)
        if second<=8:
            assert left==right==study.previous.graph('ease',seed)
            record=json.loads((study.BASELINE/f'anchor-{72+24*second:04d}.json').read_text())
            assert json.loads((a.PROJECT/record['run']/'workflow.api.json').read_text())==left
        else:
            assert left['9']['inputs']['noise_seed']==right['9']['inputs']['noise_seed']==seed
            normalized=copy.deepcopy(right)
            normalized['4']['inputs']['text']=left['4']['inputs']['text']
            normalized['11']['inputs']['filename_prefix']=left['11']['inputs']['filename_prefix']
            assert normalized==left
            expected=study.previous.graph('ease',t.SEED+20)
            expected['9']['inputs']['noise_seed']=seed
            expected['11']['inputs']['filename_prefix']=left['11']['inputs']['filename_prefix']
            assert expected==left
    source=np.asarray(Image.open(study.BASELINE/'anchors/0264.png').convert('RGB'))
    for second in range(8,14):
        np.testing.assert_array_equal(study.warp_at_time(source,3+second,4+second),source)
    a.save(study.OUT/'local-checks.json',{'passed':True,'fresh_jobs':10,'checks':
        '13 schedules per case, eight inherited graphs, only positive text/filename differences, continued seeds, identity held pixels through14s'})
    print('CHECKED inherited graphs, continued seeds, prompt-only differences and held inputs')


def build_raw():
    # Reuse the accepted opening rather than recalculate its first eight seconds.
    for case in study.LEVELS:
        root=shared.base(case,study)
        for i in range(193):
            a.copy(study.BASELINE/f'frames/{i:04d}.png',root/f'frames/{i:04d}.png')
    shared.build_raw(study=study)


def prepare(case):
    shared.prepare(case,study=study)
    root=shared.base(case,study)
    for second in range(9):
        name=f'anchors/{72+24*second:04d}.png';assert a.sha(root/name)==a.sha(study.BASELINE/name)
    for second in range(9,14):
        f=72+24*second
        np.testing.assert_array_equal(np.asarray(Image.open(root/f'warped-inputs/{f:04d}.png').convert('RGB')),
            np.asarray(Image.open(root/f'anchors/{f-24:04d}.png').convert('RGB')))
    print('VERIFIED preserved opening and held recurrent inputs',case)


def finish(case):
    shared.finish(case,study=study)
    root=shared.base(case,study)
    for i in range(193):
        np.testing.assert_array_equal(np.asarray(Image.open(root/f'interpolated/frames/{i:04d}.png')),
            np.asarray(Image.open(study.BASELINE/f'interpolated/frames/{i:04d}.png')))
    for i in range(312,336):
        np.testing.assert_array_equal(np.asarray(Image.open(root/f'interpolated/frames/{i:04d}.png')),
            np.asarray(Image.open(root/'anchors/0384.png')))
    a.save(root/'transition-verification.json',{'passed':True,'shared_opening_frames_through':192,
        'prompt_switch_after_seconds':8,'first_new_prompt_painting_seconds':9,
        'spatial_motion_stops_seconds':8,'final_native_hold_seconds':[13,14]})


def compare():
    shared.compare(study.LEVELS,'comparison',study=study,
        labels={'oracle':'Keep Oracle prompt','owl':'Change prompt to porcelain owl'},
        caption_at=lambda time:'same opening' if time<8 else ('repainting with motion held' if time<13 else 'after final repaint'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['check','build-raw','prepare','finish','compare']);p.add_argument('--case',choices=study.LEVELS)
    args=p.parse_args()
    if args.action in ('check','build-raw','compare'):globals()[args.action.replace('-','_')]()
    else:
        for case in ([args.case] if args.case else study.LEVELS):globals()[args.action](case)
