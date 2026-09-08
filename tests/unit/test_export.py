import numpy as np

from thermalmesh.export.csv import export_vertex_csv
from thermalmesh.export.json import export_json
from thermalmesh.export.numpy import export_array
from thermalmesh.models.mesh import MeshData


def test_export_array_round_trips(tmp_path):
    array = np.array([1.0, 2.0, np.nan])
    path = export_array(array, tmp_path / "out.npy")
    loaded = np.load(path)
    np.testing.assert_array_equal(loaded[:2], array[:2])
    assert np.isnan(loaded[2])


def test_export_json_handles_numpy_types(tmp_path):
    data = {"value": np.float64(1.5), "array": np.array([1, 2, 3])}
    path = export_json(data, tmp_path / "out.json")
    assert path.exists()
    import json

    loaded = json.loads(path.read_text())
    assert loaded["value"] == 1.5
    assert loaded["array"] == [1, 2, 3]


def test_export_vertex_csv(tmp_path):
    mesh = MeshData(vertices=np.eye(3), faces=np.array([[0, 1, 2]]))
    temps = np.array([10.0, np.nan, 30.0])
    confidences = np.array([0.9, 0.0, 0.8])
    counts = np.array([2, 0, 1])
    path = export_vertex_csv(mesh, temps, confidences, counts, tmp_path / "out.csv")

    import csv

    with path.open() as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["vertex_id", "x", "y", "z", "temperature", "confidence", "observation_count"]
    assert len(rows) == 4
    assert rows[2][4] == ""  # NaN temperature for the unobserved vertex
