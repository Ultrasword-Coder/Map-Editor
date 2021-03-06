"""
Editor.py

- contains Editor object
- allows for tilemap editing
- extends off the world.World object from engine

"""
import threading

import pygame
import tkinter

from engine import world, user_input, filehandler
from engine import draw, eventhandler, clock
from engine import window, state, handler, serialize
from engine.globals import *

from scripts import art, WindowObject
from scripts.globals import *

TILE_ART = 0
ENTITY_ART = 1

TOGGLE_TILE_VIS = 0
TOGGLE_ENTITY_VIS = 1


class EntityEditorTab(WindowObject.WindowObject):
    """Editor to edit entities"""

    def __init__(self, l: float, t: float, r: float, b: float, parent):
        """EntityEditor constructor"""
        super().__init__(l, t, r, b, parent)
        self.rect.x = self.parent.rect.w * l
        self.rect.y = self.parent.rect.h * t
        self.rect.w = self.parent.rect.w * (r-l)
        self.rect.h = self.parent.rect.h *(b-t)
        self.image.fill(Theme.MINOR)

        state.CURRENT.remove_object(self.object_id)

        self.tk_root = tkinter.Tk()
        self.tk_root.winfo_toplevel().title("Entity Editor")

        self.tk_area = tkinter.Canvas(width=self.rect.w//2, height=self.rect.h//2)
        self.tk_area.pack()

        self.tk_area_sliders = [tkinter.Scale(self.tk_area, from_=0, to=500, orient=tkinter.HORIZONTAL) for i in range(2)]
        for i in range(2): self.tk_area_sliders[i].pack()

        self.tk_text_input = tkinter.Text(self.tk_root, height=5, width=20)
        self.tk_text_input.pack()

        def dosomething():
            print(self.tk_text_input.get(1.0, "end-1c"))

        self.tk_button = tkinter.Button(self.tk_root, text="Button", command=dosomething)
        self.tk_button.pack()

    def create_entity(self, mpos: tuple):
        """Create an Entity"""
        # h = handler.PersistentObject()
        # mpos = self.get_rel_pos(user_input.get_mouse_pos())
        # h.rect.area = (24, 24)
        # h.rect.center = (
        # mpos[0] - self.viewport_rect.x - self.offset[0], mpos[1] - self.viewport_rect.y - self.offset[1])
        # h.sprite = filehandler.scale(filehandler.get_image("assets/art.png"), (24, 24))
        # self.world.add_persist_entity(h)
        h = handler.PersistentObject()
        h.rect.area = self.get_are_chosen()

    def get_area_chosen(self):
        """Get area chosen from tkinter object"""


    def start(self):
        """Start function"""
        pass

    def update(self, dt):
        """Update the Entity Editor Tab"""
        try:
            self.tk_root.update()
        except:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        mpos = self.get_rel_pos(user_input.get_mouse_pos())

    def render(self, surface):
        """Render the Entity Editor Tab"""

        surface.blit(self.image, self.rect.topleft)


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

        self.tile_icon = filehandler.scale(filehandler.get_image(Theme.TILE_EDIT_ICON_PATH), (50, 50))
        self.entity_icon = filehandler.scale(filehandler.get_image(Theme.ENTITY_EDIT_ICON_PATH), (50, 50))
        self.blocked_icon = filehandler.scale(filehandler.get_image(Theme.BLOCKED_ICON_PATH), (50, 50))
        self.small_blocked_icon = filehandler.scale(self.blocked_icon, (30, 30))
        self.icon_render_position = (0, 0)

        # toggles
        self.toggles = [True, True]
        self.toggle_rects = []
        self.toggle_images = []

        # entity editor
        self.e_editor = None

        art.set_current_editor(self)
        super().__init__(l, t, r, b, parent)

    def start(self):
        # create a new pygame surface for the actual drawing area
        self.viewport_float_rect = handler.Rect(0.01, 0.01, 0.99, 0.99)
        self.viewport_rect = handler.Rect(int(self.rect.w * self.viewport_float_rect.x),
                                          int(self.rect.h * self.viewport_float_rect.y),
                                          int((self.viewport_float_rect.w - self.viewport_float_rect.x) * self.rect.w),
                                          int((self.viewport_float_rect.h - self.viewport_float_rect.y) * self.rect.h))
        self.viewport = filehandler.make_surface(int(self.viewport_rect.w), int(self.viewport_rect.h))

        # load some images
        self.toggle_rects.append(handler.Rect(self.rect.w * 0.91, 0, 30, 30).topleft)
        self.toggle_rects.append(handler.Rect(self.rect.w * 0.91 + 30, 0, 30, 30).topleft)

        img = filehandler.make_surface(30, 30, flags=filehandler.SRC_ALPHA)
        img.blit(filehandler.scale(filehandler.get_image(Theme.TILE_EDIT_ICON_PATH), (30, 30)), (0, 0))
        self.toggle_images.append(img)
        img = filehandler.make_surface(30, 30, flags=filehandler.SRC_ALPHA)
        img.blit(filehandler.scale(filehandler.get_image(Theme.ENTITY_EDIT_ICON_PATH), (30, 30)), (0, 0))
        self.toggle_images.append(img)

        # entiyt editor
        self.e_editor = EntityEditorTab(0.7, 0.7, 1.0, 1.0, self)

    def update(self, dt: float):
        """Update function"""
        self.e_editor.update(dt)

        # check if visibility for anything is toggled
        if user_input.is_key_pressed(UserInput.LCONTROL):
            if user_input.is_key_pressed(pygame.K_LSHIFT):
                if user_input.is_key_clicked(pygame.K_t):
                    # toggle visibility for tiles
                    self.toggles[TOGGLE_TILE_VIS] = not self.toggles[TOGGLE_TILE_VIS]
                    self.dirty = True
                if user_input.is_key_clicked(pygame.K_e):
                    # toggle visibility for entities
                    self.toggles[TOGGLE_ENTITY_VIS] = not self.toggles[TOGGLE_ENTITY_VIS]
                    self.dirty = True
            else:
                if user_input.is_key_clicked(pygame.K_t):
                    self.art_type = TILE_ART
                    print("[Editor.py] tile art time!")
                    self.dirty = True
                elif user_input.is_key_clicked(pygame.K_e):
                    self.art_type = ENTITY_ART
                    print("[Editor.py] entity art time!")
                    self.dirty = True
        # global input commands for offset
        if user_input.is_key_pressed(pygame.K_RIGHT):
            self.offset[0] -= self.move_speed * dt
            self.dirty = True
        if user_input.is_key_pressed(pygame.K_LEFT):
            self.offset[0] += self.move_speed * dt
            self.dirty = True
        if user_input.is_key_pressed(pygame.K_DOWN):
            self.offset[1] -= self.move_speed * dt
            self.dirty = True
        if user_input.is_key_pressed(pygame.K_UP):
            self.offset[1] += self.move_speed * dt
            self.dirty = True

        # check if hovering
        if self.is_hovering():
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

            # check if currently editing level or entities
            if self.art_type == TILE_ART:
                # level editirng
                if self.is_clicked() or (user_input.is_mouse_button_press(
                        1) and self.prev_mouse_world_tile != self.mouse_world_tile_pos):
                    self.prev_mouse_world_tile[0] = self.mouse_world_tile_pos[0]
                    self.prev_mouse_world_tile[1] = self.mouse_world_tile_pos[1]
                    # print("clicked", self.mouse_world_tile_pos, self.mouse_world_chunk_pos, self.mouse_chunk_tile_pos)
                    if self.brush and self.brush.parent:
                        if not self.world.get_chunk(self.mouse_world_chunk_pos[0], self.mouse_world_chunk_pos[1]):
                            self.world.make_template_chunk(self.mouse_world_chunk_pos[0], self.mouse_world_chunk_pos[1])
                        self.brush.parent.add_to_grid(
                            self.world.get_chunk(self.mouse_world_chunk_pos[0], self.mouse_world_chunk_pos[1]),
                            {SIDEBAR_DATA_X: self.mouse_chunk_tile_pos[0], SIDEBAR_DATA_Y: self.mouse_chunk_tile_pos[1],
                             SIDEBAR_DATA_IMG: self.brush.sprite_data.image_path})
                elif (user_input.is_mouse_button_press(3) and self.prev_mouse_world_tile != self.mouse_world_tile_pos):
                    self.prev_mouse_world_tile[0] = self.mouse_world_tile_pos[0]
                    self.prev_mouse_world_tile[1] = self.mouse_world_tile_pos[1]
                    if self.world.get_chunk(self.mouse_world_chunk_pos[0], self.mouse_world_chunk_pos[1]):
                        self.world.get_chunk(self.mouse_world_chunk_pos[0], self.mouse_world_chunk_pos[1]).tile_map[
                            self.mouse_chunk_tile_pos[1]][self.mouse_chunk_tile_pos[0]] = world.Tile(
                            self.mouse_chunk_tile_pos[0], self.mouse_world_tile_pos[1], None, 0)
            elif self.art_type == ENTITY_ART:
                if user_input.is_key_clicked(pygame.K_f):
                    self.e_editor.create_entity(self.get_rel_pos(user_input.get_mouse_pos()))
                    # h = handler.PersistentObject()
                    # mpos = self.get_rel_pos(user_input.get_mouse_pos())
                    # h.rect.area = (24, 24)
                    # h.rect.center = (
                    # mpos[0] - self.viewport_rect.x - self.offset[0], mpos[1] - self.viewport_rect.y - self.offset[1])
                    # h.sprite = filehandler.scale(filehandler.get_image("assets/art.png"), (24, 24))
                    # self.world.add_persist_entity(h)

        # check if we should save
        if user_input.is_key_pressed(UserInput.LCONTROL) and user_input.is_key_clicked(pygame.K_s):
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

            # render the toggle icons :)
            for i, val in enumerate(self.toggles):
                self.viewport.blit(self.toggle_images[i], self.toggle_rects[i])
                if not val:
                    self.viewport.blit(self.small_blocked_icon, self.toggle_rects[i])

            if self.art_type == TILE_ART:
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
                    self.viewport.blit(self.brush.resized, (relx + rox, rely + roy))
                    self.brush.resized.set_alpha(255)
            # draw.DRAW_CIRCLE(self.viewport, (0, 255, 255), (CHUNK_TILE_WIDTH // 2 + self.offset[0], CHUNK_TILE_HEIGHT // 2 + self.offset[1]), CHUNK_TILE_WIDTH//2)
            draw.DRAW_CIRCLE(self.viewport, (0, 255, 0), self.offset, CHUNK_TILE_WIDTH // 2)
            # draw viewport
            self.render_grid()

            # draw the icons onto the grid
            self.viewport.blit(self.tile_icon if self.art_type == TILE_ART else self.entity_icon,
                               self.icon_render_position)
            self.image.blit(self.viewport, self.viewport_rect.topleft)
            self.e_editor.render(self.image)
            window.get_framebuffer().blit(self.image, self.rect.topleft)
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

        data = None
        try:
            data = filehandler.get_json_data(file)
        except Exception as e:
            print(e)
            return False
        self.world = state.State.deserialize(data)

    # ------------ rendering world ------------- #

    def render_world(self, rel_center: tuple) -> None:
        """Render the world with the set render distance | include a center"""
        if self.toggles[TOGGLE_TILE_VIS]:
            for cx in range(rel_center[0] - self.world.r_distance, rel_center[0] + self.world.r_distance + 1):
                for cy in range(rel_center[1] - self.world.r_distance, rel_center[1] + self.world.r_distance + 1):
                    if self.world.get_chunk(cx, cy):
                        self.render_chunk(self.world.get_chunk(cx, cy))
        if self.toggles[TOGGLE_ENTITY_VIS]:
            self.render_entities()

    def render_entities(self):
        """Render the entities in the world"""
        for eid, entity in self.world.p_objects.items():
            # render entity
            if entity.sprite:
                self.viewport.blit(entity.sprite, (entity.rect.x + self.offset[0], entity.rect.y + self.offset[1]))

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
