# -*- coding: utf-8 -*-
"""Tests for the runner module"""

import os
import shutil
from dataclasses import dataclass

import pytest
from bach_generator import runner
from bach_generator.src import manager, output_handler

# pylint: disable=protected-access

TEST_OUTPUT_DIRECTORY = "__test_directory__"


def setup():
    teardown()


def teardown():
    if os.path.isdir(TEST_OUTPUT_DIRECTORY):
        shutil.rmtree(TEST_OUTPUT_DIRECTORY)


@dataclass
class MockModel:
    inputs: int = 1

    @staticmethod
    def compute(inputs):
        return [sum(inputs)]

    @staticmethod
    def jumble(*_, **__):
        pass


@dataclass
class MockManager:
    rating: float = 0
    cloned: bool = False

    def clone(self, jumble_strategy, weight_divergence):
        return self.__class__(rating=self.rating, cloned=True)


def test_runner_data():
    """Smoke test"""
    runner.RunnerData()


@pytest.mark.parametrize(
    "model_managers, expected, amount",
    [
        ([], [], 0),
        ([], [], 1),
        (
            [MockManager(rating=0.1), MockManager(rating=0), MockManager(rating=1)],
            [MockManager(rating=1), MockManager(rating=0.1)],
            2,
        ),
    ],
)
def test_select_best_models(model_managers, expected, amount):
    models = runner._select_best_models(model_managers, amount)
    assert models == expected


@pytest.mark.parametrize(
    "model_managers, data, expected",
    [
        ([], runner.RunnerData(), []),
        (
            [MockManager(rating=0.1)],
            runner.RunnerData(clones_per_model_per_generation=2),
            [
                MockManager(rating=0.1),
                MockManager(rating=0.1, cloned=True),
                MockManager(rating=0.1, cloned=True),
            ],
        ),
    ],
)
def test_append_clones(model_managers, data, expected):
    runner._append_clones(model_managers=model_managers, data=data)
    assert model_managers == expected


@pytest.mark.usefixtures("midi_file", "mock_datetime")
def test_runner_setup(midi_file, monkeypatch, mock_datetime):
    monkeypatch.setattr(output_handler, "datetime", mock_datetime)

    runner_ = runner.GeneticAlgorithmRunner()
    runner_.setup(input_file=midi_file.path, output_directory=TEST_OUTPUT_DIRECTORY)

    output_dir = os.path.join(TEST_OUTPUT_DIRECTORY, mock_datetime.DATE_DIRECTORY)
    assert os.path.isdir(output_dir)
    assert os.path.isfile(os.path.join(output_dir, midi_file.name))
    assert runner_.quantizer._sorted_encoded_notes == midi_file.sorted_note_mapping


@pytest.mark.usefixtures("midi_file", "mock_datetime")
def test_runner_run(midi_file, monkeypatch, mock_datetime):
    monkeypatch.setattr(output_handler, "datetime", mock_datetime)

    runner_data = runner.RunnerData(
        generations=2,
        write_best_model_generation_interval=1,
        selected_models_per_generation=2,
        clones_per_model_per_generation=1,
        weight_divergence=0,
    )
    runner_ = runner.GeneticAlgorithmRunner()
    runner_.setup(input_file=midi_file.path, output_directory=TEST_OUTPUT_DIRECTORY)
    model_managers = runner_.run(
        model_managers=[manager.ModelManager.construct_with_model(MockModel(inputs=1))],
        data=runner_data,
    )

    assert len(model_managers) == 4
    assert all(manager_.rating == 1 for manager_ in model_managers)

    import glob

    print(glob.glob(f"{TEST_OUTPUT_DIRECTORY}/**/*", recursive=True))
    assert all(
        os.path.isfile(
            os.path.join(TEST_OUTPUT_DIRECTORY, mock_datetime.DATE_DIRECTORY, filename)
        )
        for filename in ["output_1_100.mid", "output_2_100.mid"]
    )


def test_runner_without_models():
    managers = runner.GeneticAlgorithmRunner().run(
        model_managers=[], data=runner.RunnerData()
    )
    assert managers == []
