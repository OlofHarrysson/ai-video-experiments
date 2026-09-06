"""Submit an existing Difforum graph to ComfyUI and retain frames and receipts.

Graph adapted from Difforum's MIT-licensed examples/_smoke_render_sdxl.py.
See DIFforum-LICENSE and README.md for source provenance.
"""

import argparse
import datetime
import json
import pathlib
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
WORKFLOW = ROOT / "workflows/sdxl-feedback.api.json"
PROJECTS = ROOT / "projects"
RENDER_TIMEOUT_SECONDS = 1800
DIFFORUM_COMMIT = "1d750efd3c1d1dda792b8ef6c14b06a14a69f879"
MODEL_SHA256 = "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b"


def slug(value):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise argparse.ArgumentTypeError("Use lowercase letters/numbers separated by hyphens.")
    return value


def init_project(name):
    folder = PROJECTS / slug(name)
    folder.mkdir(parents=True, exist_ok=False)
    for directory in ("references/assets", "experiments", "runs", "cuts", "exports"):
        (folder / directory).mkdir(parents=True)
    title = name.replace("-", " ").capitalize()
    (folder / "README.md").write_text(
        f"# {title}\n\nIntent: describe the film or creative study.\n\n"
        "Current cut: none selected.\n\n"
        "## Experiments\n\n- [Baseline](experiments/baseline.md): planned.\n\n"
        "[References](references/README.md) · [runs](runs/README.md) · "
        "[cuts](cuts/README.md) · [exports](exports/README.md)\n\n"
        "Follow the [working convention](../../../../docs/workflow.md).\n"
    )
    (folder / "experiments/baseline.md").write_text(
        "# Baseline\n\nStatus: planned.\n\n## Question\n\nTo describe.\n\n"
        "## Comparison\n\nWhat changes and what stays fixed?\n\n"
        "## Cost boundary\n\nSet before rendering.\n\n"
        "## Runs and findings\n\nNo runs yet. Record playback findings and source ranges here.\n"
    )
    for directory, description in {
        "references": "Keep original media in `assets/`. Record source, purpose and SHA-256 here.",
        "runs": "Unique render attempts go here. Keep every attempt; link reviews from experiment notes.",
        "cuts": "Save each cut as v001.md, v002.md, etc. Record source path, FPS and half-open frame ranges.",
        "exports": "Use experiment.py assemble for versioned previews. Preserve older versions and source ranges.",
    }.items():
        (folder / directory / "README.md").write_text(
            f"# {directory.capitalize()}\n\n{description}\n\n"
            "See the [working convention](../../../../../docs/workflow.md).\n"
        )
    print(f"Created {folder}; write the baseline question and add this project to projects/README.md.")


def project_for_run(project, experiment):
    folder = PROJECTS / slug(project)
    if not (folder / "README.md").is_file():
        raise ValueError(f"Project not found: {project}. Create it with init-project first.")
    note = folder / "experiments" / f"{slug(experiment)}.md"
    if not note.is_file():
        raise ValueError(f"Write the experiment note before rendering: {note}")
    return folder


def request(base, route, payload=None, binary=False):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        base.rstrip("/") + route, data=data,
        headers={"User-Agent": "deforum-experiment/0.1", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"ComfyUI {route}: HTTP {error.code}: {error.read().decode()}") from error
    return body if binary else json.loads(body)


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def make_graph(denoise, frames, prefix):
    graph = json.loads(WORKFLOW.read_text())
    graph["7"]["inputs"]["max_frames"] = frames
    graph["9"]["inputs"]["schedule"] = f"0:({denoise})"
    graph["11"]["inputs"]["filename_prefix"] = prefix
    return graph


def depth_camera_graph(graph, preview, frames, translation_x=0.02):
    graph['8']['inputs'].update(mode='3d', translation_x=f'0:({translation_x})',
                               translation_y='0:(0)', translation_z='0:(0)',
                               rotation_3d_z='0:(0)', zoom='0:(1)')
    graph['30'] = {'class_type': 'DownloadAndLoadDepthAnythingV2Model', 'inputs': {
        'model': 'depth_anything_v2_vits_fp32.safetensors', 'precision': 'fp32'}}
    graph['31'] = {'class_type': 'DepthAnything_V2', 'inputs': {'da_model': ['30', 0], 'images': ['6', 0]}}
    graph['32'] = {'class_type': 'SaveImage', 'inputs': {'images': ['31', 0], 'filename_prefix': 'depth'}}
    depth = {'depth': ['31', 0], 'near': 1.0, 'far': 10.0,
             'invert_depth': False, 'translation_scale': 1.0}
    if preview:
        # Guide poses include delta[0]; feedback starts with the untouched anchor.
        graph['8']['inputs']['translation_x'] = f'0:(0), 1:({translation_x})'
        graph['7']['inputs']['max_frames'] = frames
        graph['10'] = {'class_type': 'DifforumGuideBuilder', 'inputs': {
            'anchor_image': ['6', 0], 'camera': ['8', 0], 'params': ['7', 0],
            'warp_mode': 'force_3d', **depth}}
        graph['33'] = {'class_type': 'MaskToImage', 'inputs': {'mask': ['10', 1]}}
        graph['34'] = {'class_type': 'SaveImage', 'inputs': {'images': ['33', 0], 'filename_prefix': 'coverage'}}
    else:
        graph['10']['inputs'].update(depth)
    return graph


def preflight(base, graph):
    info = request(base, "/object_info")
    missing = sorted({node["class_type"] for node in graph.values()} - info.keys())
    if missing:
        raise RuntimeError(f"Missing ComfyUI nodes: {missing}")
    checkpoint = graph["1"]["inputs"]["ckpt_name"]
    choices = info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
    if checkpoint not in choices:
        raise RuntimeError(f"Checkpoint not installed: {checkpoint}")
    return request(base, "/system_stats")


def collect(folder):
    receipt = json.loads((folder / "submission.json").read_text())
    if receipt.get('transport') == 'runpod-serverless':
        from serverless_client import collect as collect_serverless
        return collect_serverless(folder)
    if receipt.get("collected_at"):
        assets = [folder / "preview.mp4"] + [
            folder / "frames" / f"{i:04d}.png" for i in range(receipt["frames"])
        ]
        if not all(path.is_file() and path.stat().st_size for path in assets):
            raise RuntimeError("Completed archive is missing assets; restore them from backup.")
        print(f"Already collected: {folder / 'preview.mp4'}", flush=True)
        return
    base, prompt_id = receipt["base_url"], receipt["prompt_id"]
    deadline = time.monotonic() + RENDER_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        history = request(base, f"/history/{prompt_id}")
        if prompt_id in history:
            entry = history[prompt_id]
            save_json(folder / "history.json", entry)
            status = entry.get("status", {})
            if status.get("status_str") == "error":
                raise RuntimeError(f"Render failed; inspect {folder / 'history.json'}")
            if status.get("completed"):
                images = entry.get("outputs", {}).get("11", {}).get("images", [])
                if len(images) != receipt["frames"]:
                    raise RuntimeError(f"Expected {receipt['frames']} frames, received {len(images)}")
                break
        time.sleep(3)
    else:
        raise TimeoutError("Render wait expired; the remote job may still run. Use collect to reconnect.")

    frames_dir = folder / "frames"
    frames_dir.mkdir(exist_ok=True)
    for index, image in enumerate(images):
        target = frames_dir / f"{index:04d}.png"
        if target.exists():
            with target.open("rb") as existing:
                if existing.read(8) != b"\x89PNG\r\n\x1a\n":
                    raise RuntimeError(f"Existing frame is invalid: {target}")
            continue
        query = urllib.parse.urlencode({
            "filename": image["filename"], "subfolder": image.get("subfolder", ""),
            "type": image.get("type", "output"),
        })
        data = request(base, "/view?" + query, binary=True)
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError(f"Frame {index} was not a PNG")
        with target.open("xb") as output:
            output.write(data)
    preview = folder / "preview.mp4"
    if not preview.exists():
        temporary = folder / "preview.encoding.mp4"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "8",
            "-i", str(frames_dir / "%04d.png"), "-vf", "fps=24",
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
            str(temporary),
        ], check=True)
        temporary.rename(preview)
    receipt["collected_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_json(folder / "submission.json", receipt)
    print(f"Saved {len(images)} frames and {folder / 'preview.mp4'}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init-project", help="Create a local project and baseline note.")
    init.add_argument("name", type=slug)
    run = commands.add_parser("run")
    run.add_argument("--project", type=slug, required=True)
    run.add_argument("--experiment", type=slug, required=True)
    run.add_argument("--url", help="Explicit legacy Pod URL; omit to use Serverless.")
    run.add_argument("--denoise", type=float, choices=[0.3, 0.4, 0.5], default=0.4)
    run.add_argument("--frames", type=int, choices=[8, 40], default=40)
    resume = commands.add_parser("collect")
    resume.add_argument("folder", type=pathlib.Path)
    branch = commands.add_parser('continue', help='Branch from a collected frame through Serverless.')
    branch.add_argument('--project', type=slug, required=True)
    branch.add_argument('--experiment', type=slug, default='continuation')
    branch.add_argument('--parent-run', required=True)
    branch.add_argument('--frame', type=int, required=True)
    branch.add_argument('--new-frames', type=int, default=8)
    branch.add_argument('--camera', choices=['2d', '3d'], default='2d')
    guide = commands.add_parser('camera-preview', help='Depth-based camera warp without diffusion.')
    guide.add_argument('--project', type=slug, required=True)
    guide.add_argument('--experiment', type=slug, default='3d-parallax')
    guide.add_argument('--parent-run', required=True)
    guide.add_argument('--frame', type=int, required=True)
    guide.add_argument('--new-frames', type=int, default=8)
    cut = commands.add_parser('assemble', help='Create a new cut from explicit source ranges.')
    cut.add_argument('--project', type=slug, required=True)
    cut.add_argument('--version', type=slug, required=True)
    cut.add_argument('--ranges', type=pathlib.Path, required=True,
                     help='JSON list of {run, in, out}; out is exclusive, source FPS is 8.')
    args = parser.parse_args()
    if args.command == "init-project":
        init_project(args.name)
        return
    if args.command == "collect":
        collect(args.folder.resolve())
        return
    if args.command == 'assemble':
        from editing import assemble
        print(assemble(PROJECTS / args.project, args.version, json.loads(args.ranges.read_text())))
        return
    project = project_for_run(args.project, args.experiment)
    if args.command in ('continue', 'camera-preview'):
        import editing
        import serverless_client
        parent = (project / 'runs' / args.parent_run).resolve()
        if parent.parent != (project / 'runs').resolve():
            raise ValueError('Parent must be a run in this project')
        graph, source, lineage = editing.continuation(parent, args.frame, args.new_frames)
        if args.command == 'camera-preview' or args.camera == '3d':
            graph = depth_camera_graph(graph, preview=args.command == 'camera-preview',
                                       frames=lineage['frames'])
            lineage['camera'] = 'relative-depth lateral scene translation +0.02/frame'
        if args.command == 'camera-preview':
            lineage.update(start_frame=0, end_frame=lineage['frames'])
        serverless_client.submit(project, args.experiment, graph, lineage['frames'], lineage, source)
        return
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    name = f"{stamp}-denoise-{args.denoise:.2f}-{args.frames}f"
    graph = make_graph(args.denoise, args.frames, f"deforum/{args.project}/{name}")
    if not args.url:
        from serverless_client import submit
        submit(project, args.experiment, graph, args.frames, {'denoise': args.denoise})
        return
    stats = preflight(args.url, graph)
    folder = project / "runs" / name
    folder.mkdir(parents=True, exist_ok=False)
    save_json(folder / "workflow.api.json", graph)
    save_json(folder / "system-stats.json", stats)
    # Never retry a submission automatically: a lost response can hide an accepted job.
    result = request(args.url, "/prompt", {"prompt": graph})
    save_json(folder / "submit-response.json", result)
    if result.get("node_errors") or not result.get("prompt_id"):
        raise RuntimeError(f"Workflow rejected: {result}")
    save_json(folder / "submission.json", {
        "project": args.project, "experiment": args.experiment,
        "base_url": args.url, "prompt_id": result["prompt_id"], "frames": args.frames,
        "denoise": args.denoise, "generated_fps": 8, "delivery_fps": 24,
        "difforum_commit": DIFFORUM_COMMIT, "model_sha256": MODEL_SHA256,
        "submitted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    print(f"Submitted {result['prompt_id']}; receipts: {folder}", flush=True)
    collect(folder)


if __name__ == "__main__":
    main()
