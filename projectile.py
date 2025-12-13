"""
Projectile classes for tower defense game
"""
import pygame
import math
from config import *

class Projectile:
    """Projectile that moves toward target enemy"""
    def __init__(self, x, y, target, damage, speed):
        self.position = pygame.math.Vector2(x, y)
        self.target = target
        self.damage = damage
        self.speed = speed
        self.active = True
        self.radius = 5
        
    def update(self):
        """Move projectile toward target"""
        if not self.target.alive:
            self.active = False
            return
        
        direction = self.target.position - self.position
        distance = direction.length()
        
        if distance <= self.speed:
            # Hit the target
            self.target.take_damage(self.damage)
            self.active = False
        else:
            direction = direction.normalize()
            self.position += direction * self.speed
    
    def draw(self, screen):
        """Draw projectile"""
        if self.active:
            pygame.draw.circle(screen, BLACK,
                             (int(self.position.x), int(self.position.y)),
                             self.radius)
