"""Agent-operated motion planning. Local files only; no web service or inference."""

import argparse
import json
from pathlib import Path

from deforum_lab.media.branching import BranchPlanner
from deforum_lab.records import read, save


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--app", type=Path, default=Path.cwd(), help="Deforum app root (default: cwd)"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser(
        "inspect", help="Inspect the preceding saved painting"
    )
    init = commands.add_parser("init", help="Write an editable JSON continuation plan")
    for command in (inspect, init):
        command.add_argument("source", help="MP4 path relative to --app, or inside it")
        command.add_argument(
            "--frame", type=int, required=True, help="Delivery frame, zero-based"
        )
    init.add_argument("--intent", required=True, help="What this move should achieve")
    init.add_argument(
        "--out", type=Path, required=True, help="New plan JSON path, relative to cwd"
    )
    preview = commands.add_parser(
        "preview", help="Render the plan with original lead-in"
    )
    preview.add_argument("plan", type=Path)
    save_command = commands.add_parser(
        "save", help="Preserve a preview as a continuation draft"
    )
    save_command.add_argument("id", help="ID returned by preview")
    args = parser.parse_args(argv)
    planner = BranchPlanner(args.app)
    try:
        if args.command in ("inspect", "init"):
            selected = planner.describe(args.source, args.frame)
            if args.command == "inspect":
                result = selected
            else:
                if args.out.exists():
                    raise FileExistsError(f"Plan already exists: {args.out}")
                plan = {
                    "source": selected["source"],
                    "frame": args.frame,
                    "intent": args.intent,
                    "duration": 2,
                    "zoom": 1.2,
                    "pan_x": 0,
                    "pan_y": 0,
                    "roll": 0,
                    "center_x": 0.5,
                    "center_y": 0.5,
                    "end_drift": 0.02,
                    "match_speed": True,
                    "prompt": selected["prompt"],
                    "noise": selected["noise"],
                }
                planner.plan(plan)
                save(args.out, plan)
                result = {"plan_path": str(args.out.resolve()), "selection": selected}
        elif args.command == "preview":
            plan = read(args.plan)
            if not isinstance(plan, dict):
                raise TypeError("Expected a JSON plan object")
            result = planner.preview(plan)
        else:
            result = planner.save_draft(args.id)
            result = {**result, "branch_path": str(planner.app / result["path"])}
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, f"motion-preview: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
