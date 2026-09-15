"""A continuation chosen after the small ocean doorway appears in I3."""
from branch import freeze
from run import lab

base = lab.read(lab.HERE / 'configs/i3-the-whales-dream.json')
lab.save(lab.OUT / 'i3-the-whales-dream/config.json', base)
style = ' A finely detailed surrealist oil painting, luminous ivory and turquoise water, crimson enamel and gold, strong readable silhouettes, dimensional shading, deep velvet shadows and sharp highlights.'
stages = [
 (20, 'the-open-water-door', 'A wide open circular doorway occupies the lower center of a monumental antique clock. Its thin crimson rim surrounds a bright turquoise ocean beneath a golden sunrise. An ivory whale floats above the water inside the doorway. A narrow ivory railway and tiny red train reach the bottom edge of the opening. The surrounding black and gold clock mechanism is cropped far outside the view.'),
 (22, 'beyond-the-rim', 'We are passing through a broad open crimson arch into a luminous turquoise ocean. The last curved red rim recedes at the outer edges. A large graceful ivory whale floats above the water near the center, its dark eye calm and distinct. Two smaller ivory whales float farther away. A thin ivory railway carrying a tiny red train follows the left horizon. A round golden sun hangs in spacious pale sky.'),
 (24, 'morning-without-clocks', 'An expansive turquoise sea at golden dawn, with three ivory whales floating freely above it. One large ivory whale near the center has a warm light on its back and a calm dark eye. Smaller whales travel in the distance. A tiny red train crosses a distant thin ivory bridge at the far left. Soft golden sunbeams fall through open pale sky. Dark teal waves and dimensional ivory shading. A spacious open landscape.'),
]
phrases = [p for p in base['phrases'] if p['start'] < 19.5]
phrases += [
 dict(start=19.5, duration=7, zoom=1.1, turn=9, travel=[-.1,-.12], center=[.88,.72], radius=3.5),
 dict(start=24, duration=9, zoom=-.16, turn=-13, travel=[.08,.02], center=[.75,.5], radius=3.5),
 dict(kind='wave', start=21, duration=10, amplitude=.028, wavelength=1.7, cycles=.5, axis='vertical'),
]
values=[.64,.70,.76,.78,.76,.70,.66,.72,.78,.76,.68,.62,.54,.46,.38,.32]
freeze('i3-the-whales-dream', 'i4-through-the-clock', 468, 28,
       [dict(at=t,name=n,prompt=p+style) for t,n,p in stages],
       [dict(at=20+i*.5,noise=n) for i,n in enumerate(values)], phrases)
