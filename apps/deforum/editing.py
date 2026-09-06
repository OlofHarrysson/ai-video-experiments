"""Explicit frame continuations and immutable, source-indexed cuts."""

import hashlib
import json
import shutil
import subprocess


def continuation(parent, frame, new_frames):
    receipt = json.loads((parent / 'submission.json').read_text())
    if not receipt.get('collected_at'):
        raise ValueError('Collect the parent run before branching')
    if not 0 <= frame < receipt['frames'] or not 1 <= new_frames <= 40:
        raise ValueError('Select an existing parent frame and 1–40 new frames')
    source = parent / 'frames' / f'{frame:04d}.png'
    graph = json.loads((parent / 'workflow.api.json').read_text())
    if graph['10']['class_type'] != 'DifforumFeedbackSampler':
        raise ValueError('Continuation requires a Difforum feedback parent')
    start = receipt.get('start_frame', 0) + frame
    end = start + new_frames + 1
    graph['7']['inputs']['max_frames'] = max(graph['7']['inputs']['max_frames'], end)
    graph.pop('4', None)
    graph.pop('5', None)
    graph['6'] = {'class_type': 'LoadImage', 'inputs': {'image': 'anchor.png'}}
    graph['10']['inputs'].update(init_image=['6', 0], start_frame=start, end_frame=end)
    lineage = {'parent_run': parent.name, 'parent_frame': frame,
               'parent_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'start_frame': start, 'end_frame': end, 'frames': new_frames + 1,
               'new_frames': new_frames, 'color_anchor': 'selected parent frame',
               'includes_anchor': True}
    return graph, source, lineage


def encode(frames, target, fps=8):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n',
                    '-framerate', str(fps), '-i', str(frames / '%04d.png'),
                    '-vf', 'fps=24', '-c:v', 'libx264', '-crf', '18',
                    '-pix_fmt', 'yuv420p', str(target)], check=True)


def assemble(project, version, ranges):
    """ranges: [{run, in, out}], all at 8 FPS, with exclusive out points."""
    project = project.resolve()
    export = project / 'exports' / version
    note = project / 'cuts' / f'{version}.md'
    if export.exists() or note.exists():
        raise FileExistsError('Cut versions are immutable; choose a new version')
    sources = []
    rows = []
    for part in ranges:
        run = (project / 'runs' / part['run']).resolve()
        if run.parent != (project / 'runs').resolve():
            raise ValueError('Source must be a run in this project')
        receipt = json.loads((run / 'submission.json').read_text())
        if not receipt.get('collected_at') or receipt['generated_fps'] != 8:
            raise ValueError('Cut sources must be collected 8 FPS runs')
        if not 0 <= part['in'] < part['out'] <= receipt['frames']:
            raise ValueError('Invalid half-open source range')
        for i in range(part['in'], part['out']):
            path = run / 'frames' / f'{i:04d}.png'
            if not path.is_file():
                raise FileNotFoundError(path)
            sources.append(path)
        rows.append(f'| {len(rows)+1} | runs/{run.name}/frames | 8 | {part["in"]} | {part["out"]} |')
    if not sources:
        raise ValueError('A cut needs at least one source frame')
    frames = export / 'frames'
    frames.mkdir(parents=True, exist_ok=False)
    hashes = []
    for i, source in enumerate(sources):
        target = frames / f'{i:04d}.png'
        shutil.copyfile(source, target)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Frame copy verification failed')
        hashes.append({'source': source.relative_to(project).as_posix(), 'sha256': digest})
    (export / 'cut.json').write_text(json.dumps({'version': version, 'fps': 8,
                                               'ranges': ranges, 'frames': hashes}, indent=2)+'\n')
    encode(frames, export / 'preview.mp4')
    note.write_text(f'# {version}\n\nWorking cut, {len(sources)} source frames at 8 FPS.\n\n'
                    '| Order | Source | FPS | In (inclusive) | Out (exclusive) |\n'
                    '| --- | --- | --- | --- | --- |\n'+'\n'.join(rows)+'\n\n'
                    f'[Preview](../exports/{version}/preview.mp4) · '
                    f'[Exact sources and hashes](../exports/{version}/cut.json)\n')
    return export
