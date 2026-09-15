"""Serve only the generated reviewer on loopback; lifecycle managed by Devrun."""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from media_review import APP, build

SESSION = APP / 'media_review/sessions/fluent-hour.json'
OUTPUT = APP / 'projects/modern-model-study/exports/media-review-fluent-hour-v001'
DEFAULT_PORT = 3000
NAMED_REVIEWS = {
    '/story-hour': APP / 'projects/modern-model-study/exports/media-review-story-hour-v001/full-quality.html',
    '/fluent-paths': APP / 'projects/modern-model-study/exports/media-review-fluent-paths-v001/full-quality.html',
    '/fluent-strength': APP / 'projects/modern-model-study/exports/media-review-fluent-strength-v001/full-quality.html',
    '/fluent-control': APP / 'projects/modern-model-study/exports/media-review-fluent-control-v001/full-quality.html',
    '/fluent-worlds': APP / 'projects/modern-model-study/exports/media-review-fluent-worlds-v001/full-quality.html',
    '/fluent-endings': APP / 'projects/modern-model-study/exports/media-review-fluent-endings-v001/full-quality.html',
    '/surreal-hour': APP / 'projects/modern-model-study/exports/media-review-surreal-hour-v001/full-quality.html',
    '/story-paths': APP / 'projects/modern-model-study/exports/media-review-story-paths-v001/full-quality.html',
    '/story-regional': APP / 'projects/modern-model-study/exports/media-review-story-regional-v001/full-quality.html',
    '/story-endings': APP / 'projects/modern-model-study/exports/media-review-story-endings-v001/full-quality.html',
    '/story-extras': APP / 'projects/modern-model-study/exports/media-review-story-extras-v001/full-quality.html',
    '/motion-hour': APP / 'projects/modern-model-study/exports/media-review-motion-hour-v001/full-quality.html',
    '/surreal-first': APP / 'projects/modern-model-study/exports/media-review-surreal-first-v001/full-quality.html',
    '/surreal-piano': APP / 'projects/modern-model-study/exports/media-review-surreal-piano-v001/full-quality.html',
    '/surreal-fish': APP / 'projects/modern-model-study/exports/media-review-surreal-fish-v001/full-quality.html',
    '/surreal-garden': APP / 'projects/modern-model-study/exports/media-review-surreal-garden-v001/full-quality.html',

    '/motion-paths': APP / 'projects/modern-model-study/exports/media-review-motion-paths-v001/full-quality.html',
    '/motion-travel': APP / 'projects/modern-model-study/exports/media-review-motion-travel-v001/full-quality.html',
    '/motion-pace': APP / 'projects/modern-model-study/exports/media-review-motion-pace-v001/full-quality.html',
    '/two-hour-lab': APP / 'projects/modern-model-study/exports/media-review-two-hour-lab-v001/full-quality.html',
    '/two-hour-porcelain': APP / 'projects/modern-model-study/exports/media-review-two-hour-porcelain-v001/full-quality.html',
    '/two-hour-velvet': APP / 'projects/modern-model-study/exports/media-review-two-hour-velvet-v001/full-quality.html',
    '/two-hour-conditioning': APP / 'projects/modern-model-study/exports/media-review-two-hour-conditioning-v001/full-quality.html',
    '/two-hour-controls': APP / 'projects/modern-model-study/exports/media-review-two-hour-controls-v001/full-quality.html',
    '/two-hour-models': APP / 'projects/modern-model-study/exports/media-review-two-hour-models-v001/full-quality.html',
    '/transition-stages': APP / 'projects/modern-model-study/exports/media-review-transition-stages-v001/full-quality.html',
    '/transition-frequency': APP / 'projects/modern-model-study/exports/media-review-transition-frequency-v001/full-quality.html',
    '/early-settle': APP / 'projects/modern-model-study/exports/media-review-early-settle-v001/full-quality.html',
    '/hold-transform': APP / 'projects/modern-model-study/exports/media-review-hold-transform-v001/full-quality.html',
    '/continuity-controls': APP / 'projects/modern-model-study/exports/media-review-continuity-controls-v001/full-quality.html',
    '/state-replay': APP / 'projects/modern-model-study/exports/media-review-state-replay-v001/full-quality.html',
    '/history-recurrence': APP / 'projects/modern-model-study/exports/media-review-history-recurrence-v001/full-quality.html',
}


class ReviewHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.respond(head=True)

    def do_GET(self):
        self.respond()

    def respond(self, head=False):
        route = urlsplit(self.path).path
        path = self.server.review_path if route in ('/', '/full-quality.html') else NAMED_REVIEWS.get(route)
        if path is None or not path.is_file():
            self.send_error(404)
            return
        content = path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        if not head:
            self.wfile.write(content)


def main():
    result = build(SESSION, OUTPUT)
    port = int(os.environ.get('PORT', DEFAULT_PORT))
    server = ThreadingHTTPServer(('127.0.0.1', port), ReviewHandler)
    server.review_path = Path(result['full_quality'])
    print(f'Media review ready at http://127.0.0.1:{port}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
