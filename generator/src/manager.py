# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 18:12:32 2021

@author: richa
"""

import os
import copy
import collections
from dataclasses import dataclass

import music21
from scipy import stats

from src.model import Model

@dataclass
class Manager:
    num_to_name_mapping: dict = None
    name_to_num_mapping: dict = None
    encoded_notes: list = None
    model: Model = None
    quantized_outputs: list = None
    _inputs: int = 0
    _output_counter: collections.Counter = None
    input_counter: collections.Counter = None

    def parse(self, filename):
        stream = music21.converter.parse(filename)
        # part = stream.flattenParts()
        _, part = music21.instrument.partitionByInstrument(stream)
        notes = [note for note in part.notes if isinstance(note, music21.note.Note)]
        note_names = [note.nameWithOctave for note in notes]

        unique_note_names = set(note_names)
        self.num_to_name_mapping = {i: v for i, v in enumerate(unique_note_names)}
        self.name_to_num_mapping = {v: i for i, v in enumerate(unique_note_names)}
        self.encoded_notes = [self.name_to_num_mapping.get(note.nameWithOctave) for note in notes]
        self.input_counter = collections.Counter(self.encoded_notes)
    
    def setup_model(self, inputs, outputs, layers, size):
        self._inputs = inputs
        self.model = Model(inputs, outputs)
        for _ in range(layers):
            self.model.add_layer(size)
        self.model.build()

    def clone(self, weight_divergence):
        copied_manager = copy.deepcopy(self)
        copied_manager.model.jumble(weight_divergence)
        return copied_manager

    def copy_data_from(self, manager):
        self.num_to_name_mapping = manager.num_to_name_mapping
        self.name_to_num_mapping = manager.name_to_num_mapping
        self.encoded_notes = manager.encoded_notes
        self.input_counter = manager.input_counter
    
    def run_model(self):
        output_notes = []
        inputs_ = collections.deque(maxlen=self._inputs)
        for note in self.encoded_notes:
            inputs_.append(note)
            outputs = self.model.compute(inputs_)
            output_notes.extend(outputs)

        self.quantized_outputs = self._quantize(output_notes)
        self.rating, _ = stats.pearsonr(self.encoded_notes, self.quantized_outputs) #correlation

    def write_output_score(self, filename, directory):
        score = music21.stream.Score()
        for quantized_note in self.quantized_outputs:
            note_name = self.num_to_name_mapping.get(quantized_note)
            note = music21.note.Note(nameWithOctave=note_name, type='16th')
            score.append(note)
        score.write('midi', os.path.join(directory, filename))

    def _quantize(self, outputs):
        # max_output = max(*outputs, 1)
        # mapping_len = len(self.num_to_name_mapping)
        # return [round(output / max_output * mapping_len) for output in outputs]

        max_ = max(outputs)
        length = len(self.input_counter)
        mapped_notes = [round(note / max_ * length) for note in outputs]
        self._output_counter = collections.Counter(mapped_notes)
        self._output_mapping = {output_note: input_note for (output_note, _), (input_note, _) in
                                zip(self._output_counter.most_common(), self.input_counter.most_common())}
        return [self._output_mapping.get(note) for note in mapped_notes]

        