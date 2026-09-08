# Development & Real-Data Integration

## Running tests

```bash
pytest tests/unit          # fast
pytest tests/integration   # full synthetic pipeline run (few seconds)
pytest --cov=thermalmesh   # with coverage, if pytest-cov installed
```

## Assumptions made during development

These were necessary to build and validate the system before real
Innohealth data was available; each is isolated in configuration or
clearly marked in code/metadata rather than hard-coded silently:

1. Thermal data files are single-channel numeric arrays (CSV/whitespace
   text/`.npy`) named `<camera_id>.<ext>` or referenced explicitly per
   camera.
2. Camera metadata is a single JSON file listing all cameras.
3. Without provided intrinsics, a focal length is estimated from a
   configurable default FOV (`intrinsics_source="estimated_fallback"`).
4. Without a provided camera orientation, look-at initialization targets
   the final mesh's centroid.
5. Automatic pose estimation/refinement assumes the imaged object is
   thermally distinct from its background (Otsu-segmentable).
6. Units are not assumed (no forced Celsius conversion) unless explicit
   calibration config (`thermal/calibration.py`) is supplied.
7. Geometry alignment assumes the initial and final geometry are at
   comparable scale (rigid alignment only; scale mismatch is flagged, not
   corrected).

## What still needs validation against real Innohealth data

- [ ] Real PLY files (final + initial) load and preprocess correctly at
      production scale/vertex counts (performance, not just correctness).
- [ ] Real thermal export format matches the CSV/whitespace/`.npy` parser,
      or a new adapter is needed in `thermal/parser.py` +
      `io/thermal_loader.py`.
- [ ] Real camera intrinsics (or the fallback estimate's accuracy) are
      confirmed against the actual thermal camera hardware.
- [ ] Camera pose estimation/refinement accuracy on real (non-symmetric)
      objects with real thermal contrast -- the synthetic sphere test
      cannot validate this (see `docs/camera_model.md`).
- [ ] Geometry alignment (ICP) behavior on real acquisition-vs-final
      offsets, including whether coarse alignment (centroid/PCA) is
      sufficient or additional feature-based coarse registration
      (e.g. FPFH+RANSAC) is needed for badly-misaligned real scans.
- [ ] Occlusion analysis correctness on real, more complex (non-convex)
      geometry.
- [ ] UV unwrap quality (`xatlas`) on real mesh topology/complexity at
      production resolution.
- [ ] End-to-end temperature accuracy against any reference/expected
      Innohealth output, if available.

## Real-data workflow

1. Copy sample data into a local test directory (never commit real
   patient/subject data to the repository).
2. `thermalmesh validate --mesh ... --thermal ... --cameras ...`
3. `thermalmesh inspect <mesh.ply>` / `scripts/inspect_thermal.py <file>`
4. `thermalmesh align --mesh ... --initial-mesh ... ...` and inspect
   `output/transforms/alignment_matrix.json` + the registration section of
   the quality report.
5. `thermalmesh estimate-poses ...` and inspect
   `output/cameras/poses.json` confidences.
6. `thermalmesh project ...` and inspect per-camera coverage in the
   quality report before running all views.
7. Full `thermalmesh run ...`; inspect `quality_report.txt`, `model.glb`
   visually, and the numerical outputs.
8. If anything looks wrong, capture the specific input file(s) causing it
   as a new regression fixture under `tests/regression/` (subject to any
   confidentiality/licensing constraints on the data itself) and file it
   as a documented gap in this checklist.

## Adding a new thermal file adapter

```python
# thermal/parser.py
def parse_my_format_file(path: Path) -> np.ndarray:
    ...  # return a (height, width) float64 array

# io/thermal_loader.py: extend SUPPORTED_EXTENSIONS / _resolve_thermal_file
# and dispatch to the new parser based on file extension.
```

No other pipeline code should need to change -- `ThermalImage` and
everything downstream only ever sees the parsed `(H, W)` array.

## Adding a new blending strategy

```python
from thermalmesh.thermal.blending import BaseBlender, BlendResult

class MyBlender(BaseBlender):
    def blend(self, observations):
        ...
        return BlendResult(temperature=..., confidence=..., observation_count=..., source_image_ids=[...])
```

Wire it into `pipeline/stages.py::stage_map_temperature_to_geometry` behind
a new `blending.method` config value.
