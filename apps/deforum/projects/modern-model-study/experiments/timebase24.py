"""Replay recorded diffusion calls through a 24fps clock; finish with existing RIFE."""
import argparse,json
from unittest.mock import patch
import numpy as np
from PIL import Image
import turbo_smoothing as s
import turbo_smoothing_review as review
from cathedral_review import assert_warp_matches
from feedback_timing import FeedbackTiming

a,t=s.a,s.t
OUT=a.PROJECT/'exports/timebase24-v001'
OLD_FINISHED=a.PROJECT/'exports/turbo-smoothing-v001/interpolation'


def main(interpolate=True):
    timing=FeedbackTiming(interpolate=interpolate)
    root=OUT/f'cadence-{timing.cadence}'
    checks=[]

    def replay(project,name,graph,count,*,source,lineage):
        frame=lineage['frame'];old_frame=frame//2
        assert frame%2==0 and count==1
        record=json.loads((s.CONTROL/f'anchor-{old_frame:04d}.json').read_text())
        run=a.PROJECT/record['run']
        assert graph==json.loads((run/'workflow.api.json').read_text())
        assert lineage['parent_sha256']==record['parent_sha256']
        assert_warp_matches(np.asarray(Image.open(source)),np.asarray(Image.open(run/'anchor.png')))
        assert a.sha(run/'frames/0000.png')==record['output_sha256']
        checks.append({'new_frame':frame,'old_frame':old_frame,'seconds':timing.seconds(frame),
                       'recorded_run':record['run'],'warped_input_matches':True})
        return run

    with patch.object(a.transport,'submit',side_effect=replay):
        s.render(out=OUT,study='timebase24-replay-v001',timing=timing)
    assert len(checks)==11
    for i in range(36):
        assert_warp_matches(np.asarray(Image.open(root/f'frames/{2*i:04d}.png')),
                            np.asarray(Image.open(s.CONTROL/f'frames/{i:04d}.png')))
    for i in range(12):
        assert a.sha(root/f'anchors/{72+6*i:04d}.png')==a.sha(s.CONTROL/f'anchors/{36+3*i:04d}.png')
    a.save(OUT/'timing-verification.json',{'mode':'recorded diffusion replay; no inference',
        'source_fps':24,'target_fps':24,'cadence':6,'repaint_seconds':.25,
        'repaints':checks,'all_36_shared_motion_instants_match':True,
        'all_12_anchors_hash_identical':True,'interpolation_default':True})
    if not interpolate:return
    # These endpoints and interpolation timestamps are unchanged, so reuse verified RIFE pixels.
    old_receipt=json.loads((OLD_FINISHED/'manifest.json').read_text())
    for row in old_receipt['frames']:
        assert a.sha(OLD_FINISHED/f"frames/{row['frame']:04d}.png")==row['sha256']
    finished=OUT/'interpolated';rows=[]
    for i in range(timing.count):
        source=OLD_FINISHED/f'frames/{i:04d}.png' if i<66 else root/f'frames/{i:04d}.png'
        a.copy(source,finished/f'frames/{i:04d}.png')
        rows.append({'frame':i,'seconds':i/24,'source':str(source.relative_to(a.PROJECT)),
                     'sha256':a.sha(source),'kind':'verified existing RIFE/anchor' if i<66 else 'native 24fps final warp'})
    for i in range(12):
        np.testing.assert_array_equal(np.asarray(Image.open(finished/f'frames/{6*i:04d}.png')),
                                      np.asarray(Image.open(root/f'anchors/{72+6*i:04d}.png')))
    info=review.encode(finished)
    a.save(finished/'manifest.json',{'frames':rows,'probe':info,'diffusion_regenerated':False,
        'rife_recomputed':False,'reused_receipt_sha256':a.sha(OLD_FINISHED/'manifest.json'),
        'same_pixels_until_seconds':2.75,'final_warp_fps':24})
    review.compare('timing',finished/'frames','24 fps timeline | cadence 6 + RIFE',24,
        output_root=OUT,left_frames=OLD_FINISHED/'frames',left_fps=24,
        left_label='12 fps timeline | cadence 3 + RIFE')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--no-interpolation',action='store_true')
    main(interpolate=not p.parse_args().no_interpolation)
