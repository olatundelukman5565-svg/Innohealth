"""Parsing of raw thermal data files into numerical temperature arrays.

Raw numerical temperature values are the authoritative data (Rule 1). This
module never converts temperature into color; it only produces
floating-point arrays plus a validity mask.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from thermalmesh.pipeline.errors import InvalidThermalDataError

SUPPORTED_EXTENSIONS = {".csv", ".txt", ".dat", ".npy"}


def parse_thermal_file(
    path: str | Path,
    *,
    delimiter: str | None = None,
    has_header: bool = False,
    invalid_markers: tuple[str, ...] = ("nan", "NaN", "NAN", "-", "N/A", ""),
) -> np.ndarray:
    """Parse a thermal data file into a 2D (height, width) float64 array.

    Supports CSV, whitespace-delimited text, and ``.npy`` arrays. The
    delimiter is auto-detected from the file extension unless given
    explicitly. Values matching ``invalid_markers`` become NaN rather than
    being dropped, so array shape (== image geometry) is preserved.
    """
    path = Path(path)
    if not path.exists():
        raise InvalidThermalDataError(
            f"Thermal data file not found: {path}",
            source=str(path),
            reason="File does not exist at the given path",
            recommendation="Verify the --thermal directory/file path",
        )

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise InvalidThermalDataError(
            f"Unsupported thermal file extension '{suffix}' for {path}",
            source=str(path),
            reason=f"Only {sorted(SUPPORTED_EXTENSIONS)} are supported",
            recommendation="Convert the file to CSV/space-delimited text/.npy or add a new adapter",
        )

    if suffix == ".npy":
        array = np.load(path)
        return _finalize(array, path)

    if delimiter is None:
        delimiter = "," if suffix == ".csv" else None  # None => whitespace for np.genfromtxt

    skip_header = 1 if has_header else 0
    try:
        raw_text = path.read_text()
    except UnicodeDecodeError as exc:
        raise InvalidThermalDataError(
            f"Could not read thermal file {path} as text",
            source=str(path),
            reason=str(exc),
            recommendation="Ensure the file is a plain-text CSV/whitespace-delimited numeric file",
        ) from exc

    lines = [line for line in raw_text.splitlines() if line.strip() != ""]
    lines = lines[skip_header:]
    if not lines:
        raise InvalidThermalDataError(
            f"Thermal file {path} contains no data rows",
            source=str(path),
            reason="File is empty after removing the header/blank lines",
            recommendation="Check the source export produced non-empty data",
        )

    rows: list[list[float]] = []
    for line_no, line in enumerate(lines):
        tokens = line.split(delimiter) if delimiter else line.split()
        tokens = [t.strip() for t in tokens if t.strip() != ""] if delimiter is None else [t.strip() for t in tokens]
        row: list[float] = []
        for token in tokens:
            if token in invalid_markers:
                row.append(np.nan)
                continue
            try:
                row.append(float(token))
            except ValueError as exc:
                raise InvalidThermalDataError(
                    f"Non-numeric value '{token}' in {path} at row {line_no}",
                    source=str(path),
                    reason="Thermal data must be purely numeric (or a recognized invalid marker)",
                    recommendation="Check invalid_markers configuration or clean the source export",
                ) from exc
        rows.append(row)

    widths = {len(r) for r in rows}
    if len(widths) != 1:
        raise InvalidThermalDataError(
            f"Thermal file {path} has inconsistent row widths: {sorted(widths)}",
            source=str(path),
            reason="Every row must have the same number of columns (image width)",
            recommendation="Check for missing/extra delimiters in the source export",
        )

    array = np.array(rows, dtype=np.float64)
    return _finalize(array, path)


def _finalize(array: np.ndarray, path: Path) -> np.ndarray:
    array = np.asarray(array, dtype=np.float64)
    if array.ndim != 2:
        raise InvalidThermalDataError(
            f"Thermal array from {path} is not 2D (got shape {array.shape})",
            source=str(path),
            reason="Expected a single-channel (height, width) numeric array",
            recommendation="Export raw per-pixel temperature as a 2D array, not multi-channel imagery",
        )
    return array
