"""
editor.py

- contains Editor object
- allows for tilemap editing
- extends off the world.World object from engine

"""
import pygame

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
        self.viewport_float_rect = None
        self.viewport_rect = None
        self.viewport = filehandler.make_surface(0, 0)

        self.mouse_world_tile_pos = [0, 0]
        self.mouse_world_chunk_pos = [0, 0]
        self.mouse_chunk_tile_pos = [0, 0]
        self.move_speed = 200

        # init
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
            self.relative_center[0] = self.offset[0] // CHUNK_WIDTH_PIX
            self.relative_center[1] = self.offset[1] // CHUNK_HEIGHT_PIX

            self.dirty = True
            
            # get world tile position
            mpos = self.get_rel_pos(window.mouse_window_to_framebuffer(user_input.get_mouse_pos()))
            self.mouse_world_tile_pos[0] = int((mpos[0] + self.viewport_rect.x - self.offset[0]) // CHUNK_TILE_WIDTH)
            self.mouse_world_tile_pos[1] = int((mpos[1] + self.viewport_rect.y - self.offset[1]) // CHUNK_TILE_HEIGHT)

            # get chunk position
            self.mouse_world_chunk_pos[0] = self.mouse_world_tile_pos[0] // CHUNK_WIDTH
            self.mouse_world_chunk_pos[1] = self.mouse_world_tile_pos[1] // CHUNK_HEIGHT

            # get chunk tile position
            self.mouse_chunk_tile_pos[0] = self.mouse_world_tile_pos[0] % CHUNK_WIDTH
            self.mouse_chunk_tile_pos[1] = self.mouse_chunk_tile_pos[1] % CHUNK_HEIGHT

            # also check if clicked
            if self.is_clicked():
                print("clicked", self.mouse_world_tile_pos, self.mouse_world_chunk_pos, self.mouse_chunk_tile_pos)

    def render(self):
        """Render the editor + grid"""
        if self.dirty:
            self.set_all_dirty()
            self.image.fill(self.back_color)
            self.viewport.fill(Theme.EDITOR)
            # print("Editor.py       | ", self.object_id, self.rect, self.viewport_rect)
            
            # draw debug
            rel_pos = self.get_rel_pos(user_input.get_mouse_pos())
            draw.DRAW_CIRCLE(self.viewport, (0, 0, 255), (rel_pos[0] - self.viewport_rect.x, 
                    rel_pos[1] - self.viewport_rect.y), CHUNK_TILE_WIDTH//2)
            draw.DRAW_CIRCLE(self.viewport, (255, 0, 0), (rel_pos[0] - self.viewport_rect.x + self.offset[0], 
                    rel_pos[1] - self.viewport_rect.y + self.offset[1]), CHUNK_TILE_WIDTH//2)
            draw.DRAW_CIRCLE(self.viewport, (0, 255, 255), (CHUNK_TILE_WIDTH // 2 + self.offset[0], CHUNK_TILE_HEIGHT // 2 + self.offset[1]), CHUNK_TILE_WIDTH//2)
            # draw viewport
            self.image.blit(self.viewport, self.viewport_rect.topleft)
            self.render_grid()
            window.get_framebuffer().blit(self.image, self.rect.topleft)

            # render world
            # self.render_world(self.relative_center)
            
            # set dirty
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
        
    def render_grid(self):
        """Render the grid onto the viewport"""
        linex = self.viewport_rect.w // CHUNK_TILE_WIDTH + 1
        liney = self.viewport_rect.h // CHUNK_TILE_HEIGHT + 1
        # render lines along with offset
        for x in range(linex):
            # draw the line
            lx = x * CHUNK_TILE_WIDTH + self.offset[0] % CHUNK_TILE_WIDTH
            draw.DEBUG_DRAW_LINE(self.image, (0, 0, 0), (lx, 0), (lx, self.viewport_rect.h + 20))
        
        for y in range(liney):
            # draw the line
            ly = y * CHUNK_TILE_HEIGHT + self.offset[1] % CHUNK_TILE_HEIGHT
            draw.DEBUG_DRAW_LINE(self.image, (0, 0, 0), (0, ly), (self.viewport_rect.w + 20, ly))
