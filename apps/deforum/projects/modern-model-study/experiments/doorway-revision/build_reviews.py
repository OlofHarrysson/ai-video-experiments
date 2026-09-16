"""Compare the doorway revision with the preserved original and retain trials."""
import sys
from run import lab

sys.path.insert(0,str(lab.APP))
from media_review import build

COMMON=('Recurrent Krea Turbo, CFG1, three Euler intervals. Every new painting '
        'starts from the warped previous painting encoded into latent space. '
        'Source: 24 fps, one repaint each half-second. Delivery: 1.5× faster, '
        '24 fps, three paintings per displayed second. RIFE 4.25 scale 1 runs '
        'outside the feedback loop; the final seven frames use actual spatial '
        'warps. All original paintings and earlier attempts are preserved.')
DESCRIPTIONS={
 'd1-doorway-approach':('Doorway approach','Recenter → earlier push → forest glimpse',
   'Preserves the first nine seconds of the previous film. Measures the existing '
   'doorway, overlaps a recentering pan and push, and keeps a readable open arch '
   'while a golden harp and forest appear beyond it. This stops before crossing.'),
 'd2-through-the-door':('First crossing','Doorway → close harp forest',
   'A measured push enters the opening. The new forest and red train appear, '
   'but the nearest harp and remaining pale margins crowd the result.'),
 'd3-the-music-beyond':('Crowded continuation — rejected','Lateral follow → repeated foreground shapes',
   'Tries to clear the doorway and follow the train sideways. The generated train '
   'changes position, and the ending develops repeated shapes that obscure it. '
   'Preserved as a failed attempt, not a recommended film.'),
 'd4-the-open-glade':('Meadow revision','Harp forest → meadow, with an obstructing wall',
   'Rewinds to source second 22. Gentler motion, a temporary noise rise to 0.80 '
   'and descriptions of a spacious meadow open a new landscape. A large red '
   'wall or curtain still occupies much of the right side.'),
 'd5-beyond-the-threshold':('Beyond the Threshold — revised film','Whale railway → doorway → music forest → meadow',
   'Branches before the clock dominates. Reframes and approaches the actual '
   'doorway, introduces a different world beyond it, then aims through a measured '
   'gap between the near harp and red wall toward the train and meadow. '
   'The opening matches the original through nine seconds; later passages have '
   'different timing and imagery, so this is an artistic revision rather than '
   'a controlled test of one setting.'),
}

def clip(case):
    label,note,details=DESCRIPTIONS[case]
    return dict(id=case,label=label,note=note,details=details+'\n\n'+COMMON,
        source=str((lab.OUT/case/'faster/rife-moving-tail/preview.mp4').relative_to(lab.APP)))

def main():
    new=clip('d5-beyond-the-threshold')
    old=dict(id='original',label='The Open Dream — previous film',
        note='Whale railway → clock doorway → ocean of whales',
        details='The previously liked film. Its late doorway becomes a clock and '
        'reveals another whale/train environment. Preserved unchanged for comparison.\n\n'+COMMON,
        source='projects/modern-model-study/exports/storytelling-lab-v001/i5-the-open-dream/through-0684/rife-moving-tail/preview.mp4')
    pages=[('doorway','Through the doorway — revision and original',[new,old]),
        ('doorway-attempts','Doorway revisions — preserved attempts',
         [clip(c) for c in ['d3-the-music-beyond','d4-the-open-glade','d5-beyond-the-threshold','d2-through-the-door','d1-doorway-approach']])]
    for name,title,clips in pages:
        session=lab.APP/f'media_review/sessions/{name}.json'
        lab.save(session,dict(title=title,selected=[c['id'] for c in clips[:2]],clips=clips))
        print(build(session,lab.OUT.parent/f'media-review-{name}-v001')['full_quality'])

if __name__=='__main__':main()
