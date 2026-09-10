"""Continuous Oracle motion; local preview first, leased single-branch inference only."""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import numpy as np
from PIL import Image
import oracle_steps as previous
from spatial_warp import remap_rgb

s = previous.s
a, t = s.a, s.t
OUT = a.PROJECT/'exports/motion-oracle-v001'
SESSION = a.APP/'work/motion-oracle-session'
BASELINE = previous.branch('high3')/'cadence-24'
LEVELS = ('high3',)
PROMPTS = previous.PROMPTS
START_SECONDS = 3.0
# 1.5 x average remaining baseline twist speed (global 3..5 seconds).
TWIST_SPEED = 1.5 * (t.TWIST_AMOUNT-t.parameters_at_time(3)[0])/2
# 1.5 x average baseline expansion parameter speed (global 3..10 seconds).
EXPANSION_RATE = 1.5*t.EXPANSION_AMOUNT/7
RADIUS = t.EXPANSION_RADIUS
CENTER = t.EXPANSION_CENTER
RADIAL_GRID = np.linspace(0, 2048, 8193)


def timing():
    return previous.timing()


def branch(case):
    assert case in LEVELS
    return OUT/case


def graph(case, seed):
    assert case == 'high3'
    g = previous.graph(case, seed)
    g['11']['inputs']['filename_prefix'] = 'motion-oracle/high3'
    return g


@lru_cache(maxsize=64)
def radial_flow(seconds):
    """Monotone radius table for dr/dt=k*r*exp(-r²/(2R²)); RK4 <=1/32s."""
    if not 0 <= seconds <= 12:
        raise ValueError('Local motion time must be in [0,12] seconds')
    whole = int(seconds)
    radius = RADIAL_GRID.copy() if whole == 0 else radial_flow(float(whole-1)).copy()
    duration = seconds if whole == 0 else seconds-(whole-1)
    steps = max(1, int(np.ceil(duration*32)))
    dt = duration/steps
    def velocity(r):
        return EXPANSION_RATE*r*np.exp(-r*r/(2*RADIUS**2))
    for _ in range(steps):
        k1 = velocity(radius)
        k2 = velocity(radius+dt*k1/2)
        k3 = velocity(radius+dt*k2/2)
        k4 = velocity(radius+dt*k3)
        radius += dt*(k1+2*k2+2*k3+k4)/6
    assert np.all(np.diff(radius)>0), 'Radial fold'
    return radius


def expansion(x, y, seconds, inverse=False):
    dx, dy = x-CENTER[0], y-CENTER[1]
    r = np.hypot(dx, dy)
    if np.max(r) >= RADIAL_GRID[-1]:
        raise ValueError('Coordinates outside radial lookup coverage')
    moved = radial_flow(seconds)
    target = np.interp(r, moved, RADIAL_GRID) if inverse else np.interp(r, RADIAL_GRID, moved)
    scale = np.divide(target, r, out=np.ones_like(r), where=r>1e-12)
    return CENTER[0]+dx*scale, CENTER[1]+dy*scale


def mapping_at_time(x, y, seconds, inverse=False):
    local = float(seconds)-START_SECONDS
    if not 0 <= local <= 12:
        raise ValueError('Global motion time must be in [3,15] seconds')
    if inverse:
        x, y = expansion(x, y, local, True)
        return a.motion.twist(x, y, -TWIST_SPEED*local)
    x, y = a.motion.twist(x, y, TWIST_SPEED*local)
    return expansion(x, y, local)


def coordinates_at_time(start, end, width=1536, height=1024):
    x, y = np.meshgrid(np.arange(width,dtype=float)*512/width,
                       np.arange(height,dtype=float)*320/height)
    x, y = mapping_at_time(x, y, end, True)
    x, y = mapping_at_time(x, y, start)
    return np.stack((x*width/512, y*height/320), axis=-1).astype(np.float32)


def warp_at_time(rgb, start, end):
    if start == end:
        return rgb.copy()
    h, w = rgb.shape[:2]
    return remap_rgb(rgb, coordinates_at_time(start,end,w,h))


def settings():
    return {'twist_radians_per_second':TWIST_SPEED, 'radial_rate_per_second':EXPANSION_RATE,
            'virtual_canvas_units':[512,320], 'twist_center':[256,160], 'twist_radius':125,
            'expansion_center':CENTER, 'expansion_radius':RADIUS, 'local_time_origin_global_seconds':3,
            'resampling':'Lanczos4 / BORDER_REFLECT_101', 'radial_method':'RK4 dt<=1/32s, monotone linear radius lookup',
            'initialization':'warped previous generated RGB anchor', 'reference_conditioning':False}


def render(deployment, lease):
    """Main owns execution. No infrastructure actions; scoped run archives, 11 calls."""
    if not lease.strip():
        raise ValueError('A specific main-agent lease identifier is required')
    a.transport.DEPLOYMENT = Path(deployment).resolve()
    json.loads(a.transport.DEPLOYMENT.read_text())
    (OUT/'runs').mkdir(parents=True, exist_ok=True)
    clock = timing(); root = branch('high3')/'cadence-24'
    a.save(SESSION/'lease.json', {'lease':lease,'deployment':str(a.transport.DEPLOYMENT),
                               'deployment_sha256':a.sha(a.transport.DEPLOYMENT),'calls':11})
    a.copy(BASELINE/'anchors/0072.png', root/'anchors/0072.png')
    a.save(root/'manifest.json', {'cadence':24,'fps':24,'frames':288,'start_frame':72,
        'first_repaint_seed':t.SEED+13,'seed_policy':'increment once per repaint',
        'opening_sha256':a.sha(root/'anchors/0072.png'), 'motion':settings(),
        'runner_sha256':a.sha(Path(__file__)), 'graph':graph('high3',t.SEED+13),
        'prompts':PROMPTS,'prompt_schedule':{i:previous.scene(t.SEED+12+i) for i in range(1,12)}})
    for i, f in enumerate(range(clock.start+24,clock.start+clock.count,24),1):
        parent=root/f'anchors/{f-24:04d}.png'; source=root/f'warped-inputs/{f:04d}.png'
        a.image(source, warp_at_time(np.asarray(Image.open(parent).convert('RGB')),clock.seconds(f-24),clock.seconds(f)))
        g=graph('high3',t.SEED+12+i); name=f'motion-oracle-v001-high3-cadence-24-{f:04d}'
        matches=list((OUT/'runs').glob('*-'+name+'-1f'))
        if matches:
            assert len(matches)==1
            run=matches[0]
            assert json.loads((run/'workflow.api.json').read_text())==g
            assert a.sha(run/'anchor.png')==a.sha(source)
            a.transport.collect(run)
        else:
            run=a.transport.submit(OUT,name,g,1,source=source,
                lineage={'parent_sha256':a.sha(parent),'frame':f,'repaint_index':i,'lease':lease})
        output=root/f'anchors/{f:04d}.png'; a.copy(run/'frames/0000.png',output)
        a.save(root/f'anchor-{f:04d}.json', {'run':str(run.relative_to(a.PROJECT)),
            'parent_sha256':a.sha(parent),'initialization_sha256':a.sha(source),
            'output_sha256':a.sha(output),'seed':t.SEED+12+i})
        print(f'Motion Oracle {i}/11 complete',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['render','plan'])
    p.add_argument('--deployment');p.add_argument('--lease');args=p.parse_args()
    if args.action=='plan':
        print(json.dumps({'calls':11,'motion':settings(),'baseline':str(BASELINE),'output':str(branch('high3'))},indent=2))
    else:
        if not args.deployment or not args.lease:p.error('render requires --deployment and --lease from main')
        render(args.deployment,args.lease)
