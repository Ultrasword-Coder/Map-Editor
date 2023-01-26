
import pygame

def multiply_rects(a, b):
    return pygame.Rect(a.x * b.x, a.y * b.y, a.w * b.w, a.y * b.y)

