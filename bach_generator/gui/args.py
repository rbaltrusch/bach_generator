# -*- coding: utf-8 -*-
"""Cli args helper functions to configure gui properly"""

import argparse
import tkinter as tk
from tkinter import ttk
from typing import Callable, List

from bach_generator import cli
from bach_generator.gui import app, config


def get_parser_actions() -> List[argparse.Action]:
    """Returns the cli parser actions"""
    parser = cli.construct_parser()

    # collect all cli parser option arguments except help
    return [
        x
        for x in parser._actions[1:]  # pylint: disable=protected-access
        if not x.dest in ["seed", "load_filepath", "load_best"]
    ]


def format_parser_action_name(action: argparse.Action) -> str:
    """Returns a nicely human-readable string from the action dest variable name"""
    return " ".join(x.capitalize() for x in action.dest.split("_"))


def create_scale(master: tk.Widget, action: argparse.Action) -> tk.Scale:
    """Creates and returns a new tkinter Scale"""
    value = action.default if action.default is not None else 1
    float_args = (
        {"digits": len(str(int(1 / value))), "resolution": value / 5}
        if action.type is float
        else {}
    )
    return tk.Scale(
        master,
        from_=max(0, value / 5),
        to_=value * 5,
        variable=app.data[action.dest],
        orient="horizontal",
        bd=0,
        **float_args,
        **config.SCALE_THEME,
    )


def create_dropdown(master: tk.Widget, action: argparse.Action) -> tk.OptionMenu:
    """Creates and returns a new tkinter OptionMenu"""
    combostyle = ttk.Style()
    combostyle.theme_use("alt")
    combostyle.configure(
        "MyCustomStyleName.TCombobox",
        selectbackground=config.BG3,
        fieldbackground=config.BG2,
        foreground=config.FG,
        background=config.BG2,
        activebackground=config.BG3,
        activeforeground=config.FG,
        highlightthickness=0,
    )

    options_menu = ttk.Combobox(
        master,
        textvariable=app.data[action.dest],
        values=action.choices,
        style="MyCustomStyleName.TCombobox",
    )

    return options_menu


def create_checkbox(master: tk.Widget, action: argparse.Action) -> tk.Checkbutton:
    """Creates and returns a new tkinter Checkbutton"""
    return tk.Checkbutton(
        master,
        variable=app.data[action.dest],
        bg=config.BG2,
        fg=config.FG,
        selectcolor=config.BG3,
        activebackground=config.BG2,
    )


def create_text_entry(master: tk.Widget, action: argparse.Action) -> tk.Entry:
    """Creates and returns a new tkinter Entry"""
    return tk.Entry(
        master,
        textvariable=app.data[action.dest],
        insertbackground=config.FG,
        **config.LABEL_THEME,
    )


def get_component_factory(action: argparse.Action) -> Callable[..., tk.Widget]:
    """Returns the tk widget factory function appropriate for the arg action"""
    if action.choices:
        return create_dropdown

    if action.type in [int, float]:
        return create_scale

    if action.const in [True, False]:  # boolean cli arg
        return create_checkbox
    return create_text_entry
