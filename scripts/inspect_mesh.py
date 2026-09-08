#!/usr/bin/env python3
"""Standalone mesh inspection helper (equivalent to `thermalmesh inspect <file>.ply`)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thermalmesh.geometry.quality import mesh_quality_metrics  # noqa: E402
from thermalmesh.io.mesh_loader import load_mesh  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a PLY mesh")
    parser.add_argument("path")
    args = parser.parse_args()

    mesh = load_mesh(args.path)
    for key, value in mesh_quality_metrics(mesh).items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
