# -*- coding: utf-8 -*-
"""Model test fixtures"""

import pytest
from bach_generator.src import model


@pytest.fixture
def test_model() -> model.Model:
    model_ = model.Model(inputs=3, outputs=1)
    model_.add_layer(length=3)
    model_.add_layer(length=3)
    model_.build()
    return model_
