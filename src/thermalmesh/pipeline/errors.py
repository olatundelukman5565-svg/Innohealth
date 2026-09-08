"""Custom exceptions for the ThermalMesh pipeline.

Every error explains what failed, which input caused it, a likely reason,
and a recommended action, so failures surface as actionable diagnostics
rather than opaque stack traces.
"""

from __future__ import annotations


class ThermalMeshError(Exception):
    """Base class for all ThermalMesh pipeline errors."""

    def __init__(
        self,
        message: str,
        *,
        source: str | None = None,
        reason: str | None = None,
        recommendation: str | None = None,
    ) -> None:
        self.source = source
        self.reason = reason
        self.recommendation = recommendation
        parts = [message]
        if source:
            parts.append(f"Source: {source}")
        if reason:
            parts.append(f"Likely reason: {reason}")
        if recommendation:
            parts.append(f"Recommended action: {recommendation}")
        super().__init__(" | ".join(parts))


class InvalidMeshError(ThermalMeshError):
    pass


class InvalidThermalDataError(ThermalMeshError):
    pass


class InvalidCameraDataError(ThermalMeshError):
    pass


class RegistrationError(ThermalMeshError):
    pass


class PoseEstimationError(ThermalMeshError):
    pass


class ProjectionError(ThermalMeshError):
    pass


class UVGenerationError(ThermalMeshError):
    pass


class ExportError(ThermalMeshError):
    pass


class PipelineValidationError(ThermalMeshError):
    pass
