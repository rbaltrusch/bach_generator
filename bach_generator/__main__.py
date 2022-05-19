# -*- coding: utf-8 -*-
"""Main entry point for the music generator"""

import logging
import random

from bach_generator import cli, runner
from bach_generator.src.manager import ModelManager


def run_simulation(args):
    """Runs the simulation with the specified command line arguments"""
    model_managers = [
        ModelManager(
            inputs=args.inputs,
            outputs=1,
            layers=args.layers,
            layer_size=args.layer_size,
        )
        for _ in range(args.models)
    ]

    runner_data = runner.RunnerData(
        generations=args.generations,
        weight_divergence=args.weight_divergence,
        selected_models_per_generation=args.select_models,
        clones_per_model_per_generation=args.clones,
        write_best_model_generation_interval=args.write_interval,
    )

    runner_ = runner.GeneticAlgorithmRunner()
    runner_.setup(input_file=args.filepath, output_directory=args.output_dir)
    runner_.run(model_managers, data=runner_data)


def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    parser = cli.construct_parser()
    args = parser.parse_args()
    cli.display_args(args)
    random.seed(args.seed)
    run_simulation(args)


main()
