# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 18:12:32 2021

@author: richa
"""
import collections
import copy
from dataclasses import dataclass, field
from typing import Deque, List, Optional

from src.encoder import Encoder, Quantizer
from src.judge import Judge
from src.model import Model


@dataclass
class ModelManager:
    """Encodes contents of an input file, sets up and runs the model and decodes its contents"""

    rating: float = 0.0
    encoded_outputs: List[int] = field(default_factory=list)
    decoded_outputs: List[str] = field(default_factory=list)

    def __init__(self, inputs, outputs, layers, layer_size):
        self.model = Model(inputs, outputs)
        for _ in range(layers):
            self.model.add_layer(layer_size)
        self.model.build()

    def run_model(self, inputs: List[int], quantizer: Quantizer):
        """Runs the model with the specified inputs and stores the outputs"""
        encoded_outputs: List[float] = []
        input_deque: Deque[int] = collections.deque(maxlen=self.model.inputs)
        for input_ in inputs:
            input_deque.append(input_)
            model_outputs = self.model.compute(input_deque)
            encoded_outputs.extend(model_outputs)
        self.encoded_outputs = quantizer.quantize(encoded_outputs)

    def clone(self, weight_divergence: float):
        """Clones itself and jumbles up the weights in the model copy
        with the specified weight divergence.
        """
        copied_manager = copy.deepcopy(self)
        copied_manager.model.jumble(weight_divergence)
        return copied_manager

    def decode_outputs(self, decoder: Encoder):
        """Decodes its encoded_outputs using the passed decoder and stores the results"""
        self.decoded_outputs = decoder.decode(self.encoded_outputs)

    def get_rated_by(self, judge: Judge, encoded_inputs: List[int]):
        """Sets self.rating to the rating returned by the judge on encoded inputs and outputs"""
        self.rating = judge.rate(encoded_inputs, self.encoded_outputs)
