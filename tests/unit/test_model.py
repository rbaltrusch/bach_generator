# -*- coding: utf-8 -*-
"""Tests for the model module"""

import copy
import itertools
import math
import os
import random
import statistics
from collections import namedtuple
from itertools import zip_longest

import pytest
from bach_generator.src import model

# pylint: disable=protected-access


INPUTS_OUTPUTS_TEST_ARGS = [
    (0, 0),
    (-1, -1),
    (0, 1),
    (1, 1),
    (3, 5),
    (15, 12),
]

TEST_JSON_FILENAME = "__testfile__.json"


def setup():
    teardown()


def teardown():
    if os.path.isfile(TEST_JSON_FILENAME):
        os.unlink(TEST_JSON_FILENAME)


@pytest.mark.parametrize("inputs, outputs", INPUTS_OUTPUTS_TEST_ARGS)
def test_model_init(inputs, outputs):
    model_ = model.Model(inputs=inputs, outputs=outputs)
    assert len(model_._layers) == 1
    assert len(model_._layers[0].nodes) == max(inputs, 0)
    assert model_.outputs == outputs
    assert model_.inputs == inputs


@pytest.mark.usefixtures("test_model")
def test_model_serialization(test_model: model.Model):
    serialized = test_model.serialize()
    model_ = model.Model.construct_from_list(layers=serialized)
    assert test_model == model_


@pytest.mark.usefixtures("test_model")
def test_empty_model_deserialization(test_model: model.Model):
    copied_model = copy.deepcopy(test_model)
    test_model.deserialize(layers=[])
    assert test_model == copied_model


@pytest.mark.parametrize("inputs, outputs", INPUTS_OUTPUTS_TEST_ARGS)
def test_add_layer(inputs, outputs):
    model_ = model.Model(inputs=inputs, outputs=outputs)
    layer = model_._layers[-1]

    assert layer._connected_layer is None
    assert len(model_._layers) == 1

    length = 20
    model_.add_layer(length=length)

    new_layer = model_._layers[-1]
    assert len(model_._layers) == 2
    assert layer._connected_layer is new_layer

    assert len(new_layer.nodes) == length
    assert all(node._connected_nodes == new_layer.nodes for node in layer.nodes)


@pytest.mark.parametrize("inputs, outputs", INPUTS_OUTPUTS_TEST_ARGS)
def test_model_build(inputs, outputs):
    model_ = model.Model(inputs=inputs, outputs=outputs)

    assert len(model_._layers) == 1
    assert not any(node.weights for node in model_._layers[0].nodes)

    model_.build()

    assert len(model_._layers) == 2  # input and output layers
    assert all(len(node.weights) == max(0, outputs) for node in model_._layers[0].nodes)
    assert all(len(node.weights) == 0 for node in model_._layers[1].nodes)


def test_random_model_build():
    inputs, outputs, layer_size = random.choices(list(range(0, 30)), k=3)
    layers = random.randint(0, 5)
    print(inputs, outputs, layers, layer_size)

    model_ = model.Model(inputs, outputs)
    for _ in range(layers):
        model_.add_layer(layer_size)

    assert len(model_._layers) == layers + 1  # outputs extra

    model_.build()

    assert len(model_._layers) == layers + 2  #  outputs extra
    assert all(len(layer.nodes) == layer_size for layer in model_._layers[1:-1])
    expected_lengths = [layer_size] * layers + [outputs, 0]
    for length, layer in zip(expected_lengths, model_._layers):
        print(length, layer, [len(node.weights) == length for node in layer.nodes])
        assert all(len(node.weights) == length for node in layer.nodes)
        assert all(
            all(isinstance(weight, float) for weight in node.weights)
            for node in layer.nodes
        )
        assert all(
            all(0 <= weight <= 1 for weight in node.weights) for node in layer.nodes
        )


def _offset_expected_value_function(weight_divergence, random_start_value):
    return (
        (weight_divergence * (weight_divergence + random_start_value) / 100 + 1)
        * random_start_value
        / 100
    )


def _selection_expected_value_function(weight_divergence, random_start_value):
    return (random_start_value + weight_divergence) / 100


Strategy = namedtuple("Strategy", "function, value_function")

offset_strategy_pair = Strategy(
    model.jumble_by_factor_strategy,
    _offset_expected_value_function,
)

selection_strategy_pair = Strategy(
    model.jumble_by_selection_strategy,
    _selection_expected_value_function,
)


@pytest.mark.parametrize(
    "weight_divergence, random_start_value, jumble_strategy, expected_nodes_with_value_percent",
    [
        (0, 0, offset_strategy_pair, 1),
        (0.5, 0.3, offset_strategy_pair, 1),
        (1, 0.4, offset_strategy_pair, 1),
        (0.2, 0.5, offset_strategy_pair, 1),
        (0, 0.1, selection_strategy_pair, 1),
        (0.5, 0.2, selection_strategy_pair, 0.5),
        (1, 0.3, selection_strategy_pair, 1),
        (0.2, 0.5, selection_strategy_pair, 0.2),
    ],
)
def test_model_offset_jumble(
    weight_divergence,
    random_start_value,
    jumble_strategy: Strategy,
    expected_nodes_with_value_percent,
    monkeypatch,
):
    def get_model_weights(model__: model.Model):
        return [
            weight
            for layer in model__._layers
            for node in layer.nodes
            for weight in node.weights
        ]

    inputs, outputs = (10, 10)
    monkeypatch.setattr(random, "randint", lambda *_: random_start_value)
    model_ = model.Model(inputs=inputs, outputs=outputs)
    model_.build()

    expected_initial_sum = inputs * random_start_value / 100
    assert math.isclose(sum(get_model_weights(model_)), expected_initial_sum, rel_tol=1)

    # jumble values and check new weights are different
    monkeypatch.setattr(
        random, "randint", lambda *_: random_start_value + weight_divergence
    )
    model_.jumble(jumble_strategy.function, weight_divergence)
    assert math.isclose(
        sum(get_model_weights(model_)),
        expected_initial_sum + weight_divergence * inputs / 100,
        rel_tol=1,
    )

    # check expected percentage of weights with new value matches
    expected_value = jumble_strategy.value_function(
        weight_divergence, random_start_value
    )
    print(expected_value)
    weights = get_model_weights(model_)
    expected_weights = [
        weight
        for weight in weights
        if math.isclose(weight, expected_value, rel_tol=0.03)
    ]
    assert math.isclose(
        len(expected_weights) / len(weights),
        expected_nodes_with_value_percent,
        rel_tol=0.05,
    )


@pytest.mark.parametrize(
    "input_data, inputs, outputs, random_weight",
    [
        ([], 5, 3, 0.2),
        ([1], -1, 1, 0.5),
        ([2, 5, 3], 0, 1, 0.2),
        ([0, 1, 2, 3, -1], 3, 0, 0.1),
        ([3, 0, 9, 3, -1], 54, 1, 0),
        ([1, 2, 3, 45, -1], 30, 2, 0.3),
        ([0, 1, 6, 32, -1, 5, 3, 2, 1], 14, 3, 1),
    ],
)
def test_model_compute(input_data, inputs, outputs, random_weight, monkeypatch):
    monkeypatch.setattr(random, "randint", lambda *_: random_weight)
    model_ = model.Model(inputs=inputs, outputs=outputs)
    model_.build()
    output_values = model_.compute(input_data)

    expected_value = (
        statistics.mean(
            [x for x, _ in zip_longest(input_data, range(inputs), fillvalue=0)]
        )
        * random_weight
        / 100
        if len(input_data) and inputs > 0
        else 0
    )

    assert len(output_values) == outputs
    assert all(
        math.isclose(output_value, expected_value, rel_tol=0.01)
        for output_value in output_values
    )


@pytest.mark.parametrize("length", random.choices(list(range(-5, 20)), k=10))
def test_layer_serialize(length):
    layer = model.Layer(length)
    list_ = layer.serialize()
    assert len(list_) == len(layer.nodes)

    new_layer = model.Layer(length + 10)
    assert len(new_layer.nodes) != len(layer.nodes)

    new_layer.deserialize(list_)
    assert len(new_layer.nodes) == len(layer.nodes)


@pytest.mark.parametrize(
    "lengths",
    itertools.product(
        random.choices(list(range(-5, 20)), k=3),
        random.choices(list(range(-5, 20)), k=3),
    ),
)
def test_layer_connect(lengths):
    layer, new_layer = [model.Layer(len_) for len_ in lengths]

    assert layer._connected_layer is None
    assert not any(node._connected_nodes for node in layer.nodes)

    layer.connect(new_layer)

    assert layer._connected_layer is new_layer
    assert all(
        len(node._connected_nodes) == len(new_layer.nodes) for node in layer.nodes
    )


@pytest.mark.parametrize("length", random.choices(list(range(-5, 20)), k=5))
def test_layer_build_before_connect(length):
    layer = model.Layer(length)
    assert not any(node._connected_nodes for node in layer.nodes)
    layer.build()
    assert not any(node._connected_nodes for node in layer.nodes)


@pytest.mark.parametrize(
    "lengths",
    itertools.product(
        random.choices(list(range(-5, 20)), k=3),
        random.choices(list(range(-5, 20)), k=3),
    ),
)
def test_layer_build_after_connect(lengths):
    layer, new_layer = [model.Layer(len_) for len_ in lengths]
    layer.connect(new_layer)

    assert not any(node.weights for node in layer.nodes)
    layer.build()
    assert all(len(node.weights) == len(new_layer.nodes) for node in layer.nodes)


@pytest.mark.parametrize("length", random.choices(list(range(10, 20)), k=5))
def test_layer_jumble(length, monkeypatch):
    layer = model.Layer(length)
    layer.connect(model.Layer(length=1))

    monkeypatch.setattr(random, "randint", lambda *_: 100)
    layer.build()
    assert all(weight == 1 for node in layer.nodes for weight in node.weights)

    monkeypatch.setattr(random, "randint", lambda *_: 200)
    layer.jumble(
        jumble_strategy=model.jumble_by_selection_strategy, weight_divergence=1
    )
    assert all(weight == 2 for node in layer.nodes for weight in node.weights)


@pytest.mark.parametrize(
    "values",
    [
        [],
        [1],
        [0, 5, 2, -1],
    ],
)
def test_layer_set_values(values):
    layer = model.Layer(length=5)
    layer.set_values(values)
    for value, node in zip_longest(values, layer.nodes, fillvalue=None):
        assert node._value_buffer == ([value] if value is not None else [])


@pytest.mark.parametrize("values", [[], [1], [0, 1, 2, 3]])
def test_layer_propagate(values, monkeypatch):
    # setup custom layer
    layer = model.Layer(length=3)
    node1 = model.Node()
    node2 = model.Node()
    for node in layer.nodes[:2]:
        node.connect(node1)
    layer.nodes[2].connect(node2)

    monkeypatch.setattr(random, "randint", lambda *_: 100)
    assert all(weight == 1 for node in layer.nodes for weight in node.weights)
    layer.build()

    layer.set_values(values)
    layer.propagate()

    assert node1._value_buffer == [
        val for val, _ in zip_longest(values[:2], range(2), fillvalue=0)
    ]
    assert node2._value_buffer == (values[2:3] if len(values) > 2 else [0])
    assert layer.values == [
        x for x, _ in zip_longest(values[:3], layer.nodes, fillvalue=0)
    ]


@pytest.mark.parametrize("weights", [[], [1], [-1, 0.1, 0.5]])
def test_node_serialize(weights):
    node = model.Node()
    node.weights = weights
    serialized_weights = node.serialize()
    assert weights == serialized_weights

    node.deserialize(serialized_weights)
    assert node.weights == weights


def test_node_connect():
    node1 = model.Node()
    node2 = model.Node()
    node1.connect(node2)
    assert node1._connected_nodes == [node2]
    assert node2._connected_nodes == []

    node1.connect(node2)
    assert node1._connected_nodes == [node2, node2]


@pytest.mark.parametrize("length", [0, 1, 5])
def test_node_build(length):
    node = model.Node()
    for _ in range(length):
        node.connect(model.Node())

    assert len(node._connected_nodes) == length

    node.build()
    assert len(node.weights) == length
    assert all(0 <= weight <= 1 for weight in node.weights)


@pytest.mark.parametrize("weight_divergence", [0, -1, -25, 3])
def test_node_custom_jumble_strategy(weight_divergence):
    def jumble(node: model.Node, weight_divergence: float) -> None:
        node.weights = [weight - weight_divergence for weight in node.weights]

    weights = [5, 3, 0, -1, 15]
    node = model.Node()
    node.weights = weights[:]
    node.jumble(jumble_strategy=jumble, weight_divergence=weight_divergence)
    assert node.weights == [weight - weight_divergence for weight in weights]


@pytest.mark.parametrize("weight_divergence", [0.1, 0.5, -1])
def test_node_jumble_by_offsets(weight_divergence, monkeypatch):
    weights = [0, 1, 2, 3]
    node = model.Node()
    node.weights = weights

    monkeypatch.setattr(random, "randint", lambda *_: 100)
    node.jumble(
        jumble_strategy=model.jumble_by_factor_strategy,
        weight_divergence=weight_divergence,
    )
    assert node.weights == [weight * (1 + weight_divergence) for weight in weights]


@pytest.mark.parametrize("weight_divergence", [0, 0.1, 0.5, -1])
def test_node_jumble_by_selection(weight_divergence, monkeypatch):
    weights = [0] * 10
    node = model.Node()
    node.weights = weights[:]

    monkeypatch.setattr(random, "randint", lambda *_: 50)
    print(node.weights, weights)
    node.jumble(
        jumble_strategy=model.jumble_by_selection_strategy,
        weight_divergence=weight_divergence,
    )
    print(node.weights, weights)

    expected_value = 50 / 100
    expected_changed_weights = int(abs(weight_divergence) * len(node.weights))
    assert (
        len([x for x in node.weights if math.isclose(x, expected_value, rel_tol=0.01)])
        == expected_changed_weights
    )


@pytest.mark.parametrize(
    "jumble_strategy",
    [model.jumble_by_factor_strategy, model.jumble_by_selection_strategy],
)
def test_node_jumble_zero_weight_divergence(jumble_strategy):
    weights = random.sample(list(range(10)), k=5)
    node = model.Node()
    node.weights = weights

    node.jumble(jumble_strategy=jumble_strategy, weight_divergence=0)
    assert node.weights == weights


@pytest.mark.parametrize(
    "jumble_strategy",
    [model.jumble_by_factor_strategy, model.jumble_by_selection_strategy],
)
def test_node_jumble_without_weights(jumble_strategy):
    node = model.Node()
    assert node.weights == []
    node.jumble(jumble_strategy=jumble_strategy, weight_divergence=1)
    assert node.weights == []


def test_node_propagate_without_value_buffer():
    node = model.Node()

    assert node._value_buffer == []
    assert node.value is None
    node.propagate()
    assert node._value_buffer == []
    assert node.value == 0


@pytest.mark.parametrize("values", [[], [0], [-1], [0, 2, 3], [0, 1232, -4452, 0.1]])
def test_node_propagate_without_connection(values):
    node = model.Node()
    node._value_buffer = values
    node.propagate()
    assert math.isclose(
        node.value, statistics.mean(values) if values else 0, rel_tol=0.01
    )


@pytest.mark.parametrize(
    "values", [[], [0], [-1], [0, 2, 5], [0, 4, 6, 2, 343, 0.1], [-0.1, 0.2, 0.5]]
)
def test_node_propagate(values):
    node1 = model.Node()
    node1._value_buffer = values
    node2 = model.Node()
    node1.connect(node2)
    weight = 0.1
    node1.weights = [weight]

    node1.propagate()
    average = statistics.mean(values) if values else 0
    assert math.isclose(node1.value, average, rel_tol=0.01)
    assert node2.value is None
    assert len(node2._value_buffer) == 1
    assert math.isclose(node2._value_buffer[0], average * weight)


def test_node_add_value():
    node = model.Node()
    node.add_value(1)
    assert node._value_buffer == [1]


def test_node_add_value_with_connection():
    node1 = model.Node()
    node2 = model.Node()
    node1.connect(node2)

    node1.add_value(0.2)
    assert node1._value_buffer == [0.2]
    assert node2._value_buffer == []


def test_load_save_model():
    model_ = model.Model(inputs=1, outputs=1)
    model_.add_layer(length=1)
    model_.build()
    model.save_models(models=[model_], filepath=TEST_JSON_FILENAME)

    assert os.path.isfile(TEST_JSON_FILENAME)
    deserialized_models = model.load_models(filepath=TEST_JSON_FILENAME)
    assert deserialized_models == [model_]
