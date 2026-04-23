from __future__ import annotations

from pathlib import Path


def test_api_reference_uses_current_facade_pattern() -> None:
    root = Path(__file__).resolve().parents[2]
    content = (root / "README.md").read_text(encoding="utf-8")

    assert "Robot(robot_ip=" not in content
    assert "from robot_interface import Robot" not in content
    assert "robot = Robot(" in content
    assert "UR10ArmAdapter" not in content
    assert "UR10GripperAdapter" not in content
    assert "robot.additional.move_arm_joint(" in content
