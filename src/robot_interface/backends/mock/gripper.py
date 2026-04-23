"""Deterministic mock gripper adapter."""

from __future__ import annotations

from robot_interface.interface.capabilities import GripperCapabilities
from robot_interface.interface.gripper import GripperAdapter


class MockGripperAdapter(GripperAdapter):
    def disconnect(self) -> None:
        pass

    def connect(self) -> None:
        pass

    backend_name = "mock_gripper"

    def __init__(self) -> None:
        self._position = 0

    def get_capabilities(self) -> GripperCapabilities:
        return GripperCapabilities(open=True, close=True, move=True, get_position=True, raw_command=False)

    def open(self, *, wait: bool = True, timeout_s: float = 10.0) -> None:
        _ = wait, timeout_s
        self._position = 0

    def close(self, *, wait: bool = True, timeout_s: float = 10.0) -> None:
        _ = wait, timeout_s
        self._position = 255

    def set_position(self, position: int, *, wait: bool = True, timeout_s: float = 10.0) -> None:
        _ = wait, timeout_s
        self._position = int(position)

    @property
    def position(self) -> int:
        return self._position
