"""Expand an explicit 34-bar score and save the existing renderer's recipe."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BARS = 34


def mask(active):
    return "<" + " ".join("1" if i in active else "0" for i in range(BARS)) + ">"


def main():
    bass = []
    melody = []
    roots = ["d2", "d2", "bb1", "bb1", "f2", "f2", "c2", "c2"]
    # Four related questions and answers, matched to the two-bar chord rhythm.
    phrases = [
        "~ ~ 2 ~ ~ 1 ~ ~ 0 ~ ~ ~ 4 ~ ~ ~",
        "~ ~ ~ ~ 0 ~ ~ 1 ~ ~ 2 ~ ~ ~ ~ ~",
        "~ ~ 2 ~ ~ 0 ~ ~ 4 ~ ~ ~ 2 ~ ~ ~",
        "~ ~ ~ ~ 1 ~ ~ 0 ~ ~ ~ ~ ~ ~ ~ ~",
        "~ ~ 4 ~ ~ 3 ~ ~ 2 ~ ~ ~ 1 ~ ~ ~",
        "~ ~ ~ ~ 2 ~ ~ 4 ~ ~ 5 ~ ~ ~ ~ ~",
        "~ ~ 3 ~ ~ 1 ~ ~ 0 ~ ~ ~ 1 ~ ~ ~",
        "~ ~ ~ ~ 3 ~ ~ 1 ~ ~ 0 ~ ~ ~ ~ ~",
    ]
    for bar in range(BARS):
        r = roots[bar % 8]
        steps = ["~"] * 16
        for pos in [2, 5, 7, 10, 13, 15]:
            steps[pos] = r
        if bar % 4 == 3:
            steps[15] = ["c2", "c2", "a1", "a1"][bar // 8 % 4]
        bass.append("[" + " ".join(steps) + "]")
        phrase = phrases[bar % 8]
        if bar in [4, 5, 6, 7]:
            phrase = (
                "~ ~ 2 ~ ~ ~ ~ ~ 0 ~ ~ ~ ~ ~ ~ ~"
                if bar % 2 == 0
                else "~ ~ ~ ~ ~ ~ 1 ~ ~ ~ ~ ~ ~ ~ ~ ~"
            )
        if bar == 25:
            phrase = "~ ~ ~ ~ 2 ~ ~ 4 ~ ~ 5 ~ 6 ~ ~ ~"
        if bar == 29:
            phrase = "~ ~ ~ ~ 2 ~ ~ 4 ~ ~ 5 ~ ~ 4 ~ ~"
        melody.append("[" + phrase + "]")
    masks = {
        "rhythm": mask(set(range(16)) | set(range(20, 32))),
        "low": mask(set(range(2, 16)) | set(range(22, 32))),
        "backbeat": mask(set(range(4, 16)) | set(range(22, 32))),
        "wood": mask(set(range(6, 16)) | set(range(24, 32))),
        "lead": mask(set(range(4, 16)) | set(range(18, 32))),
        "arp": mask(set(range(8, 16)) | set(range(20, 32))),
        "pads": mask(range(0, 32, 2)),
        "air": mask([14, 22, 30]),
        "last": mask([32]),
    }
    lines = [
        "// Afterglow Transit — 126 BPM, 32 musical bars + two bars for resolution/tails.",
        "setcpm(126/4)",
    ]
    lines += [f'const at{k.title()} = "{v}"' for k, v in masks.items()]
    lines += [
        f'const atBass = "<{" ".join(bass)}>"',
        f'const atMelody = "<{" ".join(melody)}>"',
    ]
    lines += [
        'kick: s("atkick*4").gain(.63).orbit(1).mask(atRhythm)',
        'clap: s("~ atclap ~ atclap").gain(.44).room(.08).orbit(2).mask(atBackbeat)',
        'hats: s("~ athat:0 ~ athat:0 ~ athat:0 ~ athat:0").gain(".60 .43 .53 .42").pan(.57).orbit(1).mask(atRhythm)',
        'shuffle: s("~ ~ ~ athat:0 ~ ~ athat:0 ~ ~ ~ ~ athat:0 ~ ~ athat:0 ~").gain(.16).pan(.3).swingBy(.10,8).orbit(1).mask(atBackbeat)',
        'open: s("~ ~ ~ athat:1 ~ ~ ~ athat:1").gain(.25).pan(.42).orbit(1).mask(atArp)',
        'wood: s("<[~ ~ ~ atwood ~ ~ ~ ~ ~ ~ atwood ~ ~ ~ ~ ~] [~ ~ ~ ~ ~ atwood ~ ~ ~ ~ ~ atwood ~ ~ atwood ~]>").gain(".20 .14 .25").pan(".28 .7").room(.10).orbit(3).mask(atWood)',
        'sub: note(atBass).transpose(-12).s("sine").attack(.008).decay(.10).sustain(.45).release(.04).gain(.40).orbit(4).mask(atLow)',
        'bass: note(atBass).s("sawtooth").lpf("<440!8 700!8 360!8 950!6 500!4>").lpenv(1.7).lpattack(.006).lpdecay(.09).lpsustain(.12).attack(.007).decay(.10).sustain(.28).release(.035).gain(.25).orbit(4).mask(atLow)',
        'pads: s("atpad").n("<0 0 1 1 2 2 3 3>").clip(3).gain("<.43!8 .50!8 .57!8 .51!8 0!2>").hpf(220).room(.20).orbit(5).mask(atPads)',
        'lead: n(atMelody).s("atlead").clip(5).gain("<.28!8 .38!8 .29!8 .42!6 .30!4>").hpf(260).lpf("<2000!8 2900!8 1800!8 3900!6 2300!4>").delay(.24).delaytime(.3571429).delayfeedback(.32).room(.15).orbit(6).mask(atLead)',
        'arp: n("<[0 ~ 4 ~ 1 ~ 2 ~] [0 ~ ~ 4 1 ~ ~ ~] [0 ~ 2 ~ 4 ~ 5 ~] [2 ~ ~ 4 0 ~ ~ ~] [2 ~ 4 ~ 5 ~ 1 ~] [2 ~ ~ 4 5 ~ ~ ~] [0 ~ 1 ~ 3 ~ 5 ~] [3 ~ ~ 1 0 ~ ~ ~]>").s("atarp").clip(2).gain(.12).pan(".30 .65 .45 .7").hpf(400).delay(.28).delaytime(.2380952).delayfeedback(.3).orbit(7).mask(atArp)',
        'air: s("atair").clip(3).gain(.24).room(.25).orbit(8).mask(atAir)',
        'resolve: s("atpad:0").clip(1.5).gain(.38).hpf(200).room(.2).orbit(5).mask(atLast)',
        'lastnote: s("atlead:0").clip(2).gain(.25).delay(.25).delaytime(.3571429).delayfeedback(.3).orbit(6).mask(atLast)',
    ]
    source = ROOT / "source/v001.strudel"
    with source.open("x") as f:
        f.write("\n".join(lines) + "\n")
    recipe = {
        "version": 1,
        "title": "Afterglow Transit",
        "revisions": {
            "v001": {
                "source": "source/v001.strudel",
                "notes": "New melodic deep-house / trance composition and original palette.",
            }
        },
        "end_cycle": BARS,
        "sample_rate": 48000,
        "samples": ["references/assets/v001"],
        "stems": {
            "kick": ["kick"],
            "bass": ["sub", "bass"],
            "clap": ["clap"],
            "hats": ["hats", "shuffle", "open"],
            "percussion": ["wood"],
            "harmony": ["pads", "resolve"],
            "melody": ["lead", "lastnote"],
            "arpeggio": ["arp"],
            "air": ["air"],
        },
        "sections": {
            "arrival": [0, 4],
            "theme": [4, 12],
            "lift": [12, 16],
            "suspension": [16, 20],
            "build": [20, 24],
            "return": [24, 30],
            "release": [30, 34],
        },
    }
    with (ROOT / "project.json").open("x") as f:
        f.write(json.dumps(recipe, indent=2) + "\n")


if __name__ == "__main__":
    main()
