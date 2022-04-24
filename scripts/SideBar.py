import pygame

from . import WindowObject, art

from engine import filehandler, spritesheet, state
from engine import eventhandler,animation, user_input
from engine import window, spritesheet
from engine.globals import *

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
    
    def update(self, dt: float):
        """Update function"""
        if self.is_clicked():
            print("PAOWDPAWod ")

    def render(self):
        """Empty render function"""
        # just render it
        if self.sprite and self.dirty:
            print("SideBar.py      | ", self.object_id, self.rect)
            window.get_framebuffer().blit(self.sprite, (self.rect.x, self.rect.y))
            state.CURRENT.dirty = True
            self.dirty = False

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
        self.y_scrolling = 0
        self.grid_count = 0

        # grid is the children stuff
        self.grid = self.children
        self.empty_grid_pos = []
    
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

