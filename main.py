import pygame
import soragl
import struct

import tkinter as tk
from threading import Thread

from pygame import draw as pgdraw
from pygame import math as pgmath
from soragl import animation, scene, physics, base_objects

# ------------------------------ #
# setup tkinter


tkr = tk.Tk()
tkr.title("Sora Map Editor")
tkr.geometry("1280x720")

# adding widget lol
but = tk.Button(tkr, text="Hello", command=lambda x: print("hello world"))
but.pack()


# ------------------------------ #
# setup pygame

SORA = soragl.SoraContext.initialize({"fps": 30, "window_size": [1280, 720], 
            "window_flags": pygame.RESIZABLE | pygame.DOUBLEBUF, 
            "window_bits": 32, "framebuffer_flags": pygame.SRCALPHA, 
            "framebuffer_size": [1280//3, 720//3], "framebuffer_bits": 32,
            "debug": True})

SORA.create_context()


"""
TODO: what to do
1. ui rendering system
2. loading spritesheets --> from aseprite + also .json + also just an image with user input!
3. layers! + misc objects + collision shapes for objects
4. saving!
5. random objects / tags / labels / etc (with image icons)
"""

sc = scene.Scene(config=scene.load_config(scene.Scene.DEFAULT_CONFIG))
uilayer = scene.World(sc.get_config())
sc.add_layer(uilayer, 0)



# ------------------------------ #
# game loop
tkr_thread = Thread(target=tkr.mainloop, args=(), daemon=True)
tkr_thread.start()

def pygame_loop():
    global tkr
    SORA.start_engine_time()
    while SORA.RUNNING:
        SORA.refresh_buffers((0, 0, 255, 255))
        # pygame update + render
        registry.update()
        scene.SceneHandler.update()
        
        # push frame to tkinter -- only works in mac mode -- not yet for mgl
        SORA.push_framebuffer()
        # grab the window object
        image = tk.PhotoImage(width=SORA.WSIZE[0], height=SORA.WSIZE[1])
        image.put(pygame.image.tostring(SORA.WINDOW, 'RGB'), (0, 0))
        label = tk.Label(tkr, image=image)
        label.pack()

        # pygame.display.flip()
        # update events
        SORA.update_hardware()
        SORA.handle_pygame_events()
        # clock tick
        SORA.CLOCK.tick(SORA.FPS)
        SORA.update_time()
    pygame.quit()


tkr_thread.join()

