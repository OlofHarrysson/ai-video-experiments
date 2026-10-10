"""Rebuild v011 from generated original assets and verified public drum sources."""
import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True, help='Fresh output directory; existing paths are never overwritten')
SANDBOX = parser.parse_args().out.resolve()
PROJECT = SANDBOX / 'pressure-study'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args):
    subprocess.run(['uv', 'run', '--locked', 'python', *map(str, args)], cwd=APP, check=True)


if SANDBOX.exists():
    raise FileExistsError(SANDBOX)
(PROJECT / 'modules').mkdir(parents=True)
(PROJECT / 'references').mkdir()
for path in (ROOT / 'modules').glob('*-v011.strudel'):
    shutil.copyfile(path, PROJECT / 'modules' / path.name)
shutil.copyfile(ROOT / 'assembly-v011.json', PROJECT / 'assembly-v011.json')
for script in ['make_palette.py', 'make_damped_morph.py']:
    shutil.copyfile(ROOT / script, PROJECT / script)
    run(PROJECT / script)

samples = []
for receipt_name in ['palette.json', 'damped-morph.json']:
    receipt = json.loads((PROJECT / 'references' / receipt_name).read_text())
    original = json.loads((ROOT / 'references' / receipt_name).read_text())
    expected = {item['path']: item['sha256'] for item in original['sounds']}
    for sound in receipt['sounds']:
        path = PROJECT / sound['path']
        actual = digest(path)
        assert actual == expected[sound['path']], sound['path']
        samples.append({'path': sound['path'], 'sha256': actual, 'regenerated_matches_original': True})

source_receipt = json.loads((APP / 'projects/practical-dogfood/drum-sources.json').read_text())
downloads = []
for source in source_receipt['samples']:
    relative = Path(source['path']).relative_to('projects')
    destination = SANDBOX / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(urllib.parse.quote(source['source'], safe=':/%?=&'), timeout=60) as response:
        destination.write_bytes(response.read())
    actual = digest(destination)
    assert actual == source['sha256'], source['source']
    downloads.append({'url': source['source'], 'sha256': actual, 'download_matches_retained_original': True})

run(APP / 'music.py', 'assemble', PROJECT / 'assembly-v011.json', '--out', PROJECT / 'assemblies/v011')
assert (PROJECT / 'assemblies/v011/source.strudel').read_bytes() == (ROOT / 'assemblies/v011/source.strudel').read_bytes()
run(APP / 'music.py', 'render-project', PROJECT / 'assemblies/v011/project.json', '--revision', 'v011', '--out', PROJECT / 'renders/v011', '--timeout', '180')
(ROOT / 'references/fresh-rebuild-v011.json').write_text(json.dumps({'project': str(PROJECT), 'source_sha256': digest(PROJECT / 'assemblies/v011/source.strudel'), 'source_matches_original': True, 'generated_samples': samples, 'downloaded_drums': downloads, 'master_sha256': digest(PROJECT / 'renders/v011/master/render.wav')}, indent=2) + '\n')
