"""Maps the ThermalMesh engine's 18 internal stage functions onto the 10
public ``ProcessingStageName`` values shown in the UI (spec section 61).
"""

from __future__ import annotations

from app.models.enums import ProcessingStageName

# Internal pipeline stage function name -> one or more public stage names.
# Order matters: this also defines display order for stages that share an
# internal function (there are none currently) and documents which
# internal work backs each public stage.
INTERNAL_TO_PUBLIC: dict[str, list[ProcessingStageName]] = {
    "stage_validate_inputs": [ProcessingStageName.INPUT_VALIDATION],
    "stage_load_geometry": [ProcessingStageName.MESH_ALIGNMENT],
    "stage_preprocess_geometry": [ProcessingStageName.MESH_ALIGNMENT],
    "stage_align_geometry": [ProcessingStageName.MESH_ALIGNMENT],
    "stage_load_cameras_and_thermal": [ProcessingStageName.CAMERA_POSE_ESTIMATION],
    "stage_initialize_camera_poses": [ProcessingStageName.CAMERA_POSE_ESTIMATION],
    "stage_estimate_camera_poses": [ProcessingStageName.CAMERA_POSE_ESTIMATION],
    "stage_refine_camera_poses": [ProcessingStageName.CAMERA_POSE_ESTIMATION],
    "stage_project_and_analyze_occlusion": [
        ProcessingStageName.THERMAL_PROJECTION,
        ProcessingStageName.OCCLUSION_ANALYSIS,
    ],
    "stage_map_temperature_to_geometry": [ProcessingStageName.TEMPERATURE_MAPPING],
    "stage_generate_uvs": [ProcessingStageName.UV_GENERATION],
    "stage_project_thermal_to_uv": [ProcessingStageName.THERMAL_BLENDING],
    "stage_blend_thermal_views": [ProcessingStageName.THERMAL_BLENDING],
    "stage_generate_visualization_outputs": [ProcessingStageName.WEB_EXPORT],
    "stage_generate_numerical_outputs": [ProcessingStageName.WEB_EXPORT],
    "stage_generate_quality_report": [ProcessingStageName.REPORT_GENERATION],
    "stage_validate_outputs": [ProcessingStageName.REPORT_GENERATION],
    "stage_complete_pipeline": [ProcessingStageName.REPORT_GENERATION],
}

PUBLIC_STAGE_ORDER: list[ProcessingStageName] = [
    ProcessingStageName.INPUT_VALIDATION,
    ProcessingStageName.MESH_ALIGNMENT,
    ProcessingStageName.CAMERA_POSE_ESTIMATION,
    ProcessingStageName.THERMAL_PROJECTION,
    ProcessingStageName.OCCLUSION_ANALYSIS,
    ProcessingStageName.TEMPERATURE_MAPPING,
    ProcessingStageName.UV_GENERATION,
    ProcessingStageName.THERMAL_BLENDING,
    ProcessingStageName.WEB_EXPORT,
    ProcessingStageName.REPORT_GENERATION,
]

TOTAL_INTERNAL_STAGES = len(INTERNAL_TO_PUBLIC)
