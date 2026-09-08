"""Build labeled matched sampler comparisons and verify preserved frame provenance."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import samplers as experiment

OUT=experiment.OUT
NAMES={'baseline':'DPM++ 2M — current baseline','euler':'Euler — same settings','ancestral':'Euler ancestral — same settings'}
FONT=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',24)


def panel(name,frame):
    im=Image.open(OUT/name/f'cadence/frames/{frame:04d}.png').convert('RGB')
    result=Image.new('RGB',(1024,628),'#151923');result.paste(im,(0,52))
    ImageDraw.Draw(result).text((18,13),NAMES[name],font=FONT,fill='white')
    return result


def compare(left,right,slug):
    folder=OUT/slug/'frames';folder.mkdir(parents=True,exist_ok=False)
    for f in range(experiment.FRAMES):
        im=Image.new('RGB',(2048,628));im.paste(panel(left,f),(0,0));im.paste(panel(right,f),(1024,0))
        im.save(folder/f'{f:04d}.png')
    experiment.recipe.editing.encode(folder,OUT/f'{slug}.mp4',fps=experiment.FPS)


def verify():
    assert json.loads((OUT/'reference-probe.json').read_text())['pixel_equal']
    graphs=[]
    for name in NAMES:
        g=experiment.graph(name,3);g['6']['inputs']['sampler_name']='matched';g['11']['inputs']['filename_prefix']='matched';graphs.append(g)
        root=OUT/name
        for f in range(3,37,3):
            record=json.loads((root/f'anchor-{f:04d}.json').read_text())
            assert experiment.recipe.sha(root/f'anchors/{f:04d}.png')==record['sha256']
        for f in range(0,36,3):
            assert experiment.recipe.sha(root/f'anchors/{f:04d}.png')==experiment.recipe.sha(root/f'cadence/frames/{f:04d}.png')
        assert len(list((root/'cadence/frames').glob('*.png')))==36
    assert graphs[0]==graphs[1]==graphs[2]
    assert (OUT/'euler/warped-inputs/0003.png').read_bytes()==(OUT/'ancestral/warped-inputs/0003.png').read_bytes()
    experiment.seq.save(OUT/'validation.json',{'graphs_differ_only_in_sampler_and_output_prefix':True,
        'first_warped_inputs_byte_equal':True,'all_anchor_hashes_verified':True,'cadence_frames_per_variant':36})


if __name__=='__main__':
    verify()
    compare('baseline','euler','baseline-vs-euler')
    compare('euler','ancestral','euler-vs-ancestral')
    im=Image.new('RGB',(1536,3*334),'#151923')
    for row,name in enumerate(NAMES):
        for col,f in enumerate([0,15,33]):im.paste(panel(name,f).resize((512,314)),(col*512,row*334))
    im.save(OUT/'overview.jpg',quality=94)
    print('Sampler graph isolation, inputs and anchors verified; comparison videos and overview saved.')
