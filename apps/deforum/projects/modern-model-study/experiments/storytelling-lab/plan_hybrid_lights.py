"""Extend the observed boat-beacon and arriving boats into a shared-light ending."""
from branch import freeze
from run import lab

base = lab.read(lab.HERE / 'configs/h3-follow-the-beacon.json')
lab.save(lab.OUT / 'h3-follow-the-beacon/config.json', base)
style = ' A luminous surrealist oil painting. Crimson folded paper, pearlescent shells, deep turquoise water and warm gold lights. Clear large silhouettes, rich dimensional shading, delicate etched detail and dark negative space.'
stages = [
 (18, 'lights-shared', 'A red folded-paper lighthouse boat shelters beneath an immense pearlescent shell arch. Its golden lantern sends a long gentle beam across dark turquoise water. Six small red paper boats gather to the right, each now carrying its own warm golden lantern. The boats form a curved trail of separate lights leading outward through the open harbor. The central red beacon remains distinct.'),
 (20, 'lanterns-rise', 'The gold lantern atop a red paper lighthouse opens into a small swarm of luminous golden fireflies. Separate golden lights rise from the little red paper boats and curve upward toward the right into the dark night sky. The pearl shell arch recedes below. A red beacon and several tiny red boats remain on calm turquoise water near the bottom. The ascending lights are bright and distinct against deep indigo.'),
 (23, 'a-path-in-the-dark', 'A winding constellation of large and small golden lights crosses a vast indigo night sky, curving from a red lighthouse boat at the lower left toward the upper right. Along the dark turquoise water below, a small procession of red paper boats carries matching gold lanterns. Pale shell roofs mark a distant safe harbor. Each warm light is separated by dark space. The single red beacon is small but recognizable beneath the spacious illuminated sky.'),
 (26, 'many-lights', 'A wide turquoise ocean at night under a sweeping golden constellation. Many separate warm lanterns are carried by small crimson paper boats across the calm water, reflecting as a winding gold path. A tiny red lighthouse glows near the lower left horizon beside distant pearl shells. Above them the same curved path continues as bright golden stars in a spacious indigo sky. An open hopeful scene, individual red boats and gold lights remain readable.'),
]
phrases = base['phrases'] + [
 dict(start=17.5,duration=11,zoom=-.25,turn=-14,travel=[-.06,.25],center=[.8,.45],radius=3.5),
 dict(kind='plane',start=19,duration=11,tilt=[-9,7],distance=3.5,center=[.75,.45]),
 dict(kind='wave',start=20,duration=12,amplitude=.028,wavelength=1.7,cycles=.5),
]
values=[.52,.60,.68,.72,.68,.66,.72,.76,.78,.72,.66,.70,.76,.78,.72,.66,.60,.54,.46,.40,.34,.30]
freeze('h3-follow-the-beacon','h4-a-sky-of-lanterns',420,29,
       [dict(at=t,name=n,prompt=p+style) for t,n,p in stages],
       [dict(at=18+i*.5,noise=n) for i,n in enumerate(values)],phrases)
