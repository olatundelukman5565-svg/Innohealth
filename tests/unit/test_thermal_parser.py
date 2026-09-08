import numpy as np
import pytest

from thermalmesh.pipeline.errors import InvalidThermalDataError
from thermalmesh.thermal.parser import parse_thermal_file


def test_parse_csv_basic(tmp_path):
    path = tmp_path / "thermal.csv"
    path.write_text("1.0,2.0,3.0\n4.0,5.0,6.0\n")
    array = parse_thermal_file(path)
    np.testing.assert_allclose(array, [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])


def test_parse_csv_invalid_markers_become_nan(tmp_path):
    path = tmp_path / "thermal.csv"
    path.write_text("1.0,N/A,3.0\n4.0,5.0,-\n")
    array = parse_thermal_file(path)
    assert np.isnan(array[0, 1])
    assert np.isnan(array[1, 2])
    assert array[0, 0] == 1.0


def test_parse_rejects_ragged_rows(tmp_path):
    path = tmp_path / "thermal.csv"
    path.write_text("1.0,2.0,3.0\n4.0,5.0\n")
    with pytest.raises(InvalidThermalDataError):
        parse_thermal_file(path)


def test_parse_rejects_non_numeric(tmp_path):
    path = tmp_path / "thermal.csv"
    path.write_text("1.0,abc,3.0\n")
    with pytest.raises(InvalidThermalDataError):
        parse_thermal_file(path)


def test_parse_missing_file_raises(tmp_path):
    with pytest.raises(InvalidThermalDataError):
        parse_thermal_file(tmp_path / "missing.csv")


def test_parse_npy(tmp_path):
    array = np.array([[1.0, 2.0], [3.0, 4.0]])
    path = tmp_path / "thermal.npy"
    np.save(path, array)
    loaded = parse_thermal_file(path)
    np.testing.assert_allclose(loaded, array)
