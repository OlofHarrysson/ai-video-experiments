"""Build a small measured guide-flow dataset for the educational animation.

uv run --with opencv-python-headless==4.12.0.88 python projects/motion-guide-study/experiments/guide_lesson.py
"""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

OUT = Path(__file__).resolve().parents[1] / 'exports/spatial-controls-lesson-v001'
WIDTH, HEIGHT, STEPS = 512, 320, 72
GRID_X, GRID_Y = 17, 11


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    x, y = np.meshgrid(np.arange(WIDTH, dtype=np.float32), np.arange(HEIGHT, dtype=np.float32))
    base = np.where((x.astype(int)//32 + y.astype(int)//32) % 2, 230, 25).astype(np.uint8)
    for row in range(10):
        for col in range(16):
            cv2.circle(base, (col*32+16, row*32+16), 3+(row*7+col*3)%4, 125, -1, cv2.LINE_AA)
    sample_x, sample_y = np.meshgrid(np.linspace(0, WIDTH-1, GRID_X, dtype=np.float32), np.linspace(0, HEIGHT-1, GRID_Y, dtype=np.float32))
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    flow = None
    errors, fields, hashes = [], [], []
    previous = base
    cv2.imwrite(str(OUT/'guide-first.png'), base)
    for frame in range(1, STEPS+1):
        phase = frame/STEPS*2*np.pi
        offset = 22*(np.sin(y/HEIGHT*2*np.pi-phase)-np.sin(y/HEIGHT*2*np.pi))
        current = cv2.remap(base, x-offset, y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        flow = dis.calc(previous, current, None if flow is None else flow.copy())
        sampled = cv2.remap(flow, sample_x, sample_y, cv2.INTER_LINEAR)
        assert np.isfinite(sampled).all()
        fields.append(np.round(sampled, 3).reshape(-1).tolist())
        old_phase = (frame-1)/STEPS*2*np.pi
        true_dx = 22*(np.sin(y/HEIGHT*2*np.pi-phase)-np.sin(y/HEIGHT*2*np.pi-old_phase))
        errors.append(float(np.median(np.hypot(flow[32:-32,48:-48,0]-true_dx[32:-32,48:-48], flow[32:-32,48:-48,1]))))
        hashes.append(hashlib.sha256(current.tobytes()).hexdigest())
        if frame in (18,36,54,72):cv2.imwrite(str(OUT/f'guide-{frame:03d}.png'), current)
        previous = current
    payload = {'width':WIDTH,'height':HEIGHT,'steps':STEPS,'fps':12,'nx':GRID_X,'ny':GRID_Y,'fields':fields}
    (OUT/'flow-data.json').write_text(json.dumps(payload, separators=(',',':'))+'\n')
    manifest={'opencv':cv2.__version__,'method':'DIS Medium, warm-started; float flow bilinearly sampled on 17x11 grid',
              'guide':'32-pixel checker cells with deterministic gray dots, horizontal sinusoidal travelling deformation; amplitude22px',
              'frames':STEPS+1,'duration_seconds':6,'guide_frame_sha256':hashes,
              'median_interior_endpoint_error_px':float(np.median(errors)),
              'presentation':'SVG reconstruction of the guide pattern; artwork vector vertices advected by measured flow, no diffusion or raster feedback resampling',
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='guide_frame_sha256'},indent=2))


if __name__=='__main__':main()
