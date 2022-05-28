# -*- coding: utf-8 -*-
"""Tests for the music_handler module"""

from typing import Type

import music21
import pytest
from bach_generator.src import music_handler

SIXTEENTH = "16th"
EIGHT = "8th"


@pytest.mark.usefixtures("midi_file")
def test_extract_notes_from_part(midi_file):
    score = music21.stream.Score()
    for note_name in midi_file.notes:
        note = music21.note.Note(nameWithOctave=note_name, type="16th")
        score.append(note)
    notes = music_handler.extract_notes_from_part(score)
    assert [note.nameWithOctave for note in notes] == midi_file.notes


@pytest.mark.usefixtures("midi_file")
@pytest.mark.parametrize(
    "handler_type", [music_handler.SimpleMusicHandler, music_handler.CopyMusicHandler]
)
def test_parse_file(midi_file, handler_type: Type[music_handler.BaseMusicHandler]):
    handler = handler_type()
    notes = handler.parse(midi_file.path)
    assert notes == midi_file.notes


def test_instantiate_fail():
    with pytest.raises(TypeError):
        music_handler.BaseMusicHandler()


@pytest.mark.usefixtures("midi_file")
@pytest.mark.parametrize(
    "handler_type, duration",
    [
        (music_handler.SimpleMusicHandler, SIXTEENTH),
        (music_handler.CopyMusicHandler, EIGHT),  # original duration
    ],
)
def test_regenerate_score(
    handler_type: Type[music_handler.BaseMusicHandler], duration, midi_file
):
    handler = handler_type()
    notes = handler.parse(midi_file.path)
    score = handler.generate_score(notes)
    assert isinstance(score, music21.stream.Score)
    notes = music_handler.extract_notes_from_part(score)
    assert all(note.duration.type == duration for note in notes)


@pytest.mark.parametrize("note_names", [[], ["A2"], ["A5", "A3", "B4"]])
def test_simple_score_generation(note_names):
    handler = music_handler.SimpleMusicHandler()
    score = handler.generate_score(note_names)
    notes = music_handler.extract_notes_from_part(score)
    assert len(notes) == len(note_names)
    assert all(note.nameWithOctave == name for note, name in zip(notes, note_names))


@pytest.mark.usefixtures("midi_file")
@pytest.mark.parametrize("note_names", [[], ["A2"], ["A5", "A3", "B4"]])
def test_copy_score_generation(note_names, midi_file):
    handler = music_handler.CopyMusicHandler()
    handler.parse(midi_file.path)
    parts = list(handler.generate_score(note_names))
    notes = music_handler.extract_notes_from_part(parts[0])
    assert len(notes) == len(midi_file.notes)
    assert all(note.nameWithOctave == name for note, name in zip(notes, note_names))


@pytest.mark.parametrize("note_names", [[], ["A2"], ["A5", "A3", "B4", "G4"]])
def test_copy_handler_without_part(note_names):
    handler = music_handler.CopyMusicHandler()
    with pytest.raises(TypeError):
        handler.generate_score(note_names)
