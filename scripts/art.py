"""
art.py contains the data required for editing the tilemap
"""

# stores data for the current editor object
# form editor.py in scripts
CURRENT_EDITOR = None

def set_current_editor(editor):
    """Set current edtior"""
    global CURRENT_EDITOR
    CURRENT_EDITOR = editor



class Brush:
    """
        Brush
    - Editors have a brush
    - brush contains a sprite data, including path and data
    """

    def __init__(self, sprite_data):
        """Brush object constructor"""
        self.sprite_data = sprite_data
        self.sprite = sprite_data.tex


