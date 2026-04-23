from __future__ import annotations

from pathlib import Path


def test_examples_directory_contains_only_getting_started_flow() -> None:
    root = Path(__file__).resolve().parents[2]
    examples_root = root / "docs/examples"
    assert examples_root.exists()
    assert {path.name for path in examples_root.iterdir() if not path.name.startswith("__")} == {"getting_started"}

    getting_started = examples_root / "getting_started"
    expected = {
        "000_connect_rtde_arm.py",
        "001_connect_urscript_arm.py",
        "002_connect_ur_gripper.py",
        "003_move.py",
        "004_pick_and_place.py",
        "005_camera_usage.py",
        "006_gripper_socket.py",
    }
    assert {path.name for path in getting_started.iterdir() if path.suffix == ".py"} == expected
    assert not (root / "examples").exists()
