# Camera Model

## Intrinsics

Standard pinhole model:

```
K = [ fx   0  cx ]
    [  0  fy  cy ]
    [  0   0   1 ]
```

plus an optional OpenCV-style distortion vector. `camera/intrinsics.py`
builds/validates `K`; `camera/projection.py::project_points` applies it
(via `cv2.projectPoints`, so distortion is honored when present).

If intrinsics are not provided, a fallback focal length is derived from a
configurable default field of view (`io/camera_loader.py`,
`default_fov_degrees`) and the camera is marked
`intrinsics_source="estimated_fallback"` in its metadata -- this is never
conflated with a measured value in diagnostics or the quality report.

## Extrinsics / pose lifecycle

A camera's pose passes through up to three stages, each producing a
`CameraPose` with an `estimation_method` and `confidence`:

1. **Initialization** (`camera/pose_initialization.py`)
   - Full pose (position + rotation) provided -> used directly, `"provided"`.
   - Position only -> look-at rotation toward the mesh centroid,
     `"look_at_init"`, confidence capped at 0.4 (never treated as ground truth).
   - Neither -> `PoseEstimationError` (no fabricated cameras).

2. **Estimation** (`camera/pose_estimation.py`)
   - `estimate_pose_pnp`: classic `cv2.solvePnP` when explicit 3D<->2D
     correspondences exist (e.g. calibration markers). Not run
     automatically -- call it directly if such correspondences are available.
   - `estimate_camera_pose` (default, automatic): thermal arrays generally
     carry no visual features, so this is correspondence-free. It
     Otsu-segments the thermal image into foreground/background
     (`camera/diagnostics.py::segment_thermal_foreground`, assuming the
     object is thermally distinct from its surroundings), renders an
     approximate mesh silhouette (convex hull of projected vertices) for
     the current pose, and applies a closed-form correction: move the
     camera along its viewing axis to match apparent scale, and laterally
     to match the silhouette bounding-box center.

3. **Refinement** (`camera/pose_refinement.py`)
   - Local optimization (`scipy.optimize.minimize`, Powell) over a bounded
     6-DOF perturbation (rotation delta capped at
     `max_rotation_delta_deg`, translation capped at a fraction of the
     scene scale) maximizing silhouette IoU. Iteration count and
     convergence are recorded; `reprojection_error` here is `1 - IoU`
     (silhouette misfit), not a keypoint reprojection error, since no
     keypoints exist.

Both `camera.estimate_pose`/`camera.refine_pose` config flags
(`config/default.yaml`) can disable stages 2/3 independently.

## Known weakness (needs real-data validation)

Silhouette-IoU-based estimation cannot distinguish poses that produce the
same apparent silhouette -- notably rotations of a rotationally-symmetric
object around its own axis, or small camera translations tangential to a
convex, texture-less surface. The synthetic test object (a sphere) exposes
this clearly: temperature recovery still succeeds because the analytic
field is smooth and the sphere is symmetric, but recovered camera
*orientations* can be tens of degrees off. Real Innohealth objects are
presumably less symmetric, but this must be validated against real
thermal signatures before trusting per-camera pose accuracy in isolation
(as opposed to end-to-end temperature mapping accuracy, which the
blending stage's confidence weighting partially absorbs).

## 2D<->3D math

- `project_points(points_world, camera, pose)` -> pixel coords, camera-space
  depth, and an "in front of camera" mask. Vectorized via `cv2.projectPoints`.
- `pixel_to_camera_ray` / `pixel_to_world_ray` invert this for ray casting
  (used both for synthetic data rendering and for the occlusion analysis
  ray-mesh intersection tests).
