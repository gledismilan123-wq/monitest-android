"""
theme.py
Palette colori condivisa (stessa identita' visiva del programma Windows),
convertita in RGBA 0-1 per Kivy/KivyMD.
"""


def hex_rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return [r, g, b, alpha]


BG = hex_rgba("#F3F4F6")
PANEL = hex_rgba("#FFFFFF")
INK = hex_rgba("#151A1E")
STEEL = hex_rgba("#2F5C94")
STEEL_SOFT = hex_rgba("#DCE7F5")
LINE = hex_rgba("#D6DBE0")
ACCENT = hex_rgba("#B8420A")
MUTED = hex_rgba("#4B565C")
MUTED_LIGHT = hex_rgba("#8B9599")
ERROR = hex_rgba("#A32626")
