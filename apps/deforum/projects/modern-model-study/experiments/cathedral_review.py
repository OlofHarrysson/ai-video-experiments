"""Verify the archived feedback lineage and make labeled, synchronized comparisons."""
import copy
import json
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cathedral_feedback as c


def assert_warp_matches(expected, actual):
    # Mac ARM and Linux x86 remaps differ at a few interpolation rounding boundaries.
    # Archived source/output file hashes below still require exact equality.
    delta = np.abs(expected.astype(np.int16) - actual.astype(np.int16))
    assert delta.max() <= 2 and np.mean(delta != 0) < 1e-5


def main():
    rows = []
    for model in ('klein', 'krea'):
        for strength in ('gentle', 'stronger'):
            root = c.OUT / model / strength
            assert c.a.sha(root/'anchors/0000.png') == c.a.sha(c.OUT/model/'opening.png')
            for f in range(3, c.FRAMES, 3):
                record = json.loads((root/f'anchor-{f:04d}.json').read_text())
                run = c.a.PROJECT / record['run']
                prior = root/f'anchors/{f-3:04d}.png'
                source = root/f'warped-inputs/{f:04d}.png'
                output = root/f'anchors/{f:04d}.png'
                assert c.a.sha(prior) == record['parent_sha256']
                assert c.a.sha(source) == c.a.sha(run/'anchor.png') == record['initialization_sha256']
                assert c.a.sha(output) == c.a.sha(run/'frames/0000.png') == record['output_sha256']
                requested = json.loads((run/'workflow.api.json').read_text())
                assert requested == c.graph(model, strength, c.SEED+f//3)
                executed = json.loads((run/'workflow.executed.json').read_text())
                normalized = copy.deepcopy(executed)
                normalized['20']['inputs']['image'] = 'anchor.png'
                assert normalized == requested
                assert executed['9']['inputs']['latent_image'] == ['24', 0]
                assert Image.open(output).size == (c.WIDTH, c.HEIGHT)
                if f in (3, 18, 33):
                    rebuilt = c.warp(np.asarray(Image.open(prior).convert('RGB')), f-3, f)
                    assert_warp_matches(rebuilt, np.asarray(Image.open(source).convert('RGB')))
                history = json.loads((run/'history.json').read_text())
                assert history['status']['completed'] and history['status']['status_str'] == 'success'
                messages = history['status']['messages']
                start = next(v['timestamp'] for k,v in messages if k == 'execution_start')
                end = next(v['timestamp'] for k,v in messages if k == 'execution_success')
                rows.append({'model': model, 'strength': strength, 'frame': f,
                             'execution_seconds': (end-start)/1000, 'run': record['run']})
            hashes = json.loads((root/'frame-hashes.json').read_text())
            assert len(hashes) == c.FRAMES
            for name, digest in hashes.items():
                assert c.a.sha(root/'frames'/name) == digest
            # Verify a cadence boundary and its neighboring warp-only images.
            for f in (23,24,25):
                anchor = f//3*3
                expected = c.warp(np.asarray(Image.open(root/f'anchors/{anchor:04d}.png').convert('RGB')), anchor, f)
                assert_warp_matches(expected, np.asarray(Image.open(root/f'frames/{f:04d}.png').convert('RGB')))
            info = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(root/'preview.mp4')]))['streams'][0]
            assert info['nb_frames'] == '72' and info['r_frame_rate'] == '24/1'
        target = c.OUT / 'comparisons' / model / 'preview.mp4'
        target.parent.mkdir(parents=True, exist_ok=True)
        labels = ['Less repaint - denoise 0.30', 'More repaint - denoise 0.45'] if model == 'krea' else ['Less starting noise - sigma 0.332', 'More starting noise - sigma 0.472']
        if not target.exists():
            font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 24)
            for f in range(c.FRAMES):
                canvas = Image.new('RGB', (1536,552), '#15191d')
                draw = ImageDraw.Draw(canvas)
                for i, strength in enumerate(('gentle','stronger')):
                    with Image.open(c.OUT/model/strength/f'frames/{f:04d}.png') as im:
                        canvas.paste(im.convert('RGB').resize((768,512), Image.Resampling.LANCZOS), (i*768,40))
                    draw.text((i*768+16,8), labels[i], font=font, fill='white')
                c.a.image(target.parent/f'frames/{f:04d}.png', np.asarray(canvas))
            c.a.editing.encode(target.parent/'frames', target, fps=c.FPS)
        c.a.save(target.parent/'manifest.json', {'labels': labels, 'source_fps': c.FPS,
            'source_manifest_hashes': [c.a.sha(c.OUT/model/s/'manifest.json') for s in ('gentle','stronger')],
            'method': 'resize and place synchronized source frames side by side; no interpolation'})
    c.a.save(c.OUT/'verification.json', {'verified': True, 'anchors': len(rows),
        'all_graphs_and_hashes_checked': True, 'recomputed_warps_per_branch': [3,18,33],
        'cross_platform_warp_tolerance': 'maximum 2/255 channel difference in less than 0.001 percent of channels; archived hashes exact',
        'checked_cadence_source_frames': [23,24,25], 'delivery': '72 frames at 24 fps; each 12 fps source frame repeated twice',
        'results': rows})
    print('Verified 44 initialized feedback anchors, 144 source frames, four clips and two comparisons')


if __name__ == '__main__':
    main()
