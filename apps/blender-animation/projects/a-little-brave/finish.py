# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Encode the reviewed native frames and record exact delivery metadata."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--version',required=True)
args=p.parse_args()
out=ROOT/'output'/args.version
frames=out/'final-frames'
movie=out/'a-little-brave.mp4'
assert not movie.exists(), 'Preserve the previous encode'
paths=sorted(frames.glob('frame_*.png'))
assert [path.name for path in paths]==[f'frame_{f:04d}.png' for f in range(1,385)]
for path in paths:
    with Image.open(path) as image:
        assert image.size==(1920,1080) and image.mode=='RGB',(path,image.size,image.mode)
        image.verify()
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-framerate','24','-start_number','1',
    '-i',str(frames/'frame_%04d.png'),'-i',str(ROOT/'assets/score-v001-master.wav'),
    '-frames:v','384','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',
    '-t','16','-movflags','+faststart',str(movie)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams',
                                        '-show_format','-of','json',str(movie)]))
video=next(stream for stream in probe['streams'] if stream['codec_type']=='video')
audio=next(stream for stream in probe['streams'] if stream['codec_type']=='audio')
assert video['width']==1920 and video['height']==1080
assert video['avg_frame_rate']=='24/1' and int(video['nb_read_frames'])==384
assert audio['sample_rate']=='48000' and audio['channels']==2
assert abs(float(probe['format']['duration'])-16)<.05
subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],check=True)
shutil.copy2(paths[-1],out/'poster.png')
shutil.copy2(paths[0],out/'opening.png')
report={'version':args.version,'movie':str(movie),'video':video,'audio':audio,
        'duration_seconds':float(probe['format']['duration']),
        'frame_sequence_count':len(paths),'all_pngs_verified':True,'full_decode_passed':True,
        'sha256':{path.name:hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in [movie,out/'a-little-brave.blend',out/'poster.png']}}
(out/'delivery-check.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'frame-hashes.json').write_text(json.dumps({path.name:hashlib.sha256(path.read_bytes()).hexdigest()
                                               for path in paths},indent=2)+'\n')
shutil.copy2(Path(__file__),out/'source/finish.py')
print(json.dumps({'movie':str(movie),'duration':report['duration_seconds'],'frames':len(paths),
                  'size_bytes':movie.stat().st_size},indent=2))
