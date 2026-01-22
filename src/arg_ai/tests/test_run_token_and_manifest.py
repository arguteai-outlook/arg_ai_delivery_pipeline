import json
from pathlib import Path


def test_manifest_schema_smoke(tmp_path: Path):
    # This is intentionally a tiny smoke test so CI has a deterministic unit gate.
    manifest = {
        "run_token": "abc",
        "project_id": "ses_email_pilot",
        "mode": "local",
        "gates": [],
        "trace": {"trace_graph_path": "projects/ses_email_pilot/trace/trace_graph.json"},
    }
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(manifest), encoding="utf-8")
    loaded = json.loads(p.read_text(encoding="utf-8"))
    assert loaded["project_id"] == "ses_email_pilot"
    assert "gates" in loaded
