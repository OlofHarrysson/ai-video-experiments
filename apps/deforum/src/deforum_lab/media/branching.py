"""Local continuation drafts and exact-renderer motion previews; never inference."""

import copy
import math
import re
import subprocess
import threading
import uuid
from pathlib import Path

import numpy as np
from PIL import Image

from deforum_lab.image.warps import mapping, warp_at_time
from deforum_lab.records import copy_verified, read, require, save, sha
from deforum_lab.rendering.schedules import recipe

FPS = 24
PREVIEW_WIDTH = 768


def under(path, root):
    path = Path(path).resolve()
    require(path.is_relative_to(root.resolve()), "Path outside workspace")
    return path


def owner_at(app, root, frame):
    """Resolve the actual motion owner of an inherited painting interval."""
    visited = set()
    while True:
        root = under(root, app)
        require(root not in visited, "Cyclic parent lineage")
        visited.add(root)
        config = read(root / "config.json")
        if frame > config.get("prefix_through", -1):
            return config
        root = app / config["prefix_root"]


def incoming_velocity(phrases, seconds, center):
    """Fit a similarity velocity to the incoming field; regional motion is approximate."""
    x, y = np.meshgrid(np.linspace(0.15, 1.35, 5), np.linspace(0.1, 0.9, 4))
    q = np.stack([x.ravel(), y.ravel()], -1)
    dt = 0.001
    previous = mapping(mapping(q, seconds, phrases, True), seconds - dt, phrases)
    velocity = (q - previous) / dt
    relative = q - np.asarray(center)
    matrix = np.zeros((len(q) * 2, 4))
    matrix[0::2] = np.stack(
        [np.ones(len(q)), np.zeros(len(q)), relative[:, 0], -relative[:, 1]], -1
    )
    matrix[1::2] = np.stack(
        [np.zeros(len(q)), np.ones(len(q)), relative[:, 1], relative[:, 0]], -1
    )
    fitted = np.linalg.lstsq(matrix, velocity.ravel(), rcond=None)[0]
    residual = float(np.sqrt(np.mean((matrix @ fitted - velocity.ravel()) ** 2)))
    return fitted.tolist(), residual


class BranchPlanner:
    def __init__(self, app):
        self.app = Path(app).resolve()
        self.work = self.app / "work/motion-planner"
        self.lock = threading.Lock()

    def resolve(self, source):
        video = under(self.app / source, self.app)
        require(video.suffix.lower() == ".mp4", "Expected a local MP4 delivery")
        manifest = read(video.parent / "manifest.json")
        timing = read(video.parent.parent / "retiming.json")
        root = video.parent.parent.parent
        config = read(root / "config.json")
        require(
            manifest["status"] == "complete" and manifest["video_sha256"] == sha(video),
            "Video provenance mismatch",
        )
        require(
            timing["source_config_sha256"] == sha(root / "config.json"),
            "Source configuration changed",
        )
        require(
            timing["fps"] == FPS and timing.get("source_start_frame", 0) == 0,
            "Only full 24 fps retimed painting sequences supported",
        )
        require(
            config.get("cadence") == 12,
            "First planner supports half-second source paintings",
        )
        require(
            len(timing["source_anchor_frames"])
            == len(timing["delivery_anchor_frames"]),
            "Invalid anchor mapping",
        )
        return video, root, config, manifest, timing

    def selection(self, source, frame):
        video, root, config, manifest, timing = self.resolve(source)
        require(
            type(frame) is int and 0 <= frame < len(manifest["output_frames"]),
            "Invalid display frame",
        )
        anchors = timing["delivery_anchor_frames"]
        index = max(i for i, f in enumerate(anchors) if f <= frame)
        display = anchors[index]
        source_frame = timing["source_anchor_frames"][index]
        painting = root / f"anchors/{source_frame:04d}.png"
        row = manifest["output_frames"][display]
        require(
            row["kind"] == "anchor" and row["sha256"] == sha(painting),
            "Painting does not match verified video anchor",
        )
        inherited = owner_at(self.app, root, source_frame)
        scene, sigmas = recipe(config, source_frame / FPS)
        return {
            "source": str(video.relative_to(self.app)),
            "requested_frame": frame,
            "display_frame": display,
            "source_frame": source_frame,
            "display_seconds": display / FPS,
            "source_seconds": source_frame / FPS,
            "speed": timing["speed_multiplier"],
            "snapped": display != frame,
            "prompt": scene["prompt"],
            "noise": sigmas[0],
            "painting_sha256": sha(painting),
            "config": config,
            "incoming_phrases": inherited["phrases"],
            "root": root,
            "video": video,
            "painting": painting,
            "manifest": manifest,
            "timing": timing,
        }

    def describe(self, source, frame):
        s = self.selection(source, frame)
        public = {
            k: s[k]
            for k in (
                "source",
                "requested_frame",
                "display_frame",
                "source_frame",
                "display_seconds",
                "source_seconds",
                "speed",
                "snapped",
                "prompt",
                "noise",
            )
        }
        velocity, residual = incoming_velocity(
            s["incoming_phrases"], s["source_seconds"], [0.75, 0.5]
        )
        public.update(
            incoming_velocity=velocity,
            incoming_residual=residual,
            painting_path=str(s["painting"]),
        )
        return public

    def plan(self, request):
        s = self.selection(request["source"], request["frame"])
        values = {}
        bounds = {
            "duration": (1, 8),
            "zoom": (0.5, 8),
            "pan_x": (-1, 1),
            "pan_y": (-1, 1),
            "roll": (-45, 45),
            "center_x": (0, 1),
            "center_y": (0, 1),
            "noise": (0.05, 0.85),
            "end_drift": (-0.15, 0.15),
        }
        for key, (lo, hi) in bounds.items():
            value = float(request[key])
            require(
                math.isfinite(value) and lo <= value <= hi, f"{key} outside {lo}…{hi}"
            )
            values[key] = value
        prompt = request["prompt"].strip()
        intent = request["intent"].strip()
        require(
            0 < len(prompt) <= 6000 and 0 < len(intent) <= 500,
            "Supply a prompt and a short story purpose",
        )
        require(
            type(request.get("match_speed")) is bool,
            "Choose whether to match incoming speed",
        )
        steps = max(1, round(values["duration"] * s["speed"] * 2))
        duration = steps / 2
        center = [values["center_x"] * 1.5, values["center_y"]]
        fitted, residual = incoming_velocity(
            s["incoming_phrases"], s["source_seconds"], center
        )
        v0 = fitted if request["match_speed"] else [0, 0, 0, 0]
        # Plan directions describe the viewpoint; image translation has the opposite sign.
        end = [
            -values["pan_x"] * 1.5,
            -values["pan_y"],
            math.log(values["zoom"]),
            math.radians(values["roll"]),
        ]
        v1 = [-values["end_drift"] * 1.5 / s["speed"], 0, 0, 0]
        phrase = {
            "kind": "continuation",
            "start": s["source_seconds"],
            "duration": duration,
            "center": center,
            "end": end,
            "velocity_start": v0,
            "velocity_end": v1,
        }
        config = copy.deepcopy(s["config"])
        last_frame = s["source_frame"] + steps * 12
        config.update(
            prefix_root=str(s["root"].relative_to(self.app)),
            prefix_through=s["source_frame"],
            duration=(last_frame + 12) / FPS,
            painting_frames=[
                f for f in config["painting_frames"] if f <= s["source_frame"]
            ]
            + list(range(s["source_frame"] + 12, last_frame + 1, 12)),
            phrases=[phrase],
        )
        prompt_events = config.get("prompt_schedule", config["scenes"])
        config["prompt_schedule"] = [
            e for e in prompt_events if e["at"] <= s["source_seconds"]
        ] + [
            {"at": s["source_seconds"] + 0.5, "name": "continuation", "prompt": prompt}
        ]
        # Preserve the inherited strength at the branch; use the chosen level for the new paintings.
        config["noise_schedule"] = [
            e for e in config.get("noise_schedule", []) if e["at"] < s["source_seconds"]
        ] + [
            {"at": s["source_seconds"], "noise": s["noise"]},
            {"at": s["source_seconds"] + 0.5, "noise": values["noise"]},
        ]
        config["seeds_by_frame"] = {
            str(f): config.get("seeds_by_frame", {}).get(
                str(f), config["seed"] + 1000 + f
            )
            for f in config["painting_frames"][1:]
        }
        u = np.linspace(0, 1, 97)
        states = (
            (-2 * u**3 + 3 * u * u)[:, None] * np.array(end)
            + (u**3 - 2 * u * u + u)[:, None] * duration * np.array(v0)
            + (u**3 - u * u)[:, None] * duration * np.array(v1)
        )
        scales = np.exp(states[:, 2])
        require(
            np.isfinite(states).all() and scales.min() >= 0.2 and scales.max() <= 12,
            "Incoming speed causes excessive zoom; shorten duration or disable speed matching",
        )
        warnings = []
        if residual > 0.005:
            warnings.append(
                "Incoming regional deformation is only approximately matched by pan, zoom and roll."
            )
        if (
            scales.max() > max(1, values["zoom"]) * 1.03
            or scales.min() < min(1, values["zoom"]) * 0.97
        ):
            warnings.append(
                "Matching the incoming speed overshoots the requested final scale before settling. Inspect playback."
            )
        timeline = [
            {
                "after": round(i / 2 / s["speed"], 3),
                "noise": values["noise"],
                "prompt": "New description",
            }
            for i in range(1, steps + 1)
        ]
        summary = {
            "display_start": s["display_seconds"],
            "source_frame": s["source_frame"],
            "duration": duration / s["speed"],
            "source_duration": duration,
            "speed": s["speed"],
            "zoom_min": float(scales.min()),
            "zoom_max": float(scales.max()),
            "zoom_end": values["zoom"],
            "incoming_velocity": fitted,
            "outgoing_start_velocity": v0,
            "incoming_residual": residual,
            "warnings": warnings,
            "timeline": timeline,
            "intent": intent,
            "prompt": prompt,
        }
        return s, config, summary

    def preview(self, request):
        require(
            self.lock.acquire(blocking=False),
            "Another preview is rendering; try again shortly",
        )
        try:
            s, config, summary = self.plan(request)
            identifier = uuid.uuid4().hex
            folder = self.work / identifier
            folder.mkdir(parents=True)
            lead = min(FPS, s["display_frame"])
            count = lead + round(summary["duration"] * FPS) + 1
            with Image.open(s["painting"]) as im:
                require(
                    im.size[0] / im.size[1] == 1.5,
                    "First planner supports the current 3:2 artwork",
                )
                rgb = np.array(
                    im.convert("RGB").resize(
                        (PREVIEW_WIDTH, PREVIEW_WIDTH * 2 // 3),
                        Image.Resampling.LANCZOS,
                    )
                )
            height = rgb.shape[0]
            command = [
                "ffmpeg",
                "-v",
                "error",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-s",
                f"{PREVIEW_WIDTH}x{height}",
                "-r",
                str(FPS),
                "-i",
                "-",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "19",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(folder / "preview.mp4"),
            ]
            with subprocess.Popen(
                command, stdin=subprocess.PIPE, stderr=subprocess.PIPE
            ) as proc:
                try:
                    for f in range(s["display_frame"] - lead, s["display_frame"]):
                        row = s["manifest"]["output_frames"][f]
                        path = under(s["video"].parent / row["file"], self.app)
                        require(sha(path) == row["sha256"], "Lead-in frame changed")
                        with Image.open(path) as im:
                            frame = np.array(
                                im.convert("RGB").resize(
                                    (PREVIEW_WIDTH, height), Image.Resampling.LANCZOS
                                )
                            )
                        proc.stdin.write(frame.tobytes())
                    for i in range(count - lead):
                        t = s["source_seconds"] + i / FPS * s["speed"]
                        frame = warp_at_time(
                            rgb, s["source_seconds"], t, config["phrases"]
                        )
                        proc.stdin.write(frame.tobytes())
                    proc.stdin.close()
                    error = proc.stderr.read().decode()
                    require(proc.wait() == 0, error or "Preview encoding failed")
                except BaseException:
                    proc.kill()
                    proc.wait()
                    raise
            summary.update(
                id=identifier,
                lead_seconds=lead / FPS,
                frame_count=count,
                fps=FPS,
                preview_path=str(folder / "preview.mp4"),
                summary_path=str(folder / "summary.json"),
                request_path=str(folder / "request.json"),
            )
            save(folder / "config.json", config)
            save(folder / "request.json", request)
            save(folder / "summary.json", summary)
            save(
                folder / "source.json",
                {
                    "source": request["source"],
                    "frame": request["frame"],
                    "painting_sha256": s["painting_sha256"],
                    "config_sha256": sha(s["root"] / "config.json"),
                    "video_sha256": sha(s["video"]),
                },
            )
            return summary
        finally:
            self.lock.release()

    def save_draft(self, identifier):
        require(
            re.fullmatch("[a-f0-9]{32}", identifier) is not None, "Invalid preview id"
        )
        folder = self.work / identifier
        with self.lock:
            if (folder / "saved.json").exists():
                return read(folder / "saved.json")
            record = read(folder / "source.json")
            s = self.selection(record["source"], record["frame"])
            require(
                s["painting_sha256"] == record["painting_sha256"]
                and sha(s["root"] / "config.json") == record["config_sha256"]
                and sha(s["video"]) == record["video_sha256"],
                "Source changed after preview; render a fresh preview",
            )
            config = read(folder / "config.json")
            summary = read(folder / "summary.json")
            # Parent is a case inside this project's exports tree.
            project = next(
                (p for p in s["root"].parents if p.parent.name == "projects"), None
            )
            require(project is not None, "Cannot find owning project")
            case = "branch-" + identifier[:12]
            root = project / "branches" / case
            prefix = []
            for f in config["painting_frames"]:
                if f > config["prefix_through"]:
                    break
                source = s["root"] / f"anchors/{f:04d}.png"
                digest = sha(source)
                index = s["timing"]["source_anchor_frames"].index(f)
                display = s["timing"]["delivery_anchor_frames"][index]
                require(
                    s["manifest"]["output_frames"][display]["sha256"] == digest,
                    "An earlier preserved painting changed",
                )
                prefix.append(
                    {
                        "frame": f,
                        "source": str(source.relative_to(self.app)),
                        "sha256": digest,
                    }
                )
            # Verify the complete retained prefix before creating the new branch.
            root.mkdir(parents=True, exist_ok=False)
            for row in prefix:
                copy_verified(
                    self.app / row["source"], root / f"anchors/{row['frame']:04d}.png"
                )
            config["case"] = case
            save(root / "config.json", config)
            save(root / "prefix.json", prefix)
            save(
                root / "draft.json",
                {
                    "status": "draft-not-generated",
                    "intent": summary["intent"],
                    "source": record,
                    "motion_preview": summary,
                },
            )
            copy_verified(folder / "preview.mp4", root / "motion-preview.mp4")
            result = {
                "id": case,
                "path": str(root.relative_to(self.app)),
                "paintings_preserved": len(prefix),
                "status": "draft-not-generated",
            }
            save(folder / "saved.json", result)
            return result
