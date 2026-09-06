# SDXL settings: lantern marsh

Three standalone 1024×576 images compare sampling effort and guidance in the same moonlit marsh. Seed 143, SDXL base 1.0 and both prompts stay fixed. This study uses the lantern-marsh scene text; its images are fresh native-resolution generations, not crops of the parent's 1280×720 overscan reference.

- [Experiment plan and review](experiments/settings.md)
- [Runnable recipe](experiments/settings.py)
- [Prepared API graph](experiments/settings-v001.api.json)
- [Ordered settings manifest](experiments/settings-v001.settings.json)

Status: completed and all three original PNGs visually inspected. At seed 143, 20 steps retained useful detail; CFG 5.0 produced a calmer color balance. All three missed important scene instructions. See the experiment report for limits and image links. Shared transport preserved receipts, immutable attempt archives and collected originals in `runs/`. No selected cut: these are three alternatives, not a temporal sequence.
