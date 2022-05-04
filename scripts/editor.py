"""
editor.py

- contains Editor object
- allows for tilemap editing
- extends off the world.World object from engine

"""
import pygame

from engine import world, user_input, filehandler
from engine import draw, eventhandler, clock
from engine import window, state, handler, serialize
from engine.globals import *

from scripts import art, WindowObject
from scripts.globals import *


TILE_ART = 0
ENTITY_ART = 1



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
        self.world = state.State()

        # create a new pygame surface for the actual drawing area
        self.viewport_float_rect = None
        self.viewport_rect = None
        self.viewport = filehandler.make_surface(0, 0)

        self.mouse_world_tile_pos = [0, 0]
        self.mouse_world_chunk_pos = [0, 0]
        self.mouse_chunk_tile_pos = [0, 0]
        self.move_speed = 300
        self.prev_mouse_world_tile = [0, 0]

        self.brush = None
        self.art_type = TILE_ART

        art.set_current_editor(self)
        WindowObject.WindowObject.__init__(self, l, t, r, b, parent)
    
    def start(self):
        # create a new pygame surface for the actual drawing area
        self.viewport_float_rect = handler.Rect(0.01, 0.01, 0.99, 0.99)
        self.viewport_rect = handler.Rect(int(self.rect.w * self.viewport_float_rect.x), 
                                    int(self.rect.h * self.viewport_float_rect.y), 
                                    int((self.viewport_float_rect.w - self.viewport_float_rect.x) * self.rect.w), 
                                    int((self.viewport_float_rect.h - self.viewport_float_rect.y) * self.rect.h))
        self.viewport = filehandler.make_surface(int(self.viewport_rect.w), int(self.viewport_rect.h))

    def update(self, dt: float):
        """Update function"""
        # check if hovering
        if self.is_hovering():
            # global input commands for offset
            if user_input.is_key_pressed(pygame.K_RIGHT):
                self.offset[0] -= self.move_speed * dt
            if user_input.is_key_pressed(pygame.K_LEFT):
                self.offset[0] += self.move_speed * dt
            if user_input.is_key_pressed(pygame.K_DOWN):
                self.offset[1] -= self.move_speed * dt
            if user_input.is_key_pressed(pygame.K_UP):
                self.offset[1] += self.move_speed * dt
            # get user input
            self.relative_center[0] = int(-self.offset[0] // CHUNK_WIDTH_PIX)
            self.relative_center[1] = int(-self.offset[1] // CHUNK_HEIGHT_PIX)

            self.dirty = True
            
            # get world tile position
            mpos = self.get_rel_pos(user_input.get_mouse_pos())
            self.mouse_world_tile_pos[0] = int((mpos[0] - self.viewport_rect.x - self.offset[0]) // CHUNK_TILE_WIDTH)
            self.mouse_world_tile_pos[1] = int((mpos[1] - self.viewport_rect.y - self.offset[1]) // CHUNK_TILE_HEIGHT)

            # get chunk position
            self.mouse_world_chunk_pos[0] = self.mouse_world_tile_pos[0] // CHUNK_WIDTH
            self.mouse_world_chunk_pos[1] = self.mouse_world_tile_pos[1] // CHUNK_HEIGHT

            # get chunk tile position
            self.mouse_chunk_tile_pos[0] = self.mouse_world_tile_pos[0] % CHUNK_WIDTH
            self.mouse_chunk_tile_pos[1] = self.mouse_world_tile_pos[1] % CHUNK_HEIGHT
            # print(self.mouse_world_tile_pos, self.mouse_world_chunk_pos, self.mouse_chunk_tile_pos)

            #   get the relative position to viewport   convert to grid positions       add offset so that they stay in each tile
            # x = (rel_pos[0]-self.viewport_rect.x)//CHUNK_TILE_WIDTH*CHUNK_TILE_WIDTH+(self.offset[0]%CHUNK_TILE_WIDTH)
            # y = (rel_pos[1]-self.viewport_rect.y)//CHUNK_TILE_HEIGHT*CHUNK_TILE_HEIGHT+(self.offset[1]%CHUNK_TILE_HEIGHT)


            # for drawing
            if self.is_clicked() or (user_input.is_mouse_button_press(1) and self.prev_mouse_world_tile != self.mouse_world_tile_pos):
                self.prev_mouse_world_tile[0] = self.mouse_world_tile_pos[0]
                self.prev_mouse_world_tile[1] = self.mouse_world_tile_pos[1]
                # print("clicked", self.mouse_world_tile_pos, self.mouse_world_chunk_pos, self.mouse_chunk_tile_pos)
                if self.brush and self.brush.parent:
                    if not self.world.get_chunk(self.mouse_world_chunk_pos[0], self.mouse_world_chunk_pos[1]):
                        self.world.make_template_chunk(self.mouse_world_chunk_pos[0], self.mouse_world_chunk_pos[1])
                    self.brush.parent.add_to_grid(self.world.get_chunk(self.mouse_world_chunk_pos[0], self.mouse_world_chunk_pos[1]), 
                            {SIDEBAR_DATA_X: self.mouse_chunk_tile_pos[0], SIDEBAR_DATA_Y: self.mouse_chunk_tile_pos[1], SIDEBAR_DATA_IMG: self.brush.sprite_data.image_path})
            elif (user_input.is_mouse_button_press(3) and self.prev_mouse_world_tile != self.mouse_world_tile_pos):
                self.prev_mouse_world_tile[0] = self.mouse_world_tile_pos[0]
                self.prev_mouse_world_tile[1] = self.mouse_world_tile_pos[1]
                if not self.world.get_chunk(self.mouse_world_chunk_pos[0], self.mouse_world_chunk_pos[1]):
                    self.world.make_template_chunk(self.mouse_world_chunk_pos[0], self.mouse_world_chunk_pos[1])
                tile = self.world.get_chunk(self.mouse_world_chunk_pos[0], self.mouse_world_chunk_pos[1]).tile_map[self.mouse_chunk_tile_pos[1]][self.mouse_chunk_tile_pos[0]]
                tile.x = 0
                tile.y = 0
                tile.img = None
                tile.collide = 0
                tile.tilestats = None
                tile.data = {}

        # check if we should save
        if user_input.is_key_pressed(pygame.K_LCTRL) and user_input.is_key_clicked(pygame.K_s):
            print("SAVING LEVEL!")
            serialize.save_to_file("test.json", self.world.serialize())

    def render(self):
        """Render the editor + grid"""
        if self.dirty:
            self.set_all_dirty()
            self.image.fill(self.back_color)
            self.viewport.fill(Theme.EDITOR)
            # print("Editor.py       | ", self.object_id, self.rect, self.viewport_rect)
            
            # draw the world
            self.render_world(self.relative_center)

            # draw debug
            if self.brush:
                # TODO - polish the outline
                rel_pos = self.get_rel_pos(user_input.get_mouse_pos())
                relx = (rel_pos[0] - self.viewport_rect.x) // CHUNK_TILE_WIDTH * CHUNK_TILE_WIDTH
                rely = (rel_pos[1] - self.viewport_rect.y) // CHUNK_TILE_HEIGHT * CHUNK_TILE_HEIGHT
                
                # get the tile offset
                rox = self.offset[0] % CHUNK_TILE_WIDTH
                roy = self.offset[1] % CHUNK_TILE_HEIGHT
                self.brush.resized.set_alpha(100)
                self.viewport.blit(self.brush.resized, (relx+rox, rely+roy))
                self.brush.resized.set_alpha(255)
            draw.DRAW_CIRCLE(self.viewport, (0, 255, 255), (CHUNK_TILE_WIDTH // 2 + self.offset[0], CHUNK_TILE_HEIGHT // 2 + self.offset[1]), CHUNK_TILE_WIDTH//2)
            # draw viewport
            self.render_grid()
            self.image.blit(self.viewport, self.viewport_rect.topleft)
            window.get_framebuffer().blit(self.image, self.rect.topleft)

            # render world
            # self.render_world(self.relative_center)
            
            # set dirty
            state.CURRENT.dirty = True
            self.dirty = False

    # ------------ arting ---------------------- #

    def set_brush(self, new):
        """Set the brush"""
        self.brush = new
    
    def get_brush(self):
        """Get the brush"""
        return self.brush

    def file_dragged(self, file):
        """Load level from file"""
        print("Loading level... not rly")

    # ------------ rendering world ------------- #

    def render_world(self, rel_center: tuple) -> None:
        """Render the world with the set render distance | include a center"""
        for cx in range(rel_center[0] - self.world.r_distance, rel_center[0] + self.world.r_distance + 1):
            for cy in range(rel_center[1] - self.world.r_distance, rel_center[1] + self.world.r_distance + 1):
                if self.world.get_chunk(cx, cy):
                    self.render_chunk(self.world.get_chunk(cx, cy))

    def render_chunk(self, chunk) -> None:
        """Renders all the grid tiles and non tile objects"""
        for x in range(CHUNK_WIDTH):
            for y in range(CHUNK_HEIGHT):
                # get block data
                block = chunk.tile_map[y][x]
                if not block.img:
                    continue
                # render the block
                block.render(self.viewport, chunk.images, self.offset)
        
    def render_grid(self):
        """Render the grid onto the viewport"""
        linex = self.viewport_rect.w // CHUNK_TILE_WIDTH + 1
        liney = self.viewport_rect.h // CHUNK_TILE_HEIGHT + 1
        # render lines along with offset
        for x in range(linex):
            # draw the line
            lx = x * CHUNK_TILE_WIDTH + self.offset[0] % CHUNK_TILE_WIDTH
            draw.DEBUG_DRAW_LINE(self.viewport, (0, 0, 0), (lx, 0), (lx, self.viewport_rect.h + 20))
        
        for y in range(liney):
            # draw the line
            ly = y * CHUNK_TILE_HEIGHT + self.offset[1] % CHUNK_TILE_HEIGHT
            draw.DEBUG_DRAW_LINE(self.viewport, (0, 0, 0), (0, ly), (self.viewport_rect.w + 20, ly))
