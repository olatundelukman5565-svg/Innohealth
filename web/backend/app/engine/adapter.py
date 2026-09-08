"""The processing-engine adapter interface.

The web platform never calls the ThermalMesh algorithms directly -- it goes
through this interface, so a different engine implementation (a remote
worker, a different version of the pipeline) can be substituted without
touching any router or frontend code (spec section 74).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class EngineInputPaths:
    mesh_path: str
    thermal_dir: str
    cameras_path: str
    initial_mesh_path: str | None = None


class ThermalMeshEngineAdapter(ABC):
    @abstractmethod
    def validate_input(self, inputs: EngineInputPaths) -> list[str]:
        """Return a list of human-readable validation error messages (empty = valid)."""

    @abstractmethod
    def start_processing(self, job_id: str, project_id: str, inputs: EngineInputPaths, output_dir: str) -> None:
        """Begin processing (may run asynchronously in a background thread)."""

    @abstractmethod
    def get_status(self, job_id: str) -> dict:
        ...

    @abstractmethod
    def cancel_processing(self, job_id: str) -> bool:
        ...

    @abstractmethod
    def get_result(self, job_id: str) -> dict | None:
        ...

    @abstractmethod
    def get_quality_report(self, job_id: str) -> dict | None:
        ...
