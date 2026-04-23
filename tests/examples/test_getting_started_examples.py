from __future__ import annotations

from pathlib import Path


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_getting_started_examples_use_current_robot_facade_pattern() -> None:
    root = Path(__file__).resolve().parents[2]
    move = _read(root / "docs/examples/getting_started/003_move.py")
    pick_and_place = _read(root / "docs/examples/getting_started/004_pick_and_place.py")
    camera_usage = _read(root / "docs/examples/getting_started/005_camera_usage.py")

    for content in (move, pick_and_place, camera_usage):
        assert "Robot(robot_ip=" not in content
        assert "from robot_interface import Robot" not in content
        assert "URRobot" not in content
        assert "Robot(" in content


def test_getting_started_examples_use_robot_commands() -> None:
    root = Path(__file__).resolve().parents[2]
    move = _read(root / "docs/examples/getting_started/003_move.py")
    pick_and_place = _read(root / "docs/examples/getting_started/004_pick_and_place.py")
    camera_usage = _read(root / "docs/examples/getting_started/005_camera_usage.py")

    assert "robot.move_arm_cartesian(" in move
    assert "with Robot(" in move

    assert "robot.move_arm_joint(" in pick_and_place
    assert "robot.close_gripper(" in pick_and_place
    assert "robot.open_gripper(" in pick_and_place

    assert "robot.capture_frame(" in camera_usage
