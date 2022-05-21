# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 17:25:02 2021

@author: richa
"""

from __future__ import annotations

import json
import random
from typing import List


class Model:
    """Neural network model comprised of layers."""

    def __init__(self, inputs: int, outputs: int):
        self.inputs = inputs
        self._layers = [Layer(inputs)]
        self._outputs = outputs

    @classmethod
    def construct_from_list(cls, layers: List[List[List[float]]]) -> Model:
        """Constructs a new Model object by deserializing the specified layers"""
        model = Model(inputs=0, outputs=0)
        model.deserialize(layers)
        return model

    def serialize(self) -> List[List[List[float]]]:
        """Serializes the model"""
        return [layer.serialize() for layer in self._layers]

    def deserialize(self, layers: List[List[List[float]]]) -> None:
        """Deserializes the passed layers"""
        if not layers:
            return

        self._layers = []
        for layer_list in layers:
            layer = Layer(length=0)
            layer.deserialize(layer_list)
            self._layers.append(layer)

        self.inputs = len(layers[0])
        self._outputs = len(layers[-1])

        for previous_layer, layer in zip(self._layers, self._layers[1:]):
            previous_layer.connect(layer)

    def add_layer(self, length: int):
        """Instantiates a new Layer of the specified length, connects it to the last layer
        and appends it to the list of layers.
        """
        new_layer = Layer(length)
        self._layers[-1].connect(new_layer)
        self._layers.append(new_layer)

    def build(self):
        """Adds an output layer, then builds all layers"""
        self.add_layer(self._outputs)  # output layer
        for layer in self._layers:
            layer.build()

    def jumble(self, weight_divergence: float):
        """Jumbles all layers with the weight_divergence specified"""
        for layer in self._layers:
            layer.jumble(weight_divergence)

    def compute(self, inputs: List[int]) -> List[float]:
        """Sets values of input layer to the specified inputs, then propagates to other layers.
        Returns values of the output layer"""
        input_layer = self._layers[0]
        input_layer.set_values(inputs)
        input_layer.propagate()
        return self._layers[-1].values


class Layer:
    """Neural network layer that manages nodes in that layer and interfaces with other layers."""

    def __init__(self, length: int):
        self.nodes = [Node() for _ in range(length)]
        self._connected_layer = None

    def serialize(self) -> List[List[float]]:
        """Serialises the layer"""
        return [node.serialize() for node in self.nodes]

    def deserialize(self, nodes: List[List[float]]) -> None:
        """Deserializes the passed nodes"""
        self.nodes = []
        for weights in nodes:
            node = Node()
            node.deserialize(weights)
            self.nodes.append(node)

    def connect(self, layer: Layer):
        """Connects specified layer to itself, then connects all nodes of the specified layer
        with all its nodes.
        """
        self._connected_layer = layer
        for foreign_node in layer.nodes:
            for own_node in self.nodes:
                own_node.connect(foreign_node)

    def build(self):
        """Builds all nodes"""
        for node in self.nodes:
            node.build()

    def jumble(self, weight_divergence: float):
        """Jumbles all nodes with the weight_divergence specified"""
        for node in self.nodes:
            node.jumble(weight_divergence)

    def set_values(self, values: List[int]):
        """Sets value of nodes to specified values"""
        try:
            iter(values)  # type: ignore
        except TypeError:
            values: List[int] = [values]  # type: ignore

        for node, value in zip(self.nodes, values):
            node.add_value(value)

    def propagate(self):
        """Propagates all own nodes, then propagates connected layer"""
        for node in self.nodes:
            node.propagate()
        if self._connected_layer:
            self._connected_layer.propagate()

    @property
    def values(self) -> List[float]:
        """Getter for values, returns list of node.value of all nodes"""
        return [node.value for node in self.nodes]


class Node:
    """Neural network node. Can be connected to other nodes.
    Contains a set of weights for each connected node.
    """

    def __init__(self):
        self._weights: List[float] = []
        self._connected_nodes: List[Node] = []
        self._value_buffer: List[float] = []
        self.value: float = None

    def serialize(self) -> List[float]:
        """Serialises the node"""
        return self._weights

    def deserialize(self, weights: List[float]) -> None:
        """Deserializes the node with the specified weights"""
        self._weights = weights

    def connect(self, node):
        """Appends node to connected_nodes list"""
        self._connected_nodes.append(node)

    def build(self):
        """Builds a random weight for each connected node"""
        self._weights = [
            random.randint(0, 100) / 100 for _ in range(len(self._connected_nodes))
        ]

    def jumble(self, weight_divergence: float):
        """Modifies all existing weights by + - the passed percentage weight_divergence."""
        self._weights = [
            weight * (1 + random.randint(-100, 100) / 100 * weight_divergence)
            for weight in self._weights
        ]

    def propagate(self):
        """Computes node value, then adds weighted node value to all connected nodes"""
        self.value = self._compute_value()
        self._value_buffer = []

        for weight, node in zip(self._weights, self._connected_nodes):
            node.add_value(self.value * weight)

    def add_value(self, value):
        """Appends a value to the value buffer"""
        self._value_buffer.append(value)

    def _compute_value(self) -> float:
        """Returns the average value in the value buffer. Returns 0 if value buffer is empty"""
        return (
            sum(self._value_buffer) / len(self._value_buffer)
            if self._value_buffer
            else 0
        )


def save_models(models: List[Model], filepath: str):
    """Saves the models to the specified filepath as json"""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump([model.serialize() for model in models], file, indent=4)


def load_models(filepath: str) -> List[Model]:
    """Loads the models from the specified json filepath"""
    with open(filepath, "r", encoding="utf-8") as file:
        contents = json.load(file)
    return [Model.construct_from_list(list_) for list_ in contents]
