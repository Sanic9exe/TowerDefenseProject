"""
Projectile classes for tower defense game
"""
import pygame
import math
from config import *

class Projectile:
    """Projectile that moves toward target enemy"""
    def __init__(self, x, y, target, damage, speed, tower_type="arrow"):
        self.position = pygame.math.Vector2(x, y)
        self.target = target
        self.damage = damage
        self.speed = speed
        self.active = True
        self.radius = 5
        self.tower_type = tower_type
        self.hit_enemies = []  # For splash damage
        
    def update(self):
        """Move projectile toward target"""
        if not self.target.alive:
            self.active = False
            return
        
        direction = self.target.position - self.position
        distance = direction.length()
        
        # Hit the target if close enough or at same position
        if distance <= self.speed:
            self.target.take_damage(self.damage)
            self.active = False
        elif distance > 0:
            # Only normalize if distance is non-zero
            direction = direction.normalize()
            self.position += direction * self.speed
    
    def draw(self, screen):
        """Draw projectile with type-specific colors"""
        if self.active:
            color = BLACK
            if self.tower_type == "laser":
                color = BLUE
            elif self.tower_type == "freeze":
                color = (100, 200, 255)
            elif self.tower_type == "splash":
                color = (255, 100, 0)
            elif self.tower_type == "cannon":
                color = DARK_GRAY
            
            pygame.draw.circle(screen, color,
                             (int(self.position.x), int(self.position.y)),
                             self.radius)
