"""Verify archived feedback lineage and make synchronized, labeled comparisons."""
import json
import copy
from PIL import Image, ImageDraw, ImageFont
import additive_reference as s


def verify(model):
    receipts=[]
    for label in ('baseline','reference'):
        root=s.OUT/model/label
        for f in range(3,s.FRAMES,3):
            record=json.loads((root/f'anchor-{f:04d}.json').read_text())
            run=s.a.PROJECT/record['run']
            actual=json.loads((run/'workflow.executed.json').read_text())
            receipt=json.loads((run/'submission.json').read_text())
            requested=json.loads((run/'workflow.api.json').read_text())
            assert requested==s.graph(model,s.a.PROMPTS[model],s.a.SEED+f//3,reference=label=='reference')
            normalized=copy.deepcopy(actual)
            for node in ('20','30'):
                if node in normalized:normalized[node]['inputs']['image']=requested[node]['inputs']['image']
            assert normalized==requested
            assert receipt.get('collected_at') and receipt.get('prompt_id')
            assert actual['9']['inputs']['latent_image']==['24',0]
            assert actual['24']['inputs']['pixels']==['20',0] and '6' not in actual
            prior=root/f'anchors/{f-3:04d}.png'
            warped=root/f'warped-inputs/{f:04d}.png'
            expected=s.warp(s.np.asarray(Image.open(prior).convert('RGB')),f-3,f)
            assert s.np.array_equal(s.np.asarray(Image.open(warped)),expected)
            assert s.a.sha(warped)==s.a.sha(run/'anchor.png')==record['initialization_sha256']==receipt['source_sha256']
            assert s.a.sha(run/'frames/0000.png')==s.a.sha(root/f'anchors/{f:04d}.png')==record['sha256']
            if label=='reference':
                assert s.a.sha(prior)==s.a.sha(run/'reference.png')==record['reference_sha256']==receipt['reference_sha256']
                assert actual['20']['inputs']['image']!=actual['30']['inputs']['image']
                if model=='klein': assert actual['7']['inputs']['positive']==['32',0]
                else: assert actual['21']['inputs']['image1']==['30',0]
            else:
                assert '30' not in actual and receipt['reference_sha256'] is None
            receipts.append(receipt['prompt_id'])
        for f in range(s.FRAMES):
            anchor=f//s.CADENCE*s.CADENCE
            expected=s.warp(s.np.asarray(Image.open(root/f'anchors/{anchor:04d}.png').convert('RGB')),anchor,f)
            assert s.np.array_equal(s.np.asarray(Image.open(root/f'frames/{f:04d}.png')),expected)
    assert len(set(receipts))==14
    assert s.a.sha(s.OUT/model/'baseline/warped-inputs/0003.png')==s.a.sha(s.OUT/model/'reference/warped-inputs/0003.png')
    s.a.save(s.OUT/model/'lineage-verification.json',{'generated_feedback_anchors':14,
        'checks':['executed graph equals declared recipe apart from uploaded filenames','first feedback pair uses byte-identical warped input',
                  'every sampler initialized from warped own previous output','separate reference equals unwarped own previous output',
                  'generated pixels and input SHA-256 match archives','intermediate pixels equal warp only, with no blend'],
        'prompt_ids':receipts})


def compare(model):
    target=s.OUT/'comparisons'/model
    roots=[s.OUT/model/x for x in ('baseline','reference')]
    labels=['Feedback + text','Same feedback + text + reference']
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',19)
    for f in range(s.FRAMES):
        canvas=Image.new('RGB',(1024,322),'#111722');draw=ImageDraw.Draw(canvas)
        for col,root in enumerate(roots):
            with Image.open(root/f'frames/{f:04d}.png') as img:
                canvas.paste(img.convert('RGB').resize((512,288),Image.Resampling.LANCZOS),(col*512,34))
            draw.text((col*512+12,7),labels[col],font=font,fill='white')
        s.a.image(target/f'frames/{f:04d}.png',s.np.asarray(canvas))
    s.a.save(target/'manifest.json',{'sources':[str(r.relative_to(s.a.PROJECT)) for r in roots],
        'source_manifest_hashes':[s.a.sha(r/'manifest.json') for r in roots],
        'labels':labels,'source_fps':s.FPS,'frames':s.FRAMES,'method':'synchronized side by side; no interpolation'})
    if not (target/'preview.mp4').exists():s.a.editing.encode(target/'frames',target/'preview.mp4',fps=s.FPS)
    print(target/'preview.mp4')


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('model',choices=('klein','krea'))
    model=p.parse_args().model
    verify(model);compare(model)
