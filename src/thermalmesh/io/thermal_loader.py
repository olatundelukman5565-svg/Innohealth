"""Adapter that discovers and loads thermal data files for each camera.

This is deliberately a thin layer over :mod:`thermalmesh.thermal.parser`: if
Innohealth's real thermal export format differs from generic CSV/whitespace
text, add a new adapter function here rather than rewriting the pipeline
(Rule: adapter-based input system).
"""

from __future__ import annotations

from pathlib import Path

from thermalmesh.models.camera import Camera
from thermalmesh.models.thermal import ThermalImage
from thermalmesh.pipeline.errors import InvalidThermalDataError
from thermalmesh.thermal.parser import SUPPORTED_EXTENSIONS, parse_thermal_file


def load_thermal_images(
    thermal_dir: str | Path,
    cameras: dict[str, Camera],
    *,
    unit: str = "unknown",
    delimiter: str | None = None,
    has_header: bool = False,
) -> dict[str, ThermalImage]:
    """Load one :class:`ThermalImage` per camera.

    Resolution order per camera: explicit ``metadata['thermal_file']`` set
    on the :class:`Camera`, else a file in ``thermal_dir`` named
    ``<camera_id>.<ext>`` for any supported extension.
    """
    thermal_dir = Path(thermal_dir)
    if not thermal_dir.exists():
        raise InvalidThermalDataError(
            f"Thermal data directory not found: {thermal_dir}",
            source=str(thermal_dir), reason="Directory does not exist",
            recommendation="Verify --thermal path",
        )

    images: dict[str, ThermalImage] = {}
    for camera_id, camera in cameras.items():
        file_path = _resolve_thermal_file(thermal_dir, camera_id, camera.metadata.get("thermal_file"))
        if file_path is None:
            raise InvalidThermalDataError(
                f"No thermal data file found for camera '{camera_id}' in {thermal_dir}",
                source=str(thermal_dir),
                reason=f"Expected a file named '{camera_id}.<ext>' or a 'thermal_file' entry in cameras.json",
                recommendation="Ensure every camera has a corresponding thermal data file",
            )
        array = parse_thermal_file(file_path, delimiter=delimiter, has_header=has_header)
        if array.shape != (camera.image_height, camera.image_width):
            raise InvalidThermalDataError(
                f"Thermal file {file_path} has shape {array.shape} but camera "
                f"'{camera_id}' specifies image size ({camera.image_height}, {camera.image_width})",
                source=str(file_path),
                reason="Thermal array dimensions must match the camera's image_height/image_width",
                recommendation="Correct the camera metadata or the thermal export dimensions",
            )
        images[camera_id] = ThermalImage(
            image_id=camera_id,
            temperature_array=array,
            unit=unit,
            source_file=str(file_path),
        )
    return images


def _resolve_thermal_file(thermal_dir: Path, camera_id: str, explicit: str | None) -> Path | None:
    if explicit:
        candidate = thermal_dir / explicit
        if candidate.exists():
            return candidate
        candidate = Path(explicit)
        if candidate.exists():
            return candidate
    for ext in SUPPORTED_EXTENSIONS:
        candidate = thermal_dir / f"{camera_id}{ext}"
        if candidate.exists():
            return candidate
    return None
