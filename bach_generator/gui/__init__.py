# -*- coding: utf-8 -*-
"""Module init code"""

import tkinter as tk

from bach_generator.gui.colour_cycle import CyclicColourPicker
from bach_generator.gui.components import Gui, Tk

root = Tk()
app = Gui(root)

# tk vars
app.data["message"] = tk.StringVar()
app.data["command_text"] = tk.StringVar()
app.data["colour_picker"] = CyclicColourPicker(
    ["#CBB1EE", "#BD9CEA", "#AF87E5", "#A172E1", "#935DDD", "#8548D8", "#7733D4"]
)
