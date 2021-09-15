# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 17:37:23 2021

@author: richa
"""

import collections
from typing import List
from dataclasses import dataclass

@dataclass
class Encoder:
    """Parses, encodes and decodes notes"""

    _num_to_name_mapping: dict = None
    _name_to_num_mapping: dict = None

    def encode(self, note_names: List[str]) -> List[int]:
        """Encodes a list of note names into a list of integers and remembers the mapping"""
        unique_note_names = set(note_names)
        self._num_to_name_mapping = dict(enumerate(unique_note_names))
        self._name_to_num_mapping = {v: i for i, v in enumerate(unique_note_names)}
        encoded_notes = [self._name_to_num_mapping.get(note_name) for note_name in note_names]
        return encoded_notes

    def decode(self, encoded_notes: List[int]) -> List[str]:
        """Decodes the list of encoded into a list of note names (str), e.g. F#5"""
        return [self._num_to_name_mapping.get(note) for note in encoded_notes]

@dataclass
class Quantizer:
    """Quantizes notes """

    _sorted_encoded_notes: list = None

    def setup(self, encoded_notes: List[int]):
        """Sets up sorted list of encoded input notes based on frequency"""
        self._sorted_encoded_notes, _ = zip(*collections.Counter(encoded_notes).most_common())

    def quantize(self, outputs: List[float]) -> List[int]:
        """Quantizes a list of floats into a list of ints based on its frequency
        relative to the sorted_encoded_notes set using the setup method.
        """
        #map outputs to values between 0 and the total number of possible encodings
        min_ = min(outputs)
        grounded_outputs = [output - min_ for output in outputs]
        scaling = max(grounded_outputs) / len(self._sorted_encoded_notes)
        mapped_outputs = [round(output / scaling) for output in grounded_outputs]

        #match values from input to output by frequency of appearance
        sorted_outputs, _ = zip(*collections.Counter(mapped_outputs).most_common())
        output_mapping = dict(zip(sorted_outputs, self._sorted_encoded_notes))
        quantized_outputs = [output_mapping.get(note) for note in mapped_outputs]
        return quantized_outputs
