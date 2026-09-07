"""Build compact image-backed interaction and overview from verified local outputs."""
import base64
import io
import json
import math
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
ASSETS = PROJECT / 'references/assets/v001'
OUT = PROJECT / 'exports/v001'


def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', size)


def jpeg(path):
    with Image.open(path) as image:
        image = image.convert('RGB')
        image.thumbnail((640, 360))
        b = io.BytesIO()
        image.save(b, format='JPEG', quality=70, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def main(fragment):
    manifest = json.loads((ASSETS / 'manifest.json').read_text())
    paths = {p.stem: p for p in ASSETS.glob('*.png') if not p.stem.endswith('packed')}
    paths.update({p.stem: p for p in OUT.glob('*-repainted.png')})
    for name in ('marsh', 'portal'):
        for condition in ('original', 'adjacent', 'visible'):
            assert f'{name}-{condition}-repainted' in paths
    data = {'pairs': manifest['pairs'], 'images': {key: jpeg(path) for key,path in paths.items()}}
    template = (HERE / 'walkthrough-fragment.html').read_text()
    html = template.replace('__MOTION_GUIDE_DATA__', json.dumps(data, separators=(',', ':')))
    assert len(html.encode()) < 1_000_000
    fragment.parent.mkdir(parents=True, exist_ok=True)
    fragment.write_text(html)
    # Scientific contact sheets use fixed colors independently of the inline UI.
    with Image.open(ASSETS / 'guide-72.png') as im:
        field = im.convert('RGB')
    pen = ImageDraw.Draw(field)
    for x,y,dx,dy in manifest['pairs']['visible']['vectors']:
        if (x-16)%64 or (y-16)%64:
            continue
        ex,ey=x+dx*.8*2,y+dy*.8*2
        angle=math.atan2(ey-y,ex-x)
        pen.line([(x,y),(ex,ey)], fill='#111111', width=5)
        pen.line([(x,y),(ex,ey)], fill='#ffc570', width=2)
        pen.polygon([(ex,ey),(ex-7*math.cos(angle-.5),ey-7*math.sin(angle-.5)),
                     (ex-7*math.cos(angle+.5),ey-7*math.sin(angle+.5))],fill='#ffc570')
    field.save(OUT / 'flow-visible.png')
    paths['flow-visible'] = OUT / 'flow-visible.png'
    for name in ('marsh', 'portal'):
        sheet = Image.new('RGB', (1536, 668), '#101719')
        draw = ImageDraw.Draw(sheet)
        entries = [('guide-72', '1  Guide A', '6.000 seconds'),
                   ('guide-84', '2  Guide B', '7.000 seconds — teaching gap'),
                   ('flow-visible', '3  Estimated movement', 'Arrow lengths x2 for visibility only'),
                   (f'{name}-original', '4  Original artwork', 'Compare its shape with the next panel'),
                   (f'{name}-visible-warped', '5  Pixels moved', 'Optical-flow warp only — no diffusion'),
                   (f'{name}-visible-repainted', '6  SDXL repaint', 'Real ComfyUI img2img output')]
        for i,(key,title,sub) in enumerate(entries):
            x,y=(i%3)*512,(i//3)*334
            with Image.open(paths[key]) as im:
                sheet.paste(im.convert('RGB').resize((512,288),Image.Resampling.LANCZOS),(x,y+46))
            draw.text((x+12,y+4),title,font=font(19),fill='white')
            draw.text((x+12,y+26),sub,font=font(14),fill='#bfcccc')
        sheet.save(OUT / f'{name}-walkthrough.jpg',quality=92)
    print(f'Wrote {fragment} ({len(html.encode())} bytes) and both overview sheets.')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
