# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==11.3.0"]
# ///
"""Label, encode, decode-check and make review sheets without changing native frames."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
FONT='/System/Library/Fonts/Avenir Next.ttc'
LABELS=['GROOVE','SIDE STEP','ROBOT']


def run(cmd):
    subprocess.run(cmd,check=True)


def finish(version,frames_dir,tag,proof):
    source=ROOT/'output'/version
    output=source/tag
    if output.exists():raise FileExistsError(output)
    output.mkdir()
    frames=source/frames_dir
    manifest=json.loads((frames/'manifest.json').read_text())
    count=len(manifest['frames']);duration=count/manifest['fps']
    images=sorted(frames.glob('[0-9][0-9][0-9][0-9].png'))
    assert len(images)==count
    width,height=Image.open(images[0]).size
    for path in images:
        with Image.open(path) as im:
            assert im.size==(width,height);im.verify()
    section=duration/3
    for i,label in enumerate(LABELS):
        title=Image.new('RGBA',(width,height),(0,0,0,0))
        draw=ImageDraw.Draw(title)
        font=ImageFont.truetype(FONT,round(width*.027))
        draw.text((width*.047,height*.067),f'0{i+1}   {label}',font=font,fill=(255,243,221,255))
        title.save(output/f'title-{i}.png')
    soundtrack=source/'score.wav'
    assert soundtrack.exists()
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-framerate',str(manifest['fps']),'-i',str(frames/'%04d.png'),'-i',str(soundtrack)]
    for i in range(3):cmd+=['-loop','1','-i',str(output/f'title-{i}.png')]
    filters='[0:v]fps=24[v0];'
    for i in range(3):
        filters+=f"[v{i}][{i+2}:v]overlay=enable='gte(t,{i*section})*lt(t,{(i+1)*section})'[v{i+1}];"
    if proof:
        filters+='[1:a]atrim=0:2,asetpts=PTS-STARTPTS[a0];[1:a]atrim=6:8,asetpts=PTS-STARTPTS[a1];[1:a]atrim=12:14,asetpts=PTS-STARTPTS[a2];[a0][a1][a2]concat=n=3:v=0:a=1,alimiter=limit=0.9[a]'
    else:filters+='[1:a]alimiter=limit=0.9[a]'
    film=output/('proof.mp4' if proof else 'side-by-side.mp4')
    cmd+=['-filter_complex',filters,'-map','[v3]','-map','[a]','-t',str(duration),'-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(film)]
    run(cmd)
    run(['ffmpeg','-v','error','-i',str(film),'-f','null','-'])
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(film)]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert int(video['nb_read_frames'])==round(duration*24)
    assert video['r_frame_rate']=='24/1'
    assert abs(float(probe['format']['duration'])-duration)<.05
    for i,label in enumerate(LABELS):
        if not proof:
            run(['ffmpeg','-v','error','-ss',str(i*section),'-i',str(film),'-t',str(section),'-c:v','libx264','-crf','17','-c:a','aac','-b:a','192k','-movflags','+faststart',str(output/(label.lower().replace(' ','-')+'.mp4'))])
        # One complete two-second loop, every other authored pose.
        indices=list(range(i*count//3,i*count//3+24,2))
        sheet=Image.new('RGB',(960,4*204),(245,238,227));draw=ImageDraw.Draw(sheet)
        for j,idx in enumerate(indices):
            with Image.open(images[idx]) as image:
                image=image.resize((320,180))
                x=(j%3)*320;y=(j//3)*204
                sheet.paste(image,(x,y))
                draw.text((x+8,y+184),f"{label} | frame {manifest['frames'][idx]}",fill=(40,30,20))
        sheet.save(output/(label.lower().replace(' ','-')+'-poses.jpg'),quality=92)
    run(['ffmpeg','-v','error','-ss','0.75','-i',str(film),'-frames:v','1',str(output/'poster.jpg')])
    files=[film,source/'clay-dance.blend',soundtrack,*images]
    if (source/'clay-dance-editable.blend').exists():files.append(source/'clay-dance-editable.blend')
    hashes={str(path.relative_to(source)):hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    (output/'delivery-check.json').write_text(json.dumps({'probe':probe,'full_decode':'passed','native_poses':count,'delivery_frames':round(duration*24),'sha256':hashes,'source_manifest':manifest},indent=2)+'\n')
    print(film)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--version',required=True);p.add_argument('--frames',default='final-frames');p.add_argument('--tag',default='delivery');p.add_argument('--proof',action='store_true')
    args=p.parse_args();finish(args.version,args.frames,args.tag,args.proof)
