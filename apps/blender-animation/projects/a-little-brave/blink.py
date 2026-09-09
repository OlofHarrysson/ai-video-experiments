"""Continuous eyelid closure using the unchanged painted head texture."""
import math
import bpy


def clamp(t):
    return max(0.,min(1.,t))


def smooth(a,b,x):
    t=clamp((x-a)/(b-a))
    return t*t*(3-2*t)


PROFILES = {
    'puppy': {'x':.605,'radius':.13,'eye_v':.505,'bottom':.15,'top':.17,
              'center':.49,'curve':.06},
    'bruno': {'x':.68,'radius':.10,'eye_v':.705,'bottom':.11,'top':.13,
              'center':.695,'curve':.035},
}


def add_blink(ob,profile):
    spec=PROFILES[profile]
    if ob.data.shape_keys is None:
        ob.shape_key_add(name='Basis')
    key=ob.shape_key_add(name='Eyelid closure')
    uv_by_vertex={loop.vertex_index:tuple(ob.data.uv_layers.active.data[loop.index].uv)
                  for loop in ob.data.loops}
    height=max(v.co.z for v in ob.data.vertices)-min(v.co.z for v in ob.data.vertices)
    for index,vertex in enumerate(key.data):
        u,v=uv_by_vertex[index]
        horizontal=abs(u-spec['x'])/spec['radius']
        if horizontal>=1:
            continue
        ellipse=math.sqrt(1-horizontal**2)
        v1=spec['eye_v']-spec['bottom']*ellipse
        v2=spec['eye_v']+spec['top']*ellipse
        v0,v3=v1-.065,v2+.035
        weight=1-smooth(.83,1,horizontal)
        if v<=v0 or v>=v3:
            continue
        arch=spec['center']+spec['curve']*ellipse
        if v<v1:
            target=v0+(arch-.0015-v0)*(v-v0)/(v1-v0)
        elif v<=v2:
            target=arch-.0015+.003*(v-v1)/(v2-v1)
        else:
            target=arch+.0015+(v3-arch-.0015)*(v-v2)/(v3-v2)
        vertex.co.z += (target-v)*height*weight
    key.slider_min=0
    key.slider_max=1
    add_lid_line(ob,key,spec,profile)
    return key


def add_lid_line(head,key,spec,profile):
    rig=next(m.object for m in head.modifiers if m.type=='ARMATURE')
    xmin,xmax=min(v.co.x for v in head.data.vertices),max(v.co.x for v in head.data.vertices)
    zmin,zmax=min(v.co.z for v in head.data.vertices),max(v.co.z for v in head.data.vertices)
    verts=[];faces=[]
    for i in range(25):
        t=i/24
        dx=-.82+1.64*t
        u=spec['x']+dx*spec['radius']
        v=spec['center']+spec['curve']*math.sqrt(1-dx*dx)
        half_width=.001+.0035*math.sin(math.pi*t)**.5
        x=xmin+(xmax-xmin)*u;z=zmin+(zmax-zmin)*v
        verts.extend([(x,-.119,z-half_width),(x,-.119,z+half_width)])
        if i:
            n=i*2;faces.append((n-2,n,n+1,n-1))
    data=bpy.data.meshes.new(head.name+' eyelid stroke')
    data.from_pydata(verts,[],faces)
    ob=bpy.data.objects.new(head.name+' | eyelid stroke',data)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent=head.parent
    group=ob.vertex_groups.new(name='HEAD');group.add(list(range(len(verts))),1,'REPLACE')
    mod=ob.modifiers.new('Eyelid follows head','ARMATURE');mod.object=rig
    material=bpy.data.materials.new(ob.name);material.use_nodes=True
    nodes=material.node_tree.nodes;nodes.clear();links=material.node_tree.links
    out=nodes.new('ShaderNodeOutputMaterial');mix=nodes.new('ShaderNodeMixShader')
    transparent=nodes.new('ShaderNodeBsdfTransparent');emit=nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value=(.055,.023,.009,1) if profile=='puppy' else (.014,.009,.006,1)
    ramp=nodes.new('ShaderNodeMapRange');ramp.clamp=True
    ramp.inputs['From Min'].default_value=.7;ramp.inputs['From Max'].default_value=1
    driver=ramp.inputs['Value'].driver_add('default_value').driver
    variable=driver.variables.new();variable.name='closure';variable.type='SINGLE_PROP'
    variable.targets[0].id_type='KEY';variable.targets[0].id=head.data.shape_keys
    variable.targets[0].data_path='key_blocks["Eyelid closure"].value'
    driver.expression='closure'
    links.new(ramp.outputs[0],mix.inputs[0]);links.new(transparent.outputs[0],mix.inputs[1])
    links.new(emit.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs['Surface'])
    data.materials.append(material)
