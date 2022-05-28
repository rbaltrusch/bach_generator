# -*- coding: utf-8 -*-
"""Main entry point for the music generator"""

import logging
import os
import random
from typing import List

from bach_generator import cli, runner
from bach_generator.src import manager, model, music_handler


def construct_model_managers(args) -> List[manager.ModelManager]:
    """Constructs model managers or loads them from file"""
    if args.load_filepath:
        model_managers = [
            manager.ModelManager.construct_with_model(model_)
            for model_ in model.load_models(args.load_filepath)
        ]
        return (
            model_managers
            if args.load_best is None
            else model_managers[: args.load_best]
        )

    return [
        manager.ModelManager(
            inputs=args.inputs,
            outputs=1,
            layers=args.layers,
            layer_size=args.layer_size,
        )
        for _ in range(args.models)
    ]


def get_weight_jumble_strategy(args) -> model.JumbleStrategy:
    """Returns the jumble strategy chosen from the cli args"""
    strategies = {
        "factor": model.jumble_by_factor_strategy,
        "selection": model.jumble_by_selection_strategy,
    }
    return strategies.get(args.weight_jumble_strategy)


def get_music_handler(args) -> music_handler.BaseMusicHandler:
    """Returns the music handler chosen from the cli args"""
    handlers = {
        "simple": music_handler.SimpleMusicHandler,
        "copy": music_handler.CopyMusicHandler,
    }
    return handlers.get(args.rhythm_handler)()


def run_simulation(args):
    """Runs the simulation with the specified command line arguments"""
    model_managers = construct_model_managers(args)
    runner_data = runner.RunnerData(
        generations=args.generations,
        weight_divergence=args.weight_divergence,
        selected_models_per_generation=args.select_models,
        clones_per_model_per_generation=args.clones,
        write_best_model_generation_interval=args.write_interval,
        weight_jumble_strategy=get_weight_jumble_strategy(args),
    )

    runner_ = runner.GeneticAlgorithmRunner(music_handler=get_music_handler(args))
    runner_.setup(input_file=args.filepath, output_directory=args.output_dir)
    evolved_model_managers = runner_.run(model_managers, data=runner_data)

    if args.save:
        filepath = os.path.join(runner_.output_handler.directory, "models.json")
        models = [model_manager.model for model_manager in evolved_model_managers]
        model.save_models(models, filepath)


def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    parser = cli.construct_parser()
    args = parser.parse_args()
    cli.display_args(args)
    random.seed(args.seed)
    run_simulation(args)


main()
