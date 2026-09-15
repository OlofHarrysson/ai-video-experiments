"""Build focused comparisons with plain-language motion descriptions."""

import sys

from run import lab

sys.path.insert(0, str(lab.APP))
from media_review import build

COMMON = (
    "Krea Turbo repaints its own warped previous painting. CFG1, three Euler "
    "intervals, independent noise and the established scene noise curves. "
    "Lanczos spatial transforms; RIFE 4.25 scale 1. Source motion is 24 fps, "
    "with half-second repaints. The 1.5× finish is 24 fps with three paintings "
    "per displayed second. All paintings are preserved and the final seven "
    "frames continue spatial warping. Interpolation never feeds back."
)


def clip(key, label, note, detail, path):
    return {
        "id": key,
        "label": label,
        "note": note,
        "details": detail + "\n\n" + COMMON,
        "source": str((lab.OUT / path / "preview.mp4").relative_to(lab.APP)),
    }


def main():
    banking = clip(
        "banking",
        "Banking voyage",
        "City → palace-fish → orchid railway",
        "An underlying drift carries a spiral bank, sideways plane turn, "
        "pullback and vertical wave. The composition travels diagonally and "
        "changes scale. A plane turn tips a flat sheet; it does not reveal "
        "the hidden sides of objects.",
        "c3-banking-voyage/faster/rife-moving-tail",
    )
    folding = clip(
        "folding",
        "Folding worlds",
        "Same story, a different spatial route",
        "Same opening, prompts, noise, seeds and repaint timing as Banking voyage. "
        "Pull back first, tilt the sheet, slide its upper and lower regions "
        "differently, then spiral and bend it. The wider framing also exposes "
        "more repeated forms near the borders.",
        "c4-folding-worlds/faster/rife-moving-tail",
    )
    continuation = clip(
        "orchids",
        "Under the orchids",
        "City → orchid railway → harp bridges",
        "A complete 24-second film. Preserves Banking voyage through its last "
        "painting, then steers beneath the large orchid toward the visible train. "
        "Rails become golden strings and harp-like bridges. The late foreground "
        "is crowded and more illustrative, despite continued movement.",
        "c5-under-the-orchids/assembled",
    )
    explicit = clip(
        "explicit",
        "Motion separated from morphing",
        "Exactly the same paintings; different in-between frames",
        "Local finishing experiment: align the next painting back to the previous "
        "painting's spatial position, ask RIFE to interpolate that pair, then "
        "apply the planned spatial movement to each intermediate frame. This "
        "reduces the motion RIFE must infer, but adds resampling and can still "
        "create distortion. No new diffusion or change to the feedback loop.",
        "motion-aware-full/explicit-motion",
    )
    for name, title, clips in [
        ("continuous-motion", "Two continuous spatial routes", [banking, folding]),
        ("continuous-film", "Under the orchids — complete film", [continuation]),
        (
            "continuous-finishing",
            "Same paintings — two ways to create movement",
            [banking, explicit],
        ),
    ]:
        session = lab.APP / f"media_review/sessions/{name}.json"
        lab.save(
            session,
            {"title": title, "selected": [c["id"] for c in clips], "clips": clips},
        )
        result = build(session, lab.OUT.parent / f"media-review-{name}-v001")
        print(result["full_quality"], flush=True)


if __name__ == "__main__":
    main()
