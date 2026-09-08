# Troubleshooting

## `RunThermalMesh.command`/`.sh`/`.bat` does nothing, or `ModuleNotFoundError: No module named 'tkinter'`

The one-click GUI (`scripts/gui.py`) uses Python's built-in `tkinter`
module. It ships by default with the python.org installers for Mac and
Windows. On minimal Linux installs it's a separate OS package:

```bash
sudo apt install python3-tk      # Debian/Ubuntu
sudo dnf install python3-tkinter # Fedora
```

macOS may also block the `.command` file as being from an "unidentified
developer" the first time -- right-click it and choose **Open** once to
approve it, then double-clicking works normally afterward.

## `InvalidThermalDataError: Thermal file ... contains N rows but camera
metadata specifies an image height of M`

The thermal array's shape must exactly match the camera's declared
`image_width`/`image_height`. Fix the camera JSON or re-export the thermal
data at the stated size.

## `PoseEstimationError: Cannot initialize pose ... no position or
orientation is known`

Every camera needs at least an approximate world-space `position` in the
camera JSON, or a full `position`+`rotation`. If truly nothing is known,
either supply an approximate position (even a coarse guess is enough for
look-at initialization + refinement to correct) or provide explicit
3D<->2D correspondences and call `camera.pose_estimation.estimate_pose_pnp`
directly.

## Camera pose confidence is low / silhouette IoU near 0

- Check that the thermal image actually shows a warm object against a
  cooler (or vice versa) background -- `segment_thermal_foreground`
  assumes thermal contrast between object and background. A thermal image
  with no contrast can't be pose-refined by this method.
  `camera.diagnostics.segment_thermal_foreground` can be called standalone
  to inspect the segmentation mask if this is suspected.
- Check the initial camera position is roughly correct (within the same
  order of magnitude of scene scale) -- refinement is a *local*
  optimization bounded by `max_rotation_delta_deg`/
  `max_translation_fraction` and will not recover from a wildly wrong
  starting point.
- Rotationally-symmetric or texture-less-silhouette objects fundamentally
  limit this method's ability to resolve orientation -- see
  `docs/camera_model.md`'s "Known weakness" section.

## Low thermal coverage (`final_coverage_percent` in the quality report)

- Check `projection.<camera_id>.coverage_percent` per camera in the
  quality report -- if most vertices are `back_facing` or
  `outside_image`, cameras likely don't actually cover that part of the
  object (expected, not a bug) or poses are wrong (see above).
- If most are `occluded` unexpectedly, check mesh normals point outward
  (`geometry/normals.py::compute_mesh_normals` uses trimesh's
  angle-weighted normals, which assumes a consistently-wound mesh).

## `UVGenerationError: Cannot generate UVs for a mesh with no faces`

The input PLY is a point cloud, not a mesh with triangle connectivity. UV
generation and GLB/GLTF texturing require faces; point-cloud-only
temperature mapping (`point_temperature.npy`) still works without UVs.

## `xatlas` not installed

UV generation automatically falls back to a lower-quality spherical
projection and logs a warning; install `xatlas` (`pip install xatlas`) for
production-quality atlasing.

## `ModuleNotFoundError: No module named 'rtree'`

`rtree` is required by `trimesh`'s ray-mesh broad-phase tree, used for
occlusion analysis. `pip install rtree` (also listed in
`requirements.txt`/`pyproject.toml`).

## Pipeline is slow on a large mesh/many thermal views

- Enable `mesh.simplify` + `mesh.target_faces` in config to decimate the
  final mesh before processing.
- Lower `uv.resolution` for faster UV rasterization.
- Occlusion ray casting is the usual bottleneck on large meshes; installing
  `trimesh`'s optional `pyembree` backend significantly speeds up ray
  casting if available for your platform.
