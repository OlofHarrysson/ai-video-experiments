"""Serve only the generated reviewer on loopback; lifecycle managed by Devrun."""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from media_review import APP, build

SESSION = APP / 'media_review/sessions/early-settle.json'
OUTPUT = APP / 'projects/modern-model-study/exports/media-review-early-settle-v001'
DEFAULT_PORT = 3000
NAMED_REVIEWS = {
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
