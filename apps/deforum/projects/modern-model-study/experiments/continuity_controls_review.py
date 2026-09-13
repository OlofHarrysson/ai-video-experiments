"""Local lineage checks, source review and staged RIFE finishing for preservation controls.

Stages: verify -> sources -> pair -> inspect pair sheets/video -> full --pair-reviewed
-> delivery. Imports and --help do not submit jobs or process media. Use --case to
work on completed cases individually; omit it to require every configured case.
"""
import argparse
import copy
from fractions import Fraction
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw

import continuity_controls as study
from interpolate import PIN, frame_plan

OUT = study.OUT
FPS, CADENCE, FRAME_COUNT = 24, 6, 96
ANCHORS = tuple(range(0, FRAME_COUNT, CADENCE))
SIZE = (1536, 1024)
# Fixed native-resolution regions; semantic interpretation waits for visual review.
CROPS = {'upper-left': (96, 96, 480, 352),
         'center-distance': (576, 256, 960, 512),
         'right-middle': (1056, 384, 1440, 640)}
METRIC_NOTE = ('Descriptive pixel statistics, not quality scores. Edge energy and '
               'Laplacian variance respond to noise as well as detail; RGB differences '
               'do not establish object retention or perceived depth.')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def pixels(path):
    with Image.open(path) as im:
        require(im.mode == 'RGB' and im.size == SIZE, f'Unexpected RGB dimensions: {path}')
        return np.array(im)


def kind(case):
    return 'reconstruction' if case == 'vae-only' else 'diffusion painting'


def label(case, frame):
    name = 'shared source painting' if frame == 0 else f'{kind(case)} {frame // CADENCE}'
    return f'{case} | {frame / FPS:.2f}s | {name}'


def inventory(folder, indices):
    expected = [f'{i:04d}.png' for i in indices]
    require(sorted(p.name for p in folder.glob('*.png')) == expected,
            f'Unexpected PNG inventory: {folder}')


def checked_config(case):
    config = read(OUT / case / 'config.json')
    require(config == read(study.CONFIGS / f'{case}.json'), f'Config archive differs: {case}')
    sampler, sigma = study.CASES[case]
    sigmas = None if sigma is None else [v * sigma / .6 for v in study.base.SIGMAS]
    prompt = read(study.HERE / 'cfg-audition-configs/cfg-10.json')['scenes'][0]['prompt']
    expected = {'case': case, 'sampler': sampler, 'seed': study.SEED, 'source': study.SOURCE,
                'duration': 4, 'cadence': CADENCE, 'fps': FPS, 'cfg': 1., 'sigmas': sigmas,
                'prompt': prompt, 'motion': 'none'}
    require(config == expected, f'Unexpected experiment settings: {case}')
    return config


def validate_execution(requested, executed, upload, history, response, submission, parent_hash):
    """Pure validation of the local submission evidence; no remote calls."""
    expected = copy.deepcopy(requested)
    require(upload.get('type') == 'input' and bool(upload.get('name')), 'Missing input upload')
    expected['20']['inputs']['image'] = '/'.join(filter(None, [upload.get('subfolder'), upload['name']]))
    require(executed == expected, 'Executed graph differs from uploaded requested graph')
    if 'sha256' in upload:
        require(upload['sha256'] == parent_hash, 'Upload checksum differs from parent')
    prompt_id = response.get('prompt_id')
    require(bool(prompt_id) and not response.get('node_errors'), 'Submission rejected or missing prompt id')
    require(submission.get('prompt_id') == prompt_id, 'Submission prompt id mismatch')
    require(submission.get('frames') == 1 and bool(submission.get('collected_at')), 'Run not collected')
    require(submission.get('parent_sha256') == parent_hash, 'Submission parent checksum mismatch')
    status = history['status']
    require(status.get('completed') is True and status.get('status_str') == 'success', 'Unsuccessful history')
    require(history['prompt'][1] == prompt_id and history['prompt'][2] == executed,
            'History prompt id or graph mismatch')
    require('11' in history['prompt'][4], 'SaveImage absent from executed outputs')
    for event, payload in status.get('messages', []):
        require(event not in ('execution_error', 'execution_interrupted'), 'History contains execution failure')
        if 'prompt_id' in payload:
            require(payload['prompt_id'] == prompt_id, 'History event prompt id mismatch')
    images = history['outputs']['11']['images']
    require(len(images) == 1 and images[0].get('type') == 'output'
            and images[0]['filename'].endswith('.png'), 'Unexpected SaveImage output')
    return prompt_id, images[0]


def check_case(case):
    config = checked_config(case)
    root = OUT / case
    inventory(root / 'anchors', ANCHORS)
    require(sorted(p.name for p in root.glob('anchor-*.json')) ==
            [f'anchor-{f:04d}.json' for f in ANCHORS[1:]], f'Receipt inventory differs: {case}')
    source_hash = study.base.sha(OUT / 'source/seed.png')
    require(source_hash == study.base.sha(study.base.APP / config['source']) ==
            study.base.sha(root / 'anchors/0000.png'), f'Source mismatch: {case}')
    pixels(root / 'anchors/0000.png')
    rows = []
    for frame in ANCHORS[1:]:
        receipt_path = root / f'anchor-{frame:04d}.json'
        rec = read(receipt_path)
        index = frame // CADENCE - 1
        for key, value in {'frame': frame, 'seconds': frame / FPS, 'seed': config['seed'] + index,
                           'sampler': config['sampler'], 'sigmas': config['sigmas']}.items():
            require(rec[key] == value, f'{case}/{frame}: incorrect receipt {key}')
        run = (OUT / rec['run']).resolve()
        require(run.is_relative_to((OUT / 'runs').resolve()), f'Run outside experiment archive: {run}')
        parent = root / f'anchors/{frame - CADENCE:04d}.png'
        target = root / f'anchors/{frame:04d}.png'
        parent_hash, output_hash = study.base.sha(parent), study.base.sha(target)
        require(parent_hash == rec['parent_sha256'] == rec['initialization_sha256'] ==
                study.base.sha(run / 'anchor.png'), f'{case}/{frame}: input lineage mismatch')
        require(output_hash == rec['output_sha256'] == study.base.sha(run / 'frames/0000.png'),
                f'{case}/{frame}: output lineage mismatch')
        inventory(run / 'frames', [0])
        require(read(run / 'frame-hashes.json') == {'0000.png': output_hash}, 'Archive frame hashes differ')
        pixels(target)
        requested = read(run / 'workflow.api.json')
        require(requested == study.graph(config, index), f'{case}/{frame}: requested graph differs')
        submission = read(run / 'submission.json')
        require(submission['frame'] == frame and submission['seconds'] == frame / FPS
                and submission['sampler'] == config['sampler'], 'Submission lineage settings differ')
        prompt_id, remote_image = validate_execution(
            requested, read(run / 'workflow.executed.json'), read(run / 'upload.json'),
            read(run / 'history.json'), read(run / 'submit-response.json'), submission, parent_hash)
        files = ['anchor.png', 'frames/0000.png', 'frame-hashes.json', 'workflow.api.json',
                 'workflow.executed.json', 'upload.json', 'history.json', 'submission.json',
                 'submit-response.json']
        rows.append({'frame': frame, 'seconds': frame / FPS, 'update_kind': kind(case),
                     'run': rec['run'], 'prompt_id': prompt_id, 'parent_sha256': parent_hash,
                     'output_sha256': output_hash, 'history_output': remote_image,
                     'receipt_sha256': study.base.sha(receipt_path),
                     'archive_sha256': {name: study.base.sha(run / name) for name in files},
                     'upload_checksum_recorded': 'sha256' in read(run / 'upload.json')})
    require(len({r['prompt_id'] for r in rows}) == 15 and len({r['run'] for r in rows}) == 15,
            f'Duplicate run or prompt id: {case}')
    return {'verified': True, 'case': case, 'source_sha256': source_hash,
            'config_sha256': study.base.sha(root / 'config.json'), 'anchors': 16,
            'diffusion_jobs': 0 if case == 'vae-only' else 15,
            'reconstruction_jobs': 15 if case == 'vae-only' else 0, 'rows': rows,
            'evidence_scope': 'Local archived inputs/outputs and recorded server history; '
                              'HTTP upload acknowledgements may lack a remote input checksum.'}


def historical_comparison():
    old = OUT.parent / 'correlated-noise-v001/independent'
    fresh = OUT / 'euler-060'
    inventory(old / 'anchors', ANCHORS)
    a, b = read(fresh / 'config.json'), read(old / 'config.json')
    for key in ('seed', 'source', 'duration', 'cadence', 'fps', 'cfg', 'sigmas', 'prompt', 'motion'):
        require(a[key] == b[key], f'Historical comparison settings differ: {key}')
    historical_ids, rows = set(), []
    for frame in ANCHORS:
        x, y = fresh / f'anchors/{frame:04d}.png', old / f'anchors/{frame:04d}.png'
        if frame:
            rec = read(old / f'anchor-{frame:04d}.json')
            require(rec['output_sha256'] == study.base.sha(y), 'Historical painting checksum differs')
            require(rec['parent_sha256'] == rec['initialization_sha256'] ==
                    study.base.sha(old / f'anchors/{frame-CADENCE:04d}.png'), 'Historical parent differs')
            historical_ids.add(read(old.parent / rec['run'] / 'submit-response.json')['prompt_id'])
        delta = np.abs(pixels(x).astype(np.int16) - pixels(y).astype(np.int16))
        rows.append({'frame': frame, 'fresh_sha256': study.base.sha(x), 'historical_sha256': study.base.sha(y),
                     'byte_identical': study.base.sha(x) == study.base.sha(y),
                     'pixel_identical': not bool(delta.any()), 'rgb_mae_0_1': float(delta.mean() / 255),
                     'max_channel_difference_0_255': int(delta.max())})
    fresh_ids = {read(fresh / f'anchor-{f:04d}.json')['run'] for f in ANCHORS[1:]}
    fresh_ids = {read(OUT / run / 'submit-response.json')['prompt_id'] for run in fresh_ids}
    require(not (fresh_ids & historical_ids), 'Fresh Euler reused historical prompt ids')
    return {'historical_case': str(old), 'all_16_pixel_identical': all(r['pixel_identical'] for r in rows),
            'all_16_byte_identical': all(r['byte_identical'] for r in rows), 'rows': rows,
            'meaning': 'Observed cross-session equality or difference; no assumed sampler/runtime parity.'}


def check_generation(cases=None, save=True):
    cases = list(study.CASES if cases is None else cases)
    reports = [check_case(case) for case in cases]
    ids = [row['prompt_id'] for report in reports for row in report['rows']]
    require(len(ids) == len(set(ids)) == 15 * len(cases), 'Duplicate prompt ids across cases')
    for report in reports:
        if report['case'] == 'euler-060':
            report['historical_comparison'] = historical_comparison()
        if save:
            study.base.save(OUT / report['case'] / 'generation-check.json', report)
    if save and set(cases) == set(study.CASES):
        study.base.save(OUT / 'generation-check.json', {'verified': True, 'jobs': len(ids), 'cases': reports})
    return reports


def image_metrics(current, previous, source):
    x = current.astype(np.float32) / 255
    luma = x @ np.array([.2126, .7152, .0722], dtype=np.float32)
    lap = (luma[:-2, 1:-1] + luma[2:, 1:-1] + luma[1:-1, :-2]
           + luma[1:-1, 2:] - 4 * luma[1:-1, 1:-1])
    return {'rgb_mean_0_1': x.mean(axis=(0, 1)).tolist(), 'luma_std_0_1': float(luma.std()),
            'luma_gradient_mean_0_1': float((np.abs(np.diff(luma, axis=0)).mean()
                                           + np.abs(np.diff(luma, axis=1)).mean()) / 2),
            'luma_laplacian_variance': float(lap.var()),
            'rgb_mae_previous_0_1': float(np.abs(x - previous.astype(np.float32) / 255).mean()),
            'rgb_mae_source_0_1': float(np.abs(x - source.astype(np.float32) / 255).mean())}


def sheet(items, target, cell=(512, 365), resize=True):
    """Small two-column pages; crop pixels remain 1:1 when resize=False."""
    board = Image.new('RGB', (cell[0] * 2, cell[1] * ((len(items) + 1) // 2)), '#171717')
    draw = ImageDraw.Draw(board)
    for i, (rgb, title) in enumerate(items):
        x, y = i % 2 * cell[0], i // 2 * cell[1]
        im = Image.fromarray(rgb)
        if resize:
            im.thumbnail((cell[0], cell[1] - 24))
        board.paste(im, (x, y + 24))
        draw.text((x + 6, y + 6), title, fill='white')
    target.parent.mkdir(parents=True, exist_ok=True)
    board.save(target)


def source_media(cases=None):
    cases = list(study.CASES if cases is None else cases)
    check_generation(cases)
    for case in cases:
        root = OUT / case
        source = previous = pixels(root / 'anchors/0000.png')
        rows, page = [], []
        crop_pages = {name: [] for name in CROPS}
        for i, frame in enumerate(ANCHORS):
            current = pixels(root / f'anchors/{frame:04d}.png')
            row = {'frame': frame, 'seconds': frame / FPS, 'label': label(case, frame),
                   'source_sha256': study.base.sha(root / f'anchors/{frame:04d}.png'),
                   'whole_image': image_metrics(current, previous, source), 'crops': {}}
            page.append((current, label(case, frame)))
            for name, (x0, y0, x1, y1) in CROPS.items():
                crop = current[y0:y1, x0:x1]
                row['crops'][name] = image_metrics(crop, previous[y0:y1, x0:x1], source[y0:y1, x0:x1])
                crop_pages[name].append((crop, f'{case} | {frame/FPS:.2f}s | '
                                              + ('source' if not frame else kind(case))))
            rows.append(row)
            if len(page) == 4:
                sheet(page, root / f'review/source-{i//4+1:02d}.jpg')
                page = []
                for name, items in crop_pages.items():
                    sheet(items, root / f'review/crops-{name}-{i//4+1:02d}.png', (384, 280), resize=False)
                    items.clear()
            previous = current
        study.base.save(root / 'source-metrics.json', {'case': case, 'note': METRIC_NOTE,
            'crop_boxes_xyxy': {name: list(box) for name, box in CROPS.items()},
            'frames': rows, 'interpolated_frames_included': False})


def check_rife(case, stage):
    root = OUT / case
    target = root / 'section-016' / ('pair' if stage == 'pair' else 'rife')
    manifest = read(target / 'manifest.json')
    require(manifest['status'] == 'complete' and manifest['anchors_verified'] is True
            and manifest['source_hashes_and_mtimes_preserved'] is True, f'Incomplete RIFE: {case}/{stage}')
    require(manifest['mode'] == ('first_pair' if stage == 'pair' else 'full'), 'RIFE mode differs')
    settings = manifest['settings']
    for key, expected in {'source_fps': 4., 'output_fps': 24., 'multiplier': 6, 'scale': 1.,
                          'scale_list': [16, 8, 4, 2, 1], 'scene_detection': False,
                          'static_frame_skipping': False}.items():
        require(settings[key] == expected, f'RIFE setting differs: {key}')
    require(manifest['provenance']['model'] == 'RIFE 4.25'
            and manifest['provenance']['commit'] == PIN, 'Unexpected RIFE implementation')
    require(len(manifest['sources']) == 16, 'RIFE source count differs')
    source_folder = root / 'section-016/sources'
    inventory(source_folder, range(16))
    for i, row in enumerate(manifest['sources']):
        p = source_folder / f'{i:04d}.png'
        require(Path(row['file']).resolve() == p.resolve(), 'RIFE source path differs')
        require(row['sha256'] == study.base.sha(p) == study.base.sha(root / f'anchors/{i*6:04d}.png')
                and row['mtime_ns'] == p.stat().st_mtime_ns and row['size'] == list(SIZE), 'RIFE source changed')
    plan = frame_plan(2 if stage == 'pair' else 16, final_holds=0 if stage == 'pair' else 5, multiplier=6)
    inventory(target / 'frames', range(len(plan)))
    require(len(manifest['output_frames']) == len(plan), 'RIFE output count differs')
    require(manifest['final_holds'] == (0 if stage == 'pair' else 5), 'Final hold count differs')
    for i, (expected, row) in enumerate(zip(plan, manifest['output_frames'])):
        require(all(row.get(k) == v for k, v in expected.items()) and row['index'] == i
                and row['time_seconds'] == i / FPS and row['file'] == f'frames/{i:04d}.png',
                f'RIFE output plan differs: {i}')
        p = target / row['file']
        require(row['sha256'] == study.base.sha(p), f'RIFE frame changed: {p}')
        pixels(p)
        if expected['kind'] != 'interpolation':
            require(row['sha256'] == study.base.sha(root / f"anchors/{expected['source_index']*6:04d}.png"),
                    'RIFE anchor/hold not byte-identical')
    require(study.base.sha(target / 'preview.mp4') == manifest['video_sha256'], 'RIFE video checksum differs')
    if stage == 'full':
        pair = check_rife(case, 'pair')
        require(Path(manifest['validated_pair']).resolve() == (root / 'section-016/pair/manifest.json').resolve(),
                'Wrong validated pair path')
        for key in ('sources', 'settings', 'provenance'):
            require(manifest[key] == pair[key], f'Pair/full {key} differ')
    return manifest


def finish_stage(stage, cases=None, pair_reviewed=False):
    require(stage in ('pair', 'full'), 'Only pair/full finishing is supported')
    require(stage != 'full' or pair_reviewed, 'Inspect pair sheets/video first; then pass --pair-reviewed')
    cases = list(study.CASES if cases is None else cases)
    check_generation(cases)
    if stage == 'full':
        for case in cases:
            check_rife(case, 'pair')
    # dynamic_journey changes its shared base.OUT on import: contain that side effect.
    previous_base_out = study.base.OUT
    try:
        import dynamic_journey_finish as finish
        previous_finish_out = finish.d.OUT
        try:
            finish.d.OUT = OUT
            for case in cases:
                finish.run(case, stage)
                check_rife(case, stage)
                # Replace the reused finisher's generic thumbnails with accurate update labels.
                for start in range(0, len(ANCHORS), 4):
                    items = [(pixels(OUT / case / f'anchors/{f:04d}.png'), label(case, f))
                             for f in ANCHORS[start:start+4]]
                    sheet(items, OUT / case / f'section-016/paintings-{start//4+1:02d}.jpg')
                if stage == 'pair':
                    folder = OUT / case / 'section-016/pair'
                    for start in (0, 4):
                        items = []
                        for f in range(start, min(start + 4, 7)):
                            title = label(case, f) if f in (0, 6) else f'{case} | {f/FPS:.3f}s | RIFE intermediate'
                            items.append((pixels(folder / f'frames/{f:04d}.png'), title))
                        sheet(items, folder / f'review-{start//4+1:02d}.jpg')
        finally:
            finish.d.OUT = previous_finish_out
    finally:
        study.base.OUT = previous_base_out


def check_delivery(cases=None):
    cases = list(study.CASES if cases is None else cases)
    check_generation(cases)
    rows = []
    for case in cases:
        manifest = check_rife(case, 'full')
        video = OUT / case / 'section-016/rife/preview.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(video), '-f', 'null', '-'], check=True)
        info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-count_frames', '-show_entries', 'stream=width,height,avg_frame_rate,r_frame_rate,duration,nb_read_frames',
            '-of', 'json', str(video)]))['streams'][0]
        require((info['width'], info['height']) == SIZE and int(info['nb_read_frames']) == FRAME_COUNT
                and Fraction(info['r_frame_rate']) == FPS and Fraction(info['avg_frame_rate']) == FPS
                and abs(float(info['duration']) - 4) < 1e-6, f'Delivery timing/dimensions differ: {case}')
        row = {'verified': True, 'case': case, 'video_sha256': study.base.sha(video), 'video': info,
               'anchors_retained': 16, 'shared_source_paintings': 1,
               'diffusion_paintings_generated': 0 if case == 'vae-only' else 15,
               'reconstructions_generated': 15 if case == 'vae-only' else 0,
               'intermediate_frames': 75, 'final_hold_frames': 5,
               'interpolation': 'RIFE 4.25 scale1, outside feedback',
               'output_frames': manifest['output_frames'],
               'manifest_sha256': study.base.sha(video.parent / 'manifest.json')}
        study.base.save(OUT / case / 'delivery-check.json', row)
        rows.append(row)
    if set(cases) == set(study.CASES):
        study.base.save(OUT / 'delivery-check.json', {'verified': True, 'videos': rows})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['verify', 'sources', 'pair', 'full', 'delivery'])
    parser.add_argument('--case', choices=list(study.CASES), nargs='+')
    parser.add_argument('--pair-reviewed', action='store_true', help='Confirm selected first-pair outputs were inspected')
    args = parser.parse_args()
    if args.case and len(args.case) != len(set(args.case)):
        parser.error('Each case must be selected only once')
    if args.stage == 'full' and not args.pair_reviewed:
        parser.error('Inspect first-pair sheets/video, then use full --pair-reviewed')
    if args.stage == 'verify':
        check_generation(args.case)
    elif args.stage == 'sources':
        source_media(args.case)
    elif args.stage == 'delivery':
        check_delivery(args.case)
    else:
        finish_stage(args.stage, args.case, args.pair_reviewed)
    print(f'Completed {args.stage}: {", ".join(args.case or study.CASES)}')


if __name__ == '__main__':
    main()
