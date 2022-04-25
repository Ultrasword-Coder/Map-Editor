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
    
    def remove_object(self, object_id):
        """Remove and object!"""
        self.p_objects.pop(object_id)
        # maybe find a better solution for bigger applications
        self.update_order.remove(object_id)


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

        # stuff
        self.z = 0
        self.dirty = True
        self.back_color = (255, 255, 255)
        self.children = []
        self.offset = [0, 0]

        # grids
        self.grid_spacing = [0, 0]
        self.parent_grid_pos = 0

        self.item_columns = 1
        self.item_width = (self.rect.w - self.grid_spacing[0] * (self.item_columns + 1)) // self.item_columns

        self.sprite = None
        self.sprite_path = None


        if self.parent:
            self.parent.apply_all_transformations(self)
        else:
            # fullscreen
            self.rect.x = window.FB_WIDTH * l
            self.rect.y = window.FB_HEIGHT * t
            self.rect.w = window.FB_WIDTH * (r - l)
            self.rect.h = window.FB_HEIGHT * (b - t)
        
        # settings
        self.image = filehandler.make_surface(int(self.rect.w), int(self.rect.h), flags=filehandler.SRC_ALPHA)
        
    
        # add to handler?
        state.CURRENT.add_entity_auto(self)
        state.CURRENT.update_order.append(self.object_id)
        state.CURRENT.sort_entities()

    def start(self):
        """Start method"""
        self.dirty = True
        self.render()

    def render(self):
        """Default Render function"""
        # only render if dirty
        if self.dirty:
            # if this is dirty, all children are dirty
            for i in self.children:
                self.set_all_dirty()
            print("WindowObject.py | ", self.object_id, self.rect)
            self.image.fill(self.back_color)
            window.get_framebuffer().blit(self.image, (self.rect.x, self.rect.y))
            state.CURRENT.dirty = True
            self.dirty = False

    def is_hovering(self, offx: int = 0, offy: int = 0) -> bool:
        """Checks if mouse is hovering over the object"""
        mpos = window.mouse_window_to_framebuffer(user_input.get_mouse_pos())
        if mpos[0] < self.rect.x + offx or mpos[0] > self.rect.x + self.rect.w + offx:
            return False
        if mpos[1] < self.rect.y + offy or mpos[1] > self.rect.y + self.rect.h + offy:
            return False
        return True

    def is_clicked(self, offx: int = 0, offy: int = 0) -> bool:
        """Check if window object is being hovered and has been clicked"""
        return self.is_hovering(offx, offy) and user_input.mouse_button_clicked(1)

    def set_columns(self, c: int):
        """Set amt of columns"""
        self.item_columns = c
        self.item_width = (self.rect.w - self.grid_spacing[0] * (self.item_columns + 1)) // self.item_columns

    def set_grid_spacing(self, x: int = None, y: int = None):
        """Set grid spacing"""
        if x:
            self.grid_spacing[0] = x
        if y:
            self.grid_spacing[1] = y
        self.set_columns(self.item_columns)

    def set_background_color(self, color: tuple):
        """Set the background"""
        self.back_color = color
        self.dirty = True

    def set_sprite(self, path: str):
        """Set the sprite path"""
        self.sprite_path = path
        self.sprite = filehandler.scale(filehandler.get_image(path), (int(self.rect.w), int(self.rect.h)))
        self.dirty = True

    def set_grid_pos(self, gridpos: int):
        """Set the grid pos and let parent apply transformations"""
        self.parent_grid_pos = gridpos
        if self.parent:
            self.parent.apply_all_transformations(self)

    def create_child(self, l: float, t: float, r: float, h: float, object_type):
        """Create a child object and return it"""
        child = object_type(l, t, r, h, self)
        self.apply_all_transformations(child)
        self.children.append(child)
        return child

    def apply_all_transformations(self, child):
        """Apply all transformations, scaling, etc"""
        child.dirty = True
        # calculate x and y pos
        child.rect.x = self.rect.x + self.rect.w * child.float_rect.x
        child.rect.y = self.rect.y + self.rect.h * child.float_rect.y
        # set child width
        child.rect.w = self.rect.w * (child.float_rect.w - child.float_rect.x)
        child.rect.h = self.rect.h * (child.float_rect.h - child.float_rect.y)
        # scale the image
        if child.sprite_path:
            child.sprite = filehandler.scale(child.sprite_path, (int(child.rect.w), int(child.rect.h)))
        else:
            child.image = filehandler.make_surface(int(child.rect.w), int(child.rect.h), flags=filehandler.SRC_ALPHA)
        child.z = self.z + 1

    def set_all_dirty(self):
        """Set all children to be dirty"""
        for child in self.children:
            child.set_all_dirty()
        self.dirty = True

    def get_rel_pos(self, position: tuple) -> tuple:
        """Get rel pos to this object"""
        return (position[0] - self.rect.x, position[1] - self.rect.y)

    @property
    def coordinates(self) -> handler.Rect:
        """Get coordinates rect"""
        return self.float_rect


# ---------- register ------------- #
handler.register_object_type(WindowObject.object_type, WindowObject)


