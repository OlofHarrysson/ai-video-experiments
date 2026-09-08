"""Labeled comparisons from existing frames; no interpolation or blending."""
from PIL import Image, ImageDraw, ImageFont
import conditioning as c


def compare(name, left, right, labels):
    target=c.OUT/'comparisons'/name
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',19)
    for f in range(c.FRAMES):
        canvas=Image.new('RGB',(1024,322),'#111722')
        draw=ImageDraw.Draw(canvas)
        for col,root in enumerate((left,right)):
            img=Image.open(root/f'frames/{f:04d}.png').convert('RGB')
            canvas.paste(img.resize((512,288),Image.Resampling.LANCZOS),(col*512,34))
            draw.text((col*512+12,7),labels[col],font=font,fill='white')
        c.a.image(target/f'frames/{f:04d}.png',c.np.asarray(canvas))
    c.a.save(target/'manifest.json',{'left':str(left.relative_to(c.a.PROJECT)),
        'right':str(right.relative_to(c.a.PROJECT)),'labels':labels,'fps':c.FPS,
        'source_manifest_hashes':[c.a.sha(p/'manifest.json') for p in (left,right)],
        'method':'resize and place side by side; synchronized source frames'})
    if not (target/'preview.mp4').exists():
        c.a.editing.encode(target/'frames',target/'preview.mp4',fps=c.FPS)
    print(target/'preview.mp4')


if __name__=='__main__':
    for model in ('klein','krea'):
        compare(model,c.OUT/model/'text',c.OUT/model/'reference',
            ['Text only','Text + warped reference'])
    compare('klein-wording',c.OUT/'klein/reference',c.OUT/'klein/preserve',
        ['Reference + scene description','Reference + preserve instruction'])
