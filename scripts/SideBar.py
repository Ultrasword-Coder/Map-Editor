import pygame

from . import WindowObject, art

from engine import filehandler, spritesheet, state
from engine import eventhandler,animation, user_input
from engine import window, spritesheet, maths, clock
from engine import draw, handler
from engine.globals import *

from scripts import art
from scripts.globals import *


# TODO - consider making a sidebar selection thing with multiple sidebars in a container


class SideBarObject(WindowObject.WindowObject):
    """
    Side Bar Object
    - sprites
    """

    def __init__(self, l, t, r, b, parent_object=None):
        """SideBarObejct constructor"""
        super().__init__(0, 0, 0, 0, parent_object)
        self.sprite_data = None
        self.brush_object = None

        state.CURRENT.remove_object(self.object_id)

    def update(self, dt: float):
        """Update function"""
        # print(self.rect, window.mouse_window_to_framebuffer(user_input.get_mouse_pos()))
        if self.is_clicked(offy = -self.offset[1]):
            print(f"Item:     | {self.object_id} clicked")
            if self.brush_object:
                art.CURRENT_EDITOR.set_brush(self.brush_object)

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
            self.parent.dirty = True

            # draw hitbox for clicking 
            # to be removed
            # there is an offset because we are adding world pos to rel pos
            # leave for now
            
            draw.DEBUG_DRAW_RECT(self.parent.image, self.rect, offset=(-self.rect.x + ppos[0], -self.offset[1] - 95))

    # --------------- methods --------------- #

    def add_to_grid(self, chunk, data: dict):
        """Add to grid"""
        if self.sprite_data.index < 0:
            # it is not from a sprite sheet
            chunk.set_tile_at(chunk.create_grid_tile(data[SIDEBAR_DATA_X], data[SIDEBAR_DATA_Y], data[SIDEBAR_DATA_IMG]))
        else:
            # it is from a sprite sheet
            # TODO - CHANGE THE COLLIDE THING
            # MAKE IT TOGGLEABLE FROM GLOBAL CONTEXT
            chunk.set_tile_at(spritesheet.SpriteTile(data[SIDEBAR_DATA_X], data[SIDEBAR_DATA_Y], 0, self.sprite_data))

    def set_sprite_data(self, data):
        """Set sprite data"""
        # data comes in the form of a SpriteData object from spritesheet.SpriteData
        self.sprite_data = data
        if self.sprite_data:
            self.sprite = filehandler.scale(self.sprite_data.tex, (int(self.rect.w), int(self.rect.h)))
            # create sprite data
            self.brush_object = art.Brush(self.sprite_data, self)


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

        self.index = 0
        self.name = "0"

        state.CURRENT.remove_object(self.object_id)
    
    def update(self, dt: float):
        """Update function"""
        # get mouse scrolling
        if self.is_hovering():
            self.offset[1] -= user_input.y_scroll * 800 * dt
            self.offset[1] = maths.clamp(self.offset[1], 0, self.max_y - self.rect.h)
            if user_input.y_scroll:
                # print(self.offset[1])
                self.set_all_dirty()
            for child in self.children:
                child.update(dt)
            if self.dirty:
                self.parent.dirty = True

    def render(self):
        """Default Render function"""
        # only render if dirty
        if self.dirty:
            # if this is dirty, all children are dirty
            self.set_all_dirty()
            # ("SideBar         | ", self.object_id, self.rect)
            self.image.fill(self.back_color)
            # render children
            for child in self.children:
                child.render()
            self.parent.image.blit(self.image, (self.rect.x, self.rect.y))
            state.CURRENT.dirty = True
            self.dirty = False
            
            # draw.DEBUG_DRAW_LINE(window.get_framebuffer(), (255, 0, 0), (self.rect.x, self.offset[1]), (self.rect.right, self.offset[1]))

    def add_item(self, obj):
        """Add a new SideBarObject"""
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
        data = filehandler.get_json_data(path)
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


class SideBarContainer(WindowObject.WindowObject):
    """
    Holds a bunch of sidebars for different spritesheets and entities
    - sidebars :O
    """

    def __init__(self, l, t, r, b, parent_object=None):
        """Side Bar Container constructor"""
        self.sidebars = []
        self.current_bar = 0
        
        self.topbars = []
        self.scroll_x = 0
        self.max_x_scroll = 0
        self.topbar_x_offset = 0

        self.secondary_color = (0, 0, 0)
        self.top_bar_frect = handler.Rect(0.01, 0.01, 0.99, 0.1)
        self.top_bar_rect = handler.Rect(0, 0, 0, 0)
        self.top_bar_image = None
        
        self.draw_area_frect = handler.Rect(0.0, 0.10, 1.0, 1.0)
        self.draw_area_rect = handler.Rect(0, 0, 0, 0)

        WindowObject.WindowObject.__init__(self, l, t, r, b, parent_object)

        self.default_children_coordinates = (0.01, 0.01, 0.99, 0.99)

        # rendered text
        self.loaded_spritesheets = set()
        self.font = filehandler.get_font(Theme.FONT_PATH).get_font_size(20)
        self.info_text = self.font.render("Please Drag SpriteSheet File!", True, (0, 0, 0))
        self.info_rect = self.info_text.get_rect()
        self.info_rect.center = (self.rect.w / 2 + self.rect.x, self.rect.h / 2 + self.rect.y)

    def start(self):
        """Start"""
        self.top_bar_rect.x = self.top_bar_frect.x * self.rect.w
        self.top_bar_rect.y = self.top_bar_frect.y * self.rect.h
        self.top_bar_rect.w = (self.top_bar_frect.w - self.top_bar_frect.x) * self.rect.w
        self.top_bar_rect.h = (self.top_bar_frect.h - self.top_bar_frect.y) * self.rect.h
        self.top_bar_image = filehandler.make_surface(int(self.top_bar_rect.w), int(self.top_bar_rect.h))        
        
        self.draw_area_rect.x = self.draw_area_frect.x * self.rect.w
        self.draw_area_rect.y = self.draw_area_frect.y * self.rect.h
        self.draw_area_rect.w = (self.draw_area_frect.w - self.draw_area_frect.x) * self.rect.w
        self.draw_area_rect.h = (self.draw_area_frect.h - self.draw_area_frect.y) * self.rect.h

    def set_secondary_color(self, color):
        """Set secondary color"""
        self.secondary_color = color

    def update(self, dt):
        """Update"""
        if self.is_hovering():
            if user_input.is_key_pressed(pygame.K_LSHIFT):
                self.scroll_x += user_input.y_scroll
                self.scroll_x = maths.clamp(self.scroll_x, 5, self.max_x_scroll)
                self.dirty = True
            if self.sidebars:
                self.sidebars[self.current_bar].update(dt)
    
    def render(self):
        """Render"""
        if self.dirty:
            self.set_all_dirty()
            print("SideBarContainer| ", self.object_id, self.rect)
            self.image.fill(self.back_color)
            self.top_bar_image.fill(self.secondary_color)
            # draw text onto topbar
            for rendered_text, rect in self.topbars:
                self.top_bar_image.blit(rendered_text, (rect.x + self.scroll_x, rect.y))
            self.image.blit(self.top_bar_image, self.top_bar_rect.topleft)
            # render only the current child
            if self.sidebars:
                self.sidebars[self.current_bar].render()
            else:
                self.image.blit(self.info_text, self.info_rect)
            window.get_framebuffer().blit(self.image, self.rect.topleft)
            state.CURRENT.dirty = True
            self.dirty = False
    
    def apply_all_transformations(self, child):
        """Transform the position of the child into the correct place"""
        child.dirty = True
        
        # set the item area to the correct area
        child.rect.x = self.draw_area_rect.x + self.draw_area_rect.w * child.float_rect.x
        child.rect.y = self.draw_area_rect.y + self.draw_area_rect.h * child.float_rect.y
        # set area
        child.rect.w = self.draw_area_rect.w * (child.float_rect.w - child.float_rect.x)
        child.rect.h = self.draw_area_rect.h * (child.float_rect.h - child.float_rect.y)
        
        # scale image
        if child.sprite_path:
            child.sprite = filehandler.scale(child.sprite_path, (int(child.rect.w), int(child.rect.h)))
        else:
            child.image = filehandler.make_surface(int(child.rect.w), int(child.rect.h))
        child.z = self.z + 1
    
    # ---------- methods ------------- #

    def add_sidebar_object(self, sidebar):
        """Add sidebar object"""
        sidebar.index = len(self.sidebars)
        sidebar.name = str(sidebar.index)

        rendered_text = self.font.render(sidebar.name, True, (255, 255, 255), Theme.TERTIARY)
        rect = rendered_text.get_rect()
        # get rect pos
        if self.topbars:
            rect.x = self.topbars[-1][1].right
        rect.y = 10
        
        self.sidebars.append(sidebar)
        self.topbars.append((rendered_text, rect))
        self.max_x_scroll += rect.w
    
    def remove_sidebar_object(self, index):
        """Remove sidebar objects"""
        bar = self.sidebars.pop(index)
        self.topbars.remove(bar.name)
        
    def file_dragged(self, file):
        """Check if a file is correct"""
        bar = self.create_child(0.01, 0.01, 0.99, 0.99, SideBar)
        bar.set_background_color(Theme.SECONDARY)
        bar.set_grid_spacing(10, 10)
        bar.set_columns(3)
        try:
            # set some default parameters
            bar.load_spritesheet(file)
            self.add_sidebar_object(bar)
            self.dirty = True
            self.loaded_spritesheets.add(file)
        except Exception as e:
            print(e)

