# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 18:29:08 2021

@author: richa
"""

from typing import List, Protocol
from dataclasses import dataclass

import music21

@dataclass
class BaseMusicHandler(Protocol):

    part: music21.stream.Part = None
    notes: list = None

    def parse(self, filename) -> List[int]:
        """Parses the specified filename and returns a list of note names"""
        stream = music21.converter.parse(filename)
        _, self.part, *_ = music21.instrument.partitionByInstrument(stream)
        self.notes = [note for note in self.part.notes if isinstance(note, music21.note.Note)]
        return [note.nameWithOctave for note in self.notes]

    def generate_score(self, note_names: List[str]) -> music21.stream.Score:
        """Generates music21.stream.Score from a list of note names"""

class SimpleMusicHandler(BaseMusicHandler):
    def generate_score(self, note_names: List[str]) -> music21.stream.Score:
        """Generates a new music21.stream.Score from a list of note names.
        All notes are 16th notes.
        """
        score = music21.stream.Score()
        for note_name in note_names:
            note = music21.note.Note(nameWithOctave=note_name, type='16th')
            score.append(note)
        return score

class CopyMusicHandler(BaseMusicHandler):
    def generate_score(self, note_names: List[str]):
        """Returns the score that was read in using the parse method, with all
        notes replaced by the specified note names.
        """
        for note, note_name in zip(self.notes, note_names):
            note.nameWithOctave = note_name
        score = music21.stream.Score()
        score.append(self.part)
        return score
