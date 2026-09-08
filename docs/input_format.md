# Input Formats

## Mesh (final reconstruction, required)

Any PLY file `trimesh` can load as a triangle mesh (ASCII or binary).
Loaded via `io/mesh_loader.py::load_mesh`. Vertex normals, colors are
preserved if present; normals are (re)computed during preprocessing
regardless (`geometry/preprocessing.py`).

Validation (`io/validators.py`): non-empty, finite vertex coordinates,
face indices in range.

## Initial acquisition geometry (optional)

A PLY mesh or point cloud. Loaded via `io/mesh_loader.py::load_point_cloud`
(falls back to loading as a mesh and taking its vertices if the file isn't
a pure point cloud). Used only for geometry alignment
(`geometry/alignment.py`) -- if absent, the final mesh is treated as
already being in world space and alignment is skipped.

## Thermal data (required, one file per camera)

Supported: `.csv`, `.txt`/`.dat` (whitespace-delimited), `.npy`. Each file
is a single 2D numeric array shaped `(image_height, image_width)` --
**not** a multi-channel image. Values are raw/calibrated temperature, not
color.

- Invalid-value markers (`NaN`, `N/A`, `-`, empty string by default,
  configurable) become `NaN` in place -- rows/columns are never dropped, so
  array shape always matches the declared image dimensions.
- Delimiter and header-row handling are configurable
  (`thermal.delimiter`, `thermal.has_header` in the YAML config).
- File resolution (`io/thermal_loader.py`): either an explicit
  `"thermal_file"` entry on the camera JSON, or a file named
  `<camera_id>.<ext>` inside `--thermal`.

If Innohealth's real thermal export is a different format (e.g. a
proprietary binary), add a new parser function to `thermal/parser.py` and
extend `io/thermal_loader.py`'s resolution logic -- do not change anything
downstream of the parsed `(H, W)` array.

## Camera metadata (required)

JSON, see `examples/sample_camera.json`:

```json
{
  "cameras": [
    {
      "camera_id": "cam_01",
      "image_width": 640,
      "image_height": 480,
      "intrinsics": {"fx": 525.0, "fy": 525.0, "cx": 320.0, "cy": 240.0},
      "distortion": [0.0, 0.0, 0.0, 0.0, 0.0],
      "position": [1.2, 0.0, 0.5],
      "rotation": [[...], [...], [...]],
      "thermal_file": "thermal_01.csv"
    }
  ]
}
```

- `intrinsics` optional: if absent, a fallback focal length is estimated
  from a configurable default FOV and the camera is marked
  `intrinsics_source="estimated_fallback"` -- never silently treated as
  measured.
- `position`/`rotation` optional and independent: position-only is the
  expected Innohealth scenario (camera location known, orientation not
  necessarily aligned to the final mesh) and drives look-at initialization
  + automatic pose estimation/refinement. Neither given raises
  `PoseEstimationError` rather than fabricating a camera.
- `distortion`: standard OpenCV 4/5/8-coefficient vector; omitted means
  zero distortion.

## Validation

`thermalmesh validate --mesh ... [--thermal ...] [--cameras ...]` (or
`io/validators.py` directly) runs every check above and prints a report
before any processing begins; errors block the run, warnings do not.
