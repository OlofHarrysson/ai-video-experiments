"""Author frozen continuation passages using measured incoming image motion."""

import copy
import json
from pathlib import Path

import numpy as np

from deforum_lab.image.warps import mapping

HERE = Path(__file__).resolve().parent
APP = HERE.parents[3]
OUT = HERE.parents[1] / "exports/seed-for-sea-long-v001"

STYLE = (
    " An exquisite dimensional surrealist oil painting, deep ultramarine and luminous "
    "turquoise, pearlescent ivory, warm copper and a small vermilion accent. Tactile "
    "carved surfaces, crisp engraved detail, luminous reflected light and deep velvet "
    "shadows. Monumental readable silhouettes, generous open space and poetic dream logic."
)


def incoming_velocity(config, seconds, center):
    """Fit translation, log-scale rate and roll to a small forward motion step."""
    y, x = np.mgrid[0.1:0.91:6j, 0.15:1.36:8j]
    points = np.stack([x.ravel(), y.ravel()], -1)
    step = 1 / 240
    target = mapping(
        mapping(points, seconds, config["phrases"], True),
        seconds + step,
        config["phrases"],
    )
    q = points - center
    design = np.zeros((len(points), 2, 4))
    design[:, 0, 0] = design[:, 1, 1] = 1
    design[:, 0, 2], design[:, 1, 2] = q[:, 0], q[:, 1]
    design[:, 0, 3], design[:, 1, 3] = -q[:, 1], q[:, 0]
    velocity = np.linalg.lstsq(
        design.reshape(-1, 4), ((target - points) / step).ravel(), rcond=None
    )[0]
    residual = np.max(
        np.linalg.norm((design @ velocity) - (target - points) / step, axis=-1)
    )
    return velocity.tolist(), float(residual)


def make(
    case,
    parent_root,
    through,
    duration,
    center,
    end,
    end_velocity,
    prompts,
    noise,
    extra=(),
):
    parent_root = Path(parent_root)
    parent = json.loads((APP / parent_root / "config.json").read_text())
    config = copy.deepcopy(parent)
    start = through / 24
    incoming, residual = incoming_velocity(parent, start, np.asarray(center))
    config.update(
        case=case,
        prefix_root=str(parent_root),
        prefix_through=through,
        duration=duration,
        painting_frames=list(range(0, round(duration * 24), 12)),
        phrases=[
            {
                "kind": "continuation",
                "start": start,
                "duration": duration - start - 0.5,
                "center": center,
                "end": end,
                "velocity_start": incoming,
                "velocity_end": end_velocity,
            },
            *extra,
        ],
        prompt_schedule=[
            {"at": start + t, "name": name, "prompt": prompt + STYLE}
            for t, name, prompt in prompts
        ],
        noise_schedule=[{"at": start + t, "noise": value} for t, value in noise],
    )
    config.pop("opening", None)
    config["seeds_by_frame"] = {str(f): 91717000 + f for f in config["painting_frames"]}
    config["motion_rebase"] = {
        "source_frame": through,
        "fitted_velocity": incoming,
        "maximum_residual_per_source_second": residual,
    }
    sample_points = np.array([[0.0, 0.0], [0.75, 0.5], [1.5, 1.0]])
    for seconds in (start, (start + duration) / 2, duration):
        mapping(sample_points, seconds, config["phrases"])
    target = HERE / "configs" / (case + ".json")
    if target.exists():
        raise FileExistsError("Create a new case instead of overwriting a direction")
    target.write_text(json.dumps(config, indent=2) + "\n")
    print(target)
    return config
