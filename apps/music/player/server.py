"""Loopback-only stem player; serves declared audio and appends study feedback."""

import argparse
import json
import os
import threading
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

WEB = Path(__file__).resolve().parent
LOCK = threading.Lock()


def make_handler(bundle):
    manifest = json.loads((bundle / "manifest.json").read_text())
    files = {
        "/": WEB / "index.html",
        "/app.js": WEB / "app.js",
        "/engine.js": WEB / "engine.js",
        "/style.css": WEB / "style.css",
        "/manifest.json": bundle / "manifest.json",
    }
    for palette in manifest["palettes"]:
        for track in palette["tracks"].values():
            path = (bundle / track["url"].lstrip("/")).resolve()
            if not path.is_relative_to(bundle.resolve()):
                raise ValueError("Audio escapes bundle")
            files[track["url"]] = path
    feedback = bundle / "feedback.jsonl"

    class Handler(BaseHTTPRequestHandler):
        def reply(self, code, body, kind="application/json"):
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            route = urlsplit(self.path).path
            if route == "/api/feedback":
                with LOCK:
                    rows = (
                        [json.loads(line) for line in feedback.read_text().splitlines()]
                        if feedback.exists()
                        else []
                    )
                return self.reply(200, json.dumps(rows).encode())
            path = files.get(route)
            if path is None or not path.is_file():
                return self.reply(404, b'{"error":"Not found"}')
            kinds = {
                ".html": "text/html; charset=utf-8",
                ".js": "text/javascript",
                ".css": "text/css",
                ".wav": "audio/wav",
                ".json": "application/json",
            }
            return self.reply(200, path.read_bytes(), kinds[path.suffix])

        def do_POST(self):
            if self.path != "/api/feedback":
                return self.reply(404, b"{}")
            origin = self.headers.get("Origin")
            if origin and urlsplit(origin).netloc != self.headers.get("Host"):
                return self.reply(403, b'{"error":"Origin rejected"}')
            try:
                length = int(self.headers.get("Content-Length", 0))
                if not 0 < length <= 10000:
                    raise ValueError("Invalid size")
                item = json.loads(self.rfile.read(length))
                note = str(item["note"]).strip()
                if not 0 < len(note) <= 2000:
                    raise ValueError("Write a note under 2000 characters")
                palette = item["palette"]
                if palette not in [p["id"] for p in manifest["palettes"]]:
                    raise ValueError("Unknown palette")
                position = float(item["time"])
                if not 0 <= position <= manifest["duration"]:
                    raise ValueError("Invalid time")
                ids = {t["id"] for t in manifest["tracks"]}
                muted, solo = item["muted"], item["solo"]
                if (
                    not isinstance(muted, list)
                    or not isinstance(solo, list)
                    or not set(muted + solo) <= ids
                ):
                    raise ValueError("Invalid sounds")
                entry = {
                    "id": str(uuid4()),
                    "created_at": datetime.now(UTC).isoformat(),
                    "note": note,
                    "palette": palette,
                    "time": round(position, 3),
                    "muted": muted,
                    "solo": solo,
                }
                with LOCK, feedback.open("a") as f:
                    f.write(json.dumps(entry) + "\n")
                self.reply(201, json.dumps(entry).encode())
            except (ValueError, KeyError, TypeError) as error:
                self.reply(400, json.dumps({"error": str(error)}).encode())

    return Handler


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "3000")))
    args = parser.parse_args()
    server = ThreadingHTTPServer(
        ("127.0.0.1", args.port), make_handler(args.bundle.resolve())
    )
    print(f"Stem player ready at http://localhost:{args.port}", flush=True)
    server.serve_forever()
