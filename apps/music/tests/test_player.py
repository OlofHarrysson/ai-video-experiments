import json
import threading
from http.server import ThreadingHTTPServer

import httpx

from player.server import make_handler


def test_shared_control_reports_actual_acknowledged_browser_state(tmp_path):
    manifest = {"duration": 30, "tracks": [{"id": "chords", "url": "/audio.wav"}]}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    (tmp_path / "audio.wav").write_bytes(b"audio")
    (tmp_path / "private.txt").write_text("not a player asset")
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{server.server_port}") as client:
            assert not client.get("/api/state").json()["connected"]
            assert (
                client.post("/api/control", json={"action": "pause"}).status_code == 409
            )
            session = client.post("/api/connect", json={}).json()["session"]
            state = {"playing": False, "time": 12.25, "only": None}
            sync = {"session": session, "lastCommand": 0, "state": state}
            assert client.post("/api/sync", json=sync).json()["commands"] == []
            result = client.post(
                "/api/control", json={"action": "only", "track": "chords"}
            )
            assert result.status_code == 202
            # Queued control is not falsely reported as applied.
            assert client.get("/api/state").json()["state"]["only"] is None
            commands = client.post("/api/sync", json=sync).json()["commands"]
            assert commands == [{"action": "only", "track": "chords", "sequence": 1}]
            sync.update(lastCommand=1, state=state | {"only": "chords"})
            assert client.post("/api/sync", json=sync).json()["commands"] == []
            actual = client.get("/api/state").json()
            assert actual["connected"] and actual["last_applied_command"] == 1
            assert actual["state"]["only"] == "chords"
            assert client.get("/audio.wav").content == b"audio"
            assert client.get("/private.txt").status_code == 404
            assert client.get("/../private.txt").status_code == 404
            for bad in [
                {"action": "seek", "value": 31},
                {"action": "only", "track": "missing"},
                {"action": "volume", "value": "NaN"},
                {"action": "enabled", "track": "chords", "value": "yes"},
            ]:
                assert client.post("/api/control", json=bad).status_code == 400
            assert (
                client.post(
                    "/api/control",
                    json={"action": "pause"},
                    headers={"Origin": "https://example.com"},
                ).status_code
                == 403
            )
            # The newest tab owns shared controls. Stale tabs cannot acknowledge them.
            client.post("/api/connect", json={})
            assert client.post("/api/sync", json=sync).status_code == 409
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
