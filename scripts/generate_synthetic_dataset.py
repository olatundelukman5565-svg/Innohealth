#!/usr/bin/env python3
"""CLI wrapper around :func:`thermalmesh.synthetic.generate_synthetic_dataset`.

See ``thermalmesh generate-test-data`` for the equivalent packaged command.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thermalmesh.synthetic import generate_synthetic_dataset  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a synthetic ThermalMesh validation dataset")
    parser.add_argument("--output", required=True)
    parser.add_argument("--num-views", type=int, default=12)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    generate_synthetic_dataset(args.output, num_views=args.num_views, seed=args.seed)
    print(f"Synthetic dataset written to {args.output}")


if __name__ == "__main__":
    main()
