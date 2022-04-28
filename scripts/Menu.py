"""
Menu.py

- contains Menu object
- allows for tools
- contains a bunch of tools and changes global variables!

"""
import pygame

from engine import world, user_input, filehandler
from engine import draw, eventhandler, clock
from engine import window, state, handler
from engine.globals import *

from scripts import WindowObject
from scripts.globals import *


class Menu(WindowObject.WindowObject):
    """
    Menu contains a bunch of butons that do certain things when pressed

    - button array
    - horizontal placed at top of the window
    """

    def __init__(self, l: float, t: float, r: float, b: float, parent=None):
        """Menu constructor"""
        pass


