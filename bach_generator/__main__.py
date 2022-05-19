# -*- coding: utf-8 -*-
"""Main entry point for the music generator"""

import logging

from bach_generator import runner
from bach_generator.src.manager import ModelManager


def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    input_file = "data/988-v02.mid"

    model_managers = [
        ModelManager(inputs=10, outputs=1, layers=3, layer_size=20) for _ in range(10)
    ]
    runner_data = runner.RunnerData()
    runner_ = runner.GeneticAlgorithmRunner()
    runner_.setup(input_file, output_directory="outputs")
    runner_.run(model_managers, data=runner_data)


main()
