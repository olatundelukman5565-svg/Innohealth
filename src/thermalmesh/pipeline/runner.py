"""Convenience entry point: build a context from paths/config and run the pipeline.

This is the single function both the CLI and any external Python caller
should use (Rule 10 - the pipeline must be usable without the CLI).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

import yaml

from thermalmesh.models.results import PipelineResult
from thermalmesh.pipeline.context import PipelineContext
from thermalmesh.pipeline.pipeline import ThermalMeshPipeline

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "default.yaml"


def load_config(config_path: str | Path | None = None) -> dict:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        return {}
    with path.open() as f:
        return yaml.safe_load(f) or {}


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def run_pipeline(
    mesh_path: str | Path,
    thermal_dir: str | Path,
    cameras_path: str | Path,
    output_dir: str | Path,
    *,
    initial_mesh_path: str | Path | None = None,
    config_path: str | Path | None = None,
    config_overrides: dict | None = None,
    stop_after: str | None = None,
    on_stage_start: Callable[[str, int, int], None] | None = None,
    on_stage_complete: Callable[[str, int, int], None] | None = None,
) -> PipelineResult:
    config = load_config(config_path)
    if config_overrides:
        config = _deep_merge(config, config_overrides)

    context = PipelineContext(
        config=config,
        mesh_path=Path(mesh_path),
        initial_mesh_path=Path(initial_mesh_path) if initial_mesh_path else None,
        thermal_dir=Path(thermal_dir),
        cameras_path=Path(cameras_path),
        output_dir=Path(output_dir),
    )
    pipeline = ThermalMeshPipeline(context)
    return pipeline.run(stop_after=stop_after, on_stage_start=on_stage_start, on_stage_complete=on_stage_complete)


def _deep_merge(base: dict, overrides: dict) -> dict:
    merged = dict(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
