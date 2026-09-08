"""The pipeline's twenty explicit, independently testable stages.

Each stage takes the shared :class:`PipelineContext`, mutates it, and logs
START/RESULT so a run's progress and provenance are always visible.

Note on ordering: thermal file loading needs each camera's declared image
dimensions to validate the corresponding thermal array shape, so cameras are
loaded immediately before thermal data rather than after it.
"""

from __future__ import annotations

import logging

import numpy as np
import trimesh

from thermalmesh.camera.pose_estimation import estimate_camera_pose
from thermalmesh.camera.pose_initialization import initialize_camera_pose
from thermalmesh.camera.pose_refinement import refine_camera_pose
from thermalmesh.export.csv import export_vertex_csv
from thermalmesh.export.glb import export_glb
from thermalmesh.export.gltf import export_gltf
from thermalmesh.export.hdf5 import export_hdf5
from thermalmesh.export.json import export_json
from thermalmesh.export.numpy import export_array
from thermalmesh.export.report import export_quality_report
from thermalmesh.geometry.alignment import align_point_sets
from thermalmesh.geometry.normals import compute_mesh_normals
from thermalmesh.geometry.preprocessing import preprocess_mesh
from thermalmesh.geometry.quality import mesh_quality_metrics, registration_quality_metrics
from thermalmesh.io.camera_loader import load_cameras
from thermalmesh.io.mesh_loader import load_mesh, load_point_cloud
from thermalmesh.io.thermal_loader import load_thermal_images
from thermalmesh.io.validators import ValidationReport, validate_camera, validate_mesh_file, validate_thermal_image
from thermalmesh.models.mesh import MeshData
from thermalmesh.models.projection import Visibility
from thermalmesh.pipeline.context import PipelineContext
from thermalmesh.pipeline.errors import PipelineValidationError
from thermalmesh.thermal.blending import WeightedTemperatureBlender, blend_all
from thermalmesh.thermal.mapping import map_vertex_to_face_temperature
from thermalmesh.thermal.projection import project_thermal_image
from thermalmesh.uv.thermal_projection import rasterize_vertex_values_to_uv
from thermalmesh.uv.unwrap import generate_uvs
from thermalmesh.uv.validation import validate_uvs

logger = logging.getLogger("thermalmesh.pipeline")


def stage_validate_inputs(ctx: PipelineContext) -> None:
    logger.info("STAGE 1/20: validate_inputs - START")
    report = ValidationReport()
    validate_mesh_file(ctx.mesh_path, report)
    if ctx.initial_mesh_path is not None:
        validate_mesh_file(ctx.initial_mesh_path, report)
    report.raise_if_invalid()
    for warning in report.warnings:
        logger.warning(warning)
    logger.info("STAGE 1/20: validate_inputs - RESULT: %d warning(s)", len(report.warnings))


def stage_load_geometry(ctx: PipelineContext) -> None:
    logger.info("STAGE 2/20: load_geometry - START")
    ctx.mesh = load_mesh(ctx.mesh_path)
    logger.info("Final mesh: %d vertices, %d faces", ctx.mesh.num_vertices, ctx.mesh.num_faces)
    if ctx.initial_mesh_path is not None:
        try:
            ctx.initial_cloud = load_point_cloud(ctx.initial_mesh_path)
            logger.info("Initial acquisition: %d points", ctx.initial_cloud.num_points)
        except Exception:  # noqa: BLE001
            initial_mesh = load_mesh(ctx.initial_mesh_path)
            from thermalmesh.models.pointcloud import PointCloudData

            ctx.initial_cloud = PointCloudData(points=initial_mesh.vertices, metadata=initial_mesh.metadata)
    logger.info("STAGE 2/20: load_geometry - RESULT: OK")


def stage_preprocess_geometry(ctx: PipelineContext) -> None:
    logger.info("STAGE 3/20: preprocess_geometry - START")
    mesh_cfg = ctx.config.get("mesh", {})
    ctx.mesh = preprocess_mesh(ctx.mesh, simplify=mesh_cfg.get("simplify", False), target_faces=mesh_cfg.get("target_faces"))
    ctx.mesh.normals = compute_mesh_normals(ctx.mesh)
    ctx.trimesh_mesh = trimesh.Trimesh(vertices=ctx.mesh.vertices, faces=ctx.mesh.faces, process=False)
    logger.info("STAGE 3/20: preprocess_geometry - RESULT: %d vertices after cleanup", ctx.mesh.num_vertices)


def stage_align_geometry(ctx: PipelineContext) -> None:
    logger.info("STAGE 4/20: align_geometry - START")
    if ctx.initial_cloud is None:
        logger.info("No initial acquisition geometry provided; skipping alignment (final mesh is authoritative)")
        ctx.log_stage("align_geometry: skipped (no initial geometry)")
        return

    reg_cfg = ctx.config.get("registration", {})
    transform, diagnostics = align_point_sets(
        ctx.initial_cloud.points, ctx.mesh.vertices,
        method=reg_cfg.get("method", "auto"),
        max_iterations=reg_cfg.get("max_iterations", 100),
        convergence_tolerance=reg_cfg.get("convergence_tolerance", 1e-6),
    )
    ctx.alignment_transform = transform
    ctx.alignment_diagnostics = registration_quality_metrics(diagnostics)
    for note in diagnostics.notes:
        logger.warning(note)
    logger.info(
        "STAGE 4/20: align_geometry - RESULT: method=%s fitness=%.3f rmse=%.4f confidence=%.3f",
        transform.method, diagnostics.coarse_result.fitness,
        diagnostics.refined_result.rmse if diagnostics.refined_result else diagnostics.coarse_result.rmse,
        transform.confidence,
    )


def stage_load_cameras_and_thermal(ctx: PipelineContext) -> None:
    logger.info("STAGE 5-6/20: load_cameras + load_thermal_data - START")
    ctx.cameras = load_cameras(ctx.cameras_path)
    thermal_cfg = ctx.config.get("thermal", {})
    ctx.thermal_images = load_thermal_images(
        ctx.thermal_dir, ctx.cameras,
        unit=thermal_cfg.get("unit", "unknown"),
        delimiter=thermal_cfg.get("delimiter"),
        has_header=thermal_cfg.get("has_header", False),
    )

    report = ValidationReport()
    for camera in ctx.cameras.values():
        validate_camera(camera, report)
    for image_id, image in ctx.thermal_images.items():
        validate_thermal_image(image, ctx.cameras.get(image_id), report)
    for warning in report.warnings:
        logger.warning(warning)
    report.raise_if_invalid()
    logger.info(
        "STAGE 5-6/20: load_cameras + load_thermal_data - RESULT: %d camera(s), %d thermal image(s)",
        len(ctx.cameras), len(ctx.thermal_images),
    )


def stage_initialize_camera_poses(ctx: PipelineContext) -> None:
    logger.info("STAGE 7/20: initialize_camera_poses - START")
    centroid = ctx.mesh.centroid
    for camera_id, camera in ctx.cameras.items():
        pose = initialize_camera_pose(camera, centroid)
        ctx.camera_poses[camera_id] = pose
        logger.info("Camera %s initialized via %s (confidence=%.2f)", camera_id, pose.estimation_method, pose.confidence)
    logger.info("STAGE 7/20: initialize_camera_poses - RESULT: %d pose(s)", len(ctx.camera_poses))


def stage_estimate_camera_poses(ctx: PipelineContext) -> None:
    logger.info("STAGE 8/20: estimate_camera_poses - START")
    camera_cfg = ctx.config.get("camera", {})
    if not camera_cfg.get("estimate_pose", True):
        logger.info("Camera pose estimation disabled by config; using initial poses")
        return
    for camera_id, camera in ctx.cameras.items():
        initial = ctx.camera_poses[camera_id]
        image = ctx.thermal_images.get(camera_id)
        if image is None:
            continue
        estimated = estimate_camera_pose(camera, ctx.mesh, image, initial)
        ctx.camera_poses[camera_id] = estimated
        logger.info("Camera %s estimated pose confidence=%.2f", camera_id, estimated.confidence)
    logger.info("STAGE 8/20: estimate_camera_poses - RESULT: OK")


def stage_refine_camera_poses(ctx: PipelineContext) -> None:
    logger.info("STAGE 9/20: refine_camera_poses - START")
    camera_cfg = ctx.config.get("camera", {})
    if not camera_cfg.get("refine_pose", True):
        logger.info("Camera pose refinement disabled by config")
        return
    for camera_id, camera in ctx.cameras.items():
        initial = ctx.camera_poses[camera_id]
        image = ctx.thermal_images.get(camera_id)
        if image is None:
            continue
        refined = refine_camera_pose(camera, ctx.mesh, image, initial)
        ctx.camera_poses[camera_id] = refined
        ctx.pose_diagnostics[camera_id] = refined.to_dict()
        logger.info(
            "Camera %s refined in %d iteration(s), converged=%s, confidence=%.2f",
            camera_id, refined.iterations, refined.converged, refined.confidence,
        )
    logger.info("STAGE 9/20: refine_camera_poses - RESULT: OK")


def stage_project_and_analyze_occlusion(ctx: PipelineContext) -> None:
    logger.info("STAGE 10-11/20: project_thermal_images + occlusion_analysis - START")
    projection_cfg = ctx.config.get("projection", {})
    thermal_cfg = ctx.config.get("thermal", {})
    for i, (camera_id, image) in enumerate(ctx.thermal_images.items(), start=1):
        camera = ctx.cameras[camera_id]
        pose = ctx.camera_poses[camera_id]
        logger.info("Projecting thermal image %d/%d (%s)", i, len(ctx.thermal_images), camera_id)
        result, observations = project_thermal_image(
            ctx.mesh, ctx.trimesh_mesh, image, camera, pose,
            occlusion_check=projection_cfg.get("occlusion_check", True),
            sampling_method=thermal_cfg.get("interpolation", "bilinear"),
        )
        ctx.projection_results[camera_id] = result
        ctx.observation_store.add_many(observations)
        logger.info(
            "Image %s: %d visible, %d occluded, %d outside image, %d back-facing",
            camera_id, result.metadata["num_visible"], result.metadata["num_occluded"],
            result.metadata["num_outside_image"], result.metadata["num_back_facing"],
        )
    logger.info("STAGE 10-11/20: project_thermal_images + occlusion_analysis - RESULT: %d observation(s) total",
                ctx.observation_store.total_observations())


def stage_map_temperature_to_geometry(ctx: PipelineContext) -> None:
    logger.info("STAGE 12/20: map_temperature_to_geometry - START")
    blending_cfg = ctx.config.get("blending", {})
    blender = WeightedTemperatureBlender(
        use_distance_weight=blending_cfg.get("distance_weight", True),
        use_angle_weight=blending_cfg.get("angle_weight", True),
        use_confidence_weight=blending_cfg.get("confidence_weight", True),
    )
    temps, confidences, counts = blend_all(ctx.observation_store, blender, ctx.mesh.num_vertices)
    ctx.vertex_temperatures = temps
    ctx.vertex_confidences = confidences
    ctx.vertex_observation_counts = counts
    ctx.mesh.vertex_temperatures = temps
    ctx.face_temperatures = map_vertex_to_face_temperature(ctx.mesh, temps)
    ctx.mesh.face_temperatures = ctx.face_temperatures

    if ctx.initial_cloud is not None and ctx.alignment_transform is not None:
        from thermalmesh.thermal.mapping import map_mesh_to_point_cloud_temperature

        mesh_in_acquisition_space = ctx.alignment_transform.inverse().apply(ctx.mesh.vertices)
        ctx.point_temperatures = map_mesh_to_point_cloud_temperature(
            ctx.initial_cloud, mesh_in_acquisition_space, temps
        )

    coverage = float(np.mean(np.isfinite(temps)))
    logger.info("STAGE 12/20: map_temperature_to_geometry - RESULT: %.1f%% vertex coverage", coverage * 100)


def stage_generate_uvs(ctx: PipelineContext) -> None:
    logger.info("STAGE 13/20: generate_uvs - START")
    uv_cfg = ctx.config.get("uv", {})
    if not uv_cfg.get("enabled", True):
        logger.info("UV generation disabled by config")
        return
    ctx.uv_mesh = generate_uvs(ctx.mesh, resolution=uv_cfg.get("resolution", 2048))
    quality = validate_uvs(ctx.uv_mesh)
    ctx.quality_metrics["uv"] = quality
    logger.info("STAGE 13/20: generate_uvs - RESULT: method=%s valid=%s", quality.get("method"), quality.get("valid"))


def stage_project_thermal_to_uv(ctx: PipelineContext) -> None:
    logger.info("STAGE 14/20: project_thermal_to_uv - START")
    if ctx.uv_mesh is None:
        logger.info("No UV mesh available; skipping per-image UV layers")
        return
    uv_cfg = ctx.config.get("uv", {})
    resolution = uv_cfg.get("resolution", 2048)
    vmapping = ctx.uv_mesh.metadata.get("uv_vertex_mapping")

    for camera_id, result in ctx.projection_results.items():
        per_vertex_temp = np.zeros(ctx.mesh.num_vertices)
        per_vertex_visible = np.zeros(ctx.mesh.num_vertices, dtype=bool)
        per_vertex_conf = np.zeros(ctx.mesh.num_vertices)
        per_vertex_temp[result.visible_geometry] = result.temperatures
        per_vertex_visible[result.visible_geometry] = True
        per_vertex_conf[result.visible_geometry] = result.confidence_map

        if vmapping is not None:
            idx = np.array(vmapping)
            uv_temp, uv_visible, uv_conf = per_vertex_temp[idx], per_vertex_visible[idx], per_vertex_conf[idx]
        else:
            uv_temp, uv_visible, uv_conf = per_vertex_temp, per_vertex_visible, per_vertex_conf

        temperature_tex, valid_mask = rasterize_vertex_values_to_uv(ctx.uv_mesh, uv_temp, uv_visible, resolution)
        confidence_tex, _ = rasterize_vertex_values_to_uv(ctx.uv_mesh, uv_conf, uv_visible, resolution)
        ctx.thermal_layers[camera_id] = {
            "temperature": temperature_tex, "valid_mask": valid_mask,
            "confidence": confidence_tex, "occlusion_mask": ~valid_mask,
        }
    logger.info("STAGE 14/20: project_thermal_to_uv - RESULT: %d layer(s)", len(ctx.thermal_layers))


def stage_blend_thermal_views(ctx: PipelineContext) -> None:
    logger.info("STAGE 15/20: blend_thermal_views - START")
    if ctx.uv_mesh is None:
        logger.info("No UV mesh; skipping UV-space blended texture (vertex-space blending already computed)")
        return
    uv_cfg = ctx.config.get("uv", {})
    resolution = uv_cfg.get("resolution", 2048)
    vmapping = ctx.uv_mesh.metadata.get("uv_vertex_mapping")
    temps = ctx.vertex_temperatures
    if vmapping is not None:
        temps = temps[np.array(vmapping)]
    valid = np.isfinite(temps)
    safe = np.where(valid, temps, 0.0)
    texture, valid_mask = rasterize_vertex_values_to_uv(ctx.uv_mesh, safe, valid, resolution)
    ctx.thermal_layers["blended"] = {"temperature": texture, "valid_mask": valid_mask}
    logger.info("STAGE 15/20: blend_thermal_views - RESULT: %.1f%% UV coverage", float(valid_mask.mean()) * 100)


def stage_generate_visualization_outputs(ctx: PipelineContext) -> None:
    logger.info("STAGE 16/20: generate_visualization_outputs - START")
    output_cfg = ctx.config.get("output", {})
    if ctx.uv_mesh is None:
        logger.info("No UV mesh; skipping GLB/GLTF export")
        return

    from thermalmesh.thermal.normalization import normalize_temperature
    import cv2

    blended = ctx.thermal_layers.get("blended")
    visualization = None
    if blended is not None:
        temp = blended["temperature"]
        mask = blended["valid_mask"]
        finite = temp[mask]
        gray = np.zeros_like(temp, dtype=np.uint8)
        if finite.size:
            lo, hi = finite.min(), finite.max()
            if hi > lo:
                gray[mask] = np.clip((temp[mask] - lo) / (hi - lo) * 255, 0, 255).astype(np.uint8)
        visualization = cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)
        visualization[~mask] = 0

    export_mesh = ctx.uv_mesh
    if output_cfg.get("glb", True):
        path = export_glb(export_mesh, visualization, ctx.output_dir / "model.glb")
        ctx.output_files["glb"] = str(path)
    if output_cfg.get("gltf", True):
        path = export_gltf(export_mesh, visualization, ctx.output_dir / "model.gltf")
        ctx.output_files["gltf"] = str(path)
    logger.info("STAGE 16/20: generate_visualization_outputs - RESULT: OK")


def stage_generate_numerical_outputs(ctx: PipelineContext) -> None:
    logger.info("STAGE 17/20: generate_numerical_outputs - START")
    output_cfg = ctx.config.get("output", {})
    data_dir = ctx.output_dir / "data"
    temp_dir = ctx.output_dir / "temperature"
    layers_dir = ctx.output_dir / "thermal_layers"

    if output_cfg.get("numpy", True):
        ctx.output_files["vertex_temperature_npy"] = str(export_array(ctx.vertex_temperatures, temp_dir / "vertex_temperature.npy"))
        ctx.output_files["face_temperature_npy"] = str(export_array(ctx.face_temperatures, temp_dir / "face_temperature.npy"))
        if ctx.point_temperatures is not None:
            ctx.output_files["point_temperature_npy"] = str(export_array(ctx.point_temperatures, temp_dir / "point_temperature.npy"))

        for image_id, layer in ctx.thermal_layers.items():
            export_array(layer["temperature"], layers_dir / f"thermal_{image_id}.npy")
            export_array(layer["valid_mask"], layers_dir / f"thermal_{image_id}_mask.npy")

    if output_cfg.get("csv", True):
        ctx.output_files["vertices_csv"] = str(export_vertex_csv(
            ctx.mesh, ctx.vertex_temperatures, ctx.vertex_confidences, ctx.vertex_observation_counts,
            data_dir / "temperatures.csv",
        ))

    if output_cfg.get("json", True):
        results_payload = {
            "camera_poses": {cid: pose.to_dict() for cid, pose in ctx.camera_poses.items()},
            "alignment": ctx.alignment_diagnostics,
            "observation_summary": ctx.observation_store.summary(),
            "temperature_statistics": _temperature_statistics(ctx.vertex_temperatures),
            "output_files": ctx.output_files,
        }
        ctx.output_files["results_json"] = str(export_json(results_payload, data_dir / "results.json"))

    if output_cfg.get("hdf5", True):
        ctx.output_files["results_h5"] = str(export_hdf5(
            data_dir / "results.h5",
            mesh=ctx.uv_mesh or ctx.mesh,
            camera_poses=ctx.camera_poses,
            thermal_images=ctx.thermal_images,
            vertex_temperature=ctx.vertex_temperatures,
            face_temperature=ctx.face_temperatures,
            point_temperature=ctx.point_temperatures,
        ))

    if ctx.alignment_transform is not None:
        transform_path = export_json(ctx.alignment_transform.to_dict(), ctx.output_dir / "transforms" / "alignment_matrix.json")
        ctx.output_files["alignment_matrix_json"] = str(transform_path)

    poses_path = export_json({cid: p.to_dict() for cid, p in ctx.camera_poses.items()}, ctx.output_dir / "cameras" / "poses.json")
    ctx.output_files["poses_json"] = str(poses_path)

    logger.info("STAGE 17/20: generate_numerical_outputs - RESULT: %d file(s)", len(ctx.output_files))


def _temperature_statistics(temperatures: np.ndarray) -> dict:
    valid = temperatures[np.isfinite(temperatures)]
    if valid.size == 0:
        return {"count": 0}
    return {
        "count": int(valid.size), "min": float(valid.min()), "max": float(valid.max()),
        "mean": float(valid.mean()), "median": float(np.median(valid)), "std": float(valid.std()),
    }


def stage_generate_quality_report(ctx: PipelineContext) -> None:
    logger.info("STAGE 18/20: generate_quality_report - START")
    metrics = {
        "mesh": mesh_quality_metrics(ctx.mesh),
        "registration": ctx.alignment_diagnostics,
        "camera_poses": {cid: p.to_dict() for cid, p in ctx.camera_poses.items()},
        "thermal": {image_id: image.statistics() for image_id, image in ctx.thermal_images.items()},
        "projection": {
            image_id: {
                "visible": result.metadata["num_visible"],
                "occluded": result.metadata["num_occluded"],
                "outside_image": result.metadata["num_outside_image"],
                "coverage_percent": result.coverage(ctx.mesh.num_vertices) * 100,
            }
            for image_id, result in ctx.projection_results.items()
        },
        "blending": {
            **ctx.observation_store.summary(),
            "average_confidence": float(np.mean(ctx.vertex_confidences[ctx.vertex_confidences > 0]))
            if np.any(ctx.vertex_confidences > 0) else 0.0,
            "final_coverage_percent": float(np.mean(np.isfinite(ctx.vertex_temperatures))) * 100,
        },
        "uv": ctx.quality_metrics.get("uv", {}),
    }
    ctx.quality_metrics = metrics
    json_path, text_path = export_quality_report(metrics, ctx.output_dir)
    ctx.output_files["quality_report_json"] = str(json_path)
    ctx.output_files["quality_report_txt"] = str(text_path)
    logger.info("STAGE 18/20: generate_quality_report - RESULT: OK")


def stage_validate_outputs(ctx: PipelineContext) -> None:
    logger.info("STAGE 19/20: validate_outputs - START")
    from pathlib import Path

    missing = [key for key, path in ctx.output_files.items() if not Path(path).exists()]
    if missing:
        raise PipelineValidationError(
            f"{len(missing)} expected output file(s) were not written",
            reason=str(missing),
            recommendation="Check export stage logs for errors",
        )
    logger.info("STAGE 19/20: validate_outputs - RESULT: %d file(s) verified", len(ctx.output_files))


def stage_complete_pipeline(ctx: PipelineContext) -> None:
    logger.info("STAGE 20/20: complete_pipeline - START")
    import platform
    import sys
    from datetime import datetime, timezone

    from thermalmesh import __version__

    metadata = {
        "pipeline_version": __version__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "configuration": ctx.config,
        "input_files": {
            "mesh": str(ctx.mesh_path),
            "initial_mesh": str(ctx.initial_mesh_path) if ctx.initial_mesh_path else None,
            "thermal_dir": str(ctx.thermal_dir),
            "cameras": str(ctx.cameras_path),
        },
        "stage_log": ctx.stage_log,
    }
    ctx.output_files["metadata_json"] = str(export_json(metadata, ctx.output_dir / "metadata.json"))
    logger.info("Pipeline completed successfully")
    logger.info("STAGE 20/20: complete_pipeline - RESULT: OK")
