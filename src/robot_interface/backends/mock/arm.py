"""Deterministic mock arm adapter."""

from __future__ import annotations

from typing import Sequence

from robot_interface.interface.arm import ArmAdapter, Orientation, CartesianPose, CartesianPosition
from robot_interface.interface.capabilities import ArmCapabilities


class MockArmAdapter(ArmAdapter):
    @property
    def orientation(self) -> Orientation:
        return Orientation(0,0,0)

    backend_name = "mock_arm"

    def __init__(self) -> None:
        self._joints = [0.0] * 6
        self._pose = CartesianPose(position=CartesianPosition(0,0,0), orientation=Orientation(0,0,0))

    def get_capabilities(self) -> ArmCapabilities:
        return ArmCapabilities(
            move_cartesian=True,
            raw_command=True,
            wait_for_motion_complete=False,
            kinematics_strategy="adapter",
            cartesian_execution_mode="ik_in_adapter",
        )

    def move_joint(self, joints_rad: Sequence[float], *, speed: float, acceleration: float) -> None:
        _ = speed, acceleration
        self._joints = [float(v) for v in joints_rad]

    def move_cartesian(self, pose: CartesianPose, *, speed: float, acceleration: float) -> None:
        _ = speed, acceleration
        self._pose = pose

    @property
    def joint_positions(self) -> list[float]:
        return list(self._joints)

    @property
    def cartesian_position(self) -> CartesianPosition:
        return self._pose.position

    def stop_motion(self, *, immediate: bool = True) -> None:
        _ = immediate

    def connect(self) -> None:
        return None

    def disconnect(self) -> None:
        return None

    def power_on(self) -> None:
        return None

    def brake_release(self) -> None:
        return None

    def run_raw_command(self, command: str, *, unsafe: bool = True) -> str | None:
        if not unsafe:
            raise ValueError("run_raw_command requires unsafe=True")
        return f"mock:{command}"

    def forward_kinematics(self, joints_rad: Sequence[float]) -> tuple[list[float], list[list[float]]]:
        joints = [float(v) for v in joints_rad]
        position = [sum(joints[:2]), sum(joints[2:4]), sum(joints[4:6])]
        orientation = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
        return position, orientation

    def inverse_kinematics(
        self,
        *,
        position: Sequence[float],
        orientation: Sequence[Sequence[float]],
        current_joints_rad: Sequence[float] | None = None,
    ) -> list[float]:
        if current_joints_rad is not None:
            return [float(v) for v in current_joints_rad]
        seed = [*list(position[:3]), 0.0, 0.0, 0.0]
        return [float(v) for v in seed[:6]]
