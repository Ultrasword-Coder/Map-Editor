import pygame

import engine
from engine import window, clock, user_input, handler, draw
from engine import filehandler, maths, animation, state, serialize
from engine import spritesheet, eventhandler
from engine.globals import *

from scripts import WindowObject, SideBar, Editor
from scripts import art
from scripts.globals import *

# ------------------------- start up stuff ------------------------------ #

# create essential instances
window.create_instance("Map Editor", 1280, 720, f=pygame.RESIZABLE)
window.set_scaling(True)
# should use framebuffer!
window.change_framebuffer(1280, 720, pygame.SRCALPHA)

# ------------------------------ your code ------------------------------ #
FPS = 60 # change fps if needed

HANDLER = WindowObject.WindowObjectManager()
state.push_state(HANDLER)

container = WindowObject.WindowObject(0, 0, 1, 1)
container.set_background_color(Theme.BACKGROUND)

sidebar_container = container.create_child(0.005, 0.01, 0.38, 0.995, SideBar.SideBarContainer)
sidebar_container.set_secondary_color(Theme.SECONDARY)

child = sidebar_container.create_child(0.01, 0.01, 0.99, 0.99, SideBar.SideBar)
child.set_background_color(Theme.SECONDARY)
child.set_grid_spacing(10, 10)
child.set_columns(3)

sidebar_container.add_sidebar_object(child)

# item = child.create_child(0, 0, 0, 0, SideBar.SideBarObject)
# item.set_sprite("assets/art.png")
# item.set_grid_pos(1)
child.load_spritesheet("assets/spritesheets/grass.json")

editor = container.create_child(0.385, 0.01, 0.995, 0.995, Editor.Editor)
editor.set_background_color(Theme.SECONDARY)
art.set_current_editor(editor)

# ----------------------------------------------------------------------- #


clock.start(fps=FPS)
window.create_clock(clock.FPS)
running = True
while running:
    # updates
    if state.CURRENT:
        state.CURRENT.handle_entities(clock.delta_time)
        # render
        if state.CURRENT.dirty:
            window.push_buffer((0,0))
            pygame.display.flip()

    # update keyboard and mouse
    # print(window.mouse_window_to_framebuffer(user_input.get_mouse_pos()))
    user_input.update()
    eventhandler.update_events()
    # for loop through events
    for e in pygame.event.get():
        # handle different events
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            # keyboard press
            user_input.key_press(e)
        elif e.type == pygame.KEYUP:
            # keyboard release
            user_input.key_release(e)
        elif e.type == pygame.MOUSEMOTION:
            # mouse movement
            user_input.mouse_move_update(e)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            # mouse press
            user_input.mouse_button_press(e)
        elif e.type == pygame.MOUSEBUTTONUP:
            # mouse release
            user_input.mouse_button_release(e)
        elif e.type == pygame.WINDOWRESIZED:
            # window resized
            window.handle_resize(e)
            user_input.update_ratio(window.WIDTH, window.HEIGHT, window.ORIGINAL_WIDTH, window.ORIGINAL_HEIGHT)
        elif e.type == pygame.WINDOWMAXIMIZED:
            # window maximized
            window.get_instance().fill(Theme.BACKGROUND)
            # re render all entities
            HANDLER.render_all()
            # push frame
            pygame.display.update()
            # prevent re push
            window.INSTANCE_CHANGED = False

    # update clock -- calculate delta time
    clock.update()
    # update global clock - time sleep for vsync
    window.GLOBAL_CLOCK.tick(clock.FPS)

pygame.quit()