"""Authored 120 BPM dance phrases, measured in beats and stage units."""
import math

BPM=120
FPS=24
SECTION_SECONDS=6
MOVES=('groove','shuffle','robot')
TAU=math.tau


def ease(x):
    x=max(0,min(1,x))
    return x*x*(3-2*x)


def mix(a,b,t):return a+(b-a)*t


def footstep(beat, side):
    """Four-beat out/together/return/together, with explicit planted intervals."""
    # Each shoe only moves during its assigned beat. Returning finishes the loop.
    xs=([-.34,-.34,.12,-.34,-.34] if side==0 else [.34,.8,.8,.8,.34])
    k=int(beat%4); u=beat%1
    active=abs(xs[k+1]-xs[k])>.01
    progress=ease((u-.12)/.7)
    lift=.24*math.sin(math.pi*progress) if active else 0
    return (mix(xs[k],xs[k+1],progress),-.03,.125+lift), active and .12<u<.82


def pose(move,seconds,character):
    b=seconds*BPM/60
    phase=character*.11
    w=TAU*(b/2-phase)
    beat=TAU*(b-phase)
    feet=[(-.34,0,.125),(.34,0,.125)]
    state={'root':(0,0,1.22),'torso':(0,0,0),'head':(0,0,0),'ears':0,
           'feet':feet,'hands':[(-.62,-.15,.1),(.62,-.15,.1)],'support':[True,True], 'blink':1}
    blink_time=(seconds-character*.21)%3
    state['blink']=1-.88*max(0,1-abs(blink_time-2.42)/.10)
    if move=='groove':
        sway=.19*math.sin(w)
        state['root']=(sway,0,1.20-.065*(1+math.cos(beat)))
        state['torso']=(.04*math.sin(beat),-.12*math.sin(w),.10*math.sin(w-.5))
        state['head']=(.06*math.sin(beat-.5),.09*math.sin(w-.7),-.12*math.sin(w-.4))
        state['hands']=[(-.65-.1*math.sin(w),-.18,.33+.32*math.sin(w)),(.65-.1*math.sin(w),-.18,.33-.32*math.sin(w))]
        state['ears']=.19*math.sin(beat-.8)
    elif move=='shuffle':
        # Travel in the same direction, keeping the space between partners consistent.
        feet_and_support=[footstep(b,i) for i in [0,1]]
        feet=[f for f,_ in feet_and_support]
        state['feet']=feet
        state['support']=[not a for _,a in feet_and_support]
        middle=(feet[0][0]+feet[1][0])/2
        # Shift toward the supporting shoe during the airborne part of each step.
        lifts=[max(0,f[2]-.125) for f in feet]
        transfer=(feet[0][0]-middle)*(lifts[1]/.24)*.55+(feet[1][0]-middle)*(lifts[0]/.24)*.55
        state['root']=(middle+transfer,0,1.15+.06*math.cos(beat))
        state['torso']=(.08,-.08*math.sin(w),.1*math.sin(w))
        state['head']=(-.035,.06*math.sin(w-.6),-.10*math.sin(w-.4))
        state['hands']=[(-.64,-.10-.16*math.sin(w),.12+.22*math.sin(w)),(.64,-.10+.16*math.sin(w),.12-.22*math.sin(w))]
        state['ears']=.23*math.sin(beat-.7)
    elif move=='robot':
        # Held angular shapes, fast attacks inside each beat; contrasting mechanical time.
        poses=[(-.2,(-.75,-.12,.85),(.68,-.20,-.02)),
               (.2,(-.68,-.20,-.02),(.75,-.12,.85)),
               (.2,(-.72,-.08,1.05),(.72,-.08,1.05)),
               (-.2,(-1.08,-.07,.45),(1.08,-.07,.45))]
        k=int(b)%4;u=b%1
        previous=poses[(k-1)%4];target=poses[k]
        f=ease(u/.22)
        yaw=mix(previous[0],target[0],f)
        state['root']=(.08*math.sin(w),0,1.16+.045*math.sin(math.pi*min(u/.3,1)))
        state['torso']=(0,0,yaw)
        state['head']=(0,.03,-yaw*1.3)
        state['hands']=[tuple(mix(previous[i][j],target[i][j],f) for j in range(3)) for i in [1,2]]
        state['ears']=.025*math.sin(beat)
    else:raise ValueError(move)
    return state
