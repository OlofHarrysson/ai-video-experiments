"""Recorded Krea sampling schedule and independently timed scene descriptions."""

import numpy as np

SIGMAS = [0.6, 0.512844085693, 0.310901075602, 0.0]


def recipe(config, seconds):
    scene = [s for s in config["scenes"] if s["at"] <= seconds][-1]
    age = seconds - scene["at"]
    if "noise_schedule" in config:
        schedule = config["noise_schedule"]
        noise = float(
            np.interp(
                seconds, [p["at"] for p in schedule], [p["noise"] for p in schedule]
            )
        )
    elif "transition_ramp" in config:
        repaint = round((seconds - max(scene["at"], 0.5)) * 2)
        ramp = config["transition_ramp"]
        noise = ramp[repaint] if 0 <= repaint < len(ramp) else config["settle_noise"]
    else:
        noise = config["transition_noise"] if age <= 1.5 else config["settle_noise"]
    # Optional text events have their own clock; they do not restart the noise ramp.
    if "prompt_schedule" in config:
        scene = [s for s in config["prompt_schedule"] if s["at"] <= seconds][-1]
    if "sigma_ratios" in config:
        ratios = np.asarray(config["sigma_ratios"], dtype=float)
        if (
            ratios.ndim != 1
            or len(ratios) < 2
            or not np.isfinite(ratios).all()
            or ratios[0] != 1
            or ratios[-1] != 0
            or not (np.diff(ratios) < 0).all()
        ):
            raise ValueError("Sigma ratios must strictly decrease from 1 to 0")
        return scene, [float(r * noise) for r in ratios]
    return scene, [s * noise / 0.6 for s in SIGMAS]
