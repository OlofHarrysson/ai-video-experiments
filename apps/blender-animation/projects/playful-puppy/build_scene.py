"""Run in Blender: blender -b --python build_scene.py -- --version v001.

Creates an original skinned puppy and editable pose animation. No external assets.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Quaternion

ROOT = Path(__file__).resolve().parent
FPS = 30
END = 90
RESOLUTION = (1280, 720)
P = argparse.ArgumentParser()
P.add_argument('--version', default='v001')
P.add_argument('--frames', default='')
args = P.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
OUT = ROOT / 'output' / args.version
if (OUT / 'playful-puppy.blend').exists():
    raise FileExistsError('Choose a new version to preserve the existing scene')
OUT.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = RESOLUTION
scene.render.resolution_percentage = 100
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, END
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.world.color = (0.25, 0.25, 0.25)
scene.view_settings.view_transform = 'AgX'
scene.render.film_transparent = False

def material(name, color, roughness=.6):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    shader = m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    return m

fur = material('Biscuit | golden coat', (.57, .265, .082))
cream = material('Warm cream | muzzle and toes', (.88, .70, .43))
ear_mat = material('Soft cocoa | ears', (.24, .081, .029))
dark = material('Espresso | nose and eyes', (.026, .012, .008), .3)
shine = material('Warm eye glints', (1, .93, .76), .24)
pink = material('Tongue', (.62, .18, .17))
floor_mat = material('Studio | sage', (.18, .29, .27), .9)

def uv(name, loc, scale, mat=None, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob

def capsule(name, a, b, r1, r2):
    d = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r1, radius2=r2,
                                  depth=d.length, location=(Vector(a) + Vector(b)) / 2)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = d.to_track_quat('Z', 'Y')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return ob

# Persistent skeleton. Paw targets are independent of the body/root controls.
arm = bpy.data.armatures.new('Biscuit skeleton')
rig = bpy.data.objects.new('BISCUIT | pose controls', arm)
scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
rig.show_in_front = True
bpy.ops.object.mode_set(mode='EDIT')

def bone(name, head, tail, parent=None, deform=True):
    b = arm.edit_bones.new(name)
    b.head, b.tail = head, tail
    b.use_deform = deform
    if parent:
        b.parent = arm.edit_bones[parent]
    return b

bone('ROOT', (0, 0, 0), (0, 0, .3), deform=False)
bone('BODY', (0, 0, 1.16), (.55, 0, 1.16), 'ROOT')
bone('HEAD', (.72, 0, 1.48), (1.14, 0, 1.84), 'BODY')
legs = {}
for end in ['front', 'back']:
    for side, y in [('near', -.34), ('far', .34)]:
        name = f'{end}.{side}'
        if end == 'front':
            shoulder, knee, ankle = (.53, y, 1.24), (.39, y, .69), (.58, y, .20)
        else:
            shoulder, knee, ankle = (-.64, y, 1.15), (-.38, y, .66), (-.66, y, .20)
        legs[name] = [Vector(shoulder), Vector(knee), Vector(ankle)]
        bone('upper.' + name, shoulder, knee, 'BODY')
        bone('lower.' + name, knee, ankle, 'upper.' + name)
        bone('paw.' + name, ankle, Vector(ankle) + Vector((.25, 0, 0)), 'lower.' + name)
        bone('CTRL.paw.' + name, ankle, Vector(ankle) + Vector((.25, 0, 0)), deform=False)
for side, sign in [('near', -1), ('far', 1)]:
    bone('ear.' + side, (.84, sign * .39, 2.09), (.76, sign * .49, 1.56), 'HEAD')
bone('tail.01', (-.91, 0, 1.37), (-1.26, 0, 1.61), 'BODY')
bone('tail.02', (-1.26, 0, 1.61), (-1.62, 0, 1.80), 'tail.01')
bpy.ops.object.mode_set(mode='OBJECT')
rig.select_set(False)

for name in legs:
    c = rig.pose.bones['lower.' + name].constraints.new('IK')
    c.name = 'Paw placement | two bone IK'
    c.target, c.subtarget, c.chain_count = rig, 'CTRL.paw.' + name, 2
    c.use_stretch = False
    c.iterations = 100
    rig.pose.bones['upper.' + name].ik_stretch = 0
    rig.pose.bones['lower.' + name].ik_stretch = 0
    c = rig.pose.bones['paw.' + name].constraints.new('COPY_ROTATION')
    c.target, c.subtarget = rig, 'CTRL.paw.' + name
    c.target_space = c.owner_space = 'WORLD'

def bind(ob, bone_name=None):
    mod = ob.modifiers.new('Skeleton deformation', 'ARMATURE')
    mod.object = rig
    mod.use_deform_preserve_volume = True
    if bone_name:
        ob.vertex_groups.new(name=bone_name).add(list(range(len(ob.data.vertices))), 1, 'REPLACE')
    return ob

# Fuse the primary volumes before skinning, so shoulders and elbows are continuous.
parts = [
    uv('torso volume', (-.12, 0, 1.16), (.84, .40, .43)),
    uv('rump volume', (-.62, 0, 1.13), (.44, .41, .43)),
    uv('chest volume', (.46, 0, 1.23), (.43, .43, .48)),
    uv('neck volume', (.72, 0, 1.48), (.29, .32, .36)),
    uv('head volume', (1.04, 0, 1.84), (.46, .43, .43)),
]
for name, (a, b, c) in legs.items():
    parts += [capsule(name + ' thigh', a, b, .195, .14),
              uv(name + ' knee', b, (.145, .15, .15)),
              capsule(name + ' shin', b, c, .14, .11)]
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:
    ob.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
skin = bpy.context.object
skin.name = 'Puppy | continuous skinned coat'
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
remesh = skin.modifiers.new('Sculpt union', 'REMESH')
remesh.mode, remesh.voxel_size = 'VOXEL', .038
bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth = skin.modifiers.new('Smooth sculpt', 'SMOOTH')
smooth.factor, smooth.iterations = .65, 12
bpy.ops.object.modifier_apply(modifier=smooth.name)
skin.data.materials.append(fur)
for p in skin.data.polygons:
    p.use_smooth = True

def clamp(x):
    return max(0, min(1, x))

def smoothstep(a, b, x):
    t = clamp((x-a)/(b-a))
    return t*t*(3-2*t)

def dist_segment(p, a, b):
    t = clamp((p-a).dot(b-a)/(b-a).length_squared)
    return (p-(a+t*(b-a))).length

groups = {n: skin.vertex_groups.new(name=n) for n in ['BODY', 'HEAD'] +
          [prefix + n for n in legs for prefix in ['upper.', 'lower.']]}
for v in skin.data.vertices:
    p = v.co
    wh = smoothstep(1.75, 2.5, p.x + p.z) * smoothstep(.38, .8, p.x)
    weights = {'HEAD': wh, 'BODY': 1-wh}
    influences = {}
    for name, (a, b, c) in legs.items():
        d1, d2 = dist_segment(p, a, b), dist_segment(p, b, c)
        envelope = (1-smoothstep(.16,.32,min(d1,d2))) * (1-smoothstep(.75,1.22,p.z))
        u, l = 1 / max(.045,d1)**4, 1 / max(.045,d2)**4
        influences['upper.'+name] = envelope*u/(u+l)
        influences['lower.'+name] = envelope*l/(u+l)
    total = sum(influences.values())
    wl = min(1, total)
    weights = {k: w*(1-wl) for k,w in weights.items()}
    if total:
        weights.update({k: wl*w/total for k,w in influences.items()})
    for n, w in weights.items():
        if w > .0001:
            groups[n].add([v.index], w, 'REPLACE')
bind(skin)
sub = skin.modifiers.new('Silhouette smoothing', 'SUBSURF')
sub.levels = sub.render_levels = 1

# Paw pads overlap the skinned ankles; their orientation is separately controllable.
for name, (_, _, ankle) in legs.items():
    bind(uv('Paw | ' + name, ankle + Vector((.065, 0, -.045)), (.235, .185, .155), fur), 'paw.' + name)
    bind(uv('Cream toes | ' + name, ankle + Vector((.20, 0, -.06)), (.11, .167, .118), cream), 'paw.' + name)

bind(uv('Soft cream muzzle', (1.39, 0, 1.65), (.32, .32, .225), cream), 'HEAD')
bind(uv('Nose', (1.687, 0, 1.72), (.092, .145, .088), dark), 'HEAD')
bind(uv('Nose highlight', (1.747, -.052, 1.762), (.018, .041, .012), shine), 'HEAD')
bind(uv('Mouth smile', (1.624, 0, 1.53), (.065, .175, .047), dark), 'HEAD')
bind(uv('Tiny tongue', (1.661, -.002, 1.501), (.044, .068, .045), pink), 'HEAD')
for side, sign in [('near', -1), ('far', 1)]:
    bind(uv('Eye socket | ' + side, (1.29, sign*.29, 1.96), (.123, .097, .125), ear_mat), 'HEAD')
    eye = bind(uv('Eye | ' + side, (1.318, sign*.329, 1.97), (.089, .065, .10), dark), 'HEAD')
    bind(uv('Eye glint | ' + side, (1.361, sign*.366, 2.01), (.024, .018, .027), shine), 'HEAD')
    ear = uv('Floppy ear | ' + side, (.79, sign*.443, 1.79), (.215, .115, .355), ear_mat)
    bind(ear, 'ear.' + side)
    # Eye compression supplies an editable blink, including its catchlight/socket.
    for ob in list(bpy.data.objects):
        if ob.type == 'MESH' and ob.name in ['Eye | '+side, 'Eye glint | '+side, 'Eye socket | '+side]:
            ob.shape_key_add(name='Basis')
            k = ob.shape_key_add(name='Blink')
            for v in k.data:
                v.co.z = (1.97-ob.location.z) + (v.co.z+ob.location.z-1.97)*.13
            for f, value in [(1,0),(12,0),(14,1),(16,0),(66,0),(69,1),(73,0),(90,0)]:
                k.value = value
                k.keyframe_insert('value', frame=f)

# A tapered tail with smoothly blended weights across two articulated segments.
points = [(-.88,0,1.37,.145),(-1.08,0,1.51,.135),(-1.30,0,1.68,.105),(-1.53,0,1.78,.075),(-1.68,0,1.81,.015)]
verts, faces = [], []
for j, (x,y,z,r) in enumerate(points):
    for k in range(12):
        angle = k*math.tau/12
        verts.append((x, y+r*math.cos(angle), z+r*math.sin(angle)))
        if j:
            a=(j-1)*12+k; b=(j-1)*12+(k+1)%12; c=j*12+(k+1)%12; d=j*12+k
            faces.append((a,b,c,d))
faces += [tuple(reversed(range(12))), tuple(range(48,60))]
mesh = bpy.data.meshes.new('Tail surface')
mesh.from_pydata(verts, [], faces)
tail = bpy.data.objects.new('Tail | two bone skin', mesh)
scene.collection.objects.link(tail)
mesh.materials.append(fur)
g1, g2 = tail.vertex_groups.new(name='tail.01'), tail.vertex_groups.new(name='tail.02')
for v in mesh.vertices:
    w = smoothstep(1.14, 1.43, -v.co.x)
    g1.add([v.index], 1-w, 'REPLACE'); g2.add([v.index], w, 'REPLACE')
for p in mesh.polygons:
    p.use_smooth = True
bind(tail)
s = tail.modifiers.new('Tail smoothing', 'SUBSURF'); s.levels = s.render_levels = 2

def key_rot(name, frame, pitch=0, yaw=0, roll=0):
    pb = rig.pose.bones[name]
    rest = rig.data.bones[name].matrix_local.to_quaternion()
    world = Quaternion((0,1,0), math.radians(pitch)) @ Quaternion((0,0,1), math.radians(yaw)) @ Quaternion((1,0,0), math.radians(roll))
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = rest.inverted() @ world @ rest
    pb.keyframe_insert('rotation_quaternion', frame=frame, group=name)

def key_move(name, frame, offset):
    pb = rig.pose.bones[name]
    pb.location = rig.data.bones[name].matrix_local.to_3x3().inverted() @ Vector(offset)
    pb.keyframe_insert('location', frame=frame, group=name)

# frame, travel, body height offset, body pitch, head counter-pitch
poses = [
    (1, 0, 0, 0, -3), (10, 0, .025, -3, -9),
    (24, 0, -.235, 23, -31), (33, 0, -.255, 25, -35),
    (43, -.035, -.22, -5, 1), (48, .015, .03, -12, 4),
    (55, .20, .48, -9, 1), (60, .34, .40, 4, -7),
    (65, .43, .09, 11, -14), (69, .46, -.19, 6, -12),
    (76, .46, .015, -1, -4), (83, .46, 0, 0, -5), (90,.46,0,0,-5),
]
for f,x,z,p,h in poses:
    key_move('ROOT', f, (x,0,z))
    key_rot('BODY', f, pitch=p)
    key_rot('HEAD', f, pitch=h, yaw=(-5 if f<43 else 0))

# Forepaws reach into the bow, then remain locked while the chest lowers.
for name in legs:
    front = name.startswith('front')
    paw_keys = [
        (1, 0, 0, 0), (10,0,0,0),
        (17, .11 if front else 0, .075 if front else 0, 0),
        (23, .22 if front else 0, 0, 0),
        (33, .22 if front else 0, 0, 0),
        (39, .08 if front else -.01, .06 if front else .015, 0),
        (43, .02 if front else -.02, 0, 0),
        (48, .04, .13 if front else 0, -20),
        (50, .07, .32 if front else .14, -22 if front else 4),
        (55, .15 if front else .10, .72 if front else .63, -22 if front else 25),
        (60, .37 if front else .25, .38 if front else .47, 8 if front else 13),
        (63, .44 if front else .32, .19 if front else .28, 3 if front else 12),
        (65, .46 if front else .36, 0 if front else .14, 0 if front else 12),
        (68, .46, 0, 0), (76,.46,0,0), (90,.46,0,0),
    ]
    for f,x,z,p in paw_keys:
        key_move('CTRL.paw.'+name, f, (x,0,z))
        key_rot('CTRL.paw.'+name, f, pitch=p)

# Offset secondary animation. Ear and tail action is stored as editable bone keys.
for f in range(1, END+1, 3):
    wag = math.sin((f-1)*.30) * (18 if f<43 else 11)
    key_rot('tail.01', f, yaw=wag, pitch=5*math.sin(f*.14))
    key_rot('tail.02', f, yaw=math.sin((f-4)*.30)*15, pitch=5*math.sin((f-4)*.14))
for side, sign in [('near', -1), ('far',1)]:
    for f,p,r in [(1,0,0),(10,4,2),(26,-11,3),(35,-7,2),(44,5,0),
                  (51,25,12),(57,17,16),(64,-20,6),(69,-27,2),
                  (74,13,7),(80,-5,1),(86,1,0),(90,0,0)]:
        key_rot('ear.'+side,f,pitch=p,roll=r*sign)

# Use bounded Bezier handles to avoid numerical overshoot around planted poses.
def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                yield from bag.fcurves

if rig.animation_data and rig.animation_data.action:
    rig.animation_data.action.name = 'Biscuit | bow, hop, settle'
    for fc in curves(rig.animation_data.action):
        for k in fc.keyframe_points:
            k.interpolation = 'BEZIER'
            k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
for f,label in [(1,'Notice'),(24,'Play bow'),(43,'Gather'),(48,'Push off'),
                (55,'Airborne'),(65,'Front paws land'),(69,'Absorb weight'),(83,'Settle')]:
    scene.timeline_markers.new(label, frame=f)

# A quiet studio keeps silhouette and floor contact readable.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-.018))
floor = bpy.context.object
floor.name = 'Plain studio floor'; floor.data.materials.append(floor_mat)
world = bpy.data.worlds.new('Soft studio environment')
scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.40,.52,.60,1)
world.node_tree.nodes['Background'].inputs[1].default_value = .35

def area(name, loc, power, color, size, target=(0,0,1)):
    data = bpy.data.lights.new(name, 'AREA'); data.energy = power; data.color=color; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
area('Large warm key', (1,-4,7), 650, (1,.83,.63), 5)
area('Soft cool fill', (3,4,5), 450, (.70,.84,1), 4)
area('Rim', (-4,1,5), 700, (1,.73,.42), 3)
data=bpy.data.cameras.new('Camera'); camera=bpy.data.objects.new('Camera',data)
scene.collection.objects.link(camera); scene.camera=camera
camera.location=(4.8,-8,3.8)
camera.rotation_euler=(Vector((.13,0,1.30))-camera.location).to_track_quat('-Z','Y').to_euler()
data.type='ORTHO'; data.ortho_scale=6.2; data.lens=50
scene.render.filepath=str(OUT/'frames'/'frame_')
scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True); bpy.context.view_layer.objects.active=rig
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.region_3d.view_perspective='CAMERA'
scene['brief']='One puppy: play bow, small hop, landing and recovery. Original procedural mesh, native armature and keyframes.'
scene['authoring_version']=args.version
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'playful-puppy.blend'))
(OUT/'manifest.json').write_text(json.dumps({'blender':bpy.app.version_string,'fps':FPS,'frames':END,
    'resolution':RESOLUTION,'bones':len(arm.bones),'skin_vertices':len(skin.data.vertices),
    'source':str(Path(__file__).resolve()),'poses':poses,'version':args.version},indent=2)+'\n')
if args.frames:
    for f in map(int,args.frames.split(',')):
        scene.frame_set(f)
        scene.render.filepath=str(OUT/'stills'/f'frame_{f:04d}.png')
        bpy.ops.render.render(write_still=True)
