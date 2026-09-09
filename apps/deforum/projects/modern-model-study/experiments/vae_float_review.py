"""Verify and compare float-only VAE recurrence with the PNG checkpoint path."""
import copy,json
from PIL import Image
import numpy as np
import vae_float_probe as p
from repaint_diagnosis_review import metrics,panel

d=p.d
root=d.OUT/'vae-float';m=json.loads((root/'manifest.json').read_text());run=d.a.PROJECT/m['run']
assert json.loads((run/'workflow.api.json').read_text())==p.graph()==m['graph']
actual=json.loads((run/'workflow.executed.json').read_text());norm=copy.deepcopy(actual);norm['20']['inputs']['image']='anchor.png';assert norm==p.graph()
assert d.a.sha(run/'anchor.png')==d.a.sha(d.SOURCE)==m['source_sha256']
hist=json.loads((run/'history.json').read_text());assert hist['status']['completed'] and hist['status']['status_str']=='success'
ref=np.asarray(Image.open(d.SOURCE).convert('RGB'));records=[]
for j,i in enumerate(p.CYCLES):
 path=root/f'anchors/{i:04d}.png';assert d.a.sha(path)==m['outputs'][str(i)]==d.a.sha(run/f'frames/{j:04d}.png')
 records.append({'cycle':i,**metrics(np.asarray(Image.open(path).convert('RGB')),ref)})
d.a.save(root/'verification.json',{'verified':True,'saved_cycles':p.CYCLES,'vae_cycles':24,'intermediate_png_feedback':False,'results':records})
paths=[d.SOURCE,d.OUT/'vae-only/anchors/0024.png',root/'anchors/0024.png',d.OUT/'repaint010/anchors/0024.png']
labels=['Original','24 VAE cycles with PNG checkpoints','24 VAE cycles with float tensors','24 repaints at 0.10, no movement']
d.a.image(root/'comparison.png',panel(paths,labels))
d.a.image(root/'detail.png',panel(paths,labels,crop=(240,100,1008,612)))
print('Float VAE outputs and graph verified')
