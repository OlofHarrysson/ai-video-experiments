# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
from pathlib import Path
import json,urllib.request,hashlib
from PIL import Image
ROOT=Path(__file__).parent
for folder in sorted((ROOT/'runs').glob('*/*')):
 files=list(folder.glob('result.json'))+list(folder.glob('submission.json'))
 for f in files:
  wrapper=json.loads(f.read_text())
  if 'content' not in wrapper: continue
  for block in wrapper['content']:
   if block.get('type')!='text' or not block['text'].startswith('{'):continue
   data=json.loads(block['text'])
   result=data.get('result',data)
   if not isinstance(result,dict):continue
   imgs=result.get('images',[])
   if not imgs:continue
   for i,img in enumerate(imgs):
    out=folder/f'output-{i}.png'
    if not out.exists():
     raw=urllib.request.urlopen(img['url']).read();(folder/f'original-{i}.bin').write_bytes(raw)
     import io
     im=Image.open(io.BytesIO(raw));im.load();im.save(out)
     record={'url':img['url'],'format':im.format,'size':im.size,'original_sha256':hashlib.sha256(raw).hexdigest(),'png_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
     (folder/f'verified-{i}.json').write_text(json.dumps(record,indent=2));print(folder.name,im.size)
