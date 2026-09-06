"""Assemble complete redraw batches and export immutable five-second comparisons."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageDraw

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT.parents[1]))
import editing


def main():
    phases = {'guide': [], 'feedback': [], 'redraw': []}
    for path in sorted((PROJECT / 'runs').glob('*/submission.json')):
        receipt = json.loads(path.read_text())
        if receipt.get('phase') in phases and receipt.get('collected_at'):
            phases[receipt['phase']].append((path.parent, receipt))
    if [len(phases[k]) for k in phases] != [1, 1, 5]:
        raise ValueError('Select one guide, one feedback and five collected redraw batches; ambiguous runs need review')
    guide = phases['guide'][0][0]
    feedback = phases['feedback'][0][0]
    redraws = sorted(phases['redraw'], key=lambda item: item[1]['start_frame'])
    if [r['start_frame'] for _, r in redraws] != [0, 8, 16, 24, 32]:
        raise ValueError('Missing or repeated redraw positions')
    reference = json.loads((PROJECT / 'references/assets/seedream-v001/reference.json').read_text())
    for rows in phases.values():
        for _, r in rows:
            if r['anchor_sha256'] != reference['anchor_sha256'] or r['camera_step'] != .012:
                raise ValueError('Comparison inputs or camera differ')
    for run, receipt in redraws:
        if receipt['guide_run'] != guide.name:
            raise ValueError('Redraw comes from a different guide')
        for row in receipt['frame_map']:
            source = guide / 'frames' / f"{row['global_frame']:04d}.png"
            if hashlib.sha256(source.read_bytes()).hexdigest() != row['guide_sha256']:
                raise ValueError('Guide source changed')
    anchor = Image.open(PROJECT / 'references/assets/seedream-v001/anchor.png').tobytes()
    for run in (guide, feedback, redraws[0][0]):
        with Image.open(run / 'frames/0000.png') as im:
            if im.tobytes() != anchor:
                raise ValueError('First frame differs from the original anchor')
    feedback_export = editing.assemble(PROJECT, 'v001-feedback', [
        {'run': feedback.name, 'in': 0, 'out': 40}])
    redraw_export = editing.assemble(PROJECT, 'v001-redraw', [
        {'run': run.name, 'in': 0, 'out': 8} for run, _ in redraws])
    target = PROJECT / 'exports/v001-comparison'
    target.mkdir(exist_ok=False)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n',
        '-i', str(feedback_export / 'preview.mp4'), '-i', str(redraw_export / 'preview.mp4'),
        '-filter_complex', '[0:v]scale=960:540[a];[1:v]scale=960:540[b];[a][b]hstack[out]',
        '-map', '[out]', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
        str(target / 'feedback-left-redraw-right.mp4')], check=True)
    sheet = Image.new('RGB', (1280, 4 * 386), '#161920')
    draw = ImageDraw.Draw(sheet)
    for row, frame in enumerate((0, 13, 26, 39)):
        for col, (name, export) in enumerate((('Feedback', feedback_export), ('Redraw', redraw_export))):
            draw.text((col*640+8, row*386+6), f'{name} / frame {frame}', fill='white')
            with Image.open(export / 'frames' / f'{frame:04d}.png') as im:
                sheet.paste(im.resize((640, 360)), (col*640, row*386+26))
    sheet.save(target / 'contact.jpg', quality=92)
    (target / 'comparison.json').write_text(json.dumps({
        'guide_run': guide.name, 'feedback_run': feedback.name,
        'redraw_runs': [p.name for p, _ in redraws], 'anchor_pixels_equal': True,
        'generated_fps': 8, 'frames': 40, 'duration_seconds': 5,
        'feedback_export': str(feedback_export.relative_to(PROJECT)),
        'redraw_export': str(redraw_export.relative_to(PROJECT))}, indent=2)+'\n')
    print(target)


if __name__ == '__main__':
    main()
