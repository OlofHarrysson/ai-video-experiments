# /// script
# requires-python = ">=3.11"
# dependencies = ["gradio-client", "pillow"]
# ///
from pathlib import Path
import json,time,shutil,hashlib,argparse
from gradio_client import Client,handle_file
from PIL import Image
ROOT=Path(__file__).parent
PROMPT='A photorealistic studio photograph of one whole round watermelon. Natural dark green winding stripes on a lighter green rind, realistic fine rind texture. The entire watermelon is visible as a sphere. Plain uniform dark charcoal background. Soft studio light from the upper left reveals its rounded volume. Only one watermelon, no cut fruit, no text, no other objects.'
p=argparse.ArgumentParser();p.add_argument('mode',choices=['edge','depth','inpaint','edge-inpaint']);p.add_argument('--case',default='left');p.add_argument('--seed',type=int,default=43);p.add_argument('--label');a=p.parse_args()
label=a.label or f'qwen21-{a.mode}-{a.case}-{a.seed}';out=ROOT/'runs/round1'/label;out.mkdir(parents=True,exist_ok=False)
c=Client('hugging-apps/qwen-image-2-1-controlnet-union-demo',verbose=False,download_files=str(out/'downloads'))
assets=ROOT/'references/assets'/a.case
args=dict(prompt=PROMPT,preprocessor='None (already a control map)',control_context_scale=1.0,resolution=1024,num_inference_steps=40,seed=a.seed,randomize_seed=False,guidance_scale=1.0)
args['control_image']=handle_file(str(assets/('edge.png' if a.mode.startswith('edge') else 'depth.png'))) if a.mode!='inpaint' else None
if 'inpaint' in a.mode:
 args['inpaint_image']={'background':handle_file(str(assets/'blank.png')),'layers':[],'composite':handle_file(str(assets/'blank.png'))}
 args['mask_image']=handle_file(str(assets/'mask.png'))
(out/'input.json').write_text(json.dumps(args,indent=2));t=time.monotonic()
try:
 job=c.submit(**args,api_name='/generate');(out/'submitted.json').write_text(json.dumps({'submitted':True,'at':time.time()}));print('submitted',label,flush=True)
 result=job.result(timeout=600)
 for src,name in zip(result[:2],['output','control']):
  ext=Path(src).suffix;shutil.copyfile(src,out/(name+'-original'+ext));Image.open(src).save(out/(name+'.png'))
 receipt={'elapsed_seconds':time.monotonic()-t,'seed':result[2],'space_revision':'93f834f7b3bf4c8f5bda498deabe0255e9fe9809','sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.png')}}
 (out/'result.json').write_text(json.dumps(receipt,indent=2));print(receipt,flush=True)
except Exception as e:
 (out/'error.json').write_text(json.dumps({'error':str(e),'elapsed_seconds':time.monotonic()-t},indent=2));raise
