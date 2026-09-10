"""Validate and finish the shared-opening motion continuation."""
import argparse
import json
import subprocess
from types import SimpleNamespace
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import eased_motion as study
import starting_noise_review as shared

a, t = study.a, study.t
shared.REFERENCE = study.BASELINE / 'rife-raw/manifest.json'


def select(case):
    shared.t = SimpleNamespace(**{**vars(t),
        'coordinates_at_time': lambda *args: study.coordinates_at_time(*args, case=case),
        'warp_at_time': lambda *args: study.warp_at_time(*args, case=case)})
    return SimpleNamespace(OUT=study.OUT, BASELINE=study.BASELINE, LEVELS=(case,),
                           timing=study.timing, graph=study.graph, branch=study.branch)


def check():
    rows = []
    rgb = np.asarray(Image.open(study.BASELINE / 'anchors/0216.png').convert('RGB'))
    for case in study.LEVELS:
        times = [study.motion_time(3+i/24, case) for i in range(289)]
        assert np.all(np.diff(times) >= 0)
        for i in range(145):
            assert times[i] == 3+i/24
        if case == 'ease':
            assert all(value == 10 for value in times[192:])
            np.testing.assert_array_equal(study.warp_at_time(rgb, 11, 15, case), rgb)
        for second in range(1, 12):
            seed = t.SEED+12+second
            g = study.graph(case, seed); expected = study.previous.graph('high3', seed)
            if second > 6:
                g['11']['inputs']['filename_prefix'] = expected['11']['inputs']['filename_prefix']
            assert g == expected
        rows.append({'case': case, 'effective_local_seconds': [study.motion_time(3+i, case)-3 for i in range(13)]})
    # The first six seconds and boundary map are exactly the old path.
    np.testing.assert_array_equal(study.coordinates_at_time(8, 9), study.previous.coordinates_at_time(8, 9))
    h = 1e-4
    for local, speed in ((6, 1), (8, 0)):
        derivative = (study.motion_time(3+local+h, 'ease')-study.motion_time(3+local-h, 'ease'))/(2*h)
        assert abs(derivative-speed) < 1e-6
    a.save(study.OUT/'local-checks.json', {'passed': True, 'schedules': rows,
        'checks': 'monotone time, exact shared prefix, smooth boundary speed, held RGB identity, all 22 graph/seed schedules'})
    print('CHECKED shared opening, easing boundaries, hold identity and graph schedules')


def preview():
    from fractions import Fraction
    from feedback_timing import FeedbackTiming
    root = study.OUT/'motion-only'
    rgb = np.asarray(Image.open(study.BASELINE/'anchors/0216.png').convert('RGB').resize((768,512),Image.Resampling.LANCZOS))
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 23)
    for i in range(144):
        canvas = Image.new('RGB',(1536,554),'#15191d'); draw=ImageDraw.Draw(canvas)
        for column,case in enumerate(study.LEVELS):
            canvas.paste(Image.fromarray(study.warp_at_time(rgb,9,9+i/24,case)),(column*768,42))
            draw.text((column*768+12,9),f'{case} | shot time {6+i/24:.2f}s | motion only',font=font,fill='white')
        a.image(root/f'frames/{i:04d}.png',np.asarray(canvas))
    clock=FeedbackTiming(repaint_seconds=Fraction(1),duration_seconds=Fraction(6))
    a.save(root/'manifest.json',{'probe':shared.encode(root,clock),'source':str(study.BASELINE/'anchors/0216.png'),
        'source_sha256':a.sha(study.BASELINE/'anchors/0216.png'),'diffusion':False,'one_direct_warp_from_source_per_frame':True})


def prepare(case):
    shared.prepare(case,study=select(case))
    root=shared.base(case,study)
    for second in range(7):
        name=f'anchors/{72+24*second:04d}.png'
        assert a.sha(root/name)==a.sha(study.BASELINE/name)
    if case=='ease':
        for second in range(9,12):
            f=72+24*second
            np.testing.assert_array_equal(
                np.asarray(Image.open(root/f'warped-inputs/{f:04d}.png').convert('RGB')),
                np.asarray(Image.open(root/f'anchors/{f-24:04d}.png').convert('RGB')))
    print('VERIFIED preserved seven paintings and held repaint inputs',case)


def finish(case):
    # Shared finish checks model/code/settings, source/output hashes and all anchors.
    shared.finish(case,study=select(case))
    root=shared.base(case,study);out=root/'interpolated'
    for i in range(145):
        np.testing.assert_array_equal(np.asarray(Image.open(out/f'frames/{i:04d}.png')),
            np.asarray(Image.open(study.BASELINE/f'interpolated/frames/{i:04d}.png')))
    if case=='ease':
        for i in range(264,288):
            np.testing.assert_array_equal(np.asarray(Image.open(out/f'frames/{i:04d}.png')),
                np.asarray(Image.open(root/'anchors/0336.png')))
    a.save(root/'continuation-verification.json',{'passed':True,'opening_frames_pixel_identical_through':144,
        'branch_at_seconds':6,'final_second':'static native hold' if case=='ease' else 'native continuous warp'})


def compare():
    shared.compare(study.LEVELS,'comparison',study=study,
        labels={'continuous':'Keep twisting + expanding','ease':'Ease motion 6–8s, then hold'},
        caption_at=lambda seconds: 'same opening' if seconds<6 else ('repainting continues' if seconds<11 else 'after final repaint'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['check','preview','build-raw','prepare','finish','compare']);p.add_argument('--case',choices=study.LEVELS)
    args=p.parse_args()
    if args.action in ('check','preview','compare'):globals()[args.action]()
    else:
        for case in ([args.case] if args.case else study.LEVELS):
            if args.action=='build-raw':shared.build_raw(study=select(case))
            else:globals()[args.action](case)
