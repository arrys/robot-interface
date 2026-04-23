"""Component-scoped protocol capability models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

KinematicsStrategy = Literal["adapter", "upstream"]
CartesianExecutionMode = Literal["native", "ik_in_adapter", "unsupported"]


@dataclass(frozen=True)
class ArmCapabilities:
    connect: bool = True
    disconnect: bool = True
    power_on: bool = True
    brake_release: bool = True
    move_joint: bool = True
    get_state: bool = True

    move_cartesian: bool = False
    raw_command: bool = False
    wait_for_motion_complete: bool = False

    # Kinematics policy
    kinematics_strategy: KinematicsStrategy = "adapter"
    cartesian_execution_mode: CartesianExecutionMode = "unsupported"


@dataclass(frozen=True)
class GripperCapabilities:
    open: bool = True
    close: bool = True
    move: bool = True
    get_position: bool = True
    raw_command: bool = False


@dataclass(frozen=True)
class CameraCapabilities:
    capture_frame: bool = True
    load_model: bool = True
    run_detection: bool = True
    supports_streams: bool = False
