# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 17:25:02 2021

@author: richa
"""

import random

class Model:
    def __init__(self, inputs: int, outputs: int):
        self.layers = [Layer(inputs)]
        self._outputs = outputs

    def add_layer(self, length):
        new_layer = Layer(length)
        self.layers[-1].connect(new_layer)
        self.layers.append(new_layer)

    def build(self):
        self.add_layer(self._outputs) #output layer
        for layer in self.layers:
            layer.build()

    def jumble(self, weight_divergence):
        for layer in self.layers:
            layer.jumble(weight_divergence)

    def compute(self, inputs):
        input_layer = self.layers[0]
        input_layer.set_values(inputs)
        input_layer.propagate()
        return self.layers[-1].values

class Layer:
    def __init__(self, length):
        self.nodes = [Node() for _ in range(length)]
        self._connected_layer = None

    def connect(self, layer):
        self._connected_layer = layer
        for foreign_node in layer.nodes:
            for own_node in self.nodes:
                own_node.connect(foreign_node)

    def build(self):
        for node in self.nodes:
            node.build()

    def jumble(self, weight_divergence):
        for node in self.nodes:
            node.jumble(weight_divergence)

    def set_values(self, values):
        try:
            iter(values)
        except TypeError:
            values = [values]

        for node, value in zip(self.nodes, values):
            node.add_value(value)

    def propagate(self):
        for node in self.nodes:
            node.propagate()
        if self._connected_layer:
            self._connected_layer.propagate()

    @property
    def values(self):
        return [node.value for node in self.nodes]

class Node:
    def __init__(self):
        self._weights = []
        self._connected_nodes = []
        self._value_buffer = []
        self.value = None

    def connect(self, node):
        self._connected_nodes.append(node)

    def build(self):
        self._weights = [random.randint(0, 100) / 100 for _ in range(len(self._connected_nodes))]

    def jumble(self, weight_divergence):
        self._weights = [weight * (1 + random.randint(-100, 100) / 100 * weight_divergence) for weight in self._weights]

    def propagate(self):
        self.value = self._compute_value()
        for weight, node in zip(self._weights, self._connected_nodes):
            node.add_value(self.value * weight)
        self._value_buffer = []

    def add_value(self, value):
        self._value_buffer.append(value)

    def _compute_value(self):
        return sum(self._value_buffer) / len(self._value_buffer) if self._value_buffer else 0
