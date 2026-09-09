"""Assemble an editable, deterministic two-character Blender film."""
import argparse
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import choreography as motion
from gaze import add_gaze

PUPPY_SCENE = ROOT.parent/'puppy-2d/output/v011/puppy-2d.blend'
BRUNO_SCENE = ROOT/'output/rottweiler-v004/puppy-2d.blend'
PARK = ROOT/'assets/park-v001.png'
SCORE = ROOT/'assets/score-v001-master.wav'

p = argparse.ArgumentParser()
p.add_argument('--version', required=True)
p.add_argument('--frames', default='')
p.add_argument('--percentage', type=int, default=50)
args = p.parse_args(sys.argv[sys.argv.index('--')+1:])
OUT = ROOT/'output'/args.version
assert not (OUT/'a-little-brave.blend').exists(), 'Use a new version to preserve the saved scene'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = False
scene.cycles.use_animated_seed = False
scene.cycles.seed = 0
scene.cycles.transparent_max_bounces = 32
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.resolution_percentage = 100
scene.render.fps = motion.FPS
scene.frame_start, scene.frame_end = 1, motion.FRAMES
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.view_settings.view_transform = 'Standard'
scene.render.film_transparent = False


def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                yield from bag.fcurves


def empty(name):
    ob = bpy.data.objects.new(name, None)
    scene.collection.objects.link(ob)
    return ob


def load_dog(path, name, origin, scale, facing):
    with bpy.data.libraries.load(str(path)) as (src, dst):
        names = [n for n in src.objects if n.startswith(('Paint |', 'Drawing |')) or 'pose controls' in n]
        dst.objects = names.copy()
    pieces = {}
    for original, ob in zip(names, dst.objects):
        scene.collection.objects.link(ob)
        ob.name = f'{name} / {original}'
        pieces[original] = ob
    rig = next(ob for ob in pieces.values() if ob.type == 'ARMATURE')
    reference = []
    for f in range(1,73):
        scene.frame_set(f)
        reference.append({'bones': {pb.name: {'location': list(pb.location),
                                             'rotation': list(pb.rotation_quaternion)} for pb in rig.pose.bones},
                          'bow': not pieces['Drawing | folded front.near'].hide_render,
                          'blink': not pieces['Drawing | delighted eyes'].hide_render})
    for ob in pieces.values():
        ob.animation_data_clear()
        ob.hide_render = ob.hide_viewport = False
    for pb in rig.pose.bones:
        pb.location = (0,0,0)
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = (1,0,0,0)
        pb.scale = (1,1,1)
        for constraint in pb.constraints:
            if constraint.type == 'COPY_ROTATION' and constraint.target == rig:
                constraint.owner_space = 'POSE'
                constraint.target_space = 'POSE'
    root = empty(f'{name} | stage placement')
    root.location = origin
    root.scale = (scale*facing, scale, scale)
    for ob in pieces.values():
        ob.parent = root
        ob.matrix_parent_inverse = Matrix.Identity(4)
    root['character'] = name
    root['source_scene'] = str(path)
    for property_name,description in [('closed_eyes','Use the closed, smiling eye drawing'),
                                      ('folded_forelegs','Use the folded foreleg drawings during a bow')]:
        rig[property_name] = False
        rig.id_properties_ui(property_name).update(description=description)
    drawing_controls = [('Drawing | delighted eyes','closed_eyes',True)]
    for side in ['near','far']:
        drawing_controls += [(f'Paint | front.{side}','folded_forelegs',False),
                             (f'Drawing | folded front.{side}','folded_forelegs',True)]
    for object_name,property_name,show_when_true in drawing_controls:
        for field in ['hide_render','hide_viewport']:
            driver = pieces[object_name].driver_add(field).driver
            variable = driver.variables.new();variable.name = 'enabled';variable.type = 'SINGLE_PROP'
            variable.targets[0].id = rig
            variable.targets[0].data_path = f'["{property_name}"]'
            driver.expression = 'not enabled' if show_when_true else 'enabled'
    return {'name':name,'rig':rig,'parts':pieces,'root':root,'scale':scale,
            'facing':facing,'reference':reference,'origin':origin}


puppy = load_dog(PUPPY_SCENE,'Biscuit',(-1.7,-.15,0),.78,1)
bruno = load_dog(BRUNO_SCENE,'Bruno',(2.1,0,0),1.20,-1)
for ob in add_gaze(bruno['parts']['Drawing | attentive']):
    original = ob.name
    ob.name = 'Bruno / '+original
    bruno['parts'][original] = ob


def move(rig, name, f, x, z):
    pb = rig.pose.bones[name]
    pb.location = rig.data.bones[name].matrix_local.to_3x3().inverted() @ Vector((x,0,z))
    pb.keyframe_insert('location', frame=f, group=name)


def pitch(rig, name, f, degrees):
    pb = rig.pose.bones[name]
    rest = rig.data.bones[name].matrix_local.to_quaternion()
    pb.rotation_quaternion = rest.inverted() @ Quaternion((0,1,0),math.radians(degrees)) @ rest
    pb.keyframe_insert('rotation_quaternion',frame=f,group=name)


def visibility(dog, f, bow, blink):
    rig = dog['rig']
    for property_name,value in [('folded_forelegs',bow),('closed_eyes',blink)]:
        rig[property_name] = value
        rig.keyframe_insert(data_path=f'["{property_name}"]',frame=f,group='Drawing controls')


def pose_dog(dog, f, pose):
    rig = dog['rig']
    if 'reference_frame' in pose:
        ref = dog['reference'][pose['reference_frame']-1]
        for name, value in ref['bones'].items():
            if name in ['tail.01','tail.02']:
                continue
            pb = rig.pose.bones[name]
            pb.location, pb.rotation_quaternion = value['location'], value['rotation']
            pb.keyframe_insert('location',frame=f,group=name)
            pb.keyframe_insert('rotation_quaternion',frame=f,group=name)
        visibility(dog,f,ref['bow'],ref['blink'])
    else:
        move(rig,'ROOT',f,pose['x'],pose['z'])
        for name, key in [('BODY','body'),('HEAD','head'),('ear.near','ear'),('ear.far','ear'),
                          ('ear.tip','ear_tip')]:
            pitch(rig,name,f,pose[key])
        for name, (x,z,rotation) in pose['paws'].items():
            move(rig,'CTRL.paw.'+name,f,x,z)
            pitch(rig,'CTRL.paw.'+name,f,rotation)
        visibility(dog,f,pose['bow'],pose['blink'])
    for name,angle in zip(['tail.01','tail.02'],motion.tail_motion(dog['name'],f)):
        pitch(rig,name,f,angle)


for f in range(1,motion.FRAMES+1):
    pose_dog(puppy,f,motion.puppy(f))
    pose_dog(bruno,f,motion.bruno(f))
    head_control = bruno['rig'].pose.bones['HEAD']
    head_control['gaze_x'] = motion.track([(1,.65),(105,.8),(122,.55),(160,.8),(282,.8)],f)
    head_control['gaze_y'] = motion.track([(1,-.6),(106,-.6),(124,-.85),(156,-.85),(186,-.5),
                                           (228,-.4),(250,.45),(270,-.6),(319,-.15),(384,-.15)],f)
    for property_name in ['gaze_x','gaze_y']:
        head_control.keyframe_insert(data_path=f'["{property_name}"]',frame=f,group='HEAD')
for dog in [puppy,bruno]:
    dog['rig'].animation_data.action.name = f"{dog['name']} | authored scene performance"
    for ob in dog['parts'].values():
        if ob.animation_data and ob.animation_data.action:
            for fc in curves(ob.animation_data.action):
                for key in fc.keyframe_points:
                    key.interpolation = 'CONSTANT' if fc.data_path in ['["closed_eyes"]','["folded_forelegs"]'] else 'LINEAR'


def flat(name, color):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emit = nodes.new('ShaderNodeEmission')
    def linear(c):
        return c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4
    emit.inputs['Color'].default_value = (*[linear(c) for c in color],1)
    material.node_tree.links.new(emit.outputs[0],out.inputs['Surface'])
    return material


def panel(name, box, depth, material):
    x0,x1,z0,z1 = box
    data = bpy.data.meshes.new(name)
    data.from_pydata([(x0,depth,z0),(x1,depth,z0),(x1,depth,z1),(x0,depth,z1)],[],[(0,1,2,3)])
    data.materials.append(material)
    uv = data.uv_layers.new()
    for loop, coord in zip(uv.data, [(0,0),(1,0),(1,1),(0,1)]):
        loop.uv = coord
    ob = bpy.data.objects.new(name,data)
    scene.collection.objects.link(ob)
    return ob


background = flat('Painted park background',(1,1,1))
nodes = background.node_tree.nodes
tex = nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load(str(PARK),check_existing=True)
tex.image.pack()
emit = next(n for n in nodes if n.type == 'EMISSION')
background.node_tree.links.new(tex.outputs['Color'],emit.inputs['Color'])
panel('Set | painted dog park',(-7,7,-1.5,6.375),2,background)


def shadow(name, width, height, strength):
    material = flat(name,(.26,.18,.10))
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
    emit = next(n for n in nodes if n.type == 'EMISSION')
    uv = nodes.new('ShaderNodeTexCoord')
    sub = nodes.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'
    sub.inputs[1].default_value = (.5,.5,0)
    length = nodes.new('ShaderNodeVectorMath'); length.operation = 'LENGTH'
    ramp = nodes.new('ShaderNodeMapRange'); ramp.clamp = True
    ramp.inputs['From Min'].default_value = .08
    ramp.inputs['From Max'].default_value = .5
    ramp.inputs['To Min'].default_value = strength
    ramp.inputs['To Max'].default_value = 0
    links.new(uv.outputs['UV'],sub.inputs[0]);links.new(sub.outputs[0],length.inputs[0])
    links.new(length.outputs['Value'],ramp.inputs['Value'])
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    mix = nodes.new('ShaderNodeMixShader')
    links.new(ramp.outputs[0],mix.inputs[0]);links.new(transparent.outputs[0],mix.inputs[1])
    links.new(emit.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],output.inputs['Surface'])
    return panel(name,(-width/2,width/2,-height/2,height/2),.35,material)


for dog in [puppy,bruno]:
    ob = shadow(f"Set | {dog['name']} contact shadow",2.65*dog['scale'],.16*dog['scale'],.35)
    rig = dog['rig']
    for f in range(1,motion.FRAMES+1):
        scene.frame_set(f)
        root = rig.matrix_world @ rig.pose.bones['ROOT'].head
        ob.location.x = root.x
        ob.scale.x = 1-max(0,root.z)*.22
        ob.scale.y = 1
        ob.keyframe_insert('location',frame=f)
        ob.keyframe_insert('scale',frame=f)


ball_root = empty('Prop | ball motion')
outline = flat('Ball | cocoa outline',(.25,.10,.065))
red = flat('Ball | terracotta red',(.77,.24,.16))
cream = flat('Ball | cream stripe',(.99,.86,.62))


def disk(name, radius, depth, mat):
    count = 64
    verts = [(radius*math.cos(i*math.tau/count),depth,radius*math.sin(i*math.tau/count)) for i in range(count)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],[tuple(range(count))])
    mesh.materials.append(mat)
    ob = bpy.data.objects.new(name,mesh)
    scene.collection.objects.link(ob)
    ob.parent = ball_root
    return ob


disk('Prop | ball outline',.13,-.30,outline)
disk('Prop | ball fill',.123,-.305,red)
curve = bpy.data.curves.new('Ball | curved seam','CURVE')
curve.dimensions = '3D'
curve.bevel_depth = .009
curve.bevel_resolution = 3
spline = curve.splines.new('POLY')
spline.points.add(31)
for i, point in enumerate(spline.points):
    t = -1+2*i/31
    point.co = (.035*math.sin(t*math.pi),-.31,t*.116,1)
ob = bpy.data.objects.new('Prop | cream ball seam',curve)
scene.collection.objects.link(ob)
curve.materials.append(cream)
ob.parent = ball_root
ball_shadow = shadow('Set | ball contact',.40,.04,.40)
for f in range(1,motion.FRAMES+1):
    x,z = motion.ball(f)
    ball_root.location = (x,0,z)
    ball_root.rotation_euler = (0,(x-.60)/.13,0)
    ball_root.keyframe_insert('location',frame=f)
    ball_root.keyframe_insert('rotation_euler',frame=f)
    ball_shadow.location.x = x
    ball_shadow.keyframe_insert('location',frame=f)


world = bpy.data.worlds.new('Warm stage surround')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.12,.09,.06,1)
scene.world = world


def camera(name, x, z, width):
    data = bpy.data.cameras.new(name)
    ob = bpy.data.objects.new(name,data)
    scene.collection.objects.link(ob)
    ob.location = (x,-15,z)
    ob.rotation_euler = (Vector((x,0,z))-ob.location).to_track_quat('-Z','Y').to_euler()
    data.type = 'ORTHO';data.ortho_scale = width
    return ob


cameras = [camera('Camera | arrival',0,2.075,12),
           camera('Camera | invitation',.1,1.72,9.8),
           camera('Camera | friends',.15,1.85,10.5)]
for f, cam in [(1,cameras[0]),(97,cameras[1]),(217,cameras[2])]:
    marker = scene.timeline_markers.new(cam.name,frame=f)
    marker.camera = cam
scene.camera = cameras[0]
for f, width in [(217,10.5),(290,10.5),(384,8.8)]:
    cameras[2].data.ortho_scale = width
    cameras[2].data.keyframe_insert('ortho_scale',frame=f)
for f, height in [(217,1.85),(290,1.85),(384,1.62)]:
    cameras[2].location.z = height
    cameras[2].keyframe_insert('location',frame=f)
for f,label in motion.BEATS:
    scene.timeline_markers.new(label,frame=f)


title_data = bpy.data.curves.new('A Little Brave | title','FONT')
title_data.body = 'A Little Brave'
title_data.align_x = 'CENTER'
title_data.size = .24
title_data.font = bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Georgia Italic.ttf')
title_data.font.pack()
title = bpy.data.objects.new('Title | A Little Brave',title_data)
scene.collection.objects.link(title)
title.location = (.15,-1,-.43)
title.rotation_euler = (math.pi/2,0,0)
title_material = flat('Title | warm ink',(.25,.16,.085))
title_data.materials.append(title_material)
tn = title_material.node_tree.nodes
tl = title_material.node_tree.links
te = next(n for n in tn if n.type == 'EMISSION')
to = next(n for n in tn if n.type == 'OUTPUT_MATERIAL')
tt = tn.new('ShaderNodeBsdfTransparent')
tm = tn.new('ShaderNodeMixShader')
tl.new(tt.outputs[0],tm.inputs[1]);tl.new(te.outputs[0],tm.inputs[2]);tl.new(tm.outputs[0],to.inputs['Surface'])
for f, alpha in [(1,0),(347,0),(372,1),(384,1)]:
    tm.inputs[0].default_value = alpha
    tm.inputs[0].keyframe_insert('default_value',frame=f)

sound = scene.sequence_editor_create().strips.new_sound('Score | original piano and celesta',str(SCORE),channel=1,frame_start=1)
sound.sound.pack()
scene.render.use_sequencer = False
scene.sync_mode = 'AUDIO_SYNC'

for name, objects in [
    ('01 Biscuit',list(puppy['parts'].values())+[puppy['root']]),
    ('02 Bruno',list(bruno['parts'].values())+[bruno['root']]),
    ('03 Park',[ob for ob in scene.objects if ob.name.startswith('Set |')]),
    ('04 Ball',[ob for ob in scene.objects if ob.name.startswith('Prop |')]),
    ('05 Cameras',cameras),('06 Title',[title])]:
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    for ob in objects:
        for previous in list(ob.users_collection):
            previous.objects.unlink(ob)
        collection.objects.link(ob)

for dog in [puppy,bruno]:
    rig = dog['rig']
    for previous in list(rig.data.collections):
        rig.data.collections.remove(previous)
    controls = rig.data.collections.new('Animation controls')
    deformation = rig.data.collections.new('Deformation bones')
    for bone in rig.data.bones:
        (controls if bone.name.startswith(('CTRL.','ROOT','BODY','HEAD','ear.','tail.')) else deformation).assign(bone)
    deformation.is_visible = False
    rig['controls'] = 'ROOT: travel and height; BODY/HEAD: pitch; CTRL.paw.*: planted feet; ear/tail: follow-through. Rotations use local pose space.'

readme = bpy.data.texts.new('START HERE')
readme.write('A LITTLE BRAVE\n\n16 seconds / 24 FPS / 1920 x 1080\n\nSpace: play the authored scene with the packed original score.\nNumpad 0: camera. Z then M: material preview.\n\nCollections 01 and 02 contain the character stage placements, painted meshes and armatures. Select an armature and enter Pose Mode to inspect ROOT, BODY, HEAD and CTRL.paw.*. The performance is baked to native editable keys. Eye and folded-leg drawings use keyed visibility. All pictures, the font and soundtrack are packed.\n\nThe scene uses native Blender animation. The artwork is generated still imagery; no image-to-video or generated intermediate frames are used.\n')

source_archive = OUT/'source'
source_archive.mkdir(exist_ok=True)
for name in ['build_film.py','choreography.py','render_film.py','build_rottweiler.py','gaze.py']:
    shutil.copy2(ROOT/name,source_archive/name)


metrics = []
for f in range(1,motion.FRAMES+1):
    scene.frame_set(f)
    row = {'frame':f,'dogs':{}}
    for dog in [puppy,bruno]:
        rig = dog['rig']
        paws = {}
        for name in motion.LEGS:
            actual = rig.matrix_world @ rig.pose.bones['paw.'+name].head
            target = rig.matrix_world @ rig.pose.bones['CTRL.paw.'+name].head
            paws[name] = {'actual':list(actual),'target':list(target),'error':(actual-target).length}
        # Painted nose landmarks in each saved character's rest coordinates.
        point = Vector((1.432,0,1.764)) if dog is puppy else Vector((1.372,0,1.912))
        transform = rig.matrix_world @ rig.pose.bones['HEAD'].matrix @ rig.data.bones['HEAD'].matrix_local.inverted()
        nose = transform @ point
        row['dogs'][dog['name']] = {'paws':paws,'nose':list(nose)}
    a,b = (Vector(row['dogs'][n]['nose']) for n in ['Biscuit','Bruno'])
    row['nose_distance_in_picture_plane'] = math.hypot(a.x-b.x,a.z-b.z)
    metrics.append(row)
maximum = max(paw['error'] for row in metrics for dog in row['dogs'].values() for paw in dog['paws'].values())
report = {'frames':motion.FRAMES,'fps':motion.FPS,'maximum_paw_error':maximum,
          'final_nose_distance':metrics[-1]['nose_distance_in_picture_plane'],'samples':metrics}
(OUT/'motion-verification.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'manifest.json').write_text(json.dumps({'version':args.version,'blender':bpy.app.version_string,
    'frames':motion.FRAMES,'fps':motion.FPS,'characters':[str(PUPPY_SCENE),str(BRUNO_SCENE)],
    'background':str(PARK),'packed_images':len([im for im in bpy.data.images if im.packed_file])},indent=2)+'\n')
print('MOTION_CHECK', maximum, report['final_nose_distance'],flush=True)

scene.frame_set(1)
scene.camera = cameras[0]
bpy.ops.object.select_all(action='DESELECT')
puppy['rig'].select_set(True)
bpy.context.view_layer.objects.active = puppy['rig']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.shading.type = 'MATERIAL'
            area.spaces.active.overlay.show_overlays = False
scene['description'] = 'A Little Brave: two painted 2D rigs, authored contacts and a continuous dog-park scene.'
scene.render.filepath = str(OUT/'frames/frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'a-little-brave.blend'))
if args.frames:
    scene.cycles.samples = 16
    scene.render.resolution_percentage = args.percentage
    for f in map(int,args.frames.split(',')):
        scene.frame_set(f)
        scene.render.filepath = str(OUT/'stills'/f'frame_{f:04d}.png')
        bpy.ops.render.render(write_still=True)
