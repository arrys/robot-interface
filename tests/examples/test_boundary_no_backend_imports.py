from __future__ import annotations

from pathlib import Path


def test_public_examples_do_not_import_backends_directly() -> None:
    root = Path(__file__).resolve().parents[2]
    example_files = sorted((root / "docs/examples/getting_started").glob("*.py"))
    assert example_files, "expected example files"
    allowed_names = {
        "000_connect_rtde_arm.py",
        "001_connect_urscript_arm.py",
        "002_connect_ur_gripper.py",
        "003_move.py",
        "004_pick_and_place.py",
        "005_camera_usage.py",
        "006_gripper_socket.py",
    }
    assert {path.name for path in example_files} == allowed_names
    for path in example_files:
        content = path.read_text(encoding="utf-8")
        if path.name == "006_gripper_socket.py":
            continue
        assert "robot_interface.backends.ur10" in content or "create_ur10_runtime" in content


def test_readme_does_not_show_backend_direct_usage_snippets() -> None:
    root = Path(__file__).resolve().parents[2]
    readme = (root / "README.md").read_text(encoding="utf-8")
    assert "from robot_interface.backends." not in readme
    assert "UR10ArmAdapter(" not in readme
    assert "UR10GripperAdapter(" not in readme
