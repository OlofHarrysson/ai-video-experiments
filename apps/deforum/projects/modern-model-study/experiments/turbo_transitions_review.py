"""Validate generated feedback and build the one/two/three-tail comparison."""
import copy,json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import turbo_transitions as t
from cathedral_review import assert_warp_matches

def main():
    rows=[]
    schedules=json.loads((t.a.APP/'work/turbo-transition-session/unpacked/receipts/schedules.json').read_text())
    for tail in (1,2,3):
        sigmas=schedules['tails'][str(tail)]
        assert sigmas==schedules['full'][8-tail:] and len(sigmas)==tail+1
        root=t.OUT/f'tail-{tail}';start,count=(0,t.FRAMES) if tail==1 else (t.BRANCH_START,t.BRANCH_FRAMES)
        assert t.a.sha(root/f'anchors/{start:04d}.png')==t.a.sha(t.initial(tail))
        for f in range(start+3,start+count,3):
            record=json.loads((root/f'anchor-{f:04d}.json').read_text());run=t.a.PROJECT/record['run']
            prior=root/f'anchors/{f-3:04d}.png';source=root/f'warped-inputs/{f:04d}.png';output=root/f'anchors/{f:04d}.png'
            assert t.a.sha(prior)==record['parent_sha256']
            assert t.a.sha(source)==record['initialization_sha256']==t.a.sha(run/'anchor.png')
            assert t.a.sha(output)==record['output_sha256']==t.a.sha(run/'frames/0000.png')
            requested=json.loads((run/'workflow.api.json').read_text());assert requested==t.graph(tail,t.SEED+f//3)
            executed=json.loads((run/'workflow.executed.json').read_text());normalized=copy.deepcopy(executed)
            normalized['20']['inputs']['image']='anchor.png';assert normalized==requested
            assert executed['9']['inputs']['latent_image']==['24',0]
            assert Image.open(output).size==(t.WIDTH,t.HEIGHT)
            if f in (3,39,60,69,117):
                rebuilt=t.warp(np.asarray(Image.open(prior).convert('RGB')),f-3,f)
                assert_warp_matches(rebuilt,np.asarray(Image.open(source).convert('RGB')))
            hist=json.loads((run/'history.json').read_text());assert hist['status']['completed'] and hist['status']['status_str']=='success'
            events={k:v for k,v in hist['status']['messages']}
            rows.append({'tail':tail,'frame':f,'seconds':(events['execution_success']['timestamp']-events['execution_start']['timestamp'])/1000})
        hashes=json.loads((root/'frame-hashes.json').read_text());assert len(hashes)==count
        for name,digest in hashes.items():assert t.a.sha(root/'frames'/name)==digest
        for local in (0,23,24,25,count-1):
            f=start+local;anchor=f//3*3
            expected=t.warp(np.asarray(Image.open(root/f'anchors/{anchor:04d}.png').convert('RGB')),anchor,f)
            assert_warp_matches(expected,np.asarray(Image.open(root/f'frames/{local:04d}.png').convert('RGB')))
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(root/'preview.mp4')]))['streams'][0]
        assert int(info['nb_frames'])==count*2 and info['r_frame_rate']=='24/1'
    assert len(rows)==61
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',19)
    for local in range(t.BRANCH_FRAMES):
        canvas=Image.new('RGB',(1536,384),'#15191d');draw=ImageDraw.Draw(canvas)
        for j,tail in enumerate((1,2,3)):
            frame=local+t.BRANCH_START if tail==1 else local
            im=Image.open(t.OUT/f'tail-{tail}/frames/{frame:04d}.png').convert('RGB')
            canvas.paste(im.resize((512,342),Image.Resampling.LANCZOS),(j*512,42))
            draw.text((j*512+12,10),f'{tail} final step'+('s' if tail>1 else '')+f' | noise {schedules["tails"][str(tail)][0]:.3f}',font=font,fill='white')
        t.a.image(t.OUT/f'comparison/frames/{local:04d}.png',np.asarray(canvas))
    target=t.OUT/'comparison/preview.mp4'
    if not target.exists():t.a.editing.encode(target.parent/'frames',target,fps=t.FPS)
    t.a.save(t.OUT/'verification.json',{'verified':True,'repaints':len(rows),'results':rows,'schedules':schedules,
        'checks':'all graphs, parent/input/output and frame hashes; sampled warps, cadence boundaries, branch start, frame counts'})
    print('Verified 61 repaints, ten-second shot, both branches, native schedule tails and comparison')

if __name__=='__main__':main()
