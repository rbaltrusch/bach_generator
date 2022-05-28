# -*- coding: utf-8 -*-
"""Tests for the judge module"""

import math

import pytest
from bach_generator.src import judge


@pytest.mark.parametrize(
    "inputs, outputs, expected_result",
    [
        ([1, 0], [1, 0], 1),
        ([0, 1], [0, -1], -1),
        ([0, 1, 2, 3, 4, 5], [0, 1, 3, 5, 7, 9], 0.99),
    ],
)
def test_judge_rate(inputs, outputs, expected_result):
    judge_ = judge.Judge()
    rating = judge_.rate(encoded_inputs=inputs, encoded_outputs=outputs)
    assert math.isclose(rating, expected_result, rel_tol=0.01)


@pytest.mark.parametrize(
    "inputs, outputs",
    [([], []), ([1], [1]), ([1, 2], [1, 2, 3])],
)
def test_judge_fail_insufficient_data(inputs, outputs):
    """Fails due to insufficient data or mismatching length"""
    judge_ = judge.Judge()
    with pytest.raises(ValueError):
        judge_.rate(encoded_inputs=inputs, encoded_outputs=outputs)
