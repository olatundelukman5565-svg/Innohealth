# Architecture

## Data flow

```
INPUT (final PLY, optional initial PLY/cloud, thermal arrays, camera JSON)
  -> validate_inputs
  -> load_geometry
  -> preprocess_geometry (cleanup, normals)
  -> align_geometry (if initial geometry provided: centroid/PCA + ICP)
  -> load_cameras + load_thermal_data
  -> initialize_camera_poses (provided pose, or look-at from position)
  -> estimate_camera_poses (silhouette-bbox correspondence-free estimate)
  -> refine_camera_poses (local optimization, silhouette IoU objective)
  -> project_thermal_images + occlusion_analysis (per image, ray-cast)
  -> map_temperature_to_geometry (blend observations -> vertex/face/point)
  -> generate_uvs (xatlas, or spherical-projection fallback)
  -> project_thermal_to_uv (per-image UV-space layers)
  -> blend_thermal_views (UV-space blended texture)
  -> generate_visualization_outputs (GLB/GLTF)
  -> generate_numerical_outputs (CSV/NumPy/JSON/HDF5)
  -> generate_quality_report
  -> validate_outputs
  -> complete_pipeline (metadata.json)
```

Each stage is a plain function in `pipeline/stages.py` taking and mutating a
single `PipelineContext` (`pipeline/context.py`). `pipeline/pipeline.py`
runs them in order, wrapping every stage in a `ThermalMeshError` if it
fails and logging START/RESULT for each. `pipeline/runner.py::run_pipeline`
is the single entry point both the CLI and any external Python code should
call (Rule 10: the pipeline is not CLI-only).

## Why stages are ordered the way they are

The spec's original stage list has `load_thermal_data` (5) before
`load_cameras` (6); this implementation loads cameras first because
validating each thermal array's shape against its camera's declared
`image_width`/`image_height` requires the camera metadata already parsed.
Functionally nothing is lost -- the combined stage is logged as
`STAGE 5-6/20`.

Occlusion analysis (11) is not a separate pass over the mesh: it's
performed inside `thermal/projection.py::project_thermal_image` (10) via
`thermal/occlusion.py::compute_visibility`, since visibility must be known
before a pixel can be sampled at all. The stage numbering in logs reflects
this (`STAGE 10-11/20`).

## Repository layout

```
config/                   default.yaml, test.yaml, synthetic.yaml
src/thermalmesh/
  models/                  MeshData, PointCloudData, ThermalImage, Camera,
                           CameraPose, Transform/CoordinateSystem,
                           ProjectionResult, TemperatureObservation,
                           PipelineResult
  io/                      mesh_loader, thermal_loader, camera_loader,
                           validators, writers
  geometry/                preprocessing, registration (Kabsch/ICP),
                           alignment (strategy selection), normals,
                           transforms, quality
  camera/                  intrinsics, extrinsics, projection,
                           pose_initialization, pose_estimation,
                           pose_refinement, diagnostics (silhouette utils)
  thermal/                 parser, calibration, normalization (viz-only),
                           sampling, projection, occlusion, mapping,
                           observations, blending
  uv/                      unwrap, validation, thermal_projection,
                           texture_generation
  export/                  glb, gltf, csv, numpy, json, hdf5, report
  pipeline/                context, stages, pipeline, runner, errors
  cli/                     main, commands
  synthetic.py             synthetic validation dataset generator
tests/
  unit/                    one focused test module per subsystem
  integration/             full pipeline run against a synthetic dataset
scripts/                   thin CLI wrappers (generate_synthetic_dataset,
                           inspect_mesh, inspect_thermal) around the
                           packaged library functions
examples/                  sample_camera.json, sample_config.yaml
docs/                      this file and its siblings
```

## Coordinate systems

Six named spaces are tracked explicitly (`models/transforms.py`):
`ACQUISITION`, `FINAL_MESH`, `WORLD`, `CAMERA`, `IMAGE`, `UV`. Every
conversion between them is an explicit `Transform` (4x4 homogeneous matrix
+ source/target + method + confidence) -- nothing is implicitly assumed
aligned. See `docs/alignment.md`.

## Extensibility points

- **Thermal file adapters**: add a new parser function in
  `thermal/parser.py` and wire it into `io/thermal_loader.py` if
  Innohealth's real export format differs from CSV/whitespace text.
- **Blending strategies**: subclass `thermal.blending.BaseBlender`.
- **Registration methods**: add a function alongside `centroid_align`/
  `pca_align`/`icp` in `geometry/registration.py` and wire it into
  `geometry/alignment.py`'s strategy selection.
- **Pose estimation**: `camera/pose_estimation.py` exposes both the
  default correspondence-free method and `estimate_pose_pnp` for when real
  2D/3D correspondences exist.
