"""Colour picker for Figure"""

from dataclasses import dataclass, field
from typing import List

HexColour = str


@dataclass
class CyclicColourPicker:
    """Cyclically picks from the list of available colours."""

    colours: List[HexColour] = field(default_factory=list)
    index: int = 0

    @property
    def colour(self) -> str:
        """Returns a hex colour picked from the colour list"""
        colour = self.colours[self.index]
        self.index = (self.index + 1) % len(self.colours)
        return colour
