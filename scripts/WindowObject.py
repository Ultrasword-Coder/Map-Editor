import pygame
from engine import handler, filehandler, user_input
from engine import window, maths, serialize
from engine import state

from .globals import *


class WindowObjectManager(state.State):
    """
    A window object manager with sorting for entities
    thats about it :D
    """

    def __init__(self):
        """constructor"""
        super().__init__()
        self.update_order = []

    @staticmethod
    def sort_method(item) -> int:
        """Sort method"""
        return state.CURRENT.p_objects[item].z

    def sort_entities(self):
        """sort entities based off z-index"""
        self.update_order.sort(key=WindowObjectManager.sort_method)

    def handle_entities(self, dt: float):
        """New update method - overrides initial method"""
        for index in self.update_order:
            self.p_objects[index].update(dt)
            self.p_objects[index].handle_changes()
            self.p_objects[index].render()
        
        # dont render non persistent stuff


class WindowObject(handler.PersistentObject):
    """
    Similar to HTML layout
    """
    object_type = WINDOW_OBJECT_TYPE

    def __init__(self, l: float, t: float, r: float, b: float, parent_object = None):
        """Window Object constructor"""
        super().__init__()
        self.object_type = WINDOW_OBJECT_TYPE
        self.parent = parent_object
        # calculate position
        self.float_rect = handler.Rect(l, t, r, b)
        if self.parent:
            self.parent.set_child_coords(child)
        else:
            # fullscreen
            self.rect.x = window.FB_WIDTH * l
            self.rect.y = window.FB_HEIGT * t
            self.rect.w = window.FB_WIDTH * (r - l)
            self.rect.h = window.FB_HEIGT * (b - t)
        
        # settings
        self.z = 0
        self.dirty = True
        self.image = filehandler.make_surface(int(self.rect.w), int(self.rect.h), flags=filehandler.SRC_ALPHA)
        self.back_color = (255, 255, 255)
        self.children = []

        self.item_columns = 1
        self.item_width = self.rect.w // self.item_columns

        self.sprite = None
        self.sprite_path = None

        # grids
        self.grid = []
        self.grid_spacing = [0, 0]
        self.parent_grid_pos = 0
    
        # add to handler?
        state.CURRENT.add_entity_auto(self)
        state.CURRENT.update_order.append(self.object_id)
        state.CURRENT.sort_entities()

    def render(self):
        """Default Render function"""
        # only render if dirty
        if self.dirty:
            print(self.rect)
            self.image.fill(self.back_color)
            window.get_framebuffer().blit(self.image, (self.rect.x, self.rect.y))
            state.CURRENT.dirty = True
            self.dirty = False

    def is_hovering(self) -> bool:
        """Checks if mouse is hovering over the object"""
        mpos = user_input.get_mouse_pos()
        if mpos[0] < self.rect.x or mpos[0] > self.rect.w + self.rect.x:
            return False
        if mpos[1] < self.rect.y or mpos[1] > self.rect.y + self.rect.h:
            return False
        return True

    def is_clicked(self) -> bool:
        """Check if window object is being hovered and has been clicked"""
        return self.is_hovering() and user_input.mouse_button_clicked(1)

    def set_background_color(self, color: tuple):
        """Set the background"""
        self.back_color = color
        self.dirty = True

    def set_sprite(self, path: str):
        """Set the sprite path"""
        self.sprite_path = path
        self.sprite = filehandler.get_image(path)

    def create_child(self, l: float, t: float, r: float, h: float, object_type):
        """Create a child object and return it"""
        child = object_type(l, t, r, h)
        self.apply_all_transformations(child)
        self.children.append(child.object_id)
        return child

    def apply_all_transformations(self, child):
        """Apply all transformations, scaling, etc"""
        # calculate x and y pos
        child.rect.x = self.rect.x + self.rect.w * child.float_rect.x
        child.rect.y = self.rect.y + self.rect.h * child.float_rect.y
        # set child width
        child.rect.w = self.rect.w * (child.float_rect.w - child.float_rect.x)
        child.rect.h = self.rect.h * (child.float_rect.h - child.float_rect.y)
        # scale the image
        if child.image:
            child.image = filehandler.scale(child.image, (int(child.rect.w), int(child.rect.h)))
        else:
            child.image = filehandler.make_surface(int(child.rect.w), int(child.rect.h), flags=filehandler.SRC_ALPHA)
        child.z = self.z + 1

    @property
    def coordinates(self) -> handler.Rect:
        """Get coordinates rect"""
        return self.float_rect


# ---------- register ------------- #
handler.register_object_type(WindowObject.object_type, WindowObject)


