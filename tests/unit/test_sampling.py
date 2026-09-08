import numpy as np

from thermalmesh.models.thermal import ThermalImage
from thermalmesh.thermal.sampling import sample_bilinear, sample_nearest


def _linear_image():
    # temperature[y, x] = x, so bilinear interpolation is exact for any x.
    array = np.tile(np.arange(10, dtype=np.float64), (10, 1))
    return ThermalImage(image_id="t", temperature_array=array)


def test_bilinear_interpolates_exact_linear_field():
    image = _linear_image()
    pixels = np.array([[2.5, 5.0], [0.0, 0.0], [8.9, 3.0]])
    temps, valid = sample_bilinear(image, pixels)
    np.testing.assert_allclose(temps, [2.5, 0.0, 8.9], atol=1e-9)
    assert valid.all()


def test_bilinear_marks_out_of_bounds_invalid():
    image = _linear_image()
    pixels = np.array([[-1.0, 0.0], [20.0, 20.0]])
    temps, valid = sample_bilinear(image, pixels)
    assert not valid.any()


def test_bilinear_rejects_neighbor_with_invalid_pixel():
    array = np.ones((4, 4))
    mask = np.ones((4, 4), dtype=bool)
    mask[1, 1] = False
    image = ThermalImage(image_id="t", temperature_array=array, validity_mask=mask)
    temps, valid = sample_bilinear(image, np.array([[0.5, 0.5]]))
    assert not valid[0]


def test_nearest_sampling():
    image = _linear_image()
    temps, valid = sample_nearest(image, np.array([[3.3, 0.0]]))
    assert valid[0]
    assert temps[0] == 3.0
