# Thermal Mapping

## Principle: raw numbers are authoritative

`ThermalImage.raw_values` is always the untouched parsed array;
`temperature_array` is what calibration (if any) produced, defaulting to
an unmodified copy. Colorization (`thermal/normalization.py`) produces a
separate uint8 BGR image purely for visualization/PNG export and is never
read back into any numerical computation.

## Per-image projection (independent, no early blending)

`thermal/projection.py::project_thermal_image` handles one
`(camera, pose, thermal_image)` triple at a time:

1. `thermal/occlusion.py::compute_visibility` classifies every mesh vertex
   as `VISIBLE`, `OCCLUDED`, `OUTSIDE_IMAGE`, `BACK_FACING`, or `INVALID`:
   - back-face cull via surface-normal-vs-view-direction dot product;
   - in-bounds check via the projected pixel coordinates;
   - true occlusion via ray casting against the mesh itself
     (`trimesh`'s ray-triangle intersector, offset along the normal to
     avoid self-intersection) -- a vertex is occluded if something else on
     the mesh is struck first along the ray toward the camera.
2. For every `VISIBLE` vertex, `thermal/sampling.py::sample_temperature`
   bilinearly interpolates the thermal array at the projected sub-pixel
   location (nearest-neighbor also available). A sample is only valid if
   *all four* surrounding pixels are valid -- invalid pixels never leak
   into a neighboring valid sample.
3. A `TemperatureObservation` is created per (image, vertex) pair with its
   own `camera_distance`, `viewing_angle`, and `confidence` (currently
   `cos(angle) * 1/(1+distance)`, clipped to `[0, 1]`).

This produces one `ProjectionResult` + observation list per image, kept
fully separate (`thermal/observations.py::ObservationStore`) until
blending.

## Mapping to geometry

`thermal/mapping.py`:

- `map_vertex_to_face_temperature`: face value = mean of its three
  vertices' blended temperatures (NaN if any vertex is unobserved).
- `map_mesh_to_point_cloud_temperature`: nearest-vertex transfer onto the
  optional initial point cloud, after applying the inverse alignment
  transform so both are in the same (acquisition) coordinate system.

## Blending

`thermal/blending.py`:

- `BaseBlender` is the strategy interface; `WeightedTemperatureBlender` is
  the configurable default: `T = sum(w_i * T_i) / sum(w_i)` where each of
  distance/angle/confidence weighting is independently toggleable
  (`blending.*_weight` in config). Occluded/invalid observations are
  excluded via `TemperatureObservation.is_usable()`.
- `blend_all` applies a blender across every geometry element in an
  `ObservationStore`, returning per-element temperature, confidence, and
  observation count arrays (unobserved elements are `NaN`, never
  fabricated).
- New strategies (uncertainty-aware, temporal, physics-based) plug in by
  subclassing `BaseBlender` -- no caller changes required.

## UV-space thermal layers

`uv/thermal_projection.py::rasterize_vertex_values_to_uv` barycentrically
rasterizes any per-vertex scalar array into UV-space, used both:

- per-image (`uv/texture_generation.py::build_thermal_layer`): one
  `temperature`/`valid_mask`/`confidence`/`occlusion_mask` layer per
  camera, kept as separate files (`thermal_layers/thermal_<id>.npy` etc.)
  and never merged permanently;
- once for the final blended vertex temperatures
  (`build_blended_texture`), which is what gets colorized into the GLB/GLTF
  visualization texture.
