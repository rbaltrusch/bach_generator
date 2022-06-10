# -*- coding: utf-8 -*-
"""Module init code"""

import tkinter as tk

from bach_generator.gui.components import Gui, Tk

root = Tk()
app = Gui(root)

# tk vars
app.data["error"] = tk.StringVar()
app.data["command_text"] = tk.StringVar()
