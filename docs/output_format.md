# Output Formats

Given `--output out/`, a full `thermalmesh run` produces:

```
out/
  model.glb                        Visualization-only textured mesh
  model.gltf (+ .bin buffers)      Same, non-binary glTF
  thermal_layers/
    thermal_<camera_id>.npy        Per-image UV-space temperature layer
    thermal_<camera_id>_mask.npy   Per-image UV-space validity mask
    thermal_blended.npy            Final blended UV-space temperature
    thermal_blended_mask.npy       Final blended UV-space validity mask
  temperature/
    vertex_temperature.npy         Blended per-vertex temperature (NaN = unobserved)
    face_temperature.npy           Mean-of-vertices per-face temperature
    point_temperature.npy          Nearest-vertex transfer onto the initial
                                    point cloud (only if --initial-mesh given)
  data/
    temperatures.csv               vertex_id,x,y,z,temperature,confidence,observation_count
    results.json                   camera poses, alignment diagnostics,
                                    observation summary, temperature stats
    results.h5                     /mesh, /cameras/poses, /thermal/images,
                                    /results/{vertex,face,point}_temperature
  cameras/
    poses.json                     Every camera's final CameraPose.to_dict()
  transforms/
    alignment_matrix.json          ACQUISITION -> FINAL_MESH Transform
                                    (only if --initial-mesh given)
  quality_report.json              Structured metrics (see below)
  quality_report.txt               Human-readable rendering of the same
  metadata.json                    Version, timestamps, config, input paths,
                                    stage log (reproducibility record)
```

Which of `model.glb`/`model.gltf`/CSV/NumPy/JSON/HDF5 get written is
controlled by the `output.*` config flags; the temperature/data/thermal_layers
files are effectively the NumPy/CSV/JSON exports and follow those same flags.

## Authoritative vs. visualization data

The GLB/GLTF texture is a colorized visualization convenience
(`thermal/normalization.py` + `uv/texture_generation.py`). **Numerical
temperature is always in the `.npy`/`.csv`/`.json`/`.h5` outputs** --
never infer temperature from the rendered color.

## Quality report structure

`quality_report.json` (see `export/report.py`,
`pipeline/stages.py::stage_generate_quality_report`):

```json
{
  "mesh": {"num_vertices": ..., "num_faces": ..., "surface_area": ..., ...},
  "registration": { ...AlignmentDiagnostics.to_dict() (if applicable)... },
  "camera_poses": {"<camera_id>": {...CameraPose.to_dict()...}, ...},
  "thermal": {"<camera_id>": {...ThermalImage.statistics()...}, ...},
  "projection": {"<camera_id>": {"visible": N, "occluded": N,
                                   "outside_image": N, "coverage_percent": F}},
  "blending": {"geometry_elements_with_observations": N,
               "total_observations": N, "average_confidence": F,
               "final_coverage_percent": F},
  "uv": {"valid": bool, "method": "xatlas"|"spherical_projection_fallback", ...}
}
```

## HDF5 layout (`results.h5`)

```
/mesh/vertices, /mesh/faces, /mesh/uv
/cameras/poses/<camera_id>/{rotation,translation} (+ confidence, estimation_method attrs)
/thermal/images/<camera_id>/{temperature,validity_mask}
/results/{vertex_temperature,face_temperature,point_temperature}
```
