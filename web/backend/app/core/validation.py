"""Upload validation: file type/extension allowlist and size limits.

Mirrors the ThermalMesh engine's own input expectations (see
../../../docs/input_format.md) so a file that fails here would also fail
pipeline validation, giving the user the error immediately on upload.
"""

from __future__ import annotations

from app.core.config import settings
from app.models.enums import ProjectFileType

_ALLOWED_EXTENSIONS: dict[ProjectFileType, set[str]] = {
    ProjectFileType.FINAL_MESH: {".ply"},
    ProjectFileType.INITIAL_MESH: {".ply"},
    ProjectFileType.THERMAL_DATA: {".csv", ".txt", ".dat", ".npy"},
    ProjectFileType.THERMAL_IMAGE: {".csv", ".txt", ".dat", ".npy", ".png", ".jpg", ".jpeg"},
    ProjectFileType.CAMERA_METADATA: {".json", ".csv"},
}


class UploadValidationError(Exception):
    def __init__(self, message: str, reason: str) -> None:
        self.reason = reason
        super().__init__(message)


def validate_upload(filename: str, file_type: ProjectFileType, size: int) -> None:
    if size <= 0:
        raise UploadValidationError("Uploaded file is empty", reason="empty_file")
    if size > settings.max_upload_bytes:
        raise UploadValidationError(
            f"File exceeds the {settings.max_upload_mb} MB upload limit",
            reason="file_too_large",
        )

    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    allowed = _ALLOWED_EXTENSIONS.get(file_type)
    if allowed is not None and suffix not in allowed:
        raise UploadValidationError(
            f"'{suffix or '(no extension)'}' is not a supported file type for {file_type.value} "
            f"(expected one of {sorted(allowed)})",
            reason="unsupported_extension",
        )
    if "/" in filename or "\\" in filename or filename in {".", ".."}:
        raise UploadValidationError("Filename contains invalid path characters", reason="unsafe_filename")
