# -*- coding: utf-8 -*-
"""Music test fixtures"""

import os
from dataclasses import dataclass
from typing import List, Tuple

import pytest


@dataclass
class MidiFile:
    path: str
    notes: List[str]
    sorted_note_mapping: Tuple[int]

    @property
    def name(self) -> str:
        return os.path.basename(self.path)


@pytest.fixture
def midi_file() -> MidiFile:
    return MidiFile(
        path=os.path.join(os.path.dirname(__file__), "..", "..", "data", "test.mid"),
        notes=[
            "C5",
            "D5",
            "E5",
            "D5",
            "C5",
            "G4",
            "E4",
            "C4",
            "C5",
            "B4",
            "G4",
            "D4",
            "B3",
            "D4",
            "G4",
            "A4",
            "B4",
            "G4",
            "F4",
            "E4",
            "F4",
            "G4",
            "E4",
            "D4",
            "C4",
            "E4",
            "G4",
            "B4",
            "C5",
        ],
        sorted_note_mapping=(3, 0, 4, 6, 7, 1, 5, 10, 2, 8, 9),
    )
