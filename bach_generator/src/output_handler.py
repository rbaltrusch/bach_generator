# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 18:04:19 2021

@author: richa
"""
import datetime
import os
import shutil

import music21


class OutputHandler:
    """Handles setup of output directory and output files"""

    def __init__(self):
        self.directory: str = ""

    def setup_output_directory(self, directory: str) -> None:
        """Sets up a timestamped subdirectory in the passed directory"""
        date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.directory = os.path.join(directory, date)
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

    def copy_files(self, *filepaths: str) -> None:
        """Copies all filepaths to the output handler directory"""
        for filepath in filepaths:
            destination_path = os.path.join(self.directory, os.path.basename(filepath))
            shutil.copyfile(filepath, destination_path)

    def write(self, score: music21.stream.Score, filename: str) -> None:
        """Writes the specified score to the output directory under the specified filename"""
        score.write("midi", os.path.join(self.directory, filename))
