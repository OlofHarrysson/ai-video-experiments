"""Publish the two geometry previews in the existing linked media reviewer."""

import sys

from render import APP, OUT

from deforum_lab.records import save

sys.path.insert(0, str(APP))
from media_review import build


def main():
    common = (
        "The same existing pomegranate-city painting, resized to 960×640. "
        "Ten seconds at 24 fps. Every frame directly warps that original image "
        "using the shared Lanczos renderer. No new diffusion, RIFE, depth or "
        "guide-flow estimation. This isolates the planned spatial movement; "
        "it does not simulate recurrent repainting or cumulative resampling. "
        "Reflected edges fill areas outside the original image. "
        "Frame zero is the single source painting; subsequent frames are spatial warps."
    )
    clips = []
    for case, label, note, details in [
        (
            "floating-drift",
            "Floating drift",
            "Glide sideways and vertically, with a gentle roll",
            (
                "Horizontal and vertical travel reverse at different times. A small "
                "continuous drift and gentle scale change carry movement through the "
                "reversals. This uses eased travel phrases inspired by Move-Float; it "
                "does not reproduce the original sine curves or turbulent guide field."
            ),
        ),
        (
            "travelling-look-around",
            "Travelling look-around",
            "Keep travelling while the sheet turns one way, then back",
            (
                "Overlapping pans, forward/backward scale changes and flat-sheet plane "
                "tilts. Watch the stairs and buildings for the changing perspective. "
                "This is a direct interpretation of Look-Around and Classic-3D-Motion; "
                "the scene has no inferred depth and no hidden object surfaces are revealed."
            ),
        ),
    ]:
        clips.append(
            {
                "id": case,
                "label": label,
                "note": note,
                "details": details + "\n\n" + common,
                "source": str((OUT / case / "preview.mp4").relative_to(APP)),
            }
        )
    session = APP / "media_review/sessions/motion-recipes.json"
    save(
        session,
        {
            "title": "Two motion recipes — without repainting",
            "selected": [c["id"] for c in clips],
            "clips": clips,
        },
    )
    result = build(session, OUT.parent / "media-review-motion-recipes-v001")
    print(result["full_quality"], flush=True)


if __name__ == "__main__":
    main()
