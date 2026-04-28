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

class ArmAdapter(ABC):
    backend_name: str

    @abstractmethod
    def get_capabilities(self) -> ArmCapabilities: ...

    @abstractmethod
    def move_joint(self, joints_rad: Sequence[float], *, speed: float, acceleration: float) -> None: ...

    @abstractmethod
    def move_cartesian(self, pose: CartesianPose, *, speed: float, acceleration: float) -> None: ...

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
