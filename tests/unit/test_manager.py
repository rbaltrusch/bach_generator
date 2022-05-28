# -*- coding: utf-8 -*-
"""Tests for the manager module"""

import random
from typing import List

import pytest
from bach_generator.src import manager, model

# pylint: disable=protected-access


class MockModel:
    def __init__(self, inputs: int = 2):
        self.inputs = inputs
        self.jumbled_with = None

    def jumble(self, jumble_strategy, weight_divergence):
        self.jumbled_with = (jumble_strategy, weight_divergence)

    @staticmethod
    def compute(inputs: List[int]) -> float:
        return [sum(inputs) / len(inputs)]


class MockDecoder:
    @staticmethod
    def decode(inputs: List[float]) -> List[int]:
        return list(map(int, inputs))


class MockJudge:
    @staticmethod
    def rate(inputs: List[int], outputs: List[int]) -> float:
        return sum(inputs) / (sum(outputs) if sum(outputs) else 1)


class MockQuantizer:
    @staticmethod
    def quantize(inputs: List[float]) -> List[int]:
        return list(map(int, inputs))


@pytest.mark.parametrize(
    "inputs, outputs, layers, layer_size",
    [
        [0, 0, 0, 0],
        [5, 1, 1, 20],
        random.choices(list(range(20)), k=4),
    ],
)
def test_model_manager_init(inputs, outputs, layers, layer_size):
    manager_ = manager.ModelManager(inputs, outputs, layers, layer_size)
    assert manager_.model is not None
    assert len(manager_.model._layers) == layers + 2  # inputs and outputs extra
    assert len(manager_.model._layers[0].nodes) == inputs
    assert len(manager_.model._layers[-1].nodes) == outputs
    for layer in manager_.model._layers[1:-1]:
        assert len(layer.nodes) == layer_size


@pytest.mark.usefixtures("test_model")
def test_model_manager_construct_from_model(test_model):
    manager_ = manager.ModelManager.construct_with_model(model=test_model)
    assert manager_.model is test_model


@pytest.mark.parametrize(
    "inputs, expected_encoded_outputs",
    [
        ([], []),
        ([0], [0]),
        ([0, 1, 5, 3], [0, 0, 3, 4]),
    ],
)
def test_model_manager_run(inputs, expected_encoded_outputs):
    manager_ = manager.ModelManager.construct_with_model(model=MockModel())
    manager_.run_model(inputs=inputs, quantizer=MockQuantizer())
    assert manager_.encoded_outputs == expected_encoded_outputs


@pytest.mark.parametrize(
    "jumble_strategy, weight_divergence",
    [
        (model.jumble_by_factor_strategy, 0),
        (model.jumble_by_selection_strategy, -2),
    ],
)
def test_model_manager_clone(jumble_strategy, weight_divergence):
    manager_ = manager.ModelManager.construct_with_model(model=MockModel())
    manager_.clone(jumble_strategy, weight_divergence)


@pytest.mark.parametrize(
    "encoded_outputs, expected_decoded_outputs",
    [
        ([], []),
        ([0.1], [0]),
        ([0.7, 1.1, 4.6, -1.2], [0, 1, 4, -1]),
    ],
)
def test_model_manager_decode(encoded_outputs, expected_decoded_outputs):
    manager_ = manager.ModelManager(inputs=1, outputs=1, layers=1, layer_size=1)
    manager_.encoded_outputs = encoded_outputs
    manager_.decode_outputs(decoder=MockDecoder())
    assert manager_.decoded_outputs == expected_decoded_outputs


@pytest.mark.parametrize(
    "inputs, outputs, expected_rating",
    [
        ([], [], 0),
        ([1], [2], 0.5),
        ([1, 2, 3], [0, 5, -2], 2),
    ],
)
def test_model_manager_rating(inputs, outputs, expected_rating):
    manager_ = manager.ModelManager(inputs=1, outputs=1, layers=1, layer_size=1)
    manager_.encoded_outputs = outputs
    manager_.get_rated_by(judge=MockJudge(), encoded_inputs=inputs)
    assert manager_.rating == expected_rating
