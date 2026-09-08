"""Input validation.

Runs before any processing and produces a structured, human-readable
report. Nothing downstream should have to guess whether inputs are sane.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from thermalmesh.models.camera import Camera
from thermalmesh.models.mesh import MeshData
from thermalmesh.models.thermal import ThermalImage
from thermalmesh.pipeline.errors import PipelineValidationError


@dataclass
class ValidationIssue:
    severity: str  # "error" | "warning"
    message: str


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.issues.append(ValidationIssue("error", message))

    def warning(self, message: str) -> None:
        self.issues.append(ValidationIssue("warning", message))

    @property
    def errors(self) -> list[str]:
        return [i.message for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[str]:
        return [i.message for i in self.issues if i.severity == "warning"]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def raise_if_invalid(self) -> None:
        if not self.is_valid:
            raise PipelineValidationError(
                "Input validation failed with " + f"{len(self.errors)} error(s)",
                reason="; ".join(self.errors),
                recommendation="Fix the reported inputs and re-run `thermalmesh validate`",
            )

    def to_text(self) -> str:
        lines = ["ThermalMesh Input Validation Report", "=" * 40]
        if not self.issues:
            lines.append("No issues found.")
        for issue in self.issues:
            lines.append(f"[{issue.severity.upper()}] {issue.message}")
        return "\n".join(lines)


def validate_mesh_file(path: str | Path, report: ValidationReport) -> None:
    path = Path(path)
    if not path.exists():
        report.error(f"Mesh file does not exist: {path}")
        return
    if not path.is_file():
        report.error(f"Mesh path is not a file: {path}")
        return
    if path.suffix.lower() != ".ply":
        report.warning(f"Mesh file {path} does not use the .ply extension")


def validate_mesh_data(mesh: MeshData, report: ValidationReport, label: str = "mesh") -> None:
    if mesh.num_vertices == 0:
        report.error(f"{label} has zero vertices")
        return
    if not np.all(np.isfinite(mesh.vertices)):
        report.error(f"{label} contains non-finite vertex coordinates")
    if mesh.faces.size:
        if mesh.faces.min() < 0 or mesh.faces.max() >= mesh.num_vertices:
            report.error(f"{label} faces reference out-of-range vertex indices")
    else:
        report.warning(f"{label} has no faces (point-cloud-like mesh)")


def validate_thermal_image(image: ThermalImage, camera: Camera | None, report: ValidationReport) -> None:
    if image.temperature_array.size == 0:
        report.error(f"Thermal image {image.image_id} is empty")
        return
    if not np.issubdtype(image.temperature_array.dtype, np.floating):
        report.error(f"Thermal image {image.image_id} is not numeric")
    if image.valid_fraction() == 0.0:
        report.error(f"Thermal image {image.image_id} has no valid pixels")
    elif image.valid_fraction() < 0.5:
        report.warning(f"Thermal image {image.image_id} has only {image.valid_fraction():.1%} valid pixels")
    if camera is not None:
        if image.height != camera.image_height or image.width != camera.image_width:
            report.error(
                f"Thermal image {image.image_id} has shape ({image.height}, {image.width}) but camera "
                f"metadata specifies an image size of ({camera.image_height}, {camera.image_width})"
            )


def validate_camera(camera: Camera, report: ValidationReport) -> None:
    if camera.image_width <= 0 or camera.image_height <= 0:
        report.error(f"Camera {camera.camera_id} has invalid image dimensions")
    if not np.all(np.isfinite(camera.intrinsic_matrix)):
        report.error(f"Camera {camera.camera_id} has non-finite intrinsics")
    if camera.fx <= 0 or camera.fy <= 0:
        report.error(f"Camera {camera.camera_id} has non-positive focal length")
    if camera.intrinsics_source == "estimated_fallback":
        report.warning(f"Camera {camera.camera_id} intrinsics were estimated (not provided)")
    if camera.pose_source == "unknown":
        report.warning(f"Camera {camera.camera_id} has no known position; pose must be fully estimated")
    elif camera.pose_source == "position_only":
        report.warning(f"Camera {camera.camera_id} has a known position but no orientation; will initialize via look-at")
