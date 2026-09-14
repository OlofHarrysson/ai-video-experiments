"""Offline validation: structure, generation (30 jobs), or delivery (both films).

From apps/deforum:
  uv run -q --with numpy --with pillow --with opencv-python python \
    projects/modern-model-study/experiments/hold_transform_check.py structure
Replace structure with generation or delivery as artifacts become available.
No rendering, cloud calls, polling, or file writes. JSON goes to stdout; failures
exit 1. --details includes per-job archive hashes. Delivery includes generation.
Exact anchor retention refers to the PNG timeline; MP4 is a lossy encoding.
"""
import argparse
import copy
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

import cv2
import numpy as np
from PIL import Image

import hold_transform as study
from interpolate import PIN, frame_plan
import deforum_lab.image.resampling as spatial_warp

HERE, OUT = study.HERE, study.OUT
journey = study.journey
sha = journey.base.sha
CASES = ('usual-hold', 'low-hold')
FPS, CADENCE, FRAME_COUNT = 24, 12, 192
ANCHORS = tuple(range(0, FRAME_COUNT, CADENCE))
SIZE = (1536, 1024)
RAMP = [.4, .43952, .53376, .64624, .74048, .78, .7437037037, .6762962963, .64]
SIGMAS = [.6, .512844085693, .310901075602, 0.]
PHRASES = [
    {'start': 0, 'duration': 4.5, 'center': [.6, .47], 'zoom': .75,
     'turn': 32, 'radius': .8, 'travel': [-.10, .04]},
    {'start': 4, 'duration': 3.5, 'center': [.95, .48], 'zoom': .08,
     'turn': -14, 'radius': .85, 'travel': [.07, -.025]},
]
ARCHIVE_FILES = ('anchor.png', 'frames/0000.png', 'frame-hashes.json', 'workflow.api.json',
                 'workflow.executed.json', 'upload.json', 'history.json', 'submission.json',
                 'submit-response.json')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def pixels(path):
    with Image.open(path) as im:
        require(im.format == 'PNG' and im.mode == 'RGB' and im.size == SIZE,
                f'Expected {SIZE} RGB PNG: {path}')
        return np.array(im)


def inventory(folder, indices):
    expected = [f'{i:04d}.png' for i in indices]
    actual = sorted(p.name for p in folder.glob('*.png'))
    require(actual == expected, f'Incomplete or unexpected PNG inventory: {folder} '
            f'(found {len(actual)}, expected {len(expected)})')


def check_structure():
    original = read(HERE / 'transition-ramp-configs/higher-peak.json')
    snail = read(HERE / 'ten-dollar-configs/clock-pulse.json')['prompts'][1]['text']
    source = 'projects/modern-model-study/exports/ten-dollar-v001/clock-pulse/anchors/0084.png'
    require(study.CASES == CASES and journey.FPS == FPS and journey.base.SIGMAS == SIGMAS,
            'Runner cases, timebase, or native sigma schedule changed')
    require(spatial_warp.INTERPOLATION == cv2.INTER_LANCZOS4
            and spatial_warp.BORDER_MODE == cv2.BORDER_REFLECT_101
            and journey.base.remap_rgb is spatial_warp.remap_rgb, 'Spatial resampler changed')
    require(original['source'] == source and original['transition_ramp'] == RAMP,
            'Referenced source or transition ramp changed')
    prompts = [{'at': 0, 'name': 'brass-snail', 'prompt': snail},
               {'at': 2, 'name': 'shell-with-buildings', 'prompt': study.SHELL_BUILDINGS},
               {'at': 3, 'name': 'hollow-architectural-shell', 'prompt': study.HOLLOW_SHELL},
               {**original['scenes'][0], 'at': 4}]
    configs = {}
    for case in CASES:
        hold, ending = (.1, .1) if case == 'low-hold' else (.6, .64)
        noise = [{'at': 0, 'noise': hold}, {'at': 1.5, 'noise': hold},
                 *[{'at': 2 + i * .5, 'noise': n} for i, n in enumerate(RAMP)],
                 {'at': 6.5, 'noise': ending}, {'at': 8, 'noise': ending}]
        config = read(study.CONFIGS / f'{case}.json')
        require(config == {'case': case, 'seed': 773401, 'duration': 8., 'cadence': CADENCE,
                           'cfg': 1., 'source': source, 'scenes': prompts[:1],
                           'prompt_schedule': prompts, 'noise_schedule': noise, 'phrases': PHRASES},
                f'Config differs from approved matched experiment: {case}')
        for frame in ANCHORS[1:]:
            seconds = frame / FPS
            level = hold if seconds < 2 else ending if seconds >= 6.5 else RAMP[(frame - 48) // 12]
            scene, sigmas = journey.recipe(config, seconds)
            expected_scene = prompts[0 if seconds < 2 else 1 if seconds < 3 else 2 if seconds < 4 else 3]
            require(scene == expected_scene and sigmas == [s * level / .6 for s in SIGMAS],
                    f'Runtime prompt/noise recipe differs: {case}/{frame}')
        configs[case] = config
    shared = [{k: v for k, v in c.items() if k not in ('case', 'noise_schedule')}
              for c in configs.values()]
    require(shared[0] == shared[1], 'Cases differ outside the holding noise policy')
    source_hash = sha(journey.APP / source)
    require(sha(OUT / 'source/seed.png') == source_hash, 'Archived shared source differs')
    rgb = pixels(OUT / 'source/seed.png')
    require(max(p['start'] + p['duration'] for p in PHRASES) == 7.5, 'Motion ends after final anchor')
    # This runner uses dynamic_journey.warp with seconds, not the older warp_at_time adapters.
    require(not np.array_equal(journey.warp(rgb, 0., .5, PHRASES), rgb), 'Opening motion is a no-op')
    require(np.array_equal(journey.warp(rgb, 7.5, 8., PHRASES), rgb), 'Final half-second still moves')
    return configs, {'verified': True, 'scope': 'offline structure only; no generated job or film verified',
                    'configs_sha256': {c: sha(study.CONFIGS / f'{c}.json') for c in CASES},
                    'source_sha256': source_hash, 'expected_jobs': 30, 'anchors_per_case': list(ANCHORS),
                    'warp': 'dynamic_journey.warp(parent RGB, previous seconds, current seconds, phrases)',
                    'motion_ends_seconds': 7.5, 'frame_count': FRAME_COUNT, 'fps': FPS}


def validate_execution(requested, executed, upload, history, response, submission,
                       parent_hash, initialization_hash):
    """Adapt continuity_controls_review checks for a warped upload, keeping both hashes."""
    expected = copy.deepcopy(requested)
    require(upload.get('type') == 'input' and bool(upload.get('name')), 'Missing input upload')
    expected['20']['inputs']['image'] = '/'.join(filter(None, [upload.get('subfolder'), upload['name']]))
    require(executed == expected, 'Executed graph differs from uploaded requested graph')
    if 'sha256' in upload:
        require(upload['sha256'] == initialization_hash, 'Upload checksum differs from warped initialization')
    require(submission.get('parent_sha256') == parent_hash, 'Submission parent checksum differs')
    if 'initialization_sha256' in submission:
        require(submission['initialization_sha256'] == initialization_hash, 'Submission initialization differs')
    prompt_id = response.get('prompt_id')
    require(bool(prompt_id) and not response.get('node_errors'), 'Submission rejected or missing prompt id')
    require(submission.get('prompt_id') == prompt_id and submission.get('frames') == 1
            and bool(submission.get('collected_at')), 'Submission not collected or prompt id differs')
    status = history['status']
    require(status.get('completed') is True and status.get('status_str') == 'success', 'Unsuccessful history')
    require(history['prompt'][1] == prompt_id and history['prompt'][2] == executed,
            'History graph or prompt id differs')
    require('11' in history['prompt'][4], 'SaveImage missing from executed outputs')
    for event, payload in status.get('messages', []):
        require(event not in ('execution_error', 'execution_interrupted'), 'History contains execution failure')
        if 'prompt_id' in payload:
            require(payload['prompt_id'] == prompt_id, 'History event prompt id differs')
    images = history['outputs']['11']['images']
    require(len(images) == 1 and images[0].get('type') == 'output'
            and images[0]['filename'].endswith('.png'), 'Unexpected SaveImage output')
    return prompt_id, images[0]


def check_generation(configs):
    rows = []
    for case, config in configs.items():
        root = OUT / case
        require(read(root / 'config.json') == config, f'Archived config differs: {case}')
        inventory(root / 'anchors', ANCHORS)
        inventory(root / 'warped-inputs', ANCHORS[1:])
        require(sorted(p.name for p in root.glob('anchor-*.json')) ==
                [f'anchor-{f:04d}.json' for f in ANCHORS[1:]], f'Receipt inventory differs: {case}')
        source_hash = sha(OUT / 'source/seed.png')
        require(sha(root / 'anchors/0000.png') == source_hash, f'Shared opening differs: {case}')
        opening = read(root / 'opening.json')
        require(opening['source'] == config['source'] and opening['source_sha256'] == source_hash,
                f'Opening provenance differs: {case}')
        for frame in ANCHORS[1:]:
            context = f'{case}/{frame:04d}'
            receipt = root / f'anchor-{frame:04d}.json'
            rec = read(receipt)
            seconds, seed = frame / FPS, config['seed'] + frame // CADENCE
            scene, sigmas = journey.recipe(config, seconds)
            require(all(rec[k] == v for k, v in {'frame': frame, 'seconds': seconds, 'seed': seed,
                        'scene': scene['name'], 'sigmas': sigmas}.items()), f'{context}: receipt settings differ')
            run = (OUT / rec['run']).resolve()
            require(run.is_relative_to((OUT / 'runs').resolve()), f'{context}: run outside archive')
            parent, target = root / f'anchors/{frame-CADENCE:04d}.png', root / f'anchors/{frame:04d}.png'
            initialization = root / f'warped-inputs/{frame:04d}.png'
            parent_hash, init_hash, output_hash = sha(parent), sha(initialization), sha(target)
            require(parent_hash == rec['parent_sha256'], f'{context}: parent checksum differs')
            require(init_hash == rec['initialization_sha256'] == sha(run / 'anchor.png'),
                    f'{context}: warped initialization checksum differs')
            require(output_hash == rec['output_sha256'] == sha(run / 'frames/0000.png'),
                    f'{context}: output checksum differs')
            expected_warp = journey.warp(pixels(parent), (frame-CADENCE)/FPS, seconds, config['phrases'])
            require(np.array_equal(pixels(initialization), expected_warp), f'{context}: actual warp pixels differ')
            pixels(target)
            inventory(run / 'frames', [0])
            require(read(run / 'frame-hashes.json') == {'0000.png': output_hash}, f'{context}: frame hashes differ')
            requested = read(run / 'workflow.api.json')
            expected_graph = journey.base.repaint_graph(scene['prompt'], seed, sigmas)
            expected_graph['9']['inputs']['cfg'] = 1.
            expected_graph['11']['inputs']['filename_prefix'] = 'dynamic-journey/' + case
            require(requested == expected_graph, f'{context}: requested graph differs')
            # Explicit recipe constraints also catch changes in the shared graph factory.
            require(set(requested) == {'1', '2', '3', '4', '5', '9', '10', '11', '20', '24', '42', '43'}
                    and requested['1']['inputs']['unet_name'] == 'krea2_turbo_fp8_scaled.safetensors'
                    and requested['3']['inputs']['vae_name'] == 'qwen_image_vae.safetensors'
                    and requested['24'] == journey.base.node('VAEEncode', pixels=['20', 0], vae=['3', 0])
                    and requested['42']['inputs']['sampler_name'] == 'euler'
                    and requested['9']['class_type'] == 'SamplerCustom'
                    and requested['9']['inputs']['add_noise'] is True
                    and requested['9']['inputs']['noise_seed'] == seed
                    and requested['9']['inputs']['latent_image'] == ['24', 0], f'{context}: native recipe changed')
            submission = read(run / 'submission.json')
            require(all(submission[k] == v for k, v in {'frame': frame, 'seconds': seconds,
                        'scene': scene['name'], 'sigma_start': sigmas[0]}.items()), f'{context}: submission settings differ')
            upload, executed = read(run / 'upload.json'), read(run / 'workflow.executed.json')
            prompt_id, remote_image = validate_execution(requested, executed, upload, read(run / 'history.json'),
                read(run / 'submit-response.json'), submission, parent_hash, init_hash)
            with Image.open(target) as im:
                embedded = im.info.get('prompt')
            require(embedded is not None, f'{context}: PNG embedded graph missing')
            embedded_graph = json.loads(embedded)
            # ComfyUI LoadImage.IS_CHANGED hashes the input file; IsChangedCache
            # adds its one-item result list to the prompt serialized by SaveImage.
            # Validate that exact runtime addition, including the warped-input hash.
            require(embedded_graph['20'].get('is_changed') == [init_hash],
                    f'{context}: PNG LoadImage fingerprint differs from warped initialization')
            expected_embedded = copy.deepcopy(executed)
            expected_embedded['20']['is_changed'] = [init_hash]
            require(embedded_graph == expected_embedded,
                    f'{context}: PNG embedded graph differs beyond validated LoadImage fingerprint')
            rows.append({'case': case, 'frame': frame, 'run': rec['run'], 'prompt_id': prompt_id,
                         'parent_sha256': parent_hash, 'initialization_sha256': init_hash,
                         'output_sha256': output_hash, 'warp_pixels_verified': True,
                         'history_output': remote_image, 'png_graph_recorded': embedded is not None,
                         'png_loadimage_fingerprint_sha256': embedded_graph['20']['is_changed'][0],
                         'upload_checksum_recorded': 'sha256' in upload, 'receipt_sha256': sha(receipt),
                         'archive_sha256': {name: sha(run / name) for name in ARCHIVE_FILES}})
        final = pixels(root / 'anchors/0180.png')
        require(np.array_equal(journey.warp(final, 7.5, 8., config['phrases']), final), f'{case}: tail still moves')
    require(len(rows) == len({r['prompt_id'] for r in rows}) ==
            len({str((OUT / r['run']).resolve()) for r in rows}) == 30, 'Expected 30 distinct recurrent jobs')
    return {'verified': True, 'jobs': 30, 'anchors_per_case': 16,
            'png_loadimage_fingerprints_verified': len(rows),
            'upload_checksums_recorded': sum(r['upload_checksum_recorded'] for r in rows),
            'scope': 'Local archived inputs/outputs and recorded execution history; '
                     'HTTP upload acknowledgements may lack a remote input checksum.', 'rows': rows}


def check_rife(case, stage):
    root = OUT / case
    section = root / 'section-016'
    target = section / ('pair' if stage == 'pair' else 'rife')
    manifest = read(target / 'manifest.json')
    require(manifest['status'] == 'complete' and manifest['anchors_verified'] is True
            and manifest['source_hashes_and_mtimes_preserved'] is True, f'Incomplete RIFE: {case}/{stage}')
    require(manifest['mode'] == ('first_pair' if stage == 'pair' else 'full'), 'RIFE mode differs')
    for key, expected in {'source_fps': 2., 'output_fps': 24., 'multiplier': 12,
                          'timesteps': [f'{i}/12' for i in range(1, 12)], 'scale': 1.,
                          'scale_list': [16, 8, 4, 2, 1], 'scene_detection': False,
                          'static_frame_skipping': False, 'ensemble': False, 'fastmode': True}.items():
        require(manifest['settings'][key] == expected, f'RIFE setting differs: {case}/{key}')
    require(manifest['provenance']['model'] == 'RIFE 4.25'
            and manifest['provenance']['commit'] == PIN, 'RIFE implementation differs')
    require(len(manifest['sources']) == 16, 'RIFE source count differs')
    inventory(section / 'sources', range(16))
    for i, row in enumerate(manifest['sources']):
        source = section / f'sources/{i:04d}.png'
        require(Path(row['file']).resolve() == source.resolve() and row['size'] == list(SIZE)
                and row['mtime_ns'] == source.stat().st_mtime_ns
                and row['sha256'] == sha(source) == sha(root / f'anchors/{i*CADENCE:04d}.png'),
                f'RIFE source changed: {case}/{i}')
    holds = 0 if stage == 'pair' else 11
    plan = frame_plan(2 if stage == 'pair' else 16, final_holds=holds, multiplier=12)
    count = 13 if stage == 'pair' else FRAME_COUNT
    require(len(plan) == len(manifest['output_frames']) == count and manifest['final_holds'] == holds,
            f'RIFE frame count or tail differs: {case}/{stage}')
    inventory(target / 'frames', range(count))
    for i, (expected, row) in enumerate(zip(plan, manifest['output_frames'])):
        require(all(row.get(k) == v for k, v in expected.items()) and row['index'] == i
                and row['time_seconds'] == i / FPS and row['file'] == f'frames/{i:04d}.png',
                f'RIFE output plan differs: {case}/{stage}/{i}')
        frame = target / row['file']
        require(sha(frame) == row['sha256'], f'RIFE frame checksum differs: {frame}')
        pixels(frame)
        if expected['kind'] != 'interpolation':
            require(sha(root / f"anchors/{expected['source_index']*CADENCE:04d}.png") == row['sha256'],
                    f'RIFE anchor/hold not byte-identical: {case}/{i}')
    require(sha(target / 'preview.mp4') == manifest['video_sha256'], 'RIFE video checksum differs')
    if stage == 'full':
        pair = check_rife(case, 'pair')
        require(Path(manifest['validated_pair']).resolve() == (section / 'pair/manifest.json').resolve(),
                'Validated pair path differs')
        require(all(manifest[k] == pair[k] for k in ('sources', 'settings', 'provenance')),
                'Pair/full sources, settings or provenance differ')
    return manifest


def check_delivery():
    reports, manifests = [], []
    for case in CASES:
        manifest = check_rife(case, 'full')
        video = OUT / case / 'section-016/rife/preview.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(video), '-f', 'null', '-'],
                       check=True, capture_output=True, text=True, timeout=60)
        info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-count_frames', '-show_entries', 'stream=width,height,avg_frame_rate,r_frame_rate,duration,nb_read_frames',
            '-of', 'json', str(video)], text=True, timeout=60))['streams'][0]
        require((info['width'], info['height']) == SIZE and int(info['nb_read_frames']) == FRAME_COUNT
                and Fraction(info['r_frame_rate']) == FPS and Fraction(info['avg_frame_rate']) == FPS
                and abs(float(info['duration']) - 8.) < 1e-6, f'Delivery timing/dimensions differ: {case}')
        reports.append({'case': case, 'video': str(video), 'video_sha256': sha(video), 'probe': info,
                        'manifest_sha256': sha(video.parent / 'manifest.json'),
                        'anchors_retained_in_png_timeline': 16, 'rife_intermediate_frames': 165,
                        'final_hold_frames': 11, 'fully_decoded': True})
        manifests.append(manifest)
    require(all(manifests[0][k] == manifests[1][k] for k in ('settings', 'provenance')),
            'Finishing settings or implementation differ across cases')
    return {'verified': True, 'videos': reports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['structure', 'generation', 'delivery'])
    parser.add_argument('--details', action='store_true', help='Include all per-job archive hashes in stdout JSON')
    args = parser.parse_args()
    report = {'stage': args.stage, 'verified': False}
    try:
        configs, report['structure'] = check_structure()
        if args.stage != 'structure':
            generation = check_generation(configs)
            report['generation'] = generation if args.details else {k: v for k, v in generation.items() if k != 'rows'}
        if args.stage == 'delivery':
            report['delivery'] = check_delivery()
        report['verified'] = True
    except (OSError, ValueError, KeyError, TypeError, IndexError, subprocess.SubprocessError) as error:
        report['error'] = f'{type(error).__name__}: {error}'
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
