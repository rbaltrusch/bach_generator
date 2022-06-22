# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 17:57:26 2021

@author: Korean_Crimson
"""
# pylint: disable=import-error
# pylint: disable=line-too-long
import os
import tkinter as tk

from bach_generator.gui import app, args, callbacks, components, config, figure, root


def init():
    """Initializes root and all views of gui app"""
    init_root()
    init_tk_variables()
    config_view = init_config_view()
    plot_view = init_plot_view()
    app.views_dict = {"config": config_view, "plot": plot_view}
    callbacks.set_command_text()


def init_root():
    """Initialize tkinter root"""
    # configure root
    root.title(config.TITLE)
    root["bg"] = config.BG
    root.option_add("*TCombobox*Listbox*Background", config.BG2)
    root.option_add("*TCombobox*Listbox*SelectBackground", config.BG2)
    root.option_add("*TCombobox*Listbox*Foreground", config.FG)
    root.option_add("*TCombobox*Listbox*SelectForeground", config.FG)
    root.focus_force()

    # set trace callbacks
    root.bind_all("<Button-1>", callbacks.focus)
    app.data["error"].trace_add("write", callbacks.set_error)

    # set window icon
    icon_path = os.path.join(os.path.dirname(__file__), "media", "icon.png")
    root.set_icon(icon_path)


def init_tk_variables():
    """Initialises tk variables with the cli parser args"""
    types = {
        int: tk.IntVar,
        float: tk.DoubleVar,
        str: tk.StringVar,
        None: tk.StringVar,
    }
    for action in args.get_parser_actions():
        tk_variable: tk.Variable = (
            tk.BooleanVar()
            if action.const in [True, False]
            else types.get(action.type)()
        )
        tk_variable.set(
            action.default
            if action.default is not None
            else (action.type() if action.type is not None else "")
        )
        tk_variable.trace_add("write", callbacks.set_command_text)
        app.data[action.dest] = tk_variable


def init_config_view():
    """Initializes config view"""
    actions = [
        x
        for x in args.get_parser_actions()
        if not any(y in x.dest for y in ["filepath", "load"])
    ]

    view = components.View()
    view.activate()

    frame = tk.Frame(root, bd=0, bg=config.BG)
    component = components.Frame(
        frame,
        sticky="NSEW",
        row=3,
        column=0,
        row_span=len(actions) + 4,
        column_span=3,
        padx=10,
        pady=10,
    )
    component.add_col(0)
    component.add_col(500)
    component.add_col(0)
    view.add_frame_component(component, "frame")

    view.add_component(
        components.Component(
            tk.Label(frame, text="Midi file", **config.LABEL_THEME),
            sticky="NSE",
            row=0,
            column=0,
            padx=5,
        )
    )

    view.add_component(
        components.Component(
            tk.Entry(
                frame, textvariable=app.data["filepath"], **config.DYNAMIC_ENTRY_THEME
            ),
            sticky="NSEW",
            row=0,
            column=1,
        )
    )

    view.add_component(
        components.Component(
            tk.Button(
                frame,
                text="Select file",
                command=callbacks.choose_file,
                **config.BUTTON_THEME,
            ),
            sticky="NSEW",
            row=0,
            column=2,
            row_span=1,
        ),
        name="file_button",
    )

    for row, action in enumerate(actions, 1):
        view.add_component(
            components.Component(
                tk.Label(
                    frame,
                    text=args.format_parser_action_name(action),
                    **config.LABEL_THEME,
                ),
                row=row,
                sticky="NSE",
                padx=5,
            )
        )

        factory = args.get_component_factory(action)
        view.add_component(
            components.Component(
                tk_component=factory(frame, action), row=row, sticky="NSEW", column=1
            )
        )

    view.add_component(
        components.Component(
            tk.Button(
                frame,
                text="Copy command",
                command=callbacks.copy_cli_command,
                **config.BUTTON_THEME,
            ),
            sticky="NSEW",
            row=len(actions) + 2,
            column=2,
            row_span=1,
        )
    )

    run_button_theme = config.BUTTON_THEME.copy()
    run_button_theme["bg"] = config.PRIM
    view.add_component(
        components.Component(
            tk.Button(
                frame,
                text="Run simulation",
                command=callbacks.run_simulation,
                **run_button_theme,
            ),
            sticky="NSEW",
            row=len(actions) + 3,
            column=2,
            row_span=1,
        )
    )

    view.add_component(
        components.Component(
            tk.Text(
                frame,
                wrap=tk.WORD,
                height=3,
                insertbackground=config.FG,
                **config.LABEL_THEME,
            ),
            sticky="NSEW",
            row=len(actions) + 2,
            column=0,
            column_span=2,
            row_span=2,
            pady=10,
        ),
        name="command_text",
    )

    view.add_component(
        components.Component(
            tk.Entry(
                frame,
                textvariable=app.data["error"],
                state="disabled",
                disabledbackground=config.BG,
                bg=config.BG,
                fg=config.FG,
                bd=0,
            ),
            sticky="NSEW",
            row=len(actions) + 4,
            column=0,
            column_span=3,
            pady=10,
        )
    )
    return view


def init_plot_view():
    """Initializes results and plots view"""
    view = components.View()
    view.activate()

    frame = tk.Frame(root, bd=0, bg=config.BG)
    component = components.Frame(
        frame,
        sticky="NSEW",
        row=4,
        column=4,
        row_span=len(args.get_parser_actions()),
        column_span=1,
        padx=10,
        pady=10,
    )
    component.add_col(0)
    view.add_frame_component(component, "frame")

    rating_fig = figure.Figure(frame, config.BG, config.FG)
    rating_fig.set_labels(title="Model ratings", x_title="Time", y_title="Rating")
    component = components.Component(rating_fig, sticky="NSEW", row=0, column=1)
    view.add_component(component, "rating_fig")
    return view
