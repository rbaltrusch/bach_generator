# -*- coding: utf-8 -*-
"""Main entry point for the music generator"""

import logging
import os
import random
import sys
from typing import Callable, List, Type

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


def get_layer_type(args) -> Type:
    """Returns the layer type chosen from the cli args"""
    layer_types = {
        "object": model.Layer,
        "matrix": model.MatrixLayer,
    }
    return layer_types.get(args.layer_type)


def get_run_function(args) -> Callable:
    """Returns the run function chosen from cli args"""
    if args.parallel:
        return runner.run_models_in_parallel
    return runner.run_models


def setup_simulation(args):
    """Sets up the simulation using the cli args"""
    random.seed(args.seed)
    model.Model.layer_class = get_layer_type(args)
    model_managers = construct_model_managers(args)
    runner_data = runner.RunnerData(
        generations=args.generations,
        weight_divergence=args.weight_divergence,
        selected_models_per_generation=args.select_models,
        clones_per_model_per_generation=args.clones,
        write_best_model_generation_interval=args.write_interval,
        weight_jumble_strategy=get_weight_jumble_strategy(args),
    )

    runner_ = runner.GeneticAlgorithmRunner(
        music_handler=get_music_handler(args), run_function=get_run_function(args)
    )
    runner_.setup(input_file=args.filepath, output_directory=args.output_dir)
    return runner_, runner_data, model_managers


def run_simulation(args):
    """Runs the simulation with the specified command line arguments"""
    runner_, runner_data, model_managers = setup_simulation(args)
    try:
        model_managers = runner_.run(model_managers, data=runner_data)
    except KeyboardInterrupt:
        logging.info("Interrupted model run")

    if args.save:
        filepath = os.path.join(runner_.output_handler.directory, "models.json")
        models = [model_manager.model for model_manager in model_managers]
        model.save_models(models, filepath)
        logging.info("Saved models to file")


def run_gui(app, init):
    """Runs the graphical interface"""
    init.init()
    app.data["setup_function"] = setup_simulation
    app.pack_all()

    try:
        app.mainloop()
    except Exception as exc:
        if app.destroyed:
            return
        raise exc


class StreamHandler(logging.StreamHandler):
    """Logging stream handler for gui mode"""

    def __init__(self, gui_app):
        super().__init__()
        self.app = gui_app

    def emit(self, record: logging.LogRecord) -> None:
        if not self.app.destroyed:
            self.app.data["message"].set("Status: " + record.getMessage())
        super().emit(record)


def main():
    """Main function"""
    gui_mode = len(sys.argv) == 1
    if gui_mode:
        from bach_generator.gui import (  # pylint: disable=import-outside-toplevel
            app,
            init,
        )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        handlers=[StreamHandler(app if gui_mode else None)],
    )
    parser = cli.construct_parser()
    if gui_mode:
        run_gui(app, init)
        return
    args = parser.parse_args()
    cli.display_args(args)
    run_simulation(args)


if __name__ == "__main__":
    main()
