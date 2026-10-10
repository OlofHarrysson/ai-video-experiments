# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11"]
# ///
"""Compare actual timeline holds with the preserved original ornate artwork."""
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parent
out = Path(sys.argv[1]).resolve()
checks = {}
for identity in ("billions", "keep"):
    original = Image.open(ROOT / "../fidelity-v014/assets" / f"{identity}.png").convert("RGB")
    hold = Image.open(out / f"{identity}-native.png").convert("RGB")
    if original.size != hold.size:
        raise ValueError(f"{identity}: native dimensions differ")
    delta = ImageChops.difference(original, hold)
    checks[identity] = {
        "dimensions": list(original.size),
        "identical": delta.getbbox() is None,
        "mean_absolute_rgb_difference": sum(ImageStat.Stat(delta).mean) / 3,
        "max_channel_difference": max(high for low, high in delta.getextrema()),
    }
report = {"passed": all(c["identical"] for c in checks.values()), "actual_timeline_holds": checks}
(out / "quality-report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
if not report["passed"]:
    raise SystemExit(1)
