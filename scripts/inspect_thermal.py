#!/usr/bin/env python3
"""Standalone thermal-file inspection helper (equivalent to `thermalmesh inspect <file>.csv`)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

from thermalmesh.thermal.parser import parse_thermal_file  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a raw thermal data file")
    parser.add_argument("path")
    args = parser.parse_args()

    array = parse_thermal_file(args.path)
    finite = array[np.isfinite(array)]
    print(f"shape (height, width): {array.shape}")
    print(f"valid pixels: {finite.size} / {array.size}")
    if finite.size:
        print(f"min: {finite.min():.3f}  max: {finite.max():.3f}  mean: {finite.mean():.3f}  std: {finite.std():.3f}")


if __name__ == "__main__":
    main()
