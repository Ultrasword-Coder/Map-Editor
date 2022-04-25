"""
editor.py

- contains Editor object
- allows for tilemap editing
- extends off the world.World object from engine

"""

from engine import world

from scripts import art, WindowObject
from scripts.globals import *


class Editor(WindowObject.WindowObject, world.World):
    """
    Editor to edit the world!

    - when focused is set to current world editor
    - only edits when user hovering over it
    - yes
    """
    
    def __init__(self, l: float, t: float, r: float, b: float, parent=None):
        """Editor constructor"""
        WindowObject.WindowObject.__init__(self, l, t, r, b, parent)
        world.World.__init__(self)
    
    def update(self, dt: float):
        """Update function"""
        pass



