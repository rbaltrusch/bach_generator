# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 17:34:59 2021

@author: richa
"""
# pylint: disable=too-few-public-methods
from typing import List

from scipy import stats


class Judge:
    """Judges a model manager"""

    @staticmethod
    def rate(encoded_inputs: List[int], encoded_outputs: List[int]) -> float:
        """Sets the manager rating to the correlation between the inputs and the outputs"""
        rating, _ = stats.pearsonr(encoded_inputs, encoded_outputs)
        return rating
