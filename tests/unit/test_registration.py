import numpy as np

from thermalmesh.geometry.alignment import align_point_sets
from thermalmesh.geometry.registration import icp, kabsch


def _random_points(n=200, seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(n, 3))


def test_kabsch_recovers_exact_rigid_transform():
    source = _random_points()
    true_rotation = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], dtype=np.float64)
    true_translation = np.array([1.0, -2.0, 0.5])
    target = (true_rotation @ source.T).T + true_translation

    rotation, translation = kabsch(source, target)
    np.testing.assert_allclose(rotation, true_rotation, atol=1e-8)
    np.testing.assert_allclose(translation, true_translation, atol=1e-8)


def test_icp_converges_on_known_transform():
    source = _random_points(300, seed=1)
    true_rotation = np.array([[np.cos(0.2), -np.sin(0.2), 0], [np.sin(0.2), np.cos(0.2), 0], [0, 0, 1]])
    true_translation = np.array([0.3, 0.1, -0.2])
    target = (true_rotation @ source.T).T + true_translation

    result = icp(source, target, max_iterations=50)
    assert result.fitness > 0.95
    assert result.rmse < 1e-3


def test_align_point_sets_recovers_known_alignment():
    source = _random_points(500, seed=2)
    true_rotation = np.array([[np.cos(0.3), 0, np.sin(0.3)], [0, 1, 0], [-np.sin(0.3), 0, np.cos(0.3)]])
    true_translation = np.array([0.5, -0.1, 0.2])
    target = (true_rotation @ source.T).T + true_translation

    transform, diagnostics = align_point_sets(source, target, method="auto")
    recovered = transform.apply(source)
    error = np.linalg.norm(recovered - target, axis=1).mean()
    assert error < 0.05
    assert diagnostics.confidence > 0.5
