"""Serve only the generated reviewer on loopback; lifecycle managed by Devrun."""

import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from media_review import APP, build

SESSION = APP / "media_review/sessions/seed-for-sea.json"
OUTPUT = APP / "projects/modern-model-study/exports/media-review-seed-for-sea-v001"
DEFAULT_PORT = 3000
NAMED_REVIEWS = {
    "/seed-for-sea": APP
    / "projects/modern-model-study/exports/media-review-seed-for-sea-v001/full-quality.html",
    "/doorway-cli": APP
    / "projects/modern-model-study/exports/media-review-doorway-cli-v001/full-quality.html",
    "/doorway": APP
    / "projects/modern-model-study/exports/media-review-doorway-v001/full-quality.html",
    "/doorway-attempts": APP
    / "projects/modern-model-study/exports/media-review-doorway-attempts-v001/full-quality.html",
    "/storytelling": APP
    / "projects/modern-model-study/exports/media-review-storytelling-v001/full-quality.html",
    "/storytelling-planned": APP
    / "projects/modern-model-study/exports/media-review-storytelling-planned-v001/full-quality.html",
    "/storytelling-improvised": APP
    / "projects/modern-model-study/exports/media-review-storytelling-improvised-v001/full-quality.html",
    "/storytelling-hybrid": APP
    / "projects/modern-model-study/exports/media-review-storytelling-hybrid-v001/full-quality.html",
    "/storytelling-release": APP
    / "projects/modern-model-study/exports/media-review-storytelling-release-v001/full-quality.html",
    "/motion-recipes": APP
    / "projects/modern-model-study/exports/media-review-motion-recipes-v001/full-quality.html",
    "/continuous-motion": APP
    / "projects/modern-model-study/exports/media-review-continuous-motion-v001/full-quality.html",
    "/continuous-film": APP
    / "projects/modern-model-study/exports/media-review-continuous-film-v001/full-quality.html",
    "/continuous-finishing": APP
    / "projects/modern-model-study/exports/media-review-continuous-finishing-v001/full-quality.html",
    "/fluent-hour": APP
    / "projects/modern-model-study/exports/media-review-fluent-hour-v001/full-quality.html",
    "/story-hour": APP
    / "projects/modern-model-study/exports/media-review-story-hour-v001/full-quality.html",
    "/fluent-paths": APP
    / "projects/modern-model-study/exports/media-review-fluent-paths-v001/full-quality.html",
    "/fluent-strength": APP
    / "projects/modern-model-study/exports/media-review-fluent-strength-v001/full-quality.html",
    "/fluent-control": APP
    / "projects/modern-model-study/exports/media-review-fluent-control-v001/full-quality.html",
    "/fluent-worlds": APP
    / "projects/modern-model-study/exports/media-review-fluent-worlds-v001/full-quality.html",
    "/fluent-endings": APP
    / "projects/modern-model-study/exports/media-review-fluent-endings-v001/full-quality.html",
    "/surreal-hour": APP
    / "projects/modern-model-study/exports/media-review-surreal-hour-v001/full-quality.html",
    "/story-paths": APP
    / "projects/modern-model-study/exports/media-review-story-paths-v001/full-quality.html",
    "/story-regional": APP
    / "projects/modern-model-study/exports/media-review-story-regional-v001/full-quality.html",
    "/story-endings": APP
    / "projects/modern-model-study/exports/media-review-story-endings-v001/full-quality.html",
    "/story-extras": APP
    / "projects/modern-model-study/exports/media-review-story-extras-v001/full-quality.html",
    "/motion-hour": APP
    / "projects/modern-model-study/exports/media-review-motion-hour-v001/full-quality.html",
    "/surreal-first": APP
    / "projects/modern-model-study/exports/media-review-surreal-first-v001/full-quality.html",
    "/surreal-piano": APP
    / "projects/modern-model-study/exports/media-review-surreal-piano-v001/full-quality.html",
    "/surreal-fish": APP
    / "projects/modern-model-study/exports/media-review-surreal-fish-v001/full-quality.html",
    "/surreal-garden": APP
    / "projects/modern-model-study/exports/media-review-surreal-garden-v001/full-quality.html",
    "/motion-paths": APP
    / "projects/modern-model-study/exports/media-review-motion-paths-v001/full-quality.html",
    "/motion-travel": APP
    / "projects/modern-model-study/exports/media-review-motion-travel-v001/full-quality.html",
    "/motion-pace": APP
    / "projects/modern-model-study/exports/media-review-motion-pace-v001/full-quality.html",
    "/two-hour-lab": APP
    / "projects/modern-model-study/exports/media-review-two-hour-lab-v001/full-quality.html",
    "/two-hour-porcelain": APP
    / "projects/modern-model-study/exports/media-review-two-hour-porcelain-v001/full-quality.html",
    "/two-hour-velvet": APP
    / "projects/modern-model-study/exports/media-review-two-hour-velvet-v001/full-quality.html",
    "/two-hour-conditioning": APP
    / "projects/modern-model-study/exports/media-review-two-hour-conditioning-v001/full-quality.html",
    "/two-hour-controls": APP
    / "projects/modern-model-study/exports/media-review-two-hour-controls-v001/full-quality.html",
    "/two-hour-models": APP
    / "projects/modern-model-study/exports/media-review-two-hour-models-v001/full-quality.html",
    "/transition-stages": APP
    / "projects/modern-model-study/exports/media-review-transition-stages-v001/full-quality.html",
    "/transition-frequency": APP
    / "projects/modern-model-study/exports/media-review-transition-frequency-v001/full-quality.html",
    "/early-settle": APP
    / "projects/modern-model-study/exports/media-review-early-settle-v001/full-quality.html",
    "/hold-transform": APP
    / "projects/modern-model-study/exports/media-review-hold-transform-v001/full-quality.html",
    "/continuity-controls": APP
    / "projects/modern-model-study/exports/media-review-continuity-controls-v001/full-quality.html",
    "/state-replay": APP
    / "projects/modern-model-study/exports/media-review-state-replay-v001/full-quality.html",
    "/history-recurrence": APP
    / "projects/modern-model-study/exports/media-review-history-recurrence-v001/full-quality.html",
}


class ReviewHandler(BaseHTTPRequestHandler):
    def send_video(self, path, head=False):
        size = path.stat().st_size
        start = 0
        end = size - 1
        requested = self.headers.get("Range")
        if requested:
            match = re.fullmatch(r"bytes=(\d+)-(\d*)", requested)
            if not match:
                self.send_error(416)
                return
            start = int(match[1])
            end = min(size - 1, int(match[2])) if match[2] else size - 1
            if not 0 <= start <= end < size:
                self.send_error(416)
                return
        self.send_response(206 if requested else 200)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        if requested:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        if not head:
            with path.open("rb") as stream:
                stream.seek(start)
                remaining = end - start + 1
                try:
                    while remaining:
                        chunk = stream.read(min(262144, remaining))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    pass

    def do_HEAD(self):
        self.respond(head=True)

    def do_GET(self):
        self.respond()

    def respond(self, head=False):
        parsed = urlsplit(self.path)
        route = parsed.path
        if route == "/review-media":
            try:
                source = parse_qs(parsed.query)["source"][0]
                if source not in self.server.media_sources:
                    raise ValueError("Unknown review media")
                path = (APP / source).resolve()
                if not path.is_relative_to(APP.resolve()):
                    raise ValueError("Path outside workspace")
                self.send_video(path, head)
            except (ValueError, KeyError, OSError) as error:
                self.send_error(400, str(error))
            return
        path = (
            self.server.review_path
            if route in ("/", "/full-quality.html")
            else NAMED_REVIEWS.get(route)
        )
        if path is None or not path.is_file():
            self.send_error(404)
            return
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if not head:
            self.wfile.write(content)


def main():
    result = build(SESSION, OUTPUT, local=True)
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = ThreadingHTTPServer(("127.0.0.1", port), ReviewHandler)
    sources = {}
    for session in (APP / "media_review/sessions").glob("*.json"):
        for item in json.loads(session.read_text()).get("clips", []):
            sources[item["source"]] = item["label"]
    server.media_sources = sources
    server.review_path = Path(result["local"])
    print(f"Media review ready at http://127.0.0.1:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
