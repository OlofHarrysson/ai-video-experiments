from pathlib import Path
import json
ROOT=Path(__file__).parent
pending=[]
for f in (ROOT/'runs').glob('*/*/submission.json'):
 if (f.parent/'result.json').exists():continue
 wrapper=json.loads(f.read_text())
 try:d=json.loads(next(b['text'] for b in wrapper['content'] if b.get('type')=='text' and b['text'].startswith('{')))
 except (StopIteration,ValueError):continue
 if d.get('status') in ('processing','submitted'):
  cfg=json.loads((f.parent/'input.json').read_text());pending.append({'folder':str(f.parent.resolve()),'endpoint_id':cfg['endpoint_id'],'request_id':d['request_id'],'status_url':d.get('status_url'),'response_url':d.get('response_url')})
print(json.dumps(pending))
