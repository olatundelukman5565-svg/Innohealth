# Geometry Alignment

## When it runs

Only if an initial acquisition mesh/point cloud is supplied
(`--initial-mesh`). If not, the final mesh is treated as already being the
authoritative coordinate frame and `stage_align_geometry` is a no-op.

## Strategy (`geometry/alignment.py::align_point_sets`)

1. **Diagnostics first**: source/target centroid, a bounding-box-diagonal
   scale estimate, and their ratio. A scale ratio far from 1.0 is recorded
   as a warning (`AlignmentDiagnostics.notes`) -- only rigid alignment is
   ever attempted; scale is never silently corrected.
2. **Coarse alignment** (`geometry/registration.py`):
   - `centroid_align`: identity rotation, centroid-to-centroid translation.
   - `pca_align`: aligns principal axes (via eigendecomposition of the
     centered covariance matrix), handling unknown relative orientation.
   - `method: auto` (default) runs both and keeps whichever gives lower
     RMSE against the target; `method: centroid`/`pca` force one;
     `method: none` skips straight to identity (coarse only, no ICP).
3. **Refinement**: point-to-point ICP (`geometry/registration.py::icp`),
   implemented directly with a `scipy.spatial.cKDTree` nearest-neighbor
   search and a per-iteration Kabsch (SVD) rigid-transform solve, so no
   Open3D dependency is required. Bounded by `max_iterations` and
   `convergence_tolerance` (config); correspondences beyond a
   distance threshold are rejected each iteration (robust to partial
   overlap). ICP is **only** run after coarse alignment -- never blindly
   on raw, potentially badly-misaligned input.
4. Both point sets are randomly subsampled to `max_points` (default
   20,000) before registration for performance on large scans; the
   final transform is still returned in full precision.

## Output

A `Transform` (`ACQUISITION -> FINAL_MESH`, 4x4 homogeneous matrix) plus
`AlignmentDiagnostics`: centroids, scales, coarse/refined method, fitness,
RMSE, iteration count, convergence flag, and a `confidence` in `[0, 1]`
derived from `fitness / (1 + rmse)`. Fitness below 0.3 adds an explicit
low-confidence warning rather than silently reporting a number nobody
reads. Everything here is written to
`output/transforms/alignment_matrix.json` and the quality report's
`registration` section.

## What needs real-data validation

- Real acquisition-vs-final-mesh coordinate relationships (scale, initial
  orientation offset) are unknown until tested against actual Innohealth
  scan pairs.
- The convergence/threshold defaults were tuned against the synthetic
  dataset's scale (~1 unit objects); they may need adjustment for
  real-world unit conventions (mm vs. m) -- nothing in the algorithm
  assumes a particular unit, but the ICP correspondence-distance threshold
  is scale-relative (half the target's bounding diagonal) so this should
  degrade gracefully, but is unverified on real data.
