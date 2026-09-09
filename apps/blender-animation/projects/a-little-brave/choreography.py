"""Authored scene timing in 24 FPS frames; distances use each dog's rig space."""
import math

FPS = 24
FRAMES = 384
LEGS = ('front.near', 'front.far', 'back.near', 'back.far')


def clamp(t):
    return min(1.0, max(0.0, t))


def ease(t):
    t = clamp(t)
    return t*t*(3-2*t)


def track(keys, f, smooth=True):
    if f <= keys[0][0]:
        return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if f <= b:
            t = (f-a)/(b-a)
            if smooth:
                t = ease(t)
            return va+(vb-va)*t
    return keys[-1][1]


def footstep(f, initial, swings, lift=.14):
    """Hold world-space foot placements between explicit swing intervals."""
    x = initial
    for start, end, target in swings:
        if f < start:
            return x, 0, 0
        if f <= end:
            u = clamp((f-start)/(end-start))
            return x+(target-x)*ease(u), lift*math.sin(math.pi*u), -12*math.sin(math.pi*u)
        x = target
    return x, 0, 0


def neutral(f):
    return {'x': 0., 'z': 0., 'body': 0., 'head': -3., 'ear': 0., 'ear_tip': 0.,
            'paws': {n: (0., 0., 0.) for n in LEGS}, 'blink': False, 'bow': False}


def tail_motion(character, f):
    """Continuous, independent rhythms across action and camera boundaries."""
    if character == 'Biscuit':
        bias=track([(1,0),(80,0),(94,-12),(125,-12),(160,5),(210,8),(270,5),(329,4),(384,3)],f)
        amplitude=track([(1,5),(80,5),(94,2),(125,3),(165,9),(220,11),(268,9),(329,6),(384,3)],f)
        return bias+amplitude*math.sin((f-1)*.19), .4*bias+.9*amplitude*math.sin((f-5)*.19)
    warmth=ease((f-94)/30)
    bias=-9*(1-warmth)+10*warmth
    amplitude=(4+6*warmth)*track([(1,1),(319,1),(384,.45)],f)
    return bias+amplitude*math.sin((f-13)*.16), .5*amplitude*math.sin((f-18)*.16)


def puppy(f):
    pose = neutral(f)
    if f < 81:
        pose['x'] = track([(1,-2.), (64,0.)], f, smooth=False)
        walking = 1-ease((f-64)/16)
        pose['z'] = (-.10+.025*math.cos((f-1)*math.tau/12))*walking
        pose['body'] = -2*math.cos((f-1)*math.tau/24)*walking
        pose['head'] = -5+2*math.sin((f-4)*math.tau/24)*walking
        pose['ear'] = 6*math.sin((f-3)*math.tau/24)*walking
        pose['ear_tip'] = 5*math.sin((f-6)*math.tau/24)*walking
        for name in LEGS:
            diagonal = name in ('front.near','back.far')
            swings = [(1,9,-1.38),(25,33,-.68),(49,60,0)] if diagonal else [(13,21,-1.),(37,45,-.34),(61,69,0)]
            pose['paws'][name] = footstep(f, -2. if diagonal else -1.68, swings)
    elif f < 210:
        pose['x'] = track([(81,0),(92,-.08),(122,-.08),(157,0)], f)
        pose['z'] = track([(81,0),(94,-.07),(128,-.04),(150,-.03),(169,-.08),(186,-.07),(205,0)], f)
        pose['body'] = track([(81,0),(93,-3),(136,0),(169,4),(187,3),(205,0)], f)
        pose['head'] = track([(81,-5),(90,-17),(115,-14),(140,-6),(160,17),(177,21),(193,6),(205,-3)], f)
        pose['ear'] = track([(81,0),(94,17),(126,10),(146,0),(174,7),(195,-3),(205,0)], f)
        pose['ear_tip'] = .55*pose['ear']
        pose['paws']['front.near'] = footstep(f, 0, [(91,111,0),(162,176,.25),(177,181,.35),(190,204,0)], lift=.13)
        pose['blink'] = f in (96,97,149,150)
    elif f <= 281:
        pose['reference_frame'] = f-209
    else:
        pose['x'] = track([(282,.46),(291,.46),(319,.76)], f, smooth=False)
        walking = ease((f-288)/4)*(1-ease((f-319)/10))
        pose['z'] = -.06*walking+.007*math.sin(f*.13)*(1-walking)*ease((f-282)/8)
        pose['body'] = -1.5*walking
        pose['head'] = track([(282,-5),(309,-8),(329,-8),(345,-6),(366,-8),(384,-7)], f)
        pose['ear'] = 3*math.sin(f*.16)*walking
        pose['ear_tip'] = 3*math.sin((f-3)*.16)*walking
        for name in LEGS:
            diagonal = name in ('front.near','back.far')
            pose['paws'][name] = footstep(f, .46, [(292,304,.76)] if diagonal else [(307,319,.76)], lift=.08)
        pose['blink'] = f in (329,330,331,354,355,356) or f >= 374
    return pose


def bruno(f):
    pose = neutral(f)
    pose['head'] = track([(1,7),(70,9),(91,12),(108,0),(120,-23),(155,-27),
                          (180,8),(224,4),(260,10),(284,8),(315,1),(347,1),(361,3),(384,1)], f)
    pose['x'] = track([(1,0),(284,0),(313,.20)], f)
    pose['z'] = track([(1,0),(104,0),(125,-.245),(152,-.255),(181,0),(284,0),(316,-.25),(384,-.25)], f)
    pose['body'] = track([(1,0),(104,0),(125,24),(152,25),(181,0),(284,0),(316,23),(384,23)], f)
    pose['ear'] = track([(1,0),(96,2),(112,6),(127,-7),(155,-3),(185,3),(211,0),(299,4),(320,-5),(345,0),(384,0)], f)
    pose['ear_tip'] = .35*pose['ear']+1.5*math.sin(f*.10)
    for name in LEGS:
        if name.startswith('front'):
            reach = .27 if name.endswith('near') else .22
            pose['paws'][name] = footstep(f, 0, [(108,125,reach),(157,177,0),(291,310,.42)], lift=.055)
        else:
            pose['paws'][name] = footstep(f, 0, [(288,306,.20)], lift=.045)
    pose['bow'] = 120 <= f <= 163 or f >= 303
    pose['blink'] = f in (88,89,90,138,139,183,184,257,258,329,330,331,354,355,356) or f >= 374
    return pose


def ball(f):
    x = track([(1,.60),(119,.60),(155,-.68),(180,-.68),(206,.84),(291,.84),(321,.02),(384,.02)],f)
    return x, .13


BEATS = [(1,'Arrival'),(81,'A much bigger dog'),(105,'An invitation'),
         (120,'A ball offered'),(162,'A small brave answer'),(181,'Back to you'),
         (210,'Play'),(282,'Coming closer'),(329,'Friends'),(384,'End')]
