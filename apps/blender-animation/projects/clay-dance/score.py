# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy==2.3.3"]
# ///
"""Original deterministic 120 BPM pocket-funk score. No recordings or model calls."""
import argparse
import json
from pathlib import Path
import wave
import numpy as np

RATE=48000
BPM=120
DURATION=18
SEED=1701


def compose(destination):
    destination=Path(destination)
    if destination.exists():raise FileExistsError(destination)
    rng=np.random.default_rng(SEED)
    audio=np.zeros((int(RATE*DURATION),2),np.float64)

    def add(sound,beat,volume=1,pan=0):
        start=round(beat*60/BPM*RATE)
        length=min(len(sound),len(audio)-start)
        if length<=0:return
        angle=(pan+1)*np.pi/4
        audio[start:start+length]+=sound[:length,None]*np.array([np.cos(angle),np.sin(angle)])[None,:]*volume

    def note(midi,seconds,kind):
        t=np.arange(int(RATE*seconds))/RATE
        hz=440*2**((midi-69)/12)
        if kind=='bass':
            signal=np.sin(2*np.pi*hz*t)+.22*np.sin(4*np.pi*hz*t)
            env=(1-np.exp(-t*130))*np.exp(-t*6)
        else:
            signal=np.sin(2*np.pi*hz*t)+.28*np.sin(2*np.pi*hz*2.003*t)*np.exp(-t*14)+.1*np.sin(2*np.pi*hz*3.98*t)*np.exp(-t*25)
            env=(1-np.exp(-t*250))*np.exp(-t*7)
        env*=np.minimum(1,(seconds-t)/.04)
        return signal*env

    for beat in range(36):
        t=np.arange(int(RATE*.30))/RATE
        kick=np.sin(2*np.pi*(48*t+75*.022*(1-np.exp(-t/.022))))*np.exp(-t*17)
        if beat%2==0 or beat%4==3:add(kick,beat,.6)
        if beat%2==1:
            noise=rng.standard_normal(len(t))
            clap=(noise*.28+np.sin(2*np.pi*180*t)*.22)*np.exp(-t*28)
            add(clap,beat,.42,.15)
        for off in [0,.5]:
            ht=np.arange(int(RATE*.075))/RATE
            noise=rng.standard_normal(len(ht))
            high=np.concatenate([[0],np.diff(noise)])
            hat=high*np.exp(-ht*85)*(1-np.exp(-ht*1000))
            add(hat,beat+off,.055 if off else .035,-.25)
        roots=[38,43,45]
        root=roots[(beat//4)%3]
        if beat%4 in [0,2,3]:
            add(note(root,.43,'bass'),beat,.42,-.05)
        if beat%4 in [1,3]:
            for n in [root+24,root+28,root+31,root+35]:
                add(note(n,.48,'bell'),beat+.5,.052,.4)
    melody=[(0,74),(.75,78),(1.5,81),(2.75,78),(3.5,76),(4.5,74),(5.5,71),(6.5,74),(7.5,76)]
    for block in [0,12,24]:
        for beat,note_number in melody:
            add(note(note_number,.45,'bell'),block+beat,.19,-.4)
    # Quiet stereo slapback lends space without blurring the rhythmic attacks.
    delay=int(.125*RATE)
    audio[delay:]+=.11*audio[:-delay,::-1].copy()
    audio*=np.minimum(1,np.arange(len(audio))/int(.012*RATE))[:,None]
    audio*=np.minimum(1,(len(audio)-np.arange(len(audio)))/int(.18*RATE))[:,None]
    audio*=.78/np.max(np.abs(audio))
    destination.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(destination),'wb') as wav:
        wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(RATE)
        wav.writeframes((audio*32767).astype('<i2').tobytes())
    destination.with_suffix('.json').write_text(json.dumps({'bpm':BPM,'duration':DURATION,'sample_rate':RATE,'seed':SEED,'provenance':'Original locally synthesized bass, mallet melody and percussion; no external samples.','peak_dbfs':float(20*np.log10(np.max(np.abs(audio))))},indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output');args=p.parse_args();compose(args.output)
