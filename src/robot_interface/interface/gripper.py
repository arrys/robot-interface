"""Gripper adapter interface (direct method API)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from robot_interface.interface.capabilities import GripperCapabilities


class GripperAdapter(ABC):
    backend_name: str

    @abstractmethod
    def get_capabilities(self) -> GripperCapabilities: ...

    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def open(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def set_position(self, position: int) -> None: ...

    @property
    @abstractmethod
    def position(self) -> int: ...
