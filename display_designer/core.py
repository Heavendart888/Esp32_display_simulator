# display_designer/core.py
"""
Core models and presets for the Display Designer.
"""

import math
import re

# ----------------- Presets -----------------
DISPLAY_PRESETS = {
    "OLED 128x64": (128, 64),
    "TFT 240x135": (240, 135),
    "TFT 320x240": (320, 240),
    "Custom...": None
}

# ----------------- Helper: Element model -----------------
class Element:
    """Model for a drawable element on canvas."""
    def __init__(self, etype, canvas_id, x=0, y=0, w=0, h=0, text="", rotation=0):
        self.type = etype  # "rect", "circle", "text"
        self.id = canvas_id
        self.x = x         # Top-left x coordinate relative to display (0, 0)
        self.y = y         # Top-left y coordinate relative to display (0, 0)
        self.w = w         # Width
        self.h = h         # Height
        self.text = text
        self.rotation = rotation  # degrees

# ----------------- Utility Functions -----------------
# For now, we'll keep only pure data/math utils here.
# The geometry and code generation logic will stay in app.py as they depend on the canvas/Tkinter context.