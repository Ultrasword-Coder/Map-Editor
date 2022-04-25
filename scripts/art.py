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

