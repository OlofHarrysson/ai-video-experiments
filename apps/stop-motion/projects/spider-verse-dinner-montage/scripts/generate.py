# /// script
# requires-python = ">=3.11"
# ///
"""Generate an experiment's base paintings and variations with fal.

Usage, from this project folder:

    uv run --script scripts/generate.py base experiments/swap-test.json
    uv run --script scripts/generate.py vary experiments/swap-test.json RUN_DIR BASE_ID [--only 05 11]

`base` creates runs/<experiment>-<timestamp>/ with the base candidates. `vary` edits the chosen
base candidate, such as base-2, never a previous variation. A repeated variation gets a new
file (05-b.png) so rejects are kept. Every call is appended to RUN_DIR/records.jsonl, and the
configured cost cap applies across the run. Requires FAL_KEY in this project's .env.
"""

import argparse
import hashlib
import json
import threading
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
FAL_RUN = "https://fal.run/"
PARALLEL_CALLS = 4
_record_lock = threading.Lock()


def now() -> datetime:
    return datetime.now(UTC).astimezone()


def fal_key() -> str:
    env = PROJECT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "FAL_KEY" and value.strip():
                return value.strip()
    raise SystemExit(f"FAL_KEY is missing: add it to {env} (see .env.example)")


def call(endpoint: str, payload: dict, key: str) -> dict:
    request = urllib.request.Request(
        FAL_RUN + endpoint,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"{endpoint} returned {error.code}: {error.read().decode()}") from None


def records(run: Path) -> list[dict]:
    path = run / "records.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def append_record(run: Path, entry: dict) -> None:
    with _record_lock, (run / "records.jsonl").open("a") as file:
        file.write(json.dumps(entry) + "\n")


def check_budget(run: Path, config: dict, images: int) -> None:
    spent = sum(entry["cost_usd"] for entry in records(run))
    planned = images * config["price_per_image_usd"]
    if spent + planned > config["cost_cap_usd"] + 1e-9:
        raise SystemExit(
            f"Refusing: ${spent:.2f} spent + ${planned:.2f} planned exceeds the ${config['cost_cap_usd']:.2f} cap"
        )


def free_path(directory: Path, stem: str) -> Path:
    for suffix in ["", *(f"-{letter}" for letter in "bcdefghijklmnopqrstuvwxyz")]:
        path = directory / f"{stem}{suffix}.png"
        if not path.exists():
            return path
    raise RuntimeError(f"too many versions of {stem}")


def save(run: Path, directory: Path, stem: str, image: dict) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(image["url"], timeout=300) as response:
        data = response.read()
    path = free_path(directory, stem)
    path.write_bytes(data)
    return {
        "file": str(path.relative_to(run)),
        "sha256": hashlib.sha256(data).hexdigest(),
        "width": image.get("width"),
        "height": image.get("height"),
        "url": image["url"],
    }


def common(config: dict) -> dict:
    return {
        "aspect_ratio": config["aspect_ratio"],
        "resolution": config["resolution"],
        "output_format": config["output_format"],
    }


def generate_base(config: dict, key: str) -> Path:
    run = PROJECT / "runs" / f"{config['experiment']}-{now():%Y%m%d-%H%M%S}"
    run.mkdir(parents=True)
    count = config["base"]["candidates"]
    check_budget(run, config, count)
    payload = {
        **common(config),
        "prompt": config["base"]["prompt"],
        "num_images": count,
        "seed": config["seed"],
    }
    result = call(config["base_endpoint"], payload, key)
    outputs = [save(run, run, f"base-{n}", image) for n, image in enumerate(result["images"], start=1)]
    append_record(run, {
        "kind": "base",
        "endpoint": config["base_endpoint"],
        "payload": payload,
        "outputs": outputs,
        "cost_usd": len(outputs) * config["price_per_image_usd"],
        "time": now().isoformat(timespec="seconds"),
    })
    return run


def generate_variation(run: Path, config: dict, key: str, base: dict, variation: dict) -> str:
    payload = {
        **common(config),
        "prompt": config["edit_prompt"].format(**variation),
        "image_urls": [base["url"]],
        "num_images": 1,
        "seed": config["seed"] + int(variation["id"]),
    }
    result = call(config["edit_endpoint"], payload, key)
    output = save(run, run / "variations", variation["id"], result["images"][0])
    append_record(run, {
        "kind": "variation",
        "id": variation["id"],
        "base": base["file"],
        "endpoint": config["edit_endpoint"],
        "payload": payload,
        "outputs": [output],
        "cost_usd": config["price_per_image_usd"],
        "time": now().isoformat(timespec="seconds"),
    })
    return output["file"]


def generate_variations(run: Path, config: dict, key: str, base_id: str, only: list[str] | None) -> None:
    bases = [output for entry in records(run) if entry["kind"] == "base" for output in entry["outputs"]]
    base = next((output for output in bases if Path(output["file"]).stem == base_id), None)
    if base is None:
        raise SystemExit(f"{base_id} is not a base candidate in {run}")
    selected = [v for v in config["variations"] if only is None or v["id"] in only]
    check_budget(run, config, len(selected))
    with ThreadPoolExecutor(PARALLEL_CALLS) as pool:
        for file in pool.map(lambda v: generate_variation(run, config, key, base, v), selected):
            print(file)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["base", "vary"])
    parser.add_argument("config", type=Path)
    parser.add_argument("run", type=Path, nargs="?")
    parser.add_argument("base_id", nargs="?")
    parser.add_argument("--only", nargs="+")
    args = parser.parse_args()

    config = json.loads(args.config.read_text())
    if args.command == "vary" and (args.run is None or args.base_id is None):
        parser.error("vary needs RUN_DIR and BASE_ID")
    key = fal_key()
    if args.command == "base":
        run = generate_base(config, key)
        print(run)
    else:
        run = args.run.resolve()
        generate_variations(run, config, key, args.base_id, args.only)
    print(f"spent ${sum(entry['cost_usd'] for entry in records(run)):.2f} of ${config['cost_cap_usd']:.2f}")


if __name__ == "__main__":
    main()
