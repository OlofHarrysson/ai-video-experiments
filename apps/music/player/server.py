"""Loopback stem player with acknowledged shared browser controls."""

import argparse
import json
import math
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

WEB = Path(__file__).resolve().parent


def make_handler(bundle):
    manifest = json.loads((bundle / "manifest.json").read_text())
    files = {"/": WEB / "index.html", "/manifest.json": bundle / "manifest.json"}
    for name in ["app.js", "engine.js", "style.css"]:
        files[f"/{name}"] = WEB / name
    ids = {t["id"] for t in manifest["tracks"]}
    for track in manifest["tracks"]:
        path = (bundle / track["url"].lstrip("/")).resolve()
        if not path.is_relative_to(bundle.resolve()):
            raise ValueError("Audio escapes bundle")
        files[track["url"]] = path
    lock = threading.Lock()
    shared = {"session": None, "state": None, "seen": 0, "sequence": 0, "ack": 0}
    commands = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            # Successful heartbeats are not actionable server logs.
            if self.path == "/api/sync" and len(args) > 1 and str(args[1]) == "200":
                return
            super().log_message(fmt, *args)

        def reply(self, code, body, kind="application/json"):
            if not isinstance(body, bytes):
                body = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            route = urlsplit(self.path).path
            if route == "/api/state":
                with lock:
                    return self.reply(
                        200,
                        {
                            "connected": time.monotonic() - shared["seen"] < 4,
                            "state": shared["state"],
                            "last_applied_command": shared["ack"],
                            "pending_commands": len(commands),
                        },
                    )
            path = files.get(route)
            if path is None or not path.is_file():
                return self.reply(404, {"error": "Not found"})
            kinds = {
                ".html": "text/html; charset=utf-8",
                ".js": "text/javascript",
                ".css": "text/css",
                ".wav": "audio/wav",
                ".json": "application/json",
            }
            return self.reply(200, path.read_bytes(), kinds[path.suffix])

        def do_POST(self):
            origin = self.headers.get("Origin")
            if origin and urlsplit(origin).netloc != self.headers.get("Host"):
                return self.reply(403, {"error": "Origin rejected"})
            if self.path not in {"/api/connect", "/api/sync", "/api/control"}:
                return self.reply(404, {"error": "Not found"})
            try:
                size = int(self.headers.get("Content-Length", 0))
                if not 0 < size <= 20000:
                    raise ValueError("Invalid request size")
                item = json.loads(self.rfile.read(size))
                with lock:
                    if self.path == "/api/connect":
                        shared.update(
                            session=str(uuid4()), state=None, seen=0, ack=0, sequence=0
                        )
                        commands.clear()
                        return self.reply(200, {"session": shared["session"]})
                    if self.path == "/api/sync":
                        if (
                            item.get("session") != shared["session"]
                            or not shared["session"]
                        ):
                            return self.reply(
                                409,
                                {
                                    "error": "Shared control moved to another tab. Reload to reconnect."
                                },
                            )
                        ack = item["lastCommand"]
                        if (
                            not isinstance(ack, int)
                            or not shared["ack"] <= ack <= shared["sequence"]
                        ):
                            raise ValueError("Invalid acknowledgement")
                        state = item["state"]
                        if not isinstance(state, dict):
                            raise ValueError("Invalid state")
                        shared.update(state=state, seen=time.monotonic(), ack=ack)
                        commands[:] = [c for c in commands if c["sequence"] > ack]
                        return self.reply(200, {"commands": commands})
                    if time.monotonic() - shared["seen"] >= 4 or not shared["state"]:
                        return self.reply(
                            409, {"error": "Open the player before controlling it"}
                        )
                    action = item.get("action")
                    if action not in {
                        "play",
                        "pause",
                        "seek",
                        "only",
                        "enabled",
                        "reset",
                        "volume",
                        "loop",
                    }:
                        raise ValueError("Unknown action")
                    command = {"action": action}
                    if action in {"only", "enabled"}:
                        track = item.get("track")
                        if track not in ids and not (
                            action == "only" and track is None
                        ):
                            raise ValueError("Unknown sound")
                        command["track"] = track
                    if action in {"enabled", "loop"}:
                        if not isinstance(item.get("value"), bool):
                            raise ValueError("Expected boolean value")
                        command["value"] = item["value"]
                    if action in {"seek", "volume"}:
                        value = float(item["value"])
                        limit = manifest["duration"] if action == "seek" else 1
                        if not math.isfinite(value) or not 0 <= value <= limit:
                            raise ValueError("Value out of range")
                        command["value"] = value
                    if len(commands) >= 32:
                        return self.reply(
                            409,
                            {"error": "Wait for the browser to apply pending controls"},
                        )
                    shared["sequence"] += 1
                    command["sequence"] = shared["sequence"]
                    commands.append(command)
                    return self.reply(202, {"queued": command["sequence"]})
            except (ValueError, KeyError, TypeError) as error:
                self.reply(400, {"error": str(error)})

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
