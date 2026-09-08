"""The top-level pipeline orchestrator.

Runs all twenty stages against a :class:`PipelineContext` in order. Callable
directly from Python (Rule 10) -- the CLI is a thin wrapper around this.
"""

from __future__ import annotations

import logging
from typing import Callable

from thermalmesh.models.results import PipelineResult
from thermalmesh.pipeline import stages
from thermalmesh.pipeline.context import PipelineContext
from thermalmesh.pipeline.errors import ThermalMeshError

logger = logging.getLogger("thermalmesh.pipeline")

STAGES = [
    stages.stage_validate_inputs,
    stages.stage_load_geometry,
    stages.stage_preprocess_geometry,
    stages.stage_align_geometry,
    stages.stage_load_cameras_and_thermal,
    stages.stage_initialize_camera_poses,
    stages.stage_estimate_camera_poses,
    stages.stage_refine_camera_poses,
    stages.stage_project_and_analyze_occlusion,
    stages.stage_map_temperature_to_geometry,
    stages.stage_generate_uvs,
    stages.stage_project_thermal_to_uv,
    stages.stage_blend_thermal_views,
    stages.stage_generate_visualization_outputs,
    stages.stage_generate_numerical_outputs,
    stages.stage_generate_quality_report,
    stages.stage_validate_outputs,
    stages.stage_complete_pipeline,
]


class ThermalMeshPipeline:
    def __init__(self, context: PipelineContext) -> None:
        self.context = context

    def run(
        self,
        *,
        stop_after: str | None = None,
        on_stage_start: Callable[[str, int, int], None] | None = None,
        on_stage_complete: Callable[[str, int, int], None] | None = None,
    ) -> PipelineResult:
        """Run every stage in order.

        ``on_stage_start``/``on_stage_complete`` are optional callbacks invoked
        with ``(stage_name, index, total_stages)`` -- used by the web backend
        to stream live progress without the pipeline knowing anything about
        HTTP, jobs, or databases.
        """
        self.context.output_dir.mkdir(parents=True, exist_ok=True)
        total = len(STAGES)
        for index, stage_fn in enumerate(STAGES, start=1):
            name = stage_fn.__name__
            if on_stage_start:
                on_stage_start(name, index, total)
            try:
                stage_fn(self.context)
            except ThermalMeshError:
                logger.exception("Stage %s failed", name)
                raise
            except Exception as exc:  # noqa: BLE001
                logger.exception("Stage %s failed with an unexpected error", name)
                raise ThermalMeshError(
                    f"Unexpected error in stage '{name}': {exc}",
                    source=name, reason=str(exc),
                    recommendation="Inspect the stage traceback above",
                ) from exc
            self.context.log_stage(f"{name}: OK")
            if on_stage_complete:
                on_stage_complete(name, index, total)
            if stop_after and name == stop_after:
                logger.info("Stopping after stage %s as requested", name)
                break
        return self._build_result()

    def _build_result(self) -> PipelineResult:
        ctx = self.context
        return PipelineResult(
            aligned_mesh=ctx.uv_mesh or ctx.mesh,
            camera_poses=ctx.camera_poses,
            thermal_observations={gid: ctx.observation_store.get(gid) for gid in ctx.observation_store.geometry_ids()},
            vertex_temperatures=ctx.vertex_temperatures,
            face_temperatures=ctx.face_temperatures,
            point_temperatures=ctx.point_temperatures,
            uv_maps=ctx.uv_mesh.uv_coordinates if ctx.uv_mesh is not None else None,
            thermal_layers=ctx.thermal_layers,
            blended_texture=ctx.thermal_layers.get("blended", {}).get("temperature") if ctx.thermal_layers else None,
            output_files=ctx.output_files,
            quality_metrics=ctx.quality_metrics,
            metadata={"stage_log": ctx.stage_log},
        )
