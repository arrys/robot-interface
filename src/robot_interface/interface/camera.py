"""Camera adapter interface (direct method API)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Sequence

from robot_interface.interface.capabilities import CameraCapabilities


@dataclass(frozen=True)
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    bounding_box: BoundingBox


class CameraAdapter(ABC):
    backend_name: str

    @abstractmethod
    def get_capabilities(self) -> CameraCapabilities: ...

    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def capture_frame(self, *, stream_id: str = "default") -> tuple[Sequence[Sequence[int]] | None, int | None, int | None]: ...

    @abstractmethod
    def load_model(
        self, *, model_name: str | None = None, model_version: str | None = None, parameters: dict[str, Any] | None = None
    ) -> bool: ...

    @abstractmethod
    def run_detection(self, *, frame: Sequence[Sequence[int]] | None = None, threshold: float = 0.5) -> list[Detection]: ...
