"""Serve only the generated reviewer on loopback; lifecycle managed by Devrun."""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from media_review import APP, build

SESSION = APP / 'media_review/sessions/cfg-audition.json'
OUTPUT = APP / 'projects/modern-model-study/exports/media-review-v002'
DEFAULT_PORT = 3000


class ReviewHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.respond(head=True)

    def do_GET(self):
        self.respond()

    def respond(self, head=False):
        if urlsplit(self.path).path not in ('/', '/full-quality.html'):
            self.send_error(404)
            return
        content = self.server.review_path.read_bytes()
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
