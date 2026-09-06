"""Reusable ComfyUI graph recipes; transport and project records live elsewhere."""
import copy


def independent_redraw_graph(parent, width, height, indices, *, steps=28, cfg=6.5,
                             denoise=0.4, preserve_anchor=False):
    """Crop a horizontal guide strip and independently repaint each global position."""
    graph = {key: copy.deepcopy(parent[key]) for key in ('1', '2', '3')}
    graph['6'] = {'class_type': 'LoadImage', 'inputs': {'image': 'anchor.png'}}
    seed = parent['7']['inputs']['seed']
    previous = None
    for order, index in enumerate(indices):
        crop, encode, sample, decode = [str(100 + 4 * order + i) for i in range(4)]
        graph[crop] = {'class_type': 'ImageCrop', 'inputs': {
            'image': ['6', 0], 'x': order * width, 'y': 0, 'width': width, 'height': height}}
        output = [crop, 0]
        if not (preserve_anchor and index == 0):
            graph[encode] = {'class_type': 'VAEEncode', 'inputs': {
                'pixels': [crop, 0], 'vae': ['1', 2]}}
            graph[sample] = {'class_type': 'KSampler', 'inputs': {
                'model': ['1', 0], 'positive': ['2', 0], 'negative': ['3', 0],
                'latent_image': [encode, 0], 'seed': seed + index,
                'steps': steps, 'cfg': cfg, 'denoise': denoise,
                'sampler_name': 'dpmpp_2m', 'scheduler': 'karras'}}
            graph[decode] = {'class_type': 'VAEDecode', 'inputs': {
                'samples': [sample, 0], 'vae': ['1', 2]}}
            output = [decode, 0]
        if previous is None:
            previous = output
        else:
            batch = str(200 + order)
            graph[batch] = {'class_type': 'ImageBatch', 'inputs': {
                'image1': previous, 'image2': output}}
            previous = [batch, 0]
    if previous is None:
        raise ValueError('At least one guide position is required')
    graph['11'] = {'class_type': 'SaveImage', 'inputs': {
        'images': previous, 'filename_prefix': 'guide-redraw'}}
    return graph
