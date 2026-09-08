"""NumPy (.npy) numerical exports."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def export_array(array: np.ndarray, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, array)
    return output_path
