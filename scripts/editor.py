"""
editor.py

- contains Editor object
- allows for tilemap editing
- extends off the world.World object from engine

"""

from engine import world, user_input, filehandler
from engine import draw, eventhandler, clock
from engine import window, state, handler
from engine.globals import *

from scripts import art, WindowObject
from scripts.globals import *



class Editor(WindowObject.WindowObject):
    """
    Editor to edit the world!

    - when focused is set to current world editor
    - only edits when user hovering over it
    

    Brush
    - Editors have a brush
    - brush contains a sprite data, including path and data
    """
    
    def __init__(self, l: float, t: float, r: float, b: float, parent=None):
        """Editor constructor"""
        self.relative_center = [0, 0]
        self.world = world.World()

        # create a new pygame surface for the actual drawing area
        self.viewport_float_rect = handler.Rect(0.1, 0.1, 0.99, 0.99)
        self.viewport_rect = handler.Rect(0, 0, 0, 0)
        self.viewport = filehandler.make_surface(int(self.viewport_rect.w), int(self.viewport_rect.h))

        # init
        WindowObject.WindowObject.__init__(self, l, t, r, b, parent)

    def update(self, dt: float):
        """Update function"""
        # get user input
        self.relative_center[0] = self.offset[0] // CHUNK_WIDTH_PIX
        self.relative_center[1] = self.offset[1] // CHUNK_HEIGHT_PIX

    def render(self):
        """Render the editor + grid"""
        if self.dirty:
            self.set_all_dirty()
            self.image.fill(self.back_color)
            print("Editor.py       | ", self.object_id, self.rect)
            window.get_framebuffer().blit(self.image, self.rect.topleft)
            # self.render_world(self.relative_center)
            state.CURRENT.dirty = True
            self.dirty = False


    # ------------ rendering world ------------- #

    def render_world(self, rel_center: tuple, offset: tuple = (0, 0)) -> None:
        """Render the world with the set render distance | include a center"""
        for cx in range(rel_center[0] - self.render_distance, rel_center[0] + self.render_distance + 1):
            for cy in range(rel_center[1] - self.render_distance, rel_center[1] + self.render_distance + 1):
                if self.world.get_chunk(cx, cy):
                    self.render_chunk(self.world.get_chunk(cx, cy), offset)

    def render_chunk(self, chunk, offset: tuple = (0, 0)) -> None:
        """Renders all the grid tiles and non tile objects"""
        for x in range(CHUNK_WIDTH):
            for y in range(CHUNK_HEIGHT):
                # get block data
                self.tile_map[y][x].render(chunk.images, offset=offset)
