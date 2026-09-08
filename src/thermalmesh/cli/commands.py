"""Implementations backing each `thermalmesh` CLI subcommand."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from thermalmesh import __version__
from thermalmesh.geometry.quality import mesh_quality_metrics
from thermalmesh.io.camera_loader import load_cameras
from thermalmesh.io.mesh_loader import load_mesh
from thermalmesh.io.thermal_loader import load_thermal_images
from thermalmesh.io.validators import ValidationReport, validate_camera, validate_mesh_data, validate_mesh_file, validate_thermal_image
from thermalmesh.pipeline.runner import configure_logging, run_pipeline

logger = logging.getLogger("thermalmesh.cli")


def cmd_run(args: argparse.Namespace) -> int:
    configure_logging(logging.DEBUG if args.verbose else logging.INFO)
    overrides = {}
    if getattr(args, "no_occlusion", False):
        overrides.setdefault("projection", {})["occlusion_check"] = False
    if getattr(args, "no_uv", False):
        overrides.setdefault("uv", {})["enabled"] = False

    run_pipeline(
        mesh_path=args.mesh, thermal_dir=args.thermal, cameras_path=args.cameras,
        output_dir=args.output, initial_mesh_path=args.initial_mesh,
        config_path=args.config, config_overrides=overrides or None,
    )
    print(f"Pipeline completed. Outputs written to {args.output}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    configure_logging(logging.INFO)
    report = ValidationReport()
    validate_mesh_file(args.mesh, report)
    if report.is_valid:
        mesh = load_mesh(args.mesh)
        validate_mesh_data(mesh, report, label="final mesh")

    if args.cameras:
        cameras = load_cameras(args.cameras)
        for camera in cameras.values():
            validate_camera(camera, report)
        if args.thermal:
            images = load_thermal_images(args.thermal, cameras)
            for image_id, image in images.items():
                validate_thermal_image(image, cameras.get(image_id), report)

    print(report.to_text())
    return 0 if report.is_valid else 1


def cmd_inspect(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if path.suffix.lower() == ".ply":
        mesh = load_mesh(path)
        metrics = mesh_quality_metrics(mesh)
        for key, value in metrics.items():
            print(f"{key}: {value}")
    else:
        from thermalmesh.thermal.parser import parse_thermal_file

        array = parse_thermal_file(path)
        print(f"shape: {array.shape}")
        import numpy as np

        finite = array[np.isfinite(array)]
        if finite.size:
            print(f"min: {finite.min()}  max: {finite.max()}  mean: {finite.mean()}")
        else:
            print("No finite values found")
    return 0


def cmd_generate_test_data(args: argparse.Namespace) -> int:
    from thermalmesh.synthetic import generate_synthetic_dataset

    generate_synthetic_dataset(Path(args.output), num_views=args.num_views, seed=args.seed)
    print(f"Synthetic dataset written to {args.output}")
    return 0


def cmd_version(_args: argparse.Namespace) -> int:
    print(f"Innohealth ThermalMesh Pipeline {__version__}")
    return 0


def cmd_partial_run(args: argparse.Namespace, stop_after: str) -> int:
    configure_logging(logging.INFO)
    run_pipeline(
        mesh_path=args.mesh, thermal_dir=args.thermal, cameras_path=args.cameras,
        output_dir=args.output, initial_mesh_path=args.initial_mesh,
        config_path=args.config, stop_after=stop_after,
    )
    print(f"Pipeline stopped after stage '{stop_after}'. Partial outputs in {args.output}")
    return 0


def cmd_align(args: argparse.Namespace) -> int:
    return cmd_partial_run(args, "stage_align_geometry")


def cmd_estimate_poses(args: argparse.Namespace) -> int:
    return cmd_partial_run(args, "stage_refine_camera_poses")


def cmd_project(args: argparse.Namespace) -> int:
    return cmd_partial_run(args, "stage_project_and_analyze_occlusion")


def cmd_blend(args: argparse.Namespace) -> int:
    return cmd_partial_run(args, "stage_blend_thermal_views")


def cmd_export(args: argparse.Namespace) -> int:
    return cmd_run(args)
