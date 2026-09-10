# /// script
# requires-python = ">=3.11"
# ///
"""Bundle the verified movie and editable native assets for handoff."""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--version',required=True)
args=p.parse_args();out=ROOT/'output'/args.version
archive=out/'a-little-brave-editable.zip'
assert not archive.exists()
delivery=json.loads((out/'delivery-check.json').read_text())
assert delivery['all_pngs_verified'] and delivery['full_decode_passed']
assert json.loads((out/'portability/packed-only-check.json').read_text())['reference_png_pixel_identical']
characters=ROOT/'output/characters-v001'
poses=ROOT/'output/poses-v001'
files={
    'A Little Brave.mp4':out/'a-little-brave.mp4',
    'A Little Brave.blend':out/'a-little-brave.blend',
    'Characters.blend':characters/'characters.blend',
    'Pose presets.blend':poses/'character-actions.blend',
    'Character assets/Biscuit.blend':characters/'biscuit-asset.blend',
    'Character assets/Bruno.blend':characters/'bruno-asset.blend',
    'Pose reference.jpg':poses/'contact-sheet.jpg',
    'Poster.png':out/'poster.png',
    'Original score.wav':ROOT/'assets/score-v001-master.wav',
    'Pose settings.json':poses/'presets.json',
}
for name in ['delivery-check.json','editability-check.json','attachment-check.json','continuity-check.json','native-frame-review.json']:
    files['Verification/'+name]=out/name
files['Verification/packed-only-check.json']=out/'portability/packed-only-check.json'
files['Verification/pose-presets-check.json']=poses/'reopened-check.json'
files['Verification/character-append-check.json']=characters/'roundtrip/check.json'
for path in sorted(ROOT.glob('*.py')):
    frozen=out/'source'/path.name
    files['Authoring source/'+path.name]=frozen if frozen.exists() else path
files['Authoring source/scripts/score.swift']=ROOT/'scripts/score.swift'
for name in ['BRIEF.md','PROMPTS.md','REVIEW.md']:
    files['Notes/'+name]=ROOT/name
readme='''A LITTLE BRAVE

Play "A Little Brave.mp4" for the 16-second film with music.

Open "A Little Brave.blend" in Blender 5.2.1 LTS for the editable film.
Its images, font and score are packed. Space plays the timeline; Numpad 0
shows the camera. The START HERE text inside the file explains the rig.

"Characters.blend" is an unanimated stage for freely posing the two dogs.
The individual collection files in "Character assets" can be appended to
another Blender scene. Enable viewport overlays, select a pose-controls
armature, and enter Pose Mode to see the animation controls.

"Pose presets.blend" contains eight single-frame native actions. Select
a character armature and choose its named preset in the Action Editor.
The action includes the eye and foreleg drawing switches. The pose
reference image shows all eight presets.

The dogs are painted side-view cutout rigs, not complete 3D models.
Bruno's HEAD bone has gaze_x and gaze_y properties. Both armatures have
closed_eyes and folded_forelegs properties. Artwork stays fixed;
Blender authors the movement. No image-to-video model is used.

The authoring source is retained for inspection. Full regeneration from
those scripts also uses the original workspace's preserved source rigs
and artwork; the packed Blender files can be opened directly.
'''
manifest={'version':args.version,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'files':{name:{'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
                   for name,path in files.items()}}
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as bundle:
    bundle.writestr('A Little Brave/START HERE.txt',readme)
    bundle.writestr('A Little Brave/Manifest.json',json.dumps(manifest,indent=2)+'\n')
    for name,path in files.items():bundle.write(path,'A Little Brave/'+name)
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    assert len(bundle.namelist())==len(files)+2
    for name,record in manifest['files'].items():
        assert hashlib.sha256(bundle.read('A Little Brave/'+name)).hexdigest()==record['sha256'],name
manifest['archive']={'name':archive.name,'bytes':archive.stat().st_size,
                     'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'crc_check_passed':True,
                     'all_entry_hashes_verified':True}
(out/'release-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest['archive'],indent=2))
