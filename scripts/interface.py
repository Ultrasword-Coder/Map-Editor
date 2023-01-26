
import pygame

from . import misc
from soragl import physics, scene


# ------------------------------ #
# interface object

class InterfaceObject(physics.Entity):
    def __init__(self, rect:pygame.Rect=None):
        super().__init__()
        # private
        self._parent = None
        self._children = []
        self._rect = rect if not rect == None else pygame.Rect()
        # public
        self.surface = pygame.Surface(self._rect.size, 0, 32)
        # add to the world
        scene.SceneHandler.current_scene().add_entity(self)
        self.add_component(InterfaceComponent())
    
    def create_child(self, float_rect: pygame.Rect, components: list):
        """Create a child"""
        rrect = misc.multiply_rects(self._rect, float_rect)
        result = InterfaceObject(rrect)
        # parental
        result._parent = self
        self._children.append(result)
        # components
        for component in components:
            result.add_component(component)
        # return
        return result
    
    def get_parent(self):
        """Get the parent"""
        return self._parent
    
    def get_children(self):
        """Get the children"""
        return self._children
    
    def get_rect(self):
        """Get the rect"""
        return self._rect
    
    def set_rect(self, rect: pygame.Rect):
        """Set the rect"""
        self._rect = rect
    
    def get_position(self):
        """Get the position"""
        return self._rect.topleft
    
    def set_position(self, position: tuple):
        """Set the position"""
        self._rect.topleft = position
    
    def get_size(self):
        """Get the size"""
        return self._rect.area

    def set_size(self, size: tuple):
        """Set the size"""
        self._rect.area = size


# ------------------------------ #
# aspect

class InterfaceAspect(scene.Aspect):
    def __init__(self):
        super().__init__(InterfaceComponent)
    
    def update(self, entity):
        """Update the entity"""
        if not isinstance(entity, InterfaceObject): return
        # update the children
        for child in entity.get_children():
            self.update(child)
        # update the surface
        entity.surface.fill((0, 0, 0, 0))
        
        # update the rect
        entity.set_rect(pygame.Rect(entity.get_position(), entity.surface.get_size()))
        # update the parent
        if not entity.get_parent() == None:
            parent = entity.get_parent()
            parent.surface.blit(entity.surface, entity.get_rect())
            parent.set_rect(pygame.Rect(parent.get_position(), parent.surface.get_size()))


# ------------------------------ #
# components

class InterfaceComponent(scene.Component):
    def __init__(self):
        super().__init__()

    def update(self):
        """Update the component"""
        pass


