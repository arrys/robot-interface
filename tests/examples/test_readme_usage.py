from __future__ import annotations

from pathlib import Path


def test_readme_documents_example_commands_and_robot_ip_precedence() -> None:
    root = Path(__file__).resolve().parents[2]
    readme = (root / "README.md").read_text(encoding="utf-8")

    assert "uv run python docs/examples/getting_started/003_move.py" in readme
    assert "docs/examples/getting_started/004_pick_and_place.py" in readme
    assert "docs/examples/getting_started/005_camera_usage.py" in readme
    assert 'os.getenv("ROBOT_IP", "127.0.0.1")' in readme or "default to `127.0.0.1`" in readme
    assert "ROBOT_IP" in readme
