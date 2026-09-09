"""A native iris control inside an authored eye aperture, attached to HEAD."""
import bpy
from mathutils import Vector


def linear(c):
    return c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4


def rgb(color):
    return (*map(linear,color),1)


def smooth_polygon(points, steps=6):
    result=[]
    for i in range(len(points)):
        a,b,c,d=[Vector(points[j%len(points)]) for j in [i-1,i,i+1,i+2]]
        for k in range(steps):
            t=k/steps
            result.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    return result


PROFILES={
    'bruno':{'size':(434,413),'outline':[(305,86),(313,91),(317,110),(315,136),(310,146),(302,149),
                  (287,146),(277,140),(271,132),(274,121),(284,105),(295,93)],
             'center':(.695,.711),'travel':(.015,.022),'iris':(.030,.069),
             'pupil':(.018,.044),'pupil_shift':(0,.013,0),
             'highlight':(.009,.014),'highlight_shift':(-.010,.034,0)},
    'biscuit':{'size':(371,352),'outline':[(238,134),(248,147),(256,173),(256,196),(250,214),(240,221),
                   (221,220),(204,214),(195,203),(194,187),(201,162),(217,142),(230,134)],
               'center':(.647,.493),'travel':(.018,.028),'iris':(.050,.119),
               'pupil':(.028,.075),'pupil_shift':(.005,.02,0),
               'highlight':(.014,.025),'highlight_shift':(-.016,.060,0)}
}


def add_gaze(head,character='bruno'):
    profile=PROFILES[character]
    rig=next(m.object for m in head.modifiers if m.type=='ARMATURE')
    control=rig.pose.bones['HEAD']
    for name in ['gaze_x','gaze_y']:
        control[name]=0.0
        control.id_properties_ui(name).update(min=-1.,max=1.,description='Iris direction within the painted eye')
    width,height=profile['size']
    points=smooth_polygon([(x/width,1-y/height) for x,y in profile['outline']])
    center=sum(points,Vector((0.,0.)))/len(points)
    xs=[v.co.x for v in head.data.vertices];zs=[v.co.z for v in head.data.vertices]
    x0,x1,z0,z1=min(xs),max(xs),min(zs),max(zs)
    material=bpy.data.materials.new(character.title()+' | controllable eye')
    material.use_nodes=True
    n=material.node_tree.nodes;l=material.node_tree.links;n.clear()
    output=n.new('ShaderNodeOutputMaterial');emit=n.new('ShaderNodeEmission')
    l.new(emit.outputs[0],output.inputs['Surface'])
    uv=n.new('ShaderNodeTexCoord')
    offset=n.new('ShaderNodeCombineXYZ')
    for channel,prop,base,amplitude in zip(['X','Y'],['gaze_x','gaze_y'],profile['center'],profile['travel']):
        socket=offset.inputs[channel];socket.default_value=base
        driver=socket.driver_add('default_value').driver
        variable=driver.variables.new();variable.name='look';variable.type='SINGLE_PROP'
        variable.targets[0].id=rig;variable.targets[0].data_path=f'pose.bones["HEAD"]["{prop}"]'
        driver.expression=f'{base}+look*{amplitude}'
    delta=n.new('ShaderNodeVectorMath');delta.operation='SUBTRACT'
    l.new(uv.outputs['UV'],delta.inputs[0]);l.new(offset.outputs[0],delta.inputs[1])

    def ellipse(radius, shift=(0,0,0)):
        sub=n.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=shift
        scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY'
        scale.inputs[1].default_value=(1/radius[0],1/radius[1],1)
        length=n.new('ShaderNodeVectorMath');length.operation='LENGTH'
        ramp=n.new('ShaderNodeMapRange');ramp.clamp=True
        ramp.inputs['From Min'].default_value=.96;ramp.inputs['From Max'].default_value=1.02
        ramp.inputs['To Min'].default_value=1;ramp.inputs['To Max'].default_value=0
        l.new(delta.outputs[0],sub.inputs[0]);l.new(sub.outputs[0],scale.inputs[0])
        l.new(scale.outputs[0],length.inputs[0]);l.new(length.outputs['Value'],ramp.inputs['Value'])
        return ramp.outputs[0]

    iris=ellipse(profile['iris'])
    pupil=ellipse(profile['pupil'],profile['pupil_shift'])
    highlight=ellipse(profile['highlight'],profile['highlight_shift'])
    sep=n.new('ShaderNodeSeparateXYZ');l.new(delta.outputs[0],sep.inputs[0])
    shade=n.new('ShaderNodeMapRange');shade.clamp=True
    shade.inputs['From Min'].default_value=-profile['iris'][1]
    shade.inputs['From Max'].default_value=profile['iris'][1]*.36
    l.new(sep.outputs['Y'],shade.inputs['Value'])
    brown=n.new('ShaderNodeMixRGB');brown.inputs[1].default_value=rgb((.58,.31,.08));brown.inputs[2].default_value=rgb((.13,.065,.02))
    l.new(shade.outputs[0],brown.inputs[0])
    color=n.new('ShaderNodeMixRGB');color.inputs[1].default_value=rgb((.99,.985,.96))
    l.new(iris,color.inputs[0]);l.new(brown.outputs[0],color.inputs[2])
    dark=n.new('ShaderNodeMixRGB');dark.inputs[2].default_value=rgb((.025,.018,.014))
    l.new(pupil,dark.inputs[0]);l.new(color.outputs[0],dark.inputs[1])
    shine=n.new('ShaderNodeMixRGB');shine.inputs[2].default_value=rgb((1,1,1))
    l.new(highlight,shine.inputs[0]);l.new(dark.outputs[0],shine.inputs[1]);l.new(shine.outputs[0],emit.inputs['Color'])

    border=bpy.data.materials.new(character.title()+' | eye outline');border.use_nodes=True
    bn=border.node_tree.nodes;bn.clear()
    bo=bn.new('ShaderNodeOutputMaterial');be=bn.new('ShaderNodeEmission');be.inputs[0].default_value=rgb((.11,.065,.036))
    border.node_tree.links.new(be.outputs[0],bo.inputs['Surface'])
    objects=[]
    for label,scale,depth,mat in [('outline',1.035,-.103,border),('aperture',.94,-.104,material)]:
        polygon=[center+(point-center)*scale for point in points]
        mesh=bpy.data.meshes.new('Eye | '+label)
        mesh.from_pydata([(x0+u*(x1-x0),depth,z0+v*(z1-z0)) for u,v in polygon],[],[tuple(range(len(polygon)))])
        uv_layer=mesh.uv_layers.new()
        for loop in mesh.loops:uv_layer.data[loop.index].uv=polygon[loop.vertex_index]
        mesh.materials.append(mat)
        ob=bpy.data.objects.new('Eye | '+label,mesh);bpy.context.scene.collection.objects.link(ob)
        ob.parent=head.parent
        group=ob.vertex_groups.new(name='HEAD');group.add(list(range(len(polygon))),1,'REPLACE')
        mod=ob.modifiers.new('Follow head','ARMATURE');mod.object=rig
        objects.append(ob)
    return objects
