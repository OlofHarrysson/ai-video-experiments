from pathlib import Path
import json, hashlib, shutil
ROOT=Path(__file__).parent
WORK=ROOT.parents[1]/'work/watermelon-scene'
def payload(path):
 wrapper=json.loads(path.read_text())
 if not isinstance(wrapper,dict):return wrapper
 return next((json.loads(c['text']) for c in wrapper.get('content',[]) if c.get('type')=='text' and c['text'].startswith('{')),wrapper)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assets={}
for receipt in WORK.glob('upload-*.json'):
 d=payload(receipt)
 if not isinstance(d,dict) or not d.get('file_url'):continue
 name=receipt.name.removeprefix('upload-').removesuffix('.json')
 path=ROOT/'references/assets'/name
 if name=='reference.png':path=ROOT.parent/'spatial-control-lab/runs/round1/sunburst-shape-left/output-0.png'
 if path.exists():assets[d['file_url']]={'local_path':str(path.relative_to(ROOT.parent)),'sha256':digest(path)}
for path in (ROOT/'runs').glob('*/*/verified-*.json'):
 d=json.loads(path.read_text());out=path.parent/('output.mp4' if path.name=='verified-video.json' else 'output-'+path.stem.removeprefix('verified-')+'.png')
 if out.exists():assets[d['url']]={'local_path':str(out.relative_to(ROOT.parent)),'sha256':digest(out)}
def replace(value):
 if isinstance(value,str):return assets.get(value,value)
 if isinstance(value,list):return [replace(v) for v in value]
 if isinstance(value,dict):return {k:replace(v) for k,v in value.items()}
 return value
records=[]
for folder in sorted((ROOT/'runs').glob('*/*')):
 cfgpath=folder/'input.json'
 if not cfgpath.exists():continue
 cfg=json.loads(cfgpath.read_text());submission=payload(folder/'submission.json');result=payload(folder/'result.json') if (folder/'result.json').exists() else submission
 status=result.get('status');outputs={p.name:digest(p) for p in folder.glob('output*') if p.is_file()}
 records.append({'run':str(folder.relative_to(ROOT)),'endpoint_id':cfg['endpoint_id'],'parameters':replace(cfg['input']),'input_receipt_sha256':digest(cfgpath),'request_id':submission.get('request_id'),'status':status,'error':result.get('error'),'field_errors':result.get('field_errors'),'allowance_usd':cfg.get('allowance_usd'),'outputs':outputs})
(ROOT/'run-index.json').write_text(json.dumps(records,indent=2)+'\n')
for src,dst in [('exports/stills/metrics.json','still-measurements.json'),('exports/video/metrics.json','video-measurements.json'),('exports/video/background-lock-verification.json','background-lock-verification.json')]:
 if (ROOT/src).exists():shutil.copyfile(ROOT/src,ROOT/dst)
print(json.dumps({'runs':len(records),'image_outputs':sum(any(n.endswith('.png') for n in r['outputs']) for r in records),'video_outputs':sum('output.mp4' in r['outputs'] for r in records),'allowance_usd':round(sum(r['allowance_usd'] or 0 for r in records),4),'pending':[r['run'] for r in records if r['status'] not in ('completed','error')]},indent=2))
