"""Authored profile-to-horse drawing: geometry preview only, no diffusion."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, FPS, FRAMES, SCALE = 1280, 720, 24, 96, 2
INK, PAPER, BACKGROUND = "#191727", "#fffdf3", "#302b40"
RAINBOW = ["#ff496c", "#ff9c46", "#f9e55f", "#79d594", "#5bc9ee", "#a889ef"]

# Identical curve topology gives each control point a persistent correspondence.
HEAD_START = [
    (506, 246),
    (552, 204),
    (609, 201),
    (650, 225),
    (681, 246),
    (690, 276),
    (691, 301),
    (693, 316),
    (711, 322),
    (729, 336),
    (744, 345),
    (737, 356),
    (713, 363),
    (708, 371),
    (719, 382),
    (710, 387),
    (715, 408),
    (693, 438),
    (663, 455),
    (643, 467),
    (623, 471),
    (606, 466),
    (607, 510),
    (627, 539),
    (672, 563),
    (719, 589),
    (748, 628),
    (756, 684),
    (640, 684),
    (525, 684),
    (410, 684),
    (419, 621),
    (473, 577),
    (508, 548),
    (540, 521),
    (548, 480),
    (531, 449),
    (484, 421),
    (471, 366),
    (476, 321),
    (480, 285),
    (487, 265),
    (506, 246),
]
HEAD_END = [
    (522, 220),
    (549, 207),
    (595, 207),
    (631, 222),
    (672, 228),
    (699, 263),
    (722, 301),
    (756, 343),
    (801, 392),
    (848, 422),
    (875, 438),
    (892, 464),
    (881, 486),
    (877, 501),
    (855, 515),
    (832, 515),
    (791, 510),
    (747, 473),
    (705, 438),
    (677, 420),
    (654, 395),
    (641, 380),
    (631, 471),
    (660, 558),
    (726, 610),
    (752, 639),
    (771, 663),
    (780, 684),
    (640, 684),
    (495, 684),
    (358, 684),
    (381, 597),
    (413, 510),
    (438, 443),
    (465, 380),
    (480, 310),
    (490, 272),
    (497, 252),
    (508, 234),
    (511, 228),
    (515, 225),
    (520, 222),
    (522, 220),
]
EAR_START = [
    (539, 370),
    (503, 381),
    (486, 313),
    (531, 318),
    (554, 317),
    (556, 352),
    (539, 370),
]
EAR_END = [
    (582, 230),
    (553, 208),
    (535, 134),
    (544, 97),
    (581, 113),
    (602, 184),
    (582, 230),
]
ROOT_START = [
    (662, 233),
    (635, 208),
    (602, 198),
    (567, 199),
    (535, 209),
    (509, 228),
    (491, 256),
]
ROOT_END = [
    (634, 228),
    (582, 209),
    (532, 221),
    (487, 293),
    (448, 395),
    (409, 510),
    (365, 672),
]
TIP_START = [
    (677, 164),
    (640, 100),
    (593, 74),
    (537, 82),
    (480, 113),
    (446, 167),
    (441, 230),
]
TIP_END = [
    (684, 198),
    (586, 129),
    (473, 159),
    (422, 239),
    (381, 365),
    (346, 505),
    (301, 669),
]


def mix(a, b, u):
    return np.asarray(a, dtype=float) * (1 - u) + np.asarray(b, dtype=float) * u


def ease(t, start, end):
    u = float(np.clip((t - start) / (end - start), 0, 1))
    return u * u * u * (10 + u * (-15 + u * 6))


class Drawing:
    """One curve description rendered to both editable SVG and sampled PNG."""

    def __init__(self):
        self.image = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), BACKGROUND)
        self.draw = ImageDraw.Draw(self.image)
        self.svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}">',
            f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BACKGROUND}"/>',
        ]

    def curve(self, points, fill=None, stroke=INK, width=5, closed=False):
        p = np.asarray(points, dtype=float)
        assert (len(p) - 1) % 3 == 0
        sampled = [p[0]]
        d = f"M {p[0, 0]:.3f} {p[0, 1]:.3f}"
        for i in range(1, len(p), 3):
            a, b, c, e = p[i - 1 : i + 3]
            d += " C " + " ".join(f"{v:.3f}" for v in p[i : i + 3].flat)
            for u in np.linspace(0, 1, 33)[1:]:
                sampled.append(
                    (1 - u) ** 3 * a
                    + 3 * (1 - u) ** 2 * u * b
                    + 3 * (1 - u) * u * u * c
                    + u**3 * e
                )
        if closed:
            d += " Z"
            sampled.append(p[0])
        xy = [tuple(v * SCALE) for v in sampled]
        if fill:
            self.draw.polygon(xy, fill=fill)
        if stroke and width:
            self.draw.line(xy, fill=stroke, width=round(width * SCALE), joint="curve")
        self.svg.append(
            f'<path d="{d}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>'
        )

    def ellipse(self, center, radii, fill, stroke=None, width=0):
        x, y = center
        rx, ry = radii
        self.draw.ellipse(
            tuple(v * SCALE for v in (x - rx, y - ry, x + rx, y + ry)),
            fill=fill,
            outline=stroke,
            width=round(width * SCALE),
        )
        self.svg.append(
            f'<ellipse cx="{x:.3f}" cy="{y:.3f}" rx="{rx:.3f}" ry="{ry:.3f}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{width}"/>'
        )

    def finish(self, directory, index):
        self.image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).save(
            directory / "frames" / f"{index:04d}.png"
        )
        (directory / "svg" / f"{index:04d}.svg").write_text(
            "\n".join(self.svg + ["</svg>"]) + "\n"
        )


def paint(index, out):
    t = index / FPS
    face = ease(t, 0.45, 3.25)
    hair = ease(t, 0.50, 3.35)
    ear = ease(t, 0.65, 2.90)
    head = mix(HEAD_START, HEAD_END, face)
    roots = mix(ROOT_START, ROOT_END, hair)
    tips = mix(TIP_START, TIP_END, hair)
    eye = mix((651, 307), (677, 291), face)
    nostril = mix((724, 351), (847, 456), face)
    d = Drawing()

    # Static, unobtrusive ground line makes the fixed camera legible.
    d.curve(
        [(208, 687), (480, 687), (808, 687), (1050, 687)], stroke="#51475f", width=2
    )

    # Six connected color regions retain their order as the crest becomes a mane.
    for i, color in enumerate(RAINBOW):
        r0, r1, o0, o1 = roots[i], roots[i + 1], tips[i], tips[i + 1]
        mid = (o0 + o1) / 2
        spike = mid + mix((0, -17), (-13, 4), hair)
        points = [
            r0,
            mix(r0, r1, 0.33),
            mix(r0, r1, 0.66),
            r1,
            mix(r1, o1, 0.4),
            mix(r1, o1, 0.8),
            o1,
            mix(o1, spike, 0.3),
            mix(o1, spike, 0.7),
            spike,
            mix(spike, o0, 0.3),
            mix(spike, o0, 0.7),
            o0,
            mix(o0, r0, 0.3),
            mix(o0, r0, 0.7),
            r0,
        ]
        d.curve(points, color, width=4, closed=True)

    # Far ear begins occluded by the head, then emerges from the crown.
    far = mix(
        [
            (592, 242),
            (595, 227),
            (603, 220),
            (610, 221),
            (619, 229),
            (620, 240),
            (615, 251),
        ],
        [
            (604, 235),
            (610, 184),
            (636, 124),
            (648, 111),
            (666, 151),
            (646, 211),
            (623, 246),
        ],
        ear,
    )
    d.curve(far, "#d8d0e4", width=5, closed=True)
    d.curve(head, PAPER, width=6, closed=True)

    # A restrained cheek/neck contour, rather than changing painted texture.
    d.curve(
        mix(
            [(549, 403), (572, 431), (582, 448), (584, 472)],
            [(605, 312), (568, 348), (591, 396), (628, 405)],
            face,
        ),
        stroke="#ccc4d9",
        width=5,
    )

    pinna = mix(EAR_START, EAR_END, ear)
    d.curve(pinna, PAPER, width=5, closed=True)
    d.curve(
        mix(
            [(529, 339), (516, 334), (510, 348), (526, 357)],
            [(579, 207), (562, 182), (550, 146), (552, 126)],
            ear,
        ),
        stroke="#b1a0c3",
        width=4,
    )

    # The same visible eye survives the whole transformation.
    d.ellipse(eye, mix((22, 27), (22, 22), face), PAPER, INK, 5)
    d.ellipse(eye + (7, 0), mix((10, 16), (11, 14), face), INK)
    d.ellipse(eye + (10, -7), (3, 4), PAPER)
    d.curve(
        [eye + (-21, -39), eye + (-6, -48), eye + (12, -43), eye + (23, -34)],
        stroke=INK,
        width=4,
    )
    d.ellipse(nostril, mix((4, 3), (12, 8), face), INK)
    d.curve(
        mix(
            [(679, 398), (694, 398), (704, 393), (711, 387)],
            [(798, 480), (831, 495), (859, 494), (878, 483)],
            face,
        ),
        stroke=INK,
        width=4,
    )
    d.finish(out, index)
    return {
        "frame": index,
        "time_seconds": t,
        "face_progress": face,
        "ear_progress": ear,
        "mane_progress": hair,
        "eye": eye.tolist(),
        "nostril": nostril.tolist(),
        "outline_control_points": head.tolist(),
        "ear_control_points": pinna.tolist(),
        "mane_roots": roots.tolist(),
        "mane_tips": tips.tolist(),
    }


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "frames").mkdir()
    (out / "svg").mkdir()
    (out / "source.py").write_bytes(Path(__file__).read_bytes())
    landmarks = [paint(i, out) for i in range(FRAMES)]
    (out / "landmarks.json").write_text(json.dumps(landmarks, indent=2) + "\n")
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-framerate",
            str(FPS),
            "-i",
            str(out / "frames/%04d.png"),
            "-c:v",
            "libx264",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(out / "preview.mp4"),
        ],
        check=True,
    )
    font = ImageFont.load_default(size=20)
    sheet = Image.new("RGB", (1280, 3 * 394), "#221e2d")
    draw = ImageDraw.Draw(sheet)
    selected = [0, 24, 36, 48, 60, 84]
    for cell, frame in enumerate(selected):
        x, y = cell % 2 * 640, cell // 2 * 394
        im = Image.open(out / "frames" / f"{frame:04d}.png")
        sheet.paste(im.resize((640, 360), Image.Resampling.LANCZOS), (x, y))
        draw.text((x + 18, y + 363), f"{frame / FPS:.2f}s", fill="#ede5f6", font=font)
    sheet.save(out / "keyframes.jpg", quality=95)
    files = sorted(p for p in out.rglob("*") if p.is_file())
    manifest = {
        "kind": "authored drawing, no diffusion or optical-flow interpolation",
        "source_sha256": digest(Path(__file__)),
        "width": WIDTH,
        "height": HEIGHT,
        "fps": FPS,
        "frames": FRAMES,
        "duration_seconds": FRAMES / FPS,
        "camera": "fixed",
        "opening_hold_seconds": 0.45,
        "morph_complete_seconds": 3.35,
        "landmark_file": "landmarks.json",
        "files": [
            {"path": str(p.relative_to(out)), "sha256": digest(p)} for p in files
        ],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(out / "preview.mp4")


if __name__ == "__main__":
    main()
