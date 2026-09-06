"""Constrain independent sampling and compositing to gaps in a depth guide.

Inputs verified in ComfyUI v0.34.0 nodes.py and comfy_extras/nodes_mask.py.
"""

def constrain_to_gaps(graph, indices, width, height):
    for order,index in enumerate(indices):
        if index == 0: continue
        crop,encode,sample,decode = [str(100+4*order+i) for i in range(4)]
        mc,mt,mg,lm,comp = [str(500+5*order+i) for i in range(5)]
        for node in graph.values():
            for key,value in list(node['inputs'].items()):
                if value == [decode,0]: node['inputs'][key]=[comp,0]
        graph[mc]={'class_type':'ImageCrop','inputs':{
            'image':['6',0],'x':order*width,'y':height,'width':width,'height':height}}
        graph[mt]={'class_type':'ImageToMask','inputs':{'image':[mc,0],'channel':'red'}}
        graph[mg]={'class_type':'GrowMask','inputs':{'mask':[mt,0],'expand':8,'tapered_corners':True}}
        graph[lm]={'class_type':'SetLatentNoiseMask','inputs':{'samples':[encode,0],'mask':[mg,0]}}
        graph[sample]['inputs']['latent_image']=[lm,0]
        graph[comp]={'class_type':'ImageCompositeMasked','inputs':{
            'destination':[crop,0],'source':[decode,0],'x':0,'y':0,
            'resize_source':False,'mask':[mg,0]}}
    return graph
