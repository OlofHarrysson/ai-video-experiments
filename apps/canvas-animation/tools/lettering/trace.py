# /// script
# requires-python = ">=3.11"
# dependencies = ["vtracer==0.6.15", "pillow>=11,<13"]
# ///
"""Trace manifest-owned lettering plates into a new, immutable asset directory."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image
import vtracer


def clean_polygon(d, tolerance):
    """Simplify only VTracer's linear contours; reject unsupported path syntax."""
    if re.search(r"[A-KN-Yac-z]", d):
        raise ValueError("Polygon cleanup only supports absolute M/L/Z paths")
    contours = []
    for part in d.split("Z"):
        nums = list(map(float, re.findall(r"-?\d+(?:\.\d+)?", part)))
        points = list(zip(nums[::2], nums[1::2]))
        if not points:
            continue
        changed = True
        while changed and len(points) > 3:
            changed = False
            for i, p in enumerate(points):
                a, b = points[i - 1], points[(i + 1) % len(points)]
                dx, dy = b[0] - a[0], b[1] - a[1]
                length = math.hypot(dx, dy)
                if not length:
                    continue
                distance = abs(dx * (p[1] - a[1]) - dy * (p[0] - a[0])) / length
                along = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length**2
                if distance < tolerance and 0 <= along <= 1:
                    points.pop(i)
                    changed = True
                    break
        contours.append("M" + " L".join(f"{x:g},{y:g}" for x, y in points) + " Z")
    return " ".join(contours)


def trace_asset(asset, base):
    source = (base / asset["source"]).resolve()
    image = Image.open(source).convert("RGB")
    threshold = asset.get("threshold", 130)
    if not 0 <= threshold <= 255:
        raise ValueError("threshold must be 0..255")
    if asset.get("foreground", "light") not in ("light", "dark"):
        raise ValueError("foreground must be light or dark")
    pixels = list(image.getdata())
    mask = [sum(rgb) / 3 > threshold for rgb in pixels]
    if asset.get("foreground", "light") == "dark":
        mask = [not p for p in mask]
    binary = Image.new("L", image.size)
    binary.putdata([255 if p else 0 for p in mask])
    bounds = binary.getbbox()
    if bounds is None:
        raise ValueError(f"{asset['id']}: empty foreground")
    w, h = image.size
    margin = min(bounds[0] / w, bounds[1] / h, (w - bounds[2]) / w, (h - bounds[3]) / h)
    if margin == 0:
        raise ValueError(f"{asset['id']}: foreground touches image boundary; inspect cropping")
    params = dict(colormode="binary", mode=asset.get("mode", "spline"),
                  filter_speckle=asset.get("filterSpeckle", 12),
                  corner_threshold=asset.get("cornerThreshold", 70),
                  length_threshold=asset.get("lengthThreshold", 3),
                  splice_threshold=asset.get("spliceThreshold", 45), path_precision=3)
    svg = vtracer.convert_pixels_to_svg(
        [(0, 0, 0, 255) if p else (255, 255, 255, 255) for p in mask], image.size, **params)
    tree = ET.fromstring(svg)
    parts = []
    for i, el in enumerate(tree):
        if not el.tag.endswith("path"):
            continue
        d = el.attrib["d"]
        tolerance = asset.get("simplify", 0)
        if tolerance:
            if params["mode"] != "polygon":
                raise ValueError("Simplification requires polygon mode")
            d = clean_polygon(d, tolerance)
        el.set("d", d)
        el.set("fill", "white")
        el.set("id", f"p{i:03}")
        parts.append(dict(id=el.attrib["id"], d=d, transform=el.attrib.get("transform", "")))
    if not parts:
        raise ValueError(f"{asset['id']}: no traced paths")
    groups = asset.get("groups", [])
    if not groups or len({g["id"] for g in groups}) != len(groups):
        raise ValueError("Each asset needs uniquely named semantic groups")
    for group in groups:
        if ("region" in group) == ("parts" in group):
            raise ValueError("Group requires exactly one of region or parts")
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    return dict(id=asset["id"], text=asset["text"], width=w, height=h,
                source=asset["source"], sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                threshold=threshold, foreground=asset.get("foreground", "light"),
                foregroundBounds=bounds, margin=margin,
                warnings=["Below requested safe margin"] if margin < asset.get("minimumMargin", .04) else [],
                trace=params, simplify=asset.get("simplify", 0), parts=parts, groups=groups,
                svg=ET.tostring(tree, encoding="unicode"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    manifest = args.manifest.resolve()
    config = json.loads(manifest.read_text())
    if args.output.exists():
        raise SystemExit("Output exists. Choose a fresh version; sources and prior traces are preserved.")
    ids = [a["id"] for a in config["assets"]]
    if len(set(ids)) != len(ids) or any(not re.fullmatch(r"[a-z][a-z0-9-]*", id) for id in ids):
        raise ValueError("Asset IDs must be unique lowercase slugs")
    assets = [trace_asset(a, manifest.parent) for a in config["assets"]]
    args.output.mkdir(parents=True)
    for asset in assets:
        (args.output / f"{asset['id']}.svg").write_text(asset.pop("svg"))
    record = dict(schema=1, vectorizer="vtracer 0.6.15",
                  manifestSha256=hashlib.sha256(manifest.read_bytes()).hexdigest(), assets=assets)
    (args.output / "assets.json").write_text(json.dumps(record, indent=2) + "\n")
    (args.output / "manifest.json").write_bytes(manifest.read_bytes())
    print(json.dumps([dict(id=a["id"], paths=len(a["parts"]), margin=round(a["margin"], 3), warnings=a["warnings"]) for a in assets]))


if __name__ == "__main__":
    main()
