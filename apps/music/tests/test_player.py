import json
import threading
from http.server import ThreadingHTTPServer

import httpx

from player.server import make_handler


def test_feedback_persists_mix_context_and_server_exposes_only_declared_files(tmp_path):
    manifest = {
        "duration": 30,
        "tracks": [{"id": "chords"}],
        "palettes": [{"id": "v002", "tracks": {}}],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    (tmp_path / "private.txt").write_text("not a player asset")
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with httpx.Client(base_url=base) as client:
            payload = {
                "note": "This tone is the one",
                "palette": "v002",
                "time": 12.25,
                "muted": [],
                "solo": ["chords"],
            }
            r = client.post("/api/feedback", json=payload)
            assert r.status_code == 201
            saved = client.get("/api/feedback").json()
            assert saved[0]["solo"] == ["chords"] and saved[0]["time"] == 12.25
            assert saved[0]["note"] == payload["note"]
            assert client.get("/private.txt").status_code == 404
            assert client.get("/../private.txt").status_code == 404
            assert (
                client.post("/api/feedback", json=payload | {"time": 31}).status_code
                == 400
            )
            assert (
                client.post(
                    "/api/feedback", json=payload | {"solo": ["unknown"]}
                ).status_code
                == 400
            )
            assert (
                client.post(
                    "/api/feedback",
                    json=payload,
                    headers={"Origin": "https://example.com"},
                ).status_code
                == 403
            )
            assert len(client.get("/api/feedback").json()) == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
