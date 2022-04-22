import pygame
from engine import handler, filehandler, user_input
from engine import window, maths, serialize


class WindowObject(handler.PersistentObject):
    """
    Similar to HTML layout
    """
    def __init__(self, l: float, t: float, r: float, b: float, parent_object: WindowObject = None):
        """Window Object constructor"""
        super().__init__()
        self.parent = parent_object
        # calculate position
        self.float_rect = handler.Rect(l, t, r, b)
        if self.parent:
            self.parent.set_child_coords(child)
        else:
            # fullscreen
            self.rect.x = window.WIDTH * l
            self.rect.y = window.HEIGHT * t
            self.rect.w = window.WIDTH * (r - l)
            self.rect.h = window.HEIGHT * (b - t)
    
    def set_child_coords(self, child: WindowObject):
        """Set the coordinates of this object given parent coords"""
        # calculate based off parent object
        child.rect.x = self.rect.x + self.rect.w * l
        child.rect.y = self.rect.y + self.rect.h * t
        child.rect.w = self.rect.w * (r - l)
        child.rect.h = self.rect.h * (b - t)
    
    @property
    def coordinates(self) -> handler.Rect:
        """Get coordinates rect"""
        return self.float_rect
    

        

