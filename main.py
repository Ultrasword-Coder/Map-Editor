import pygame

import engine
from engine import window, clock, user_input, handler, draw
from engine import filehandler, maths, animation, state, serialize
from engine import spritesheet, eventhandler
from engine.globals import *

from scripts import WindowObject, SideBar
from scripts.globals import *


# create essential instances
window.create_instance("Map Editor", 1280, 720, f=pygame.RESIZABLE)
window.set_scaling(True)
# should use framebuffer!
window.change_framebuffer(1920, 1080, pygame.SRCALPHA)

# ------------------------------ your code ------------------------------ #
FPS = 60 # change fps if needed

HANDLER = WindowObject.WindowObjectManager()
state.push_state(HANDLER)

container = WindowObject.WindowObject(0, 0, 1, 1)
container.set_background_color(Theme.BACKGROUND)

child = container.create_child(0.005, 0.01, 0.38, 0.995, SideBar.SideBar)
child.set_background_color(Theme.SECONDARY)
child.set_columns(3)

item = child.create_child(0, 0, 0, 0, SideBar.SideBarObject)
item.set_sprite("assets/art.png")

print(HANDLER.update_order)

# ----------------------------------------------------------------------- #


clock.start(fps=FPS)
window.create_clock(clock.FPS)
running = True
while running:

    # updates
    if state.CURRENT:
        state.CURRENT.update(clock.delta_time)
        # render
        if state.CURRENT.dirty:
            window.push_buffer((0,0))
            pygame.display.flip()

    # update keyboard and mouse
    # print(window.mouse_window_to_framebuffer(user_input.get_mouse_pos()))
    user_input.update()
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
            window.get_instance().fill(BACKGROUND)
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