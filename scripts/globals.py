import os
import sys
import pygame
# Window Object

WINDOW_OBJECT_TYPE = "windowObject"

# Sprite sheet stuff
SIDEBAR_SS_IMG = "ssimg"
SIDEBAR_SS_WIDTH = "sswidth"
SIDEBAR_SS_HEIGHT = "ssheight"
SIDEBAR_SS_TILES = "sstiles"
SIDEBAR_SS_XSPACE = "ssxspace"
SIDEBAR_SS_YSPACE = "ssyspace"

SIDEBAR_DATA_X = "sdata_x"
SIDEBAR_DATA_Y = "sdata_y"
SIDEBAR_DATA_IMG = "sdata_img"

CONFIG_PATH = "config.json"
CONFIG_FILES_ARRAY = "startup-files"


# color theme
class Theme:

    BACKGROUND = (23, 32, 42)
    SECONDARY = (0, 21, 37)
    TERTIARY = (0, 35, 61)

    MINOR = (43, 104, 146)

    EDITOR = (255, 255, 255)

    FONT_PATH = "assets/important/CONSOLA.TTF"
    TILE_EDIT_ICON_PATH = "assets/important/tile.png"
    ENTITY_EDIT_ICON_PATH = "assets/important/entity.png"
    
    BLOCKED_ICON_PATH = "assets/important/blocked.png"

    EDITOR_ENTITY_ICON = "assets/important/editor_entity.png"




# menu butons and stuff
class Menu:

    FILL = False
    ERASE = False


class UserInput:

    LCONTROL = pygame.K_LCTRL
    LALT = pygame.K_LALT
    RCONTROL = pygame.K_RCTRL
    RALT = pygame.K_RALT