"""Small story comparisons with every preserved attempt available by name."""
import sys
from run import lab

sys.path.insert(0, str(lab.APP))
from media_review import build

COMMON = ('Recurrent Krea Turbo: each painting uses the warped previous painting, '
          'text and recorded independent noise. CFG1 and three Euler intervals. '
          'Continuous Lanczos spatial motion; RIFE 4.25 scale 1. Source: 24 fps '
          'and one repaint every half-second. Delivery: 1.5× faster at 24 fps, '
          'three paintings per displayed second. Original paintings and complete versions are retained. '
          'The last seven frames continue spatial warping. No audio.')

DESCRIPTIONS = {
 'p1-captive-light': ('Captive Light — original plan', 'Cage → free wings → growing forest',
   'The whole story was written before generation: liberation becoming renewal. '
   'The golden bird and cage-shaped tree provide a clear visual link. Its actual '
   'exit is ambiguous, and the final forest is less extensive than intended.'),
 'p2-the-open-door': ('Captive Light — revised', 'An earlier open door; more birds and branches',
   'Rewinds to the same 2.5-second source painting and makes the door/threshold '
   'descriptions more explicit, with an earlier noise rise. The door opens sooner, '
   'but extra birds complicate the identity of the original captive. Motion is unchanged.'),
 'p3-release-direct': ('Release probe — 0.78', 'Can the bird leave the cage?',
   'A short preserved-prefix test describes one bird to the right of an empty cage. '
   'The model adds a second bird instead of relocating the original.'),
 'p4-release-stronger': ('Release probe — 0.86', 'More repaint freedom; still an extra bird',
   'Same source painting, prompts, seeds, motion and timing as the 0.78 probe. '
   'Only the first four new starting-noise values rise to 0.86. The door and wings '
   'change more, but the requested single-bird departure still fails.'),
 'i1-whale-station': ('Whale Station — opening', 'A whale, a train and a red moon',
   'Only this opening was planned. The next scene was chosen after inspecting '
   'the whale’s nose pointing toward the moon.'),
 'i2-bridge-to-the-moon': ('Bridge to the Moon', 'Whale → ivory railway → clock doorway',
   'Improvised from the opening: the whale’s back becomes a railway viaduct '
   'toward the moon. The small station clock returns as the giant destination. '
   'Literal train travel remains less clear than the changing world.'),
 'i3-the-whales-dream': ('The Whale’s Dream — clock ending', 'Sleeping whale → clock → ocean of whales',
   'The whale’s closed eye suggested a dream. The clock becomes a doorway '
   'onto whales and water. The ending remains enclosed in monumental clockwork.'),
 'i4-through-the-clock': ('Through the Clock', 'A railway journey into the whale’s dream',
   'Branches from the actual small ocean doorway in The Whale’s Dream. A focused '
   'push and new scene descriptions try to pass beyond its rim. The doorway '
   'drifts toward the lower-left corner, so this ending misses its framing goal.'),
 'i5-the-open-dream': ('The Open Dream', 'Whale railway → clock doorway → open ocean',
   'Rewinds to the visible ocean window. Its measured position guides a new '
   'spatial push, checked first without diffusion. The story grows from what '
   'the model actually painted; the red train and whale motif link its worlds. '
   'This complete version retains the crowded, distorted final paintings.'),
 'i5-the-open-dream-edit': ('The Open Dream — selected ending', 'Whale railway → clock doorway → open ocean',
   'The improvised story ends at the clearer ocean reveal, before the last '
   'six crowded paintings. All generated paintings remain in the complete '
   'version. A measured spatial push into the actual window improves the reveal '
   'and retains a red train on the far bridge. Literal train travel is still ambiguous.'),
 'h1-lantern-harbour': ('A Light Seeks Shelter — opening', 'Lantern boat → sheltering shell',
   'Hybrid approach: keep the intention of finding refuge, but adapt the route. '
   'The wave becomes shelter around the boat rather than the boat entering '
   'the originally distant shell.'),
 'h2-a-light-for-others': ('A Light for Others — wide route', 'Boat → beacon → arriving boats',
   'Keeps the surprising shelter and turns the lantern boat into a lighthouse '
   'for others. The wider motion exposes a distracting reflected foreground.'),
 'h3-follow-the-beacon': ('Follow the Beacon — closer route', 'Same story; more attention on the red beacon',
   'Same prompts, noise, seeds and timing as the wide route after the preserved '
   'opening. A closer spatial path keeps the beacon more central. A gray '
   'foreground still intrudes, so framing has not solved that artifact.'),
 'h4-a-sky-of-lanterns': ('A Sky of Lanterns', 'One vulnerable light becomes many lights',
   'Continues the observed lighthouse and smaller lantern boats. The proposed '
   'ending carries their shared light upward into a constellation, retaining '
   'the original red and gold motif.'),
}

def clip(case):
    label,note,details=DESCRIPTIONS[case]
    path=(lab.OUT/'i5-the-open-dream/through-0684/rife-moving-tail/preview.mp4'
          if case=='i5-the-open-dream-edit' else lab.OUT/case/'faster/rife-moving-tail/preview.mp4')
    return dict(id=case,label=label,note=note,details=details+'\n\n'+COMMON,
                source=str(path.relative_to(lab.APP)))

def main():
    pages=[
      ('storytelling','Surreal stories — three approaches',
       ['i5-the-open-dream-edit','h4-a-sky-of-lanterns','p1-captive-light'],2),
      ('storytelling-planned','A prewritten story, then a revision',
       ['p1-captive-light','p2-the-open-door'],2),
      ('storytelling-improvised','Follow the paintings — two endings',
       ['i5-the-open-dream-edit','i3-the-whales-dream','i5-the-open-dream','i4-through-the-clock','i2-bridge-to-the-moon','i1-whale-station'],2),
      ('storytelling-hybrid','Keep the meaning, adapt the route',
       ['h4-a-sky-of-lanterns','h3-follow-the-beacon','h2-a-light-for-others','h1-lantern-harbour'],2),
      ('storytelling-release','An action that resisted direction',
       ['p3-release-direct','p4-release-stronger'],2),
    ]
    for name,title,cases,selected in pages:
        session=lab.APP/f'media_review/sessions/{name}.json'
        lab.save(session,dict(title=title,selected=cases[:selected],clips=[clip(c) for c in cases]))
        print(build(session,lab.OUT.parent/f'media-review-{name}-v001')['full_quality'])

if __name__=='__main__':main()
