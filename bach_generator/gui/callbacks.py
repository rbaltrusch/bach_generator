# -*- coding: utf-8 -*-
"""Gui callbacks"""

import logging
from tkinter.filedialog import askopenfilename

from bach_generator.gui import app, args, config, figure, root

MAX_LENGTH = 120


def set_gui_config_defaults(*_):
    """Sets the gui configuration default values"""


def set_error(*_):
    """Callback for error StringVar write trace"""
    background = config.ERR if app.data["error"].get() else config.BG2
    app["config"]["file_button"].config(bg=background)


def choose_file():
    """Callback for select file button"""
    filepath = askopenfilename(
        filetypes=[("Audio files (*.mid, *.midi)", ("*.mid", "*.midi"))]
    )
    if filepath:
        app.data["filepath"].set(filepath)
        app.data["error"].set("")


def get_cli_command() -> str:
    """Constructs the current cli command with all configuration arguments"""
    command = f"python -m bach_generator {app.data['filepath'].get()}"

    actions = [
        action
        for action in args.get_parser_actions()
        if action.option_strings and app.data[action.dest].get() != action.default
    ]
    if actions:
        command += " " + " ".join(
            f"{action.option_strings[0]} {app.data[action.dest].get()}"
            for action in actions
        )
    return command.replace("  ", " ")


def set_command_text(*_):
    """Sets the command text entry to the current command"""
    widget = app["config"]["command_text"].tk_component
    widget.delete("1.0", "end")
    widget.insert("1.0", get_cli_command())


def copy_cli_command(*_):
    """Copies the cli command including all configuration settings chosen to the clipboard"""
    root.clipboard_clear()
    command = get_cli_command()
    root.clipboard_append(command)


def focus(event):
    """Callback for left-click -- stores the selected widget"""
    app.focused_widget_name = str(event.widget)


def _set_filepath_error():
    error_message = "An input MIDI file must be selected to run the simulation!"
    logging.error(error_message)
    app.data["error"].set(error_message)


def run_simulation(*_):
    """Callback for run button"""
    command = app["config"]["command_text"].tk_component.get(
        "1.0", "end-1c"
    )  # get all text in the widget except the trailing newline
    logging.info("Running command %s", command)

    parser = args.cli.construct_parser()
    try:
        args_ = parser.parse_args(
            command.replace("python -m bach_generator", "").strip(" ").split(" ")
        )
    except SystemExit:
        _set_filepath_error()
        return

    if not args_.filepath:
        _set_filepath_error()
        return

    function = app.data["setup_function"]
    runner_, runner_data, model_managers = function(args_)
    generations = runner_data.generations
    runner_data.generations = 1

    ratings = []
    for _ in range(generations):
        model_managers = runner_.run(model_managers, data=runner_data)
        ratings.append(model_managers[0].rating if model_managers else 0)
        _plot_data(ratings)
        root.update()  # avoid window freeze

    logging.info("Finished running command.")


def _plot_data(ratings):
    app["plot"]["rating_fig"].tk_component.plot(
        figure.DataSet(y=ratings, line_colour=config.SEC)
    )
    app["plot"].pack()
