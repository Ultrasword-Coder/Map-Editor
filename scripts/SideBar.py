from . import WindowObject, art

from engine import filehandler, spritesheet, state
from engine import eventhandler,animation, user_input
from engine import window
from engine.globals import *


class SideBarObject(WindowObject.WindowObject):
    """
    Side Bar Object
    - sprites
    """
    def __init__(self, l, t, r, b, parent_object=None):
        """SideBarObejct constructor"""
        super().__init__(0, 0, 0, 0, parent_object)
        
    def render(self):
        """Empty render function"""
        # just render it
        if self.sprite and self.dirty:
            print("SideBar.py   | ", self.rect)
            window.get_framebuffer().blit(self.sprite, self.parent.get_rel_pos((self.rect.x, self.rect.y)))
            state.CURRENT.dirty = True
            self.dirty = False

class SideBar(WindowObject.WindowObject):
    """
    SideBar object
    - the sidebar
    - holds an array of side bar objects
    """

    def __init__(self, l: float, t: float, r: float, b: float, parent_object = None):
        """Sidebar constructor"""
        super().__init__(l, t, r, b, parent_object)
        self.y_scrolling = 0
    
    def update(self, dt: float):
        """Update function"""
        pass

    def add_item(self, sprite_path: str, obj):
        """Add a new SideBarObject"""
        obj.set_sprite(sprite_path)
        self.grid.append(obj)
        # set obj new position
        self.apply_all_transformations(obj)
    
    def apply_all_transformations(self, child):
        """Transform the position of the child into the correct place"""
        child.dirty = True
        # get grid position
        n = child.parent_grid_pos
        x = n % self.item_columns
        y = n // self.item_columns

        # calculate item pos
        child.rect.x = x * self.item_width + self.grid_spacing[0] * (x + 1)
        child.rect.y = y * self.item_width + self.grid_spacing[1] * (y + 1)

        child.rect.w = self.item_width
        child.rect.h = self.item_width

        child.z = self.z + 1
