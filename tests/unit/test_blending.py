import numpy as np

from thermalmesh.models.projection import TemperatureObservation, Visibility
from thermalmesh.thermal.blending import WeightedTemperatureBlender


def _obs(temp, confidence=1.0, distance=1.0, angle=0.0, visibility=Visibility.VISIBLE):
    return TemperatureObservation(
        image_id="img", geometry_id=0, temperature=temp, pixel_x=0, pixel_y=0,
        visibility=visibility, camera_distance=distance, viewing_angle=angle, confidence=confidence,
    )


def test_blend_equal_weights_averages():
    blender = WeightedTemperatureBlender(use_distance_weight=False, use_angle_weight=False, use_confidence_weight=False)
    observations = [_obs(10.0), _obs(20.0)]
    result = blender.blend(observations)
    assert result.temperature == 15.0
    assert result.observation_count == 2


def test_blend_confidence_weighting_favors_high_confidence():
    blender = WeightedTemperatureBlender(use_distance_weight=False, use_angle_weight=False, use_confidence_weight=True)
    observations = [_obs(10.0, confidence=0.05), _obs(20.0, confidence=0.95)]
    result = blender.blend(observations)
    assert result.temperature > 15.0


def test_blend_ignores_occluded_and_invalid_observations():
    blender = WeightedTemperatureBlender()
    observations = [
        _obs(100.0, visibility=Visibility.OCCLUDED),
        _obs(20.0, visibility=Visibility.VISIBLE),
    ]
    result = blender.blend(observations)
    assert result.temperature == 20.0
    assert result.observation_count == 1


def test_blend_empty_returns_none():
    blender = WeightedTemperatureBlender()
    result = blender.blend([])
    assert result.temperature is None
    assert result.confidence == 0.0
