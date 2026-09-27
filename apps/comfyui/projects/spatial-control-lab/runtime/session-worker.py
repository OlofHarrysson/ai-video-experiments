import os,time,json,hashlib,traceback
from pathlib import Path
import torch,numpy as np
from PIL import Image
from load_pipeline import pipe
ROOT=Path(__file__).parent
OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
REQ=ROOT/'requests'; REQ.mkdir(exist_ok=True)
def tensor(p):
 im=Image.open(p).convert('RGB').resize((1024,1024));return torch.from_numpy(np.array(im)).permute(2,0,1).unsqueeze(0).float()/255.0
print('WORKER_READY',flush=True)
while not (ROOT/'STOP').exists() and time.time()<1790538900:
 pending=[f for f in sorted(REQ.glob('*.json')) if not (OUT/f.stem/'result.json').exists() and not (OUT/f.stem/'error.json').exists()]
 if not pending:
  time.sleep(2);continue
 for f in pending:
  cfg=json.loads(f.read_text());out=OUT/f.stem;out.mkdir(exist_ok=True); (out/'input.json').write_text(f.read_text());start=time.monotonic()
  try:
   kwargs={};assets=ROOT/'assets'/cfg['case'];mode=cfg['mode']
   if mode in ['edge','depth','edge-inpaint']:kwargs['control_image']=tensor(assets/('edge.png' if mode.startswith('edge') else 'depth.png'))
   if 'inpaint' in mode:
    kwargs['image']=tensor(assets/'blank.png');kwargs['mask_image']=tensor(assets/'mask.png')[:,:1]
   control_scale=cfg.get('control_scale',1.0)
   image=pipe(cfg['prompt'],height=1024,width=1024,generator=torch.Generator(device='cuda').manual_seed(cfg['seed']),true_cfg_scale=1.0,num_inference_steps=40,control_context_scale=control_scale,use_kv_cache=True,**kwargs).images[0]
   image.save(out/'output.png')
   receipt={'seconds':time.monotonic()-start,'sha256':hashlib.sha256((out/'output.png').read_bytes()).hexdigest(),'size':image.size,'mode':image.mode,'gpu':torch.cuda.get_device_name(),'max_memory_allocated':torch.cuda.max_memory_allocated(),'torch':torch.__version__}
   (out/'result.json').write_text(json.dumps(receipt,indent=2));print('DONE',f.stem,receipt,flush=True)
  except Exception as e:
   (out/'error.json').write_text(json.dumps({'error':str(e),'traceback':traceback.format_exc()},indent=2));print('ERROR',f.stem,traceback.format_exc(),flush=True)
print('WORKER_EXIT',flush=True)
