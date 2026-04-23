"""Composable robot facade with direct synchronous commands."""

from __future__ import annotations

import math
from dataclasses import dataclass

from robot_interface.backends import MockCameraAdapter, MockGripperAdapter, MockArmAdapter
from robot_interface.interface.arm import ArmAdapter, CartesianPosition, Orientation, CartesianPose
from robot_interface.interface.camera import CameraAdapter, Detection
from robot_interface.interface.gripper import GripperAdapter


@dataclass(frozen=True)
class ArmDebugInfo:
    backend: str
    joint_positions: list[float]
    cartesian_position: list[float] | None


@dataclass(frozen=True)
class GripperDebugInfo:
    backend: str
    position_raw: int
    position_percent: float


@dataclass(frozen=True)
class CameraDebugInfo:
    backend: str
    width: int | None
    height: int | None


class Robot:
    def __init__(self, arm: ArmAdapter = MockArmAdapter(), gripper: GripperAdapter = MockGripperAdapter(), camera: CameraAdapter = MockCameraAdapter()) -> None:
        self.arm = arm
        self.gripper = gripper
        self.camera = camera
        self._entered = False

    def __enter__(self) -> Robot:
        self.arm.connect()
        self.gripper.connect()
        self.camera.connect()
        self._entered = True
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.camera.disconnect()
        self.gripper.disconnect()
        self.arm.disconnect()
        self._entered = False


    def move_arm_cartesian(self, pose: CartesianPose, *, speed: float = 0.1, acceleration: float = 0.3) -> None:
        self.arm.move_cartesian(pose, speed=speed, acceleration=acceleration)

    @property
    def arm_position_cartesian(self) -> CartesianPosition:
        return self.arm.cartesian_position

    @property
    def arm_orientation(self) -> Orientation:
        return self.arm.orientation


    def set_gripper(self, percent: float) -> None:
        gripper = self.gripper
        clamped = max(0.0, min(100.0, float(percent)))
        gripper.set_position(int(round((clamped / 100.0) * 255.0)))

    @property
    def gripper_position(self) -> float:
        gripper = self.gripper
        return float(gripper.position) / 255.0 * 100.0

    def power_on(self) -> None:
        self.arm.power_on()

    def brake_release(self) -> None:
        self.arm.brake_release()

    def move_arm_joint(self, joints_rad: list[float], *, speed: float = 0.3, acceleration: float = 0.6) -> None:
        self.arm.move_joint(joints_rad, speed=speed, acceleration=acceleration)

    @property
    def arm_joint_positions_radians(self) -> list[float]:
        return self.arm.joint_positions

    @property
    def arm_joint_positions_degrees(self) -> list[float]:
        return [math.degrees(value) for value in self.arm_joint_positions_radians]

    def stop_motion(self, *, immediate: bool = True) -> None:
        self.arm.stop_motion(immediate=immediate)

    def open_gripper(self) -> None:
        self.gripper.open()

    def close_gripper(self) -> None:
        self.gripper.close()

    def capture_frame(self, *, stream_id: str = "default"):
        return self.camera.capture_frame(stream_id=stream_id)

    def load_model(self, *, model_name: str, model_version: str | None = None) -> bool:
        return self.camera.load_model(model_name=model_name, model_version=model_version)

    def run_detection(self, *, threshold: float = 0.5) -> list[Detection]:
        return self.camera.run_detection(threshold=threshold)

    def forward_kinematics(self, joints_rad: list[float]) -> tuple[list[float], list[list[float]]]:
        return self.arm.forward_kinematics(joints_rad)

    def inverse_kinematics(
        self,
        *,
        position: list[float],
        orientation: list[list[float]],
        current_joints_rad: list[float] | None = None,
    ) -> list[float]:
        return self.arm.inverse_kinematics(position=position, orientation=orientation, current_joints_rad=current_joints_rad)

    def debug_gripper(self) -> GripperDebugInfo:
        gripper = self.gripper
        raw = gripper.position
        return GripperDebugInfo(backend=gripper.backend_name, position_raw=raw, position_percent=float(raw) / 255.0 * 100.0)

    def debug_camera(self) -> CameraDebugInfo:
        camera = self.camera
        _, width, height = camera.capture_frame()
        return CameraDebugInfo(backend=camera.backend_name, width=width, height=height)

    def debug_arm_command(self, command: str, *, unsafe: bool = True) -> str | None:
        return self.arm.run_raw_command(command, unsafe=unsafe)
