"""Check projected, textured head/torso overlap on evaluated Blender meshes.

This measures the artwork silhouettes, including alpha, rather than bone proximity.
It is a contact check, not a judgement of anatomy, seams, or drawing quality.
"""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np

PIXELS_PER_UNIT = 120
LEFT, TOP = -2.5, 3.5
WIDTH, HEIGHT = 780, 540


def texture_alpha(ob):
    nodes = ob.data.materials[0].node_tree.nodes
    image = next(n.image for n in nodes if n.type == 'TEX_IMAGE')
    pixels = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(pixels)
    alpha = pixels.reshape(image.size[1], image.size[0], 4)[:, :, 3].copy()
    # Read the head material's UV feather from the saved scene itself.
    feather = next((n for n in nodes if n.type == 'MATH' and n.operation == 'MAXIMUM'), None)
    if feather is not None:
        yy, xx = np.mgrid[0:image.size[1], 0:image.size[0]]
        coordinates = {'X': xx/(image.size[0]-1), 'Y': yy/(image.size[1]-1)}
        values = []
        for socket in feather.inputs[:2]:
            node = socket.links[0].from_node
            channel = node.inputs['Value'].links[0].from_socket.name
            start, end = (node.inputs[n].default_value for n in ['From Min', 'From Max'])
            values.append(np.clip((coordinates[channel]-start)/(end-start), 0, 1))
        alpha *= np.maximum(*values)
    return alpha


def silhouette(ob, alpha, depsgraph):
    evaluated = ob.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    mask = np.zeros((HEIGHT, WIDTH), dtype=bool)
    positions = np.array([tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices])
    projected = np.stack(((positions[:, 0]-LEFT)*PIXELS_PER_UNIT,
                          (TOP-positions[:, 2])*PIXELS_PER_UNIT), axis=1)
    uv_layer = mesh.uv_layers.active.data
    for tri in mesh.loop_triangles:
        xy = projected[list(tri.vertices)]
        lo = np.maximum(np.floor(xy.min(axis=0)).astype(int), [0, 0])
        hi = np.minimum(np.ceil(xy.max(axis=0)).astype(int), [WIDTH-1, HEIGHT-1])
        if np.any(hi < lo):
            continue
        matrix = np.column_stack((xy[1]-xy[0], xy[2]-xy[0]))
        if abs(np.linalg.det(matrix)) < 1e-8:
            continue
        yy, xx = np.mgrid[lo[1]:hi[1]+1, lo[0]:hi[0]+1]
        coords = np.stack((xx+.5-xy[0, 0], yy+.5-xy[0, 1]), axis=-1)
        weights = coords @ np.linalg.inv(matrix).T
        inside = (weights[:, :, 0] >= 0) & (weights[:, :, 1] >= 0) & (weights.sum(axis=-1) <= 1)
        uv = np.array([tuple(uv_layer[i].uv) for i in tri.loops])
        sample = uv[0]+weights[:, :, :1]*(uv[1]-uv[0])+weights[:, :, 1:]*(uv[2]-uv[0])
        tx = np.clip(np.rint(sample[:, :, 0]*(alpha.shape[1]-1)).astype(int), 0, alpha.shape[1]-1)
        ty = np.clip(np.rint(sample[:, :, 1]*(alpha.shape[0]-1)).astype(int), 0, alpha.shape[0]-1)
        mask[lo[1]:hi[1]+1, lo[0]:hi[0]+1] |= inside & (alpha[ty, tx] > .5)
    evaluated.to_mesh_clear()
    return mask


def check_attachment():
    scene = bpy.context.scene
    objects = [bpy.data.objects[n] for n in ['Paint | torso', 'Drawing | attentive']]
    alphas = [texture_alpha(ob) for ob in objects]
    rows = []
    for frame in range(scene.frame_start, scene.frame_end+1):
        scene.frame_set(frame)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        masks = [silhouette(ob, alpha, depsgraph) for ob, alpha in zip(objects, alphas)]
        count = int(np.count_nonzero(masks[0] & masks[1]))
        rows.append({'frame': frame, 'overlap_pixels': count,
                     'overlap_square_scene_units': count/PIXELS_PER_UNIT**2})
    return {'scene': bpy.data.filepath, 'pixels_per_scene_unit': PIXELS_PER_UNIT,
            'alpha_threshold': .5, 'minimum_overlap': min(rows, key=lambda r: r['overlap_pixels']),
            'frames': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True)
    p.add_argument('--minimum-area', type=float, default=0)
    args = p.parse_args(sys.argv[sys.argv.index('--')+1:])
    report = check_attachment()
    Path(args.output).write_text(json.dumps(report, indent=2)+'\n')
    print('ATTACHMENT', json.dumps(report['minimum_overlap']), flush=True)
    assert report['minimum_overlap']['overlap_square_scene_units'] >= args.minimum_area
