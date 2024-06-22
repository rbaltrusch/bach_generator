# -*- coding: utf-8 -*-
"""Runner module"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from functools import partial
from multiprocessing import Pool
from typing import Callable, List

from bach_generator.src.encoder import Encoder, Quantizer
from bach_generator.src.judge import Judge
from bach_generator.src.manager import ModelManager
from bach_generator.src.model import JumbleStrategy, jumble_by_factor_strategy
from bach_generator.src.music_handler import CopyMusicHandler
from bach_generator.src.output_handler import OutputHandler


@dataclass
class RunnerData:
    """Encapsulates data required for a Runner.run function"""

    generations: int = 10
    weight_divergence: float = 0.05
    selected_models_per_generation: int = 20
    clones_per_model_per_generation: int = 5
    write_best_model_generation_interval: int = 10
    weight_jumble_strategy: JumbleStrategy = jumble_by_factor_strategy


def _select_best_models(
    model_managers: List[ModelManager], amount: int
) -> List[ModelManager]:
    return sorted(model_managers, key=lambda x: x.rating, reverse=True)[:amount]


def _append_clones(model_managers: List[ModelManager], data: RunnerData) -> None:
    clones = [
        manager.clone(data.weight_jumble_strategy, data.weight_divergence)
        for _ in range(data.clones_per_model_per_generation)
        for manager in model_managers
    ]
    model_managers.extend(clones)


def run_models(
    runner: GeneticAlgorithmRunner, model_managers: List[ModelManager]
) -> List[ModelManager]:
    """Runs models in sequence using the specified runner"""
    for model_manager in model_managers:
        run_model(runner.encoded_inputs, runner.quantizer, runner.judge, model_manager)
    return model_managers


def run_models_in_parallel(
    runner: GeneticAlgorithmRunner, model_managers: List[ModelManager]
) -> List[ModelManager]:
    """Runs models in parallel using the specified runner"""
    function_ = partial(
        run_model, runner.encoded_inputs, runner.quantizer, runner.judge
    )
    with Pool() as pool:
        model_managers = pool.map(function_, model_managers, chunksize=20)
    return model_managers


def run_model(
    encoded_inputs: List[int],
    quantizer: Quantizer,
    judge: Judge,
    model_manager: ModelManager,
) -> ModelManager:
    """Runs and rates the specified model"""
    model_manager.run_model(encoded_inputs, quantizer)
    model_manager.get_rated_by(judge, encoded_inputs)
    return model_manager


@dataclass
class GeneticAlgorithmRunner:
    """Runs the music generation by running a number of ModelManager objects
    through an input file over a number of generations.
    """

    judge: Judge = field(default_factory=Judge)
    output_handler: OutputHandler = field(default_factory=OutputHandler)
    music_handler: CopyMusicHandler = field(default_factory=CopyMusicHandler)
    encoder: Encoder = field(default_factory=Encoder)
    quantizer: Quantizer = field(default_factory=Quantizer)
    run_function: Callable[
        [GeneticAlgorithmRunner, List[ModelManager]], List[ModelManager]
    ] = run_models

    def __post_init__(self):
        self.encoded_inputs: List[int] = []

    def setup(self, input_file: str, output_directory: str) -> None:
        """Sets up the output directory and parses the input file"""
        self._setup_output_directory(input_file, output_directory)
        self._parse_input_file(input_file)

    def _setup_output_directory(self, input_file: str, output_directory: str) -> None:
        self.output_handler.setup_output_directory(output_directory)
        self.output_handler.copy_files(input_file)

    def _parse_input_file(self, input_file: str):
        note_names = self.music_handler.parse(input_file)
        self.encoded_inputs = self.encoder.encode(note_names)
        self.quantizer.setup(self.encoded_inputs)

    def run(
        self, model_managers: List[ModelManager], data: RunnerData
    ) -> List[ModelManager]:
        """Runs a genetic algorithm with the models using the input RunnerData.
        Returns a sorted list of evolved models once finished.
        """
        if not model_managers:
            return []

        for i in range(1, data.generations + 1):
            start_time = time.time()

            model_managers = self.run_function(self, model_managers)
            model_managers = _select_best_models(
                model_managers, amount=data.selected_models_per_generation
            )
            _append_clones(model_managers, data)

            best_manager = model_managers[0]
            logging.info(
                "Generation %i (steptime=%s). Amount of models: %s. Best manager rating: %s%%",
                i,
                round(time.time() - start_time, 2),
                len(model_managers),
                round(best_manager.rating * 100, 2),
            )
            if i % data.write_best_model_generation_interval == 0:
                self._write_model_output(model_manager=best_manager, generation=i)
        return model_managers

    def _write_model_output(self, model_manager: ModelManager, generation: int) -> None:
        rounded_rating = int(round(model_manager.rating, 2) * 100)
        model_manager.decode_outputs(self.encoder)
        score = self.music_handler.generate_score(model_manager.decoded_outputs)
        self.output_handler.write(score, f"output_{generation}_{rounded_rating}.mid")
