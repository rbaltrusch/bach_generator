# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 18:29:08 2021

@author: richa
"""
from abc import ABC, abstractmethod
from typing import List

import music21


def extract_notes_from_part(part: music21.stream.Part) -> List[music21.note.Note]:
    """Extracts all note objects from the specified part"""
    return [note for note in part.notes if isinstance(note, music21.note.Note)]


class BaseMusicHandler(ABC):
    """Base music handler class. Template: already implements the parse method"""

    def __init__(self):
        self.part: music21.stream.Part = None
        self.notes: List[music21.note.Note] = None

    def parse(self, filename) -> List[int]:
        """Parses the specified filename and returns a list of note names"""
        stream = music21.converter.parse(filename)
        parts = list(music21.instrument.partitionByInstrument(stream))
        self.part = parts[1] if len(parts) > 1 else parts[0]
        self.notes = extract_notes_from_part(self.part)
        return [note.nameWithOctave for note in self.notes]

    @abstractmethod
    def generate_score(self, note_names: List[str]) -> music21.stream.Score:
        """Generates music21.stream.Score from a list of note names"""


class SimpleMusicHandler(BaseMusicHandler):
    """Music handler that writes a stream of notes as 16th to a midi file"""

    def generate_score(self, note_names: List[str]) -> music21.stream.Score:
        """Generates a new music21.stream.Score from a list of note names.
        All notes are 16th notes.
        """
        score = music21.stream.Score()
        for note_name in note_names:
            note = music21.note.Note(nameWithOctave=note_name, type="16th")
            score.append(note)
        return score


class CopyMusicHandler(BaseMusicHandler):
    """Music handler that copies the rhythms from the input midi and applies it
    to the score generated with the output notes.
    """

    def generate_score(self, note_names: List[str]) -> music21.stream.Score:
        """Returns the score that was read in using the parse method, with all
        notes replaced by the specified note names.
        """
        for note, note_name in zip(self.notes, note_names):
            note.nameWithOctave = note_name
        score = music21.stream.Score()
        score.append(self.part)
        return score
