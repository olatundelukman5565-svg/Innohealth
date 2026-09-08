# Innohealth ThermalMesh Pipeline

Standalone, automated 3D geometry + thermal imaging processing software.
Takes a reconstructed 3D mesh, an optional initial acquisition scan, and a
set of thermal camera views (raw numerical temperature arrays + camera
metadata), and produces a temperature-mapped, UV-textured, web-ready 3D
model plus fully numerical temperature outputs.

> **Status.** The pipeline is implemented and validated end-to-end against
> a synthetic dataset with known ground truth (see [Synthetic
> validation](#synthetic-validation)). It has **not** yet been validated
> against Innohealth's real PLY meshes, thermal exports, or camera
> hardware -- see [Known limitations](#known-limitations--what-needs-real-data-validation).

## Easiest way to run it (no command line)

1. Download/clone this repository and switch to this branch.
2. Double-click the launcher for your OS in the repository root:
   - **Mac**: `RunThermalMesh.command` (first time, you may need to
     right-click -> Open once if macOS blocks unidentified scripts)
   - **Windows**: `RunThermalMesh.bat`
   - **Linux**: `RunThermalMesh.sh`
3. The first launch installs everything automatically (takes a minute or
   two); a window opens afterward.
4. Click **Generate Demo Dataset** to try it immediately with no real data,
   or use the **Browse...** buttons to point at your own final mesh,
   thermal data folder, and cameras file.
5. Click **Run Pipeline** and watch the log. When it finishes, click
   **Open Output Folder** to see the results (`model.glb`,
   `quality_report.txt`, temperature CSVs, etc.).

Requires Python 3.11+ installed with the standard `tkinter` GUI module
(included by default in the python.org Mac/Windows installers; on minimal
Linux installs, `sudo apt install python3-tk` first).

Prefer the command line? See [Quick start](#quick-start) below.

## Product overview

Given:

- a final reconstructed PLY mesh,
- an optional initial acquisition mesh/point cloud,
- N thermal views (raw per-pixel temperature arrays) with camera metadata,

the pipeline:

1. Validates and loads all inputs.
2. Aligns the initial acquisition geometry onto the final mesh (if provided).
3. Initializes, estimates, and refines each camera's pose.
4. Projects every thermal image onto the mesh independently, with
   occlusion/visibility analysis and sub-pixel sampling.
5. Maps temperature onto mesh vertices, faces, and (optionally) the initial
   point cloud, keeping every individual observation before blending.
6. Generates UVs automatically and blends multi-view observations into
   per-vertex, per-image-layer, and UV-space temperature data.
7. Exports GLB/GLTF for web visualization plus CSV/NumPy/JSON/HDF5 for
   authoritative numerical data, along with a quality report.

Raw numerical temperature is always authoritative; colorized textures are a
visualization convenience only and are never the source of truth.

## Architecture

```
src/thermalmesh/
  models/     data classes: MeshData, PointCloudData, ThermalImage, Camera,
              CameraPose, Transform/CoordinateSystem, ProjectionResult,
              TemperatureObservation, PipelineResult
  io/         mesh/thermal/camera loaders, input validators, writer helpers
  geometry/   preprocessing, PCA/ICP registration, alignment orchestration,
              normals, coordinate transforms, quality metrics
  camera/     intrinsics/extrinsics, projection math, pose
              initialization/estimation/refinement, silhouette diagnostics
  thermal/    raw-data parser, calibration, sampling, occlusion (ray
              casting), per-image projection, observation storage, blending
  uv/         automatic UV unwrapping (xatlas, with a fallback), validation,
              UV-space rasterization, per-image texture layers
  export/     GLB/GLTF, CSV, NumPy, JSON, HDF5, quality report
  pipeline/   PipelineContext, the 20 explicit stages, orchestrator, runner,
              custom exceptions
  cli/        `thermalmesh` command-line interface
```

See `docs/architecture.md` for the full stage-by-stage data flow.

## Installation

Requires Python 3.11+.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
# or: pip install -r requirements.txt
```

Core dependencies: NumPy, SciPy, trimesh, OpenCV, Pillow, h5py, PyYAML,
rtree (ray-mesh broad-phase). `xatlas` is used for UV unwrapping if
installed; otherwise a lower-quality spherical-projection fallback is used
automatically (this is logged and recorded in output metadata).

No paid or cloud APIs are required or used; everything runs locally.

## Quick start

Generate a synthetic dataset and run the full pipeline against it:

```bash
thermalmesh generate-test-data --output examples/synthetic_dataset --num-views 12
thermalmesh run \
    --mesh examples/synthetic_dataset/final_mesh.ply \
    --initial-mesh examples/synthetic_dataset/initial_mesh.ply \
    --thermal examples/synthetic_dataset/thermal \
    --cameras examples/synthetic_dataset/cameras.json \
    --config config/synthetic.yaml \
    --output output/
```

Or programmatically:

```python
from thermalmesh.pipeline.runner import run_pipeline

result = run_pipeline(
    mesh_path="final_mesh.ply",
    thermal_dir="thermal/",
    cameras_path="cameras.json",
    output_dir="output/",
    initial_mesh_path="initial_mesh.ply",   # optional
    config_path="config/default.yaml",       # optional
)
print(result.vertex_temperatures)
```

## Input formats

See `docs/input_format.md` for full detail. Summary:

- **Mesh**: PLY (ASCII or binary), loaded via `trimesh`.
- **Thermal data**: CSV, whitespace-delimited text, or `.npy`, one
  `(height, width)` numeric array per camera. Invalid-value markers (`NaN`,
  `N/A`, `-`, empty) become `NaN`, never dropped rows/columns.
- **Cameras**: JSON (`examples/sample_camera.json`) with per-camera
  `image_width`/`image_height`, optional `intrinsics`, optional
  `position`/`rotation`, and an optional `thermal_file` link.

## Camera model

See `docs/camera_model.md`. Camera location alone (no orientation) is
supported: the pipeline initializes a look-at pose, then runs
correspondence-free silhouette-based estimation and local refinement
(`scipy.optimize`) to improve it. Explicit 3D<->2D correspondences (e.g.
calibration markers) can instead drive classic PnP
(`camera.pose_estimation.estimate_pose_pnp`).

## Thermal mapping

See `docs/thermal_mapping.md`. Every thermal image is projected onto the
mesh independently (occlusion-checked via ray casting, sub-pixel bilinear
sampled), producing a full observation history per vertex before any
blending. Blending is a pluggable, configurable weighted average
(distance/angle/confidence), implemented via `BaseBlender` so alternative
strategies can be added later.

## UV generation & outputs

Automatic UV unwrapping via `xatlas` (spherical-projection fallback if
unavailable). See `docs/output_format.md` for the full output directory
layout (`model.glb`/`model.gltf`, per-image `thermal_layers/`,
`temperature/*.npy`, `data/{temperatures.csv,results.json,results.h5}`,
`cameras/poses.json`, `transforms/alignment_matrix.json`,
`quality_report.{json,txt}`, `metadata.json`).

## CLI

```
thermalmesh run               --mesh ... --thermal ... --cameras ... --output ...
thermalmesh validate          --mesh ... [--thermal ...] [--cameras ...]
thermalmesh inspect           <mesh.ply | thermal_file>
thermalmesh align             (partial run through geometry alignment)
thermalmesh estimate-poses    (partial run through pose refinement)
thermalmesh project           (partial run through thermal projection/occlusion)
thermalmesh blend             (partial run through multi-view blending)
thermalmesh export            (full run; all configured outputs)
thermalmesh generate-test-data --output ... [--num-views N] [--seed S]
thermalmesh version
```

Every subcommand supports `--help`.

## Configuration

All tunable parameters live in YAML (`config/default.yaml`); see that file
for the full set (registration method/iterations, camera pose
estimation/refinement toggles, thermal interpolation, occlusion checking,
UV resolution, blending weights, which outputs to write). Pass
`--config <file>.yaml` or `config_path=...` to override; `config/test.yaml`
and `config/synthetic.yaml` are faster presets for testing.

## Testing

```bash
pytest tests/unit          # fast, isolated unit tests
pytest tests/integration   # full pipeline run against a synthetic dataset
pytest                     # everything
```

## Synthetic validation

`thermalmesh.synthetic.generate_synthetic_dataset` builds a mesh with known
geometry, a known analytic temperature field, a known acquisition-to-final
rigid transform, and camera-rendered (ray-cast) thermal images with known
ground-truth poses -- but only gives the pipeline camera *positions*,
forcing it to genuinely estimate orientation. `tests/integration/` asserts
the recovered temperature field and output files are correct. This proves
the architecture and math are sound; it does not prove accuracy on real
Innohealth data (see below).

## Known limitations / what needs real-data validation

- **Camera pose estimation/refinement** is correspondence-free (thermal
  arrays generally lack visual features): it segments the thermal
  foreground via Otsu thresholding and fits a silhouette convex hull. This
  is weak on rotationally-symmetric or non-thermally-distinct objects and
  has not been tuned against Innohealth's actual thermal signatures. If
  real correspondences (markers, known keypoints) are available, prefer
  `estimate_pose_pnp` instead.
- **Geometry alignment** (initial-vs-final registration) uses
  centroid/PCA coarse alignment + ICP; it assumes comparable scale and
  reasonable initial overlap. Real acquisition-vs-reconstruction offsets
  are unvalidated.
- **UV unwrapping** falls back to a lower-quality spherical projection if
  `xatlas` is unavailable in the target environment.
- Real camera intrinsics/lens distortion for Innohealth's actual thermal
  hardware are unknown; the fallback FOV-based intrinsic estimate is
  clearly marked (`intrinsics_source="estimated_fallback"`) but unvalidated.
- Real thermal export format(s) may differ from generic CSV/whitespace
  text; add a new adapter in `io/thermal_loader.py` /
  `thermal/parser.py` rather than modifying pipeline logic.

See `docs/development.md` for the full real-data integration checklist.

## Repository layout

See the top of `docs/architecture.md` for the annotated tree.
