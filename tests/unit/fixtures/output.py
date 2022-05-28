# -*- coding: utf-8 -*-
"""Output test fixtures"""

import os
from datetime import datetime

import pytest


@pytest.fixture
def mock_datetime():
    class MockDateTime:
        """Required to mock datetime inside output_handler module, as datetime is a built-in
        and cannot be mocked directly.
        """

        DIRECTORY = os.path.join("test_output_directory", "something")
        DATE = datetime(year=2012, month=12, day=21, hour=14, minute=15, second=1)
        DATE_DIRECTORY = "20121221_141501"
        EXPECTED_DIRECTORY = os.path.join(DIRECTORY, DATE_DIRECTORY)

        @classmethod
        def now(cls):
            return cls.DATE

    MockDateTime.datetime = MockDateTime
    return MockDateTime
