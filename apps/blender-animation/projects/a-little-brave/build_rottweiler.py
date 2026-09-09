"""Author Bruno's native 2D rig from the Rottweiler's keyed painted parts."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Quaternion, Matrix

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets/rottweiler'
HEAD_OFFSET=(-.20,-.14)
SOURCE=ROOT.parent/'playful-puppy/output/v003/playful-puppy.blend'
P=argparse.ArgumentParser()
P.add_argument('--version',default='v001')
P.add_argument('--frames',default='')
args=P.parse_args(sys.argv[sys.argv.index('--')+1:])
OUT=ROOT/'output'/args.version
assert not (OUT/'puppy-2d.blend').exists(), 'Preserve the old scene: use a new version'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
with bpy.data.libraries.load(str(SOURCE)) as (src,dst):
    dst.objects=['BISCUIT | pose controls']
rig=dst.objects[0]; scene.collection.objects.link(rig)
rig.name='BRUNO 2D | pose controls'; rig.show_in_front=True
scene.render.engine='CYCLES'; scene.cycles.samples=16
scene.cycles.use_denoising=False
scene.cycles.transparent_max_bounces=24
scene.render.resolution_x=1920; scene.render.resolution_y=1080
scene.render.resolution_percentage=100
scene.render.fps=24; scene.frame_start=1; scene.frame_end=72
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGB'
scene.view_settings.view_transform='Standard'
scene.render.film_transparent=False

def fcurves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                yield from bag.fcurves

def frame30(f): return 1+(f-1)*.8

action=rig.animation_data.action
action.name='2D | bow, hop, settle'
for fc in fcurves(action):
    for key in fc.keyframe_points:
        key.co.x=frame30(key.co.x)
        key.handle_left.x=frame30(key.handle_left.x)
        key.handle_right.x=frame30(key.handle_right.x)

# In profile, stagger the distant legs horizontally to keep four paws readable.
bpy.context.view_layer.objects.active=rig; rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for bone in rig.data.edit_bones:
    if bone.name.endswith('.far') and 'ear' not in bone.name:
        bone.head.x-=.14; bone.tail.x-=.14
for name in ['ear.near','ear.far']:
    b=rig.data.edit_bones[name]
    b.head=(.62,b.head.y,2.27)
    b.tail=(.40,b.tail.y,1.78)
tip=rig.data.edit_bones.new('ear.tip')
tip.head=(.46,-.34,2.05);tip.tail=(.40,-.34,1.68)
tip.parent=rig.data.edit_bones['ear.near']
bpy.ops.object.mode_set(mode='OBJECT'); rig.select_set(False)

def key_pitch(name,f,pitch):
    pb=rig.pose.bones[name]; rest=rig.data.bones[name].matrix_local.to_quaternion()
    pb.rotation_mode='QUATERNION'
    pb.rotation_quaternion=rest.inverted() @ Quaternion((0,1,0),math.radians(pitch)) @ rest
    pb.keyframe_insert('rotation_quaternion',frame=frame30(f),group=name)

# Head leads the invitation and follows the landing, independently of the spine.
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fc in list(bag.fcurves):
                if fc.data_path.startswith('pose.bones["HEAD"]'):
                    bag.fcurves.remove(fc)
for f,p in [(1,-3),(7,-3),(13,8),(19,-8),(24,-29),(33,-34),
            (39,-21),(43,-6),(48,-2),(55,-6),(60,1),(65,-5),
            (69,2),(74,-10),(81,-2),(86,-5),(90,-5)]:
    key_pitch('HEAD',f,p)
for f in range(1,91,3):
    key_pitch('tail.01',f,9*math.sin((f-1)*.32))
    key_pitch('tail.02',f,12*math.sin((f-4)*.32))
for side in ['near','far']:
    for f,p in [(1,0),(10,4),(26,-11),(35,-7),(44,5),(51,25),(57,17),
                (64,-20),(69,-27),(74,13),(80,-5),(86,1),(90,0)]:
        key_pitch('ear.'+side,f,p)
for f,p in [(1,0),(12,2),(24,-6),(31,3),(39,0),(47,-6),(54,15),
            (60,10),(66,-11),(71,-17),(77,12),(83,-5),(90,0)]:
    key_pitch('ear.tip',f,p)
for fc in fcurves(action):
    for k in fc.keyframe_points:
        k.handle_left_type=k.handle_right_type='AUTO_CLAMPED'

def mat_image(name,path,tint=(1,1,1),fade_root=False):
    m=bpy.data.materials.new(name); m.use_nodes=True
    tree=m.node_tree; tree.nodes.clear()
    out=tree.nodes.new('ShaderNodeOutputMaterial')
    mix=tree.nodes.new('ShaderNodeMixShader')
    trans=tree.nodes.new('ShaderNodeBsdfTransparent')
    emit=tree.nodes.new('ShaderNodeEmission'); emit.inputs['Strength'].default_value=1
    tex=tree.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(path),check_existing=True)
    tex.image.pack(); tex.interpolation='Linear'; tex.extension='CLIP'
    mul=tree.nodes.new('ShaderNodeMixRGB'); mul.blend_type='MULTIPLY'; mul.inputs[0].default_value=1
    mul.inputs[2].default_value=(*tint,1)
    tree.links.new(tex.outputs['Color'],mul.inputs[1]);tree.links.new(mul.outputs[0],emit.inputs['Color'])
    alpha=tex.outputs['Alpha']
    # The still generator supplied RGB. Chroma removal remains editable in Blender.
    rgb=tree.nodes.new('ShaderNodeSeparateColor');rgb.mode='RGB'
    tree.links.new(tex.outputs['Color'],rgb.inputs['Color'])
    red=tree.nodes.new('ShaderNodeMath');red.operation='SUBTRACT'
    blue=tree.nodes.new('ShaderNodeMath');blue.operation='SUBTRACT'
    tree.links.new(rgb.outputs['Red'],red.inputs[0]);tree.links.new(rgb.outputs['Green'],red.inputs[1])
    tree.links.new(rgb.outputs['Blue'],blue.inputs[0]);tree.links.new(rgb.outputs['Green'],blue.inputs[1])
    chroma=tree.nodes.new('ShaderNodeMath');chroma.operation='MINIMUM'
    tree.links.new(red.outputs[0],chroma.inputs[0]);tree.links.new(blue.outputs[0],chroma.inputs[1])
    matte=tree.nodes.new('ShaderNodeMapRange');matte.clamp=True
    matte.inputs['From Min'].default_value=.04;matte.inputs['From Max'].default_value=.72
    matte.inputs['To Min'].default_value=1;matte.inputs['To Max'].default_value=0
    tree.links.new(chroma.outputs[0],matte.inputs['Value'])
    edge=tree.nodes.new('ShaderNodeMath');edge.operation='MULTIPLY'
    tree.links.new(matte.outputs[0],edge.inputs[0]);tree.links.new(tex.outputs['Alpha'],edge.inputs[1])
    alpha=edge.outputs[0]
    key=tree.nodes.new('ShaderNodeMath');key.operation='SUBTRACT';key.inputs[0].default_value=1
    tree.links.new(matte.outputs[0],key.inputs[1])
    spill=tree.nodes.new('ShaderNodeVectorMath');spill.operation='SCALE';spill.inputs[0].default_value=(1,0,1)
    tree.links.new(key.outputs[0],spill.inputs['Scale'])
    clean=tree.nodes.new('ShaderNodeVectorMath');clean.operation='SUBTRACT'
    tree.links.new(tex.outputs['Color'],clean.inputs[0]);tree.links.new(spill.outputs[0],clean.inputs[1])
    limit=tree.nodes.new('ShaderNodeMath');limit.operation='MAXIMUM';limit.inputs[1].default_value=.001
    tree.links.new(matte.outputs[0],limit.inputs[0])
    inv=tree.nodes.new('ShaderNodeMath');inv.operation='DIVIDE';inv.inputs[0].default_value=1
    tree.links.new(limit.outputs[0],inv.inputs[1])
    unmix=tree.nodes.new('ShaderNodeVectorMath');unmix.operation='SCALE'
    tree.links.new(clean.outputs[0],unmix.inputs[0]);tree.links.new(inv.outputs[0],unmix.inputs['Scale'])
    edge_weight=tree.nodes.new('ShaderNodeMapRange');edge_weight.clamp=True
    edge_weight.label='Keep the painted outline neutral at keyed edges'
    edge_weight.inputs['From Min'].default_value=.85
    edge_weight.inputs['From Max'].default_value=1
    edge_weight.inputs['To Min'].default_value=1
    edge_weight.inputs['To Max'].default_value=0
    tree.links.new(matte.outputs[0],edge_weight.inputs['Value'])
    outline=tree.nodes.new('ShaderNodeMixRGB')
    outline.inputs[2].default_value=(.018,.012,.007,1)
    tree.links.new(edge_weight.outputs[0],outline.inputs[0])
    tree.links.new(unmix.outputs[0],outline.inputs[1])
    tree.links.new(outline.outputs[0],mul.inputs[1])
    if name=='Drawing | attentive':
        # Blend the deliberately open jaw base into the overlapping neck artwork.
        uv=tree.nodes.new('ShaderNodeTexCoord');sep=tree.nodes.new('ShaderNodeSeparateXYZ')
        tree.links.new(uv.outputs['UV'],sep.inputs[0])
        fades=[]
        for channel,start,end in [('Y',.005,.09),('X',.53,.70)]:
            fade=tree.nodes.new('ShaderNodeMapRange');fade.clamp=True
            fade.inputs['From Min'].default_value=start;fade.inputs['From Max'].default_value=end
            tree.links.new(sep.outputs[channel],fade.inputs['Value']);fades.append(fade.outputs[0])
        keep=tree.nodes.new('ShaderNodeMath');keep.operation='MAXIMUM'
        tree.links.new(fades[0],keep.inputs[0]);tree.links.new(fades[1],keep.inputs[1])
        mult=tree.nodes.new('ShaderNodeMath');mult.operation='MULTIPLY'
        tree.links.new(alpha,mult.inputs[0]);tree.links.new(keep.outputs[0],mult.inputs[1]);alpha=mult.outputs[0]
    if path.name in ['front_leg.png','front_leg_bow.png','front_paw.png']:
        uv=tree.nodes.new('ShaderNodeTexCoord');sep=tree.nodes.new('ShaderNodeSeparateXYZ');tree.links.new(uv.outputs['UV'],sep.inputs[0])
        cut=tree.nodes.new('ShaderNodeMapRange');cut.clamp=True
        if path.name=='front_leg.png':
            cut.inputs['From Min'].default_value=.15;cut.inputs['From Max'].default_value=.24
            cut.inputs['To Min'].default_value=0;cut.inputs['To Max'].default_value=1
            tree.links.new(sep.outputs['Y'],cut.inputs['Value'])
        elif path.name=='front_leg_bow.png':
            cut.inputs['From Min'].default_value=.52;cut.inputs['From Max'].default_value=.65
            cut.inputs['To Min'].default_value=1;cut.inputs['To Max'].default_value=0
            tree.links.new(sep.outputs['X'],cut.inputs['Value'])
        else:
            cut.inputs['From Min'].default_value=.90;cut.inputs['From Max'].default_value=1
            cut.inputs['To Min'].default_value=1;cut.inputs['To Max'].default_value=0
            tree.links.new(sep.outputs['Y'],cut.inputs['Value'])
        mult=tree.nodes.new('ShaderNodeMath');mult.operation='MULTIPLY'
        tree.links.new(alpha,mult.inputs[0]);tree.links.new(cut.outputs[0],mult.inputs[1]);alpha=mult.outputs[0]
    if name=='Drawing | delighted eyes':
        uv=tree.nodes.new('ShaderNodeTexCoord')
        sub=tree.nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.685,.705,0)
        scale=tree.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(1/.125,1/.14,1)
        length=tree.nodes.new('ShaderNodeVectorMath');length.operation='LENGTH'
        mask=tree.nodes.new('ShaderNodeMapRange');mask.inputs['From Min'].default_value=.78;mask.inputs['From Max'].default_value=1
        mask.inputs['To Min'].default_value=1;mask.inputs['To Max'].default_value=0;mask.clamp=True
        tree.links.new(uv.outputs['UV'],sub.inputs[0]);tree.links.new(sub.outputs[0],scale.inputs[0])
        tree.links.new(scale.outputs[0],length.inputs[0]);tree.links.new(length.outputs['Value'],mask.inputs['Value'])
        mult=tree.nodes.new('ShaderNodeMath');mult.operation='MULTIPLY'
        tree.links.new(alpha,mult.inputs[0]);tree.links.new(mask.outputs[0],mult.inputs[1]);alpha=mult.outputs[0]
    if fade_root:
        uv=tree.nodes.new('ShaderNodeTexCoord'); sep=tree.nodes.new('ShaderNodeSeparateXYZ')
        tree.links.new(uv.outputs['UV'],sep.inputs[0])
        ramp=tree.nodes.new('ShaderNodeMapRange')
        ramp.inputs['From Min'].default_value=.77; ramp.inputs['From Max'].default_value=.98
        ramp.inputs['To Min'].default_value=1; ramp.inputs['To Max'].default_value=0
        ramp.clamp=True; tree.links.new(sep.outputs['Y'],ramp.inputs['Value'])
        mult=tree.nodes.new('ShaderNodeMath'); mult.operation='MULTIPLY'
        tree.links.new(alpha,mult.inputs[0]);tree.links.new(ramp.outputs[0],mult.inputs[1]);alpha=mult.outputs[0]
    tree.links.new(alpha,mix.inputs[0]);tree.links.new(trans.outputs[0],mix.inputs[1])
    tree.links.new(emit.outputs[0],mix.inputs[2]);tree.links.new(mix.outputs[0],out.inputs['Surface'])
    return m

def clamp(v):return max(0,min(1,v))
def smooth(a,b,v):
    t=clamp((v-a)/(b-a));return t*t*(3-2*t)

def mesh_piece(name,path,mapper,weights,depth,tint=(1,1,1),fade_root=False,nx=24,ny=32,bake_pose=False):
    verts=[];faces=[];uvs=[]
    for j in range(ny+1):
        for i in range(nx+1):
            u,v=i/nx,j/ny
            x,z=mapper(u,v);verts.append((x,depth-(.025*v if 'leg' in path.stem else 0),z));uvs.append((u,1-v))
    for j in range(ny):
        for i in range(nx):
            k=j*(nx+1)+i;faces.extend([(k,k+1,k+nx+2),(k,k+nx+2,k+nx+1)])
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob)
    uv=data.uv_layers.new(name='Painted artwork UV')
    for poly in data.polygons:
        for li in poly.loop_indices:uv.data[li].uv=uvs[data.loops[li].vertex_index]
    data.materials.append(mat_image(name,path,tint,fade_root))
    groups={}
    for n,(x,y,z) in enumerate(verts):
        u,v=uvs[n][0],1-uvs[n][1]
        assignments=weights(u,v,x,z)
        for group,w in assignments.items():
            if w>.00001:
                if group not in groups:groups[group]=ob.vertex_groups.new(name=group)
                groups[group].add([n],w,'REPLACE')
        if bake_pose:
            deform=Matrix.Identity(4)*0
            for group,w in assignments.items():
                deform += (rig.pose.bones[group].matrix @ rig.data.bones[group].matrix_local.inverted())*w
            data.vertices[n].co=deform.inverted() @ Vector((x,y,z))
    mod=ob.modifiers.new('2D skeleton deformation','ARMATURE');mod.object=rig
    mod.use_deform_preserve_volume=False
    return ob

def rect(x0,x1,z0,z1):return lambda u,v:(x0+(x1-x0)*u,z1-(z1-z0)*v)
def rigid(bone):return lambda u,v,x,z:{bone:1}

def body_weights(u,v,x,z):
    neck=smooth(.0,.55,x)*smooth(1.08,1.62,z)
    return {'BODY':1-neck,'HEAD':neck}
def body_map(u,v):
    x,z=rect(-1.03,.78,.65,1.74)(u,v)
    extension=smooth(.53,.85,u)*smooth(.90,.30,v)
    return x+.14*extension,z+.06*extension
body=mesh_piece('Paint | torso',ASSETS/'body.png',body_map,body_weights,0)

# Atlas centerline landmarks are mapped to the skeleton in its rest pose.
def leg_mapper(name):
    front=name.startswith('front'); dx=-.14 if name.endswith('far') else 0
    if front:
        anchors=[(0,126,.53,1.40),(65,126,.53,1.24),(255,66,.39,.69),(410,104,.58,.20),(531,154,.66,-.19)]
        width,height=250,531
    else:
        anchors=[(0,126,-.64,1.34),(80,126,-.64,1.15),(235,163,-.38,.66),(425,115,-.66,.20),(511,163,-.57,-.015)]
        width,height=282,511
    def mapper(u,v):
        yy=v*height
        for a,b in zip(anchors,anchors[1:]):
            if yy<=b[0]+.001:
                t=(yy-a[0])/(b[0]-a[0]); xp=a[1]+t*(b[1]-a[1]); x=a[2]+t*(b[2]-a[2]);z=a[3]+t*(b[3]-a[3])
                return x+(u*width-xp)*.0028+dx,z
        raise ValueError(yy)
    def weights(u,v,x,z):
        elbow=(255 if front else 235)/height;ankle=(410 if front else 425)/height
        lower=smooth(elbow-.10,elbow+.10,v);paw=smooth(ankle-.045,ankle+.045,v)
        return {'upper.'+name:1-lower,'lower.'+name:lower*(1-paw),'paw.'+name:lower*paw}
    return mapper,weights
leg_objects={}
for name in ['front.far','back.far','back.near','front.near']:
    far=name.endswith('far');mapper,weights=leg_mapper(name)
    leg_objects[name]=mesh_piece('Paint | '+name,ASSETS/('front_leg.png' if name.startswith('front') else 'hind_leg.png'),
               mapper,weights,.08 if far else -.025,tint=(.88,.82,.74) if far else (1,1,1),fade_root=not far)
    if name.startswith('front'):
        ankle=rig.data.bones['paw.'+name].head_local
        paw_map=rect(ankle.x-.14,ankle.x+.36,-.01,.29)
        mesh_piece('Paint | shared paw '+name,ASSETS/'paw_clean.png',paw_map,rigid('paw.'+name),
                   .02 if far else -.065,tint=(.88,.82,.74) if far else (1,1,1),nx=10,ny=10)

def drawing_swap(normal,replacement,keys):
    for f,on in keys:
        for ob,hidden in [(normal,on),(replacement,not on)]:
            ob.hide_render=hidden;ob.hide_viewport=hidden
            ob.keyframe_insert('hide_render',frame=f);ob.keyframe_insert('hide_viewport',frame=f)
    for ob in [normal,replacement]:
        for fc in fcurves(ob.animation_data.action):
            for k in fc.keyframe_points:k.interpolation='CONSTANT'

scene.frame_set(20)
for name in ['front.near','front.far']:
    a=rig.pose.bones['upper.'+name].head; b=rig.pose.bones['lower.'+name].head; c=rig.pose.bones['paw.'+name].head
    def bow_weights(u,v,x,z,name=name):
        lower=smooth(.59,.81,v);paw=smooth(.58,.77,u)*smooth(.67,.83,v)
        return {'upper.'+name:(1-lower)*(1-paw),'lower.'+name:lower*(1-paw),'paw.'+name:paw}
    far=name.endswith('far')
    left,right,top=b.x-.13,c.x+.34,a.z+.12
    def bow_map(u,v,left=left,right=right,top=top):
        z=top-(top-.24)*(v/.8) if v<=.8 else .24*(1-v)/.2
        return left+(right-left)*u,z
    alt=mesh_piece('Drawing | folded '+name,ASSETS/'front_leg_bow.png',
        bow_map,bow_weights,.08 if far else -.026,
        tint=(.88,.82,.74) if far else (1,1,1),fade_root=not far,bake_pose=True)
    drawing_swap(leg_objects[name],alt,[(1,False),(16,False),(17,True),(28,True),(29,False),(72,False)])
scene.frame_set(1)

head_box=rect(.22,1.42,1.20,2.39)
head=mesh_piece('Drawing | attentive',ASSETS/'head.png',head_box,rigid('HEAD'),-.10)
happy=mesh_piece('Drawing | delighted eyes',ASSETS/'head-delighted.png',head_box,rigid('HEAD'),-.11)
# Discrete, held drawing replacements; no dissolve between facial expressions.
expression=[(1,False),(19,False),(20,True),(21,True),(22,False),(54,False),(55,True),(56,True),(57,False),(72,False)]
drawing_swap(head,happy,expression)
head.animation_data_clear();head.hide_render=False;head.hide_viewport=False

def ear_weights(u,v,x,z):
    root=1-smooth(.02,.25,v)
    tip=smooth(.40,.90,v)
    return {'HEAD':root,'ear.near':(1-root)*(1-tip),'ear.tip':(1-root)*tip}
ear=mesh_piece('Paint | floppy ear',ASSETS/'ear.png',
    rect(.35,.69,1.78,2.30),ear_weights,-.16)
def tail_map(u,v):return (-.67-1.0*u,1.21+.93*(1-v))
def tail_weights(u,v,x,z):
    w=smooth(.30,.75,u);return {'tail.01':1-w,'tail.02':w}
tail=mesh_piece('Paint | tail',ASSETS/'tail.png',tail_map,tail_weights,.04)

paper=(.93,.88,.77,1)
world=bpy.data.worlds.new('Paper backdrop');world.use_nodes=True;scene.world=world
world.node_tree.nodes['Background'].inputs[0].default_value=paper
world.node_tree.nodes['Background'].inputs[1].default_value=1

# A soft drawn contact shadow, flattened in the same picture plane.
shadow_mat=bpy.data.materials.new('Warm soft contact shadow');shadow_mat.use_nodes=True
nodes=shadow_mat.node_tree.nodes;nodes.clear();links=shadow_mat.node_tree.links
out=nodes.new('ShaderNodeOutputMaterial');emit=nodes.new('ShaderNodeEmission')
tex=nodes.new('ShaderNodeTexCoord');distance=nodes.new('ShaderNodeVectorMath');distance.operation='DISTANCE'
distance.inputs[1].default_value=(.5,.5,0);links.new(tex.outputs['UV'],distance.inputs[0])
ramp=nodes.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=.0;ramp.inputs['From Max'].default_value=.50
ramp.inputs['To Min'].default_value=.19;ramp.inputs['To Max'].default_value=0;ramp.clamp=True
links.new(distance.outputs['Value'],ramp.inputs['Value'])
mixcolor=nodes.new('ShaderNodeMixRGB');mixcolor.inputs[1].default_value=paper;mixcolor.inputs[2].default_value=(.43,.31,.17,1)
links.new(ramp.outputs[0],mixcolor.inputs[0]);links.new(mixcolor.outputs[0],emit.inputs['Color']);links.new(emit.outputs[0],out.inputs['Surface'])
mesh=bpy.data.meshes.new('Contact shadow');mesh.from_pydata([(-1.4,.2,-.07),(1.4,.2,-.07),(1.4,.2,.13),(-1.4,.2,.13)],[],[(0,1,2,3)])
shadow=bpy.data.objects.new('Drawn contact shadow',mesh);scene.collection.objects.link(shadow);mesh.materials.append(shadow_mat)
uv=mesh.uv_layers.new();
for loop,coord in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=coord
for f,x,z in [(1,0,0),(43,-.035,-.22),(48,.015,.03),(55,.20,.48),(60,.34,.40),(65,.43,.09),(69,.46,-.19),(90,.46,0)]:
    shadow.location.x=x;shadow.scale.x=1-max(0,z)*.22
    shadow.keyframe_insert('location',frame=frame30(f));shadow.keyframe_insert('scale',frame=frame30(f))

data=bpy.data.cameras.new('Orthographic 2D camera');camera=bpy.data.objects.new('Orthographic 2D camera',data)
scene.collection.objects.link(camera);scene.camera=camera
camera.location=(.10,-12,1.52);camera.rotation_euler=(Vector((.10,0,1.52))-camera.location).to_track_quat('-Z','Y').to_euler()
data.type='ORTHO';data.ortho_scale=6.6
for f,label in [(1,'Notice'),(19,'Play bow | drawing swap'),(34,'Gather'),(39,'Push off'),(44,'Airborne'),(52,'Land'),(57,'Recovery'),(67,'Settle')]:
    scene.timeline_markers.new(label,frame=f)
scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
scene['description']='2D skinned painted parts with discrete expression replacement drawings. Native Blender keys and rendering.'
scene.render.filepath=str(OUT/'frames/frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'puppy-2d.blend'))
(OUT/'manifest.json').write_text(json.dumps({'version':args.version,'blender':bpy.app.version_string,
    'frames':72,'fps':24,'source_rig':str(SOURCE),'expression_keys':expression,'packed_images':len([im for im in bpy.data.images if im.packed_file])},indent=2)+'\n')
if args.frames:
    for f in map(int,args.frames.split(',')):
        scene.frame_set(f);scene.render.filepath=str(OUT/'stills'/f'frame_{f:04d}.png')
        bpy.ops.render.render(write_still=True)
