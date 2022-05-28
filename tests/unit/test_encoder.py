# -*- coding: utf-8 -*-
"""Tests for the encoder module"""

import random
import string

import pytest
from bach_generator.src import encoder

# pylint: disable=protected-access


@pytest.mark.parametrize(
    "note_names, expected_encoded_outputs",
    [
        ([], []),
        (["a"], [0]),
        (["a", "b", "a", "c"], [0, 1, 0, 2]),
    ],
)
def test_encoder_encode_notes(note_names, expected_encoded_outputs):
    encoder_ = encoder.Encoder()
    encoded_outputs = encoder_.encode(note_names=note_names)
    assert encoded_outputs == expected_encoded_outputs


@pytest.mark.parametrize(
    "note_names, expected_num_mapping, expected_name_mapping",
    [
        ([], {}, {}),
        (["a"], {0: "a"}, {"a": 0}),
        (["AA", "B3", "AA"], {0: "AA", 1: "B3"}, {"AA": 0, "B3": 1}),
    ],
)
def test_encoder_mappings(note_names, expected_num_mapping, expected_name_mapping):
    encoder_ = encoder.Encoder()
    encoder_.encode(note_names=note_names)
    assert encoder_._name_to_num_mapping == expected_name_mapping
    assert encoder_._num_to_name_mapping == expected_num_mapping


@pytest.mark.parametrize(
    "num_mapping, encoded_notes, expected_note_names",
    [
        ({}, [], []),
        ({123: "B", 4: "23"}, [123, 123, 4, 123, 2], ["B", "B", "23", "B", ""]),
    ],
)
def test_encoder_decode(num_mapping, encoded_notes, expected_note_names):
    encoder_ = encoder.Encoder()
    encoder_._num_to_name_mapping = num_mapping
    note_names = encoder_.decode(encoded_notes=encoded_notes)
    assert note_names == expected_note_names


def _get_random_encode_decode_test_parameters(length=5):
    note_names = random.sample(string.ascii_uppercase, k=length)
    encoded_notes = random.choices(list(range(length)), k=length)
    expected_output_note_names = [note_names[i] for i in encoded_notes]
    return note_names, encoded_notes, expected_output_note_names


@pytest.mark.parametrize(
    "note_names, encoded_notes, expected_output_note_names",
    [
        (
            ["A3", "B3", "C3"],
            [0, 1, 0, 1, 2, 1, 0],
            ["A3", "B3", "A3", "B3", "C3", "B3", "A3"],
        ),
        _get_random_encode_decode_test_parameters(length=0),
        _get_random_encode_decode_test_parameters(length=1),
        _get_random_encode_decode_test_parameters(length=5),
        _get_random_encode_decode_test_parameters(length=24),
    ],
)
def test_encoder_encode_decode(note_names, encoded_notes, expected_output_note_names):
    encoder_ = encoder.Encoder()
    encoder_.encode(note_names)
    decoded_notes = encoder_.decode(encoded_notes)
    assert decoded_notes == expected_output_note_names


@pytest.mark.parametrize(
    "note_names", [["a", "b", "c"], [], random.sample(string.ascii_uppercase, k=20)]
)
def test_encoder_encode_decode_same_data(note_names):
    encoder_ = encoder.Encoder()
    assert encoder_.decode(encoder_.encode(note_names)) == note_names


@pytest.mark.parametrize(
    "encoded_notes, expected_sorted_notes",
    [([], []), ([0], [0]), ([0, 1, 1], [1, 0]), ([0, 1, 0, 2, 2, 1, 2], [2, 0, 1])],
)
def test_quantizer_setup(encoded_notes, expected_sorted_notes):
    quantizer_ = encoder.Quantizer()
    quantizer_.setup(encoded_notes)
    assert quantizer_._sorted_encoded_notes == tuple(expected_sorted_notes)


@pytest.mark.parametrize(
    "encoded_notes, unquantized_inputs, expected_quantized_outputs",
    [
        ([0], [], []),
        ([], [0], []),
        ([0], [0.54], [0]),
        ([0, 1, 1], [0.23, 0.53], [1, 0]),
        (
            [0, 1, 5, 3, 7, 2, 2, 3, 1],
            [0.0, 0.15, 0.75, 0.232, 0.754, 0.96, 0.43, 0.264],
            [2, 1, 3, 1, 3, 0, 5, 7],
        ),
    ],
)
def test_quantizer_quantize(
    encoded_notes, unquantized_inputs, expected_quantized_outputs
):
    quantizer_ = encoder.Quantizer()
    quantizer_.setup(encoded_notes)
    quantized_outputs = quantizer_.quantize(outputs=unquantized_inputs)
    assert quantized_outputs == expected_quantized_outputs
