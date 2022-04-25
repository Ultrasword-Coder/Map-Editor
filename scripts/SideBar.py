import pygame

from . import WindowObject, art

from engine import filehandler, spritesheet, state
from engine import eventhandler,animation, user_input
from engine import window, spritesheet, maths, clock
from engine import draw
from engine.globals import *

from scripts import art
from scripts.globals import *


class SideBarObject(WindowObject.WindowObject):
    """
    Side Bar Object
    - sprites
    """

    def __init__(self, l, t, r, b, parent_object=None):
        """SideBarObejct constructor"""
        super().__init__(0, 0, 0, 0, parent_object)
        
        self.sprite_data = None
        state.CURRENT.remove_object(self.object_id)
  
    def update(self, dt: float):
        """Update function"""
        # print(self.rect, window.mouse_window_to_framebuffer(user_input.get_mouse_pos()))
        if self.is_clicked(offy = -self.offset[1]):
            print(f"Item: {self.object_id} clicked")

    def render(self):
        """Empty render function"""
        # just render it
        if self.sprite and self.dirty:
            self.offset[1] = self.parent.offset[1]
            ppos = self.parent.get_rel_pos((self.rect.x, self.rect.y - self.offset[1]))
            # print("SideBar.py      | ", self.object_id, ppos)
            self.parent.image.blit(self.sprite, ppos)
            state.CURRENT.dirty = True
            self.dirty = False

            # draw hitbox for clicking 
            # to be removed
            draw.DEBUG_DRAW_RECT(self.parent.image, self.rect, offset=(self.offset[0], -self.offset[1]))

    def set_sprite_data(self, data):
        """Set sprite data"""
        self.sprite_data = data
        if self.sprite_data:
            self.sprite = filehandler.scale(self.sprite_data.tex, (int(self.rect.w), int(self.rect.h)))


class SideBar(WindowObject.WindowObject):
    """
    SideBar object
    - the sidebar
    - holds an array of side bar objects
    """

    def __init__(self, l: float, t: float, r: float, b: float, parent_object = None):
        """Sidebar constructor"""
        super().__init__(l, t, r, b, parent_object)
        self.grid_count = 0
        self.max_y = 100

        # grid is the children stuff
        self.grid = self.children
        self.empty_grid_pos = []
    
    def update(self, dt: float):
        """Update function"""
        # get mouse scrolling
        # print(user_input.get_mouse_pos(), window.mouse_window_to_framebuffer(user_input.get_mouse_pos()))
        if self.is_hovering():
            self.offset[1] -= user_input.y_scroll * 800 * dt
            self.offset[1] = maths.clamp(self.offset[1], 0, self.max_y - self.rect.h)
            if user_input.y_scroll:
                # print(self.offset[1])
                self.set_all_dirty()
            for child in self.children:
                child.update(dt)
    
    def render(self):
        """Default Render function"""
        # only render if dirty
        if self.dirty:
            # if this is dirty, all children are dirty
            for i in self.children:
                self.set_all_dirty()
            # print("SideBar.py      | ", self.object_id, self.rect)
            self.image.fill(self.back_color)
            # render children
            for child in self.children:
                child.render()
            window.get_framebuffer().blit(self.image, (self.rect.x, self.rect.y))
            state.CURRENT.dirty = True
            self.dirty = False
            
            # draw.DEBUG_DRAW_LINE(window.get_framebuffer(), (255, 0, 0), (self.rect.x, self.offset[1]), (self.rect.right, self.offset[1]))

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
        child.rect.x = self.rect.x + x * self.item_width + self.grid_spacing[0] * (x + 1)
        child.rect.y = self.rect.y + y * self.item_width + self.grid_spacing[1] * (y + 1)
        child.rect.w = self.item_width
        child.rect.h = self.item_width

        child.z = self.z + 1

        # now update some stuff for grid position
        f = False
        for i in range(len(self.grid)):
            if not self.grid[i]:
                f = True
                self.empty_grid_pos.append(i)
        if not f:
            self.grid_count = len(self.grid)
        
        # calculate new max_y
        self.max_y = max(self.max_y, child.rect.bottom)

    def get_empty_grid_pos(self):
        """Get an empty grid pos"""
        if self.empty_grid_pos:
            return self.empty_grid_pos.pop(0)
        self.grid_count += 1
        return self.grid_count - 1
    
    def load_spritesheet(self, path: str):
        """Load a spritesheet and yeet into the sidebar"""
        data = filehandler.load_json(path)
        img_path = data[SIDEBAR_SS_IMG]
        width = data[SIDEBAR_SS_WIDTH]
        height = data[SIDEBAR_SS_HEIGHT]
        tiles = data[SIDEBAR_SS_TILES]
        xspace = data[SIDEBAR_SS_XSPACE]
        yspace = data[SIDEBAR_SS_YSPACE]
        sheet = spritesheet.get_sprite_sheet(img_path, width, height, xspace, yspace)

        # add SideBarObjects with tile sprite
        for tile in tiles:
            obj = self.create_child(0, 0, 0, 0, SideBarObject)
            # get spritesheet index
            if tile:
                xi, yi = map(int, tile.split("."))
                index = xi + yi * sheet.sprite_x_count
                sprite = sheet.get_sprite(index)
                obj.set_sprite_data(sprite)
            else:
                obj.set_sprite_data(None)
            
            # set grid pos!
            option = self.get_empty_grid_pos()
            obj.set_grid_pos(option)
