"""`thermalmesh` command-line entry point."""

from __future__ import annotations

import argparse
import sys

from thermalmesh.cli import commands


def _add_pipeline_args(parser: argparse.ArgumentParser, *, require_output: bool = True) -> None:
    parser.add_argument("--mesh", required=True, help="Path to the final reconstructed PLY mesh")
    parser.add_argument("--initial-mesh", default=None, help="Optional path to the initial acquisition PLY/point cloud")
    parser.add_argument("--thermal", required=True, help="Path to the directory containing thermal data files")
    parser.add_argument("--cameras", required=True, help="Path to the camera metadata JSON file")
    parser.add_argument("--config", default=None, help="Path to a YAML configuration file")
    parser.add_argument("--output", required=require_output, default="output", help="Output directory")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="thermalmesh", description="Innohealth ThermalMesh Pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the full pipeline end-to-end")
    _add_pipeline_args(run_parser)
    run_parser.add_argument("--no-occlusion", action="store_true", help="Disable occlusion checking")
    run_parser.add_argument("--no-uv", action="store_true", help="Disable UV generation/export")
    run_parser.add_argument("-v", "--verbose", action="store_true")
    run_parser.set_defaults(func=commands.cmd_run)

    validate_parser = subparsers.add_parser("validate", help="Validate inputs without running the pipeline")
    validate_parser.add_argument("--mesh", required=True)
    validate_parser.add_argument("--thermal", default=None)
    validate_parser.add_argument("--cameras", default=None)
    validate_parser.set_defaults(func=commands.cmd_validate)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect a mesh (.ply) or thermal data file")
    inspect_parser.add_argument("path")
    inspect_parser.set_defaults(func=commands.cmd_inspect)

    align_parser = subparsers.add_parser("align", help="Run the pipeline up to geometry alignment")
    _add_pipeline_args(align_parser)
    align_parser.set_defaults(func=commands.cmd_align)

    estimate_parser = subparsers.add_parser("estimate-poses", help="Run the pipeline up to camera pose refinement")
    _add_pipeline_args(estimate_parser)
    estimate_parser.set_defaults(func=commands.cmd_estimate_poses)

    project_parser = subparsers.add_parser("project", help="Run the pipeline up to thermal projection/occlusion")
    _add_pipeline_args(project_parser)
    project_parser.set_defaults(func=commands.cmd_project)

    blend_parser = subparsers.add_parser("blend", help="Run the pipeline up to multi-view thermal blending")
    _add_pipeline_args(blend_parser)
    blend_parser.set_defaults(func=commands.cmd_blend)

    export_parser = subparsers.add_parser("export", help="Run the full pipeline and produce all configured outputs")
    _add_pipeline_args(export_parser)
    export_parser.set_defaults(func=commands.cmd_export)

    gen_parser = subparsers.add_parser("generate-test-data", help="Generate a synthetic validation dataset")
    gen_parser.add_argument("--output", required=True, help="Directory to write the synthetic dataset into")
    gen_parser.add_argument("--num-views", type=int, default=12)
    gen_parser.add_argument("--seed", type=int, default=0)
    gen_parser.set_defaults(func=commands.cmd_generate_test_data)

    version_parser = subparsers.add_parser("version", help="Print the pipeline version")
    version_parser.set_defaults(func=commands.cmd_version)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
