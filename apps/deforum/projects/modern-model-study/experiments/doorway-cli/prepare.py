"""Freeze the previewed motion with staged story prompts, preserving the CLI draft."""

import copy
from pathlib import Path

from deforum_lab.records import copy_verified, read, save, sha

HERE = Path(__file__).resolve().parent
APP = HERE.parents[3]
CASE = "doorway-clear-passage"
DRAFT = APP / "projects/modern-model-study/branches/branch-379a1d60345e"
ROOT = DRAFT.parent / CASE
STYLE = (
    " An exquisite dimensional surrealist oil painting with luminous jade and emerald greens, "
    "golden sunbeams, carved ivory, rich shadows, delicate blue flowers and crisp engraved textures."
)


def main():
    config = copy.deepcopy(read(DRAFT / "config.json"))
    config["case"] = CASE
    config["prompt_schedule"] = [
        e for e in config["prompt_schedule"] if e["at"] <= 17.5
    ] + [
        {
            "at": 18,
            "name": "clear-passage",
            "prompt": "A broad open carved ivory doorway in a crimson wall. Curving railway rails enter an open sunlit green meadow visible through the doorway. Empty mossy ground occupies the center of the passage. Far beyond the threshold, a few slender golden trees stand along the edges of the meadow. The arch remains two tall straight jambs with a curved top, framing golden daylight and open space."
            + STYLE,
        },
        {
            "at": 21,
            "name": "approaching-daylight",
            "prompt": "The open ivory doorway fills the view, its pillars cropped by the left and right edges. Between them a railway curves out into an expansive sunlit emerald meadow. A tiny red steam locomotive is visible far along the railway. Distant delicate golden trees stand around the far edges of the meadow, with thin harp strings among their branches. The center is open grass beneath a warm pale sky."
            + STYLE,
        },
        {
            "at": 23.5,
            "name": "through-the-threshold",
            "prompt": "Inside a vast sunlit emerald meadow, a curved golden railway leads across open mossy ground toward a small red steam train in the middle distance. Tiny blue flowers grow beside the rails. Slender trees with delicate golden harp-string branches stand far apart at the distant sides of the valley, leaving an uninterrupted view of the open green clearing and warm golden sky."
            + STYLE,
        },
        {
            "at": 26,
            "name": "arrival-and-reveal",
            "prompt": "A broad quiet emerald valley opens beneath a pale golden sky. A small red steam locomotive travels along curving rails across the middle distance, trailing a fine ribbon of white steam. Soft blue wildflowers and luminous moss line the foreground. On the distant rolling hills stand slender golden harp-shaped trees, widely spaced. Deep shadows and shafts of sunlight make the spacious landscape feel dimensional and dreamlike."
            + STYLE,
        },
    ]
    config["noise_schedule"] = [
        e for e in config["noise_schedule"] if e["at"] <= 17.5
    ] + [
        {"at": t, "noise": n}
        for t, n in [
            (18, 0.60),
            (19, 0.62),
            (20, 0.65),
            (21, 0.66),
            (22, 0.68),
            (23, 0.70),
            (24, 0.68),
            (25, 0.60),
            (26, 0.52),
            (26.5, 0.46),
            (27, 0.42),
            (28, 0.38),
            (29.5, 0.36),
        ]
    ]
    config["painting_frames"] = list(range(0, 709, 12))
    config["duration"] = 30
    config["seeds_by_frame"] = {
        str(f): config["seed"] + 1000 + f for f in config["painting_frames"][1:]
    }
    save(ROOT / "config.json", config)
    save(HERE / "configs" / f"{CASE}.json", config)
    prefix = read(DRAFT / "prefix.json")
    for row in prefix:
        copy_verified(
            DRAFT / f"anchors/{row['frame']:04d}.png",
            ROOT / f"anchors/{row['frame']:04d}.png",
        )
    save(ROOT / "prefix.json", prefix)
    save(
        HERE / "production-plan.json",
        {
            "branch": str(ROOT.relative_to(APP)),
            "preview_id": "379a1d60345e4bc78ae0bd75586231d0",
            "preview_motion_unchanged": config["phrases"]
            == read(DRAFT / "config.json")["phrases"],
            "frozen_config_sha256": sha(ROOT / "config.json"),
            "checkpoint_source_frame": 528,
            "planned_new_paintings": 24,
            "preserved_paintings": len(prefix),
            "purpose": "Clear the doorway with a continuous push, then reveal the new world without further enlargement. Prompt and noise staging are separate from the warp-only preview.",
        },
    )
    print(ROOT)


if __name__ == "__main__":
    main()
