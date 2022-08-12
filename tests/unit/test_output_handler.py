# -*- coding: utf-8 -*-
"""Tests for the output_handler module"""

import os
import shutil
from datetime import datetime

import music21
import pytest
from bach_generator.src import output_handler

# corresponding to mock datetime fixture
DIRECTORY = os.path.join("test_output_directory", "something")
DATE = datetime(year=2012, month=12, day=21, hour=14, minute=15, second=1)
EXPECTED_DIRECTORY = os.path.join(DIRECTORY, "20121221_141501")


def setup():
    teardown()


def teardown():
    for file in ["something.test", "a.txt", "bcd.json", "a.b"]:
        if os.path.isfile(file):
            os.unlink(file)

    if os.path.isdir(DIRECTORY):
        shutil.rmtree(DIRECTORY)


def make_empty_files(*filepaths):
    """Helper to make empty files for tests"""
    for filepath in filepaths:
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filepath, "w"):
            pass


@pytest.mark.usefixtures("mock_datetime")
def test_output_setup(monkeypatch, mock_datetime):
    monkeypatch.setattr(output_handler, "datetime", mock_datetime)
    output_handler_ = output_handler.OutputHandler()
    assert not os.path.isdir(mock_datetime.EXPECTED_DIRECTORY)
    output_handler_.setup_output_directory(directory=mock_datetime.DIRECTORY)
    assert os.path.isdir(mock_datetime.EXPECTED_DIRECTORY)


@pytest.mark.usefixtures("mock_datetime")
@pytest.mark.parametrize(
    "filepaths",
    [
        [],
        ["something.test"],
        ["a.txt", "bcd.json"],
        [os.path.join(DIRECTORY, "something", "a.b")],
    ],
)
def test_copy_files(filepaths, monkeypatch, mock_datetime):
    monkeypatch.setattr(output_handler, "datetime", mock_datetime)
    output_handler_ = output_handler.OutputHandler()
    output_handler_.setup_output_directory(directory=mock_datetime.DIRECTORY)
    assert not any(
        os.path.isfile(os.path.join(mock_datetime.EXPECTED_DIRECTORY, file))
        for file in filepaths
    )
    make_empty_files(*filepaths)
    output_handler_.copy_files(*filepaths)
    assert all(
        os.path.isfile(
            os.path.join(mock_datetime.EXPECTED_DIRECTORY, os.path.basename(file))
        )
        for file in filepaths
    )


@pytest.mark.usefixtures("mock_datetime")
@pytest.mark.parametrize(
    "filepaths, directory, exception",
    [
        (["something.test"], "", shutil.SameFileError),
        (["a.txt", "bcd.json"], "", shutil.SameFileError),
        (
            [os.path.join(DIRECTORY, "something", "a.b")],
            EXPECTED_DIRECTORY,
            FileNotFoundError,
        ),
    ],
)
def test_copy_fail(filepaths, directory, exception):
    """Tests fail when output directory is not setup before copying"""
    print(filepaths)
    make_empty_files(*filepaths)
    assert all(os.path.isfile(file) for file in filepaths)

    output_handler_ = output_handler.OutputHandler()
    output_handler_.directory = (
        directory  # need to set manually because we arent calling setup
    )
    with pytest.raises(exception):
        output_handler_.copy_files(*filepaths)


@pytest.mark.usefixtures("mock_datetime")
def test_score_write(monkeypatch, mock_datetime):
    monkeypatch.setattr(output_handler, "datetime", mock_datetime)
    score = music21.stream.Score()
    output_handler_ = output_handler.OutputHandler()
    output_handler_.setup_output_directory(directory=mock_datetime.DIRECTORY)

    filename = "test.mid"
    assert not os.path.isfile(os.path.join(mock_datetime.EXPECTED_DIRECTORY, filename))
    output_handler_.write(score, filename)
    assert os.path.isfile(os.path.join(mock_datetime.EXPECTED_DIRECTORY, filename))
