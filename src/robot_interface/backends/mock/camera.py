"""Deterministic mock camera adapter."""

from __future__ import annotations

from typing import Any, Sequence

from robot_interface.interface.camera import BoundingBox, CameraAdapter, Detection
from robot_interface.interface.capabilities import CameraCapabilities


class MockCameraAdapter(CameraAdapter):
    backend_name = "mock_camera"

    def __init__(self) -> None:
        self._model_name = "mock-model"
        self._frame = [[10, 20], [30, 40]]

    def get_capabilities(self) -> CameraCapabilities:
        return CameraCapabilities(capture_frame=True, load_model=True, run_detection=True, supports_streams=False)

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def capture_frame(self, *, stream_id: str = "default") -> tuple[Sequence[Sequence[int]] | None, int | None, int | None]:
        _ = stream_id
        return self._frame, 2, 2

    def load_model(
        self, *, model_name: str | None = None, model_version: str | None = None, parameters: dict[str, Any] | None = None
    ) -> bool:
        _ = model_version, parameters
        self._model_name = model_name or "mock-model"
        return True

    def run_detection(self, *, frame: Sequence[Sequence[int]] | None = None, threshold: float = 0.5) -> list[Detection]:
        _ = frame, threshold
        detection = Detection(
            label=self._model_name,
            confidence=0.95,
            bounding_box=BoundingBox(x1=0.1, y1=0.2, x2=0.8, y2=0.9),
        )
        return [detection]
