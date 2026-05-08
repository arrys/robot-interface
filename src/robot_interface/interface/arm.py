"""Arm adapter interface (direct method API)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import math
from typing import Sequence, Tuple

from robot_interface.interface.capabilities import ArmCapabilities

@dataclass
class CartesianPosition:
    x: float # mm
    y: float
    z: float

@dataclass
class Orientation:
    rx: float #rad
    ry: float
    rz: float

    @classmethod
    def from_radians(cls, rx: float, ry: float, rz: float) -> "Orientation":
        return cls(rx=float(rx), ry=float(ry), rz=float(rz))

    @classmethod
    def from_degrees(cls, rx: float, ry: float, rz: float) -> "Orientation":
        return cls(
            rx=math.radians(float(rx)),
            ry=math.radians(float(ry)),
            rz=math.radians(float(rz)),
        )

@dataclass
class CartesianPose:
    position: CartesianPosition
    orientation: Orientation

    @staticmethod
    def lerp(a: "CartesianPose", b: "CartesianPose", t: float) -> "CartesianPose":
        return CartesianPose(
            position=CartesianPosition(
                x=a.position.x + (b.position.x - a.position.x) * t,
                y=a.position.y + (b.position.y - a.position.y) * t,
                z=a.position.z + (b.position.z - a.position.z) * t,
            ),
            orientation=Orientation(
                rx=a.orientation.rx + (b.orientation.rx - a.orientation.rx) * t,
                ry=a.orientation.ry + (b.orientation.ry - a.orientation.ry) * t,
                rz=a.orientation.rz + (b.orientation.rz - a.orientation.rz) * t,
            ),
        )

    @staticmethod
    def quadratic_through_three(
        start: "CartesianPose",
        middle: "CartesianPose",
        end: "CartesianPose",
        t: float,
    ) -> "CartesianPose":
        # Quadratic interpolation passing exactly through:
        # t=0.0 -> start, t=0.5 -> middle, t=1.0 -> end
        l0 = 2.0 * (t - 0.5) * (t - 1.0)
        l1 = -4.0 * t * (t - 1.0)
        l2 = 2.0 * t * (t - 0.5)
        return CartesianPose(
            position=CartesianPosition(
                x=(start.position.x * l0) + (middle.position.x * l1) + (end.position.x * l2),
                y=(start.position.y * l0) + (middle.position.y * l1) + (end.position.y * l2),
                z=(start.position.z * l0) + (middle.position.z * l1) + (end.position.z * l2),
            ),
            orientation=Orientation(
                rx=(start.orientation.rx * l0) + (middle.orientation.rx * l1) + (end.orientation.rx * l2),
                ry=(start.orientation.ry * l0) + (middle.orientation.ry * l1) + (end.orientation.ry * l2),
                rz=(start.orientation.rz * l0) + (middle.orientation.rz * l1) + (end.orientation.rz * l2),
            ),
        )

class ArmAdapter(ABC):
    backend_name: str

    @abstractmethod
    def get_capabilities(self) -> ArmCapabilities: ...

    @abstractmethod
    def move_joint(self, joints_rad: Sequence[float], *, speed: float, acceleration: float) -> None: ...

    @abstractmethod
    def move_cartesian(self, pose: CartesianPose, *, speed: float, acceleration: float) -> None: ...

    def interpolate_cartesian_path(self, path: Sequence[CartesianPose], *, segments: int) -> list[CartesianPose]:
        if len(path) < 2:
            raise ValueError("path must contain at least 2 poses")
        if segments < 1:
            raise ValueError("segments must be >= 1")

        if len(path) == 2:
            start, end = path
            return [CartesianPose.lerp(start, end, i / segments) for i in range(segments + 1)]

        if len(path) == 3:
            start, mid, end = path
            return [CartesianPose.quadratic_through_three(start, mid, end, i / segments) for i in range(segments + 1)]

        raise ValueError("path must contain exactly 2 poses (line) or 3 poses (curve through all points)")


    @property
    @abstractmethod
    def joint_positions(self) -> list[float]: ...

    @property
    @abstractmethod
    def cartesian_position(self) -> CartesianPosition: ...

    @property
    @abstractmethod
    def orientation(self) -> Orientation: ...

    @abstractmethod
    def stop_motion(self, *, immediate: bool = True) -> None: ...

    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def power_on(self) -> None: ...

    @abstractmethod
    def brake_release(self) -> None: ...

    @abstractmethod
    def run_raw_command(self, command: str, *, unsafe: bool = True) -> str | None: ...

    @abstractmethod
    def forward_kinematics(self, joints_rad: Sequence[float]) -> Tuple[CartesianPosition, Orientation]: ...

    @abstractmethod
    def inverse_kinematics(
        self,
        *,
        position: Sequence[float],
        orientation: Sequence[Sequence[float]],
        current_joints_rad: Sequence[float] | None = None,
    ) -> list[float]: ...
