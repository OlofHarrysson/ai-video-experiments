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
    return scene, [s * noise / 0.6 for s in SIGMAS]
