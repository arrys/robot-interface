from __future__ import annotations

from robot_interface.backends.mock import MockArmAdapter, MockCameraAdapter, MockGripperAdapter
from robot_interface.interface.arm import CartesianPose, CartesianPosition, Orientation
from robot_interface.robot import Robot


def test_core_commands_cover_basic_motion_and_gripper() -> None:
    robot = Robot(arm=MockArmAdapter(), gripper=MockGripperAdapter(), camera=MockCameraAdapter())

    robot.move_arm_cartesian(
        CartesianPose(position=CartesianPosition(0.4, -0.2, 0.3), orientation=Orientation(0.0, 3.14, 0.0))
    )
    pose = robot.arm_position_cartesian
    assert pose.x == 0.4

    robot.set_gripper(35)
    percent = robot.gripper_position
    assert 0.0 <= percent <= 100.0


def test_additional_debug_commands_return_typed_data() -> None:
    robot = Robot(arm=MockArmAdapter(), gripper=MockGripperAdapter(), camera=MockCameraAdapter())

    gripper_debug = robot.debug_gripper()
    camera_debug = robot.debug_camera()

    assert gripper_debug.backend == "mock_gripper"
    assert camera_debug.backend == "mock_camera"
