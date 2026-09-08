"""End-to-end validation against the synthetic dataset (known ground truth).

This validates the pipeline's architecture and math on data the software
can perfectly explain by construction. It does NOT validate accuracy
against Innohealth's real thermal signatures, cameras, or acquisition
geometry -- see docs/development.md.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from thermalmesh.pipeline.runner import run_pipeline
from thermalmesh.synthetic import generate_synthetic_dataset


@pytest.fixture(scope="module")
def synthetic_dataset(tmp_path_factory):
    dataset_dir = tmp_path_factory.mktemp("synthetic_dataset")
    ground_truth = generate_synthetic_dataset(
        dataset_dir, num_views=8, image_width=64, image_height=48, subdivisions=2, seed=0,
    )
    return dataset_dir, ground_truth


@pytest.fixture(scope="module")
def pipeline_result(synthetic_dataset):
    dataset_dir, _ = synthetic_dataset
    output_dir = dataset_dir / "output"
    result = run_pipeline(
        mesh_path=dataset_dir / "final_mesh.ply",
        thermal_dir=dataset_dir / "thermal",
        cameras_path=dataset_dir / "cameras.json",
        output_dir=output_dir,
        initial_mesh_path=dataset_dir / "initial_mesh.ply",
        config_overrides={"uv": {"resolution": 64}},
    )
    return result, output_dir


def test_pipeline_produces_expected_output_files(pipeline_result):
    _, output_dir = pipeline_result
    assert (output_dir / "model.glb").exists()
    assert (output_dir / "model.gltf").exists()
    assert (output_dir / "data" / "temperatures.csv").exists()
    assert (output_dir / "data" / "results.json").exists()
    assert (output_dir / "data" / "results.h5").exists()
    assert (output_dir / "temperature" / "vertex_temperature.npy").exists()
    assert (output_dir / "quality_report.json").exists()
    assert (output_dir / "quality_report.txt").exists()
    assert (output_dir / "metadata.json").exists()
    assert (output_dir / "cameras" / "poses.json").exists()
    assert (output_dir / "transforms" / "alignment_matrix.json").exists()


def test_pipeline_achieves_reasonable_thermal_coverage(pipeline_result):
    result, _ = pipeline_result
    coverage = np.mean(np.isfinite(result.vertex_temperatures))
    assert coverage > 0.5


def test_pipeline_recovers_known_temperature_field(synthetic_dataset, pipeline_result):
    dataset_dir, ground_truth = synthetic_dataset
    result, _ = pipeline_result

    true_temperatures = np.array(ground_truth["vertex_temperatures"])
    recovered = result.vertex_temperatures
    valid = np.isfinite(recovered)
    assert valid.sum() > 0

    error = np.abs(recovered[valid] - true_temperatures[valid])
    assert np.median(error) < 2.0  # degrees; allows for noise + sampling/blending error


def test_pipeline_estimates_reasonable_camera_poses(pipeline_result):
    result, _ = pipeline_result
    assert len(result.camera_poses) > 0
    for pose in result.camera_poses.values():
        assert pose.confidence >= 0.0


def test_quality_report_is_valid_json(pipeline_result):
    _, output_dir = pipeline_result
    data = json.loads((output_dir / "quality_report.json").read_text())
    assert "mesh" in data
    assert "thermal" in data
    assert "blending" in data
