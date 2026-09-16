"""Exercise the loopback HTTP boundary with temporary media, without inference."""

import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

import media_review_server as server


class QuietHandler(server.ReviewHandler):
    def log_message(self, *args):
        pass


class ServerTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.app = Path(tmp.name)
        (self.app / "movie.mp4").write_bytes(b"0123456789")
        (self.app / "local.html").write_text("local review")
        mocked_app = patch.object(server, "APP", self.app)
        mocked_app.start()
        self.addCleanup(mocked_app.stop)
        self.http = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        self.http.media_sources = {"movie.mp4": "Fixture"}
        self.http.review_path = self.app / "local.html"
        thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        thread.start()

        def stop():
            self.http.shutdown()
            self.http.server_close()
            thread.join()

        self.addCleanup(stop)

    def request(self, method, path, body=None, headers=None):
        conn = HTTPConnection(*self.http.server_address, timeout=5)
        try:
            conn.request(method, path, body, headers or {})
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            conn.close()

    def test_original_video_is_streamed_with_seek_and_head_support(self):
        path = "/review-media?source=movie.mp4"
        status, headers, content = self.request(
            "GET", path, headers={"Range": "bytes=3-6"}
        )
        self.assertEqual((status, content), (206, b"3456"))
        self.assertEqual(headers["Content-Range"], "bytes 3-6/10")
        status, headers, content = self.request("HEAD", path)
        self.assertEqual((status, content, headers["Content-Length"]), (200, b"", "10"))
        self.assertEqual(
            self.request("GET", path, headers={"Range": "bytes=99-"})[0], 416
        )
        self.assertEqual(self.request("GET", "/")[2], b"local review")

    def test_unknown_paths_cannot_read_workspace_files(self):
        (self.app / "private.txt").write_text("private fixture")
        for source in ("private.txt", "../private.txt"):
            status, _, content = self.request(
                "GET", "/review-media?" + urlencode({"source": source})
            )
            self.assertEqual(status, 400)
            self.assertNotIn(b"private fixture", content)
        self.assertEqual(self.request("GET", "/branch-assets/../private.txt")[0], 404)

    def test_reviewer_has_no_authoring_routes_or_write_api(self):
        for route in (
            "/branch",
            "/branch.js",
            "/api/branch/source",
            "/api/branch/painting",
        ):
            self.assertEqual(self.request("GET", route)[0], 404)
        before = sorted(self.app.iterdir())
        for route in ("/api/branch/save", "/api/branch/preview"):
            self.assertEqual(
                self.request("POST", route, "{}", {"Content-Type": "application/json"})[
                    0
                ],
                501,
            )
        self.assertEqual(sorted(self.app.iterdir()), before)


if __name__ == "__main__":
    unittest.main()
