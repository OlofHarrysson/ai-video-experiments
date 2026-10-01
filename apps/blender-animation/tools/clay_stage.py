"""Reusable clay-puppet construction and deterministic two-link posing for Blender.

Run inside Blender's Python. Every rendered pose is baked to ordinary object keys;
saved scenes need no scripts, handlers, add-ons or external image assets to play.
"""
import math
import bpy
from mathutils import Vector, Euler


def clay(name, color, roughness=.68, texture=True):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    if texture:
        noise = tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 72
        noise.inputs['Detail'].default_value = 2
        bump = tree.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .2
        bump.inputs['Distance'].default_value = .025
        tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
        tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return mat


def empty(name, parent=None):
    ob = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(ob)
    ob.empty_display_type = 'SPHERE'
    ob.empty_display_size = .09
    ob.parent = parent
    return ob


def ellipsoid(name, location, scale, material, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16)
    ob = bpy.context.object
    ob.name = name
    ob.parent = parent
    ob.location, ob.scale = location, scale
    ob.data.materials.append(material)
    for face in ob.data.polygons:
        face.use_smooth = True
    return ob


def curve(name, points, radius, material, parent=None):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth, data.bevel_resolution = radius, 3
    poly = data.splines.new('POLY')
    poly.points.add(len(points)-1)
    for p, co in zip(poly.points, points):
        p.co = (*co, 1)
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = parent
    ob.data.materials.append(material)
    return ob


def two_link(a, b, length_a, length_b, pole):
    """Analytic IK with explicit reach validation, no stretch or silent clamping."""
    a, b, pole = Vector(a), Vector(b), Vector(pole)
    delta = b-a
    distance = delta.length
    if not abs(length_a-length_b)+1e-5 < distance < length_a+length_b-1e-5:
        raise ValueError(f'Unreachable limb target: {distance:.4f} / {length_a+length_b:.4f}')
    direction = delta.normalized()
    bend = pole - direction * pole.dot(direction)
    if bend.length < 1e-5:
        raise ValueError('IK pole is parallel to the limb')
    along = (length_a**2-length_b**2+distance**2)/(2*distance)
    height = math.sqrt(max(0, length_a**2-along**2))
    return a + direction*along + bend.normalized()*height


def key(ob, frame, paths=('location', 'rotation_euler', 'scale')):
    for path in paths:
        ob.keyframe_insert(data_path=path, frame=frame)


def segment_pose(ob, a, b, radius, frame):
    a, b = Vector(a), Vector(b)
    ob.location = (a+b)/2
    ob.rotation_mode = 'QUATERNION'
    q = (b-a).to_track_quat('Z', 'Y')
    # Keep quaternion signs continuous for optional linear interpolation.
    if ob.rotation_quaternion.dot(q) < 0:
        q = -q
    ob.rotation_quaternion = q
    ob.scale = (radius, radius, (b-a).length/2 + radius*.32)
    key(ob, frame, ('location', 'rotation_quaternion', 'scale'))


def set_interpolation(mode='CONSTANT'):
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fcurve in bag.fcurves:
                        for point in fcurve.keyframe_points:
                            point.interpolation = mode


class Puppet:
    """Jointed clay creature. Foot/hand targets are independent of body motion."""
    def __init__(self, name, species, position, coat, accent):
        self.name, self.species = name, species
        self.stage = empty(name+' | stage')
        self.stage.location = position
        self.body = empty(name+' | pelvis & chest', self.stage)
        self.head = empty(name+' | head', self.stage)
        self.cream = clay(name+' | vanilla clay', (.85, .71, .49))
        self.coat, self.accent = coat, accent
        self.dark = clay(name+' | cocoa eyes', (.022, .014, .02), .24, False)
        self.glint = clay(name+' | catchlights', (.95, .92, .84), .18, False)
        self.blush = clay(name+' | rosy cheeks', (.59, .15, .12))
        ellipsoid(name+' belly', (0, 0, .22), (.43, .31, .56), coat, self.body)
        ellipsoid(name+' tummy patch', (0, -.267, .22), (.28, .075, .36), self.cream, self.body)
        # Scarf collar and little asymmetric hanging ends.
        ellipsoid(name+' collar', (0, -.005, .65), (.30, .29, .10), accent, self.body)
        tail = ellipsoid(name+' scarf end', (.24, .03, .41), (.11, .075, .28), accent, self.body)
        tail.rotation_euler[1] = -.3
        ellipsoid(name+' head', (0, 0, 0), (.49, .37, .46), coat, self.head)
        self.eyes=[]
        for sign in [-1, 1]:
            ellipsoid(name+f' muzzle {sign}', (sign*.105, -.335, -.115), (.16, .095, .12), self.cream, self.head)
            eye = ellipsoid(name+f' eye {sign}', (sign*.19, -.335, .09), (.055, .035, .08), self.dark, self.head)
            glint=ellipsoid(name+f' glint {sign}', (sign*.19-.014, -.366, .117), (.017, .009, .02), self.glint, self.head)
            self.eyes.append((eye,glint))
            ellipsoid(name+f' cheek {sign}', (sign*.32, -.283, -.07), (.065, .02, .045), self.blush, self.head)
            curve(name+f' brow {sign}', [(sign*.19 + d*.05, -.326, .23 + .018*(1-d*d)) for d in [-1,0,1]], .017, self.dark, self.head)
        ellipsoid(name+' nose', (0, -.433, -.06), (.076, .046, .052), self.dark, self.head)
        curve(name+' smile', [(x*.16, -.399, -.18-.035*(1-x*x)) for x in [-1,-.5,0,.5,1]], .013, self.dark, self.head)
        self.ears=[]
        for sign in [-1,1]:
            ear=empty(name+f' | ear {sign}',self.head)
            if species == 'rabbit':
                ear.location=(sign*.26,.01,.32)
                ellipsoid(name+f' long ear {sign}', (0,0,.36), (.125,.12,.48),coat,ear)
                ellipsoid(name+f' inner ear {sign}', (0,-.105,.38), (.065,.022,.31),accent,ear)
            else:
                ear.location=(sign*.4,0,.22)
                ellipsoid(name+f' floppy ear {sign}', (sign*.055,.005,-.25), (.17,.125,.36),accent,ear)
            self.ears.append(ear)
        ellipsoid(name+' tail', (0,.36,-.06), (.16,.26,.15), coat,self.body)
        self.limbs={}
        for kind in ['leg','arm']:
            for sign in [-1,1]:
                prefix=name+f' {kind} {sign}'
                parts=[ellipsoid(prefix+' '+part,(0,0,0),(1,1,1),coat if part=='upper' else self.cream,self.stage) for part in ['upper','lower']]
                joint=ellipsoid(prefix+' joint',(0,0,0),(.12,.12,.12),coat,self.stage)
                tip=ellipsoid(prefix+' '+('shoe' if kind=='leg' else 'mitten'),(0,0,0),(.195,.29,.125) if kind=='leg' else (.14,.12,.17),accent if kind=='leg' else self.cream,self.stage)
                self.limbs[kind,sign]=(*parts,joint,tip)

    def pose(self, state, frame):
        self.body.location=state['root']
        self.body.rotation_euler=state['torso']
        rotation=Euler(state['torso']).to_matrix()
        root=Vector(state['root'])
        self.head.location=root+rotation@Vector((0,0,.92))
        self.head.rotation_euler=state['head']
        key(self.body,frame); key(self.head,frame)
        for eye,glint in self.eyes:
            blink=state.get('blink',1)
            eye.scale.z=.08*blink;glint.scale.z=.02*blink
            glint.location.z=.09+.027*blink
            key(eye,frame,('scale',));key(glint,frame,('scale','location'))
        for i,ear in enumerate(self.ears):
            sign=(-1,1)[i]
            ear.rotation_euler=(state['ears']*.45,sign*.15+state['ears']*.5,sign*.04)
            key(ear,frame,('rotation_euler',))
        evidence=[]
        for kind in ['leg','arm']:
            for i,sign in enumerate([-1,1]):
                upper,lower,joint,tip=self.limbs[kind,sign]
                if kind=='leg':
                    a=root+rotation@Vector((sign*.24,0,-.08))
                    foot=Vector(state['feet'][i])
                    b=foot+Vector((0,.025,.13))
                    mid=two_link(a,b,.57,.57,(sign*.18,-1,.05))
                    radius=.115
                    tip.location=foot
                    tip.rotation_euler=(0,0,state.get('foot_yaw',[0,0])[i])
                else:
                    a=root+rotation@Vector((sign*.36,0,.5))
                    b=root+Vector(state['hands'][i])
                    mid=two_link(a,b,.46,.46,(sign, -.3, -.6))
                    radius=.11
                    tip.location=b
                    tip.rotation_euler=(.12,sign*.2,sign*.1)
                segment_pose(upper,a,mid,radius,frame)
                segment_pose(lower,mid,b,radius*.86,frame)
                joint.location=mid
                key(joint,frame,('location',)); key(tip,frame)
                evidence.append({'limb':f'{kind}.{sign}','lengths':[(mid-a).length,(b-mid).length],'tip':list(b)})
        return evidence


def light(name,location,energy,color,size,target=(0,0,1.3)):
    data=bpy.data.lights.new(name,'AREA')
    data.energy,data.color,data.shape,data.size=energy,color,'DISK',size
    ob=bpy.data.objects.new(name,data); bpy.context.scene.collection.objects.link(ob)
    ob.location=location
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob


def stage():
    scene=bpy.context.scene
    floor=clay('Apricot paper backdrop',(.32,.15,.12),.85,False)
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.20))
    bpy.context.object.name='Infinite studio floor'
    bpy.context.object.data.materials.append(floor)
    wood=clay('Sandstone stage',(.55,.36,.23),.8)
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=4.4,depth=.18,location=(0,.1,-.09))
    ob=bpy.context.object; ob.name='Low circular dance stage'; ob.scale.y=.67
    ob.data.materials.append(wood)
    bevel=ob.modifiers.new('Soft stage edge','BEVEL');bevel.width=.1;bevel.segments=3
    for face in ob.data.polygons:face.use_smooth=True
    # Rings etched into the clay stage, behind the moving feet.
    brass=clay('Stage rim',(.73,.50,.29),.5)
    curve('Stage rim',[(4.27*math.cos(a),.1+2.86*math.sin(a),.012) for a in [i*math.tau/192 for i in range(193)]],.016,brass)
    light('Key softbox',(-4,-5,8),1100,(1,.78,.58),5)
    light('Blue fill',(4,-2,5),850,(.65,.82,1),4)
    light('Warm rim',(1,4,7),1450,(1,.59,.36),3.5)
    scene.world.use_nodes=True
    scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.23,.27,.34,1)
    scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.35
    bpy.ops.object.camera_add(location=(2.6,-15,6.3))
    camera=bpy.context.object;camera.name='Locked wide | motion comparison'
    camera.rotation_euler=(Vector((0,0,1.55))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.ortho_scale=8.5;camera.data.lens=45
    scene.camera=camera
    scene.render.engine='CYCLES'
    scene.cycles.samples=32
    scene.cycles.use_denoising=True
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='METAL';prefs.get_devices()
    for device in prefs.devices: device.use=device.type=='METAL'
    scene.cycles.device='GPU'
    scene.render.resolution_x=1280;scene.render.resolution_y=720
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.view_settings.view_transform='AgX'
    return scene
