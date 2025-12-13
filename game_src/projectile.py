"""
Projectile classes for tower defense game
"""
import pygame
import math
from config import *

class Projectile:
    """Projectile that moves toward target enemy"""
    def __init__(self, x, y, target, damage, speed, tower_type="arrow", splash_radius=0):
        self.position = pygame.math.Vector2(x, y)
        self.target = target
        self.damage = damage
        self.speed = speed
        self.active = True
        self.radius = 5
        self.tower_type = tower_type
        self.splash_radius = splash_radius  # AOE damage radius
        self.hit_enemies = []  # For splash damage
        self.all_enemies = []  # Reference to all enemies for splash damage
        
    def update(self, all_enemies=None):
        """Move projectile toward target"""
        if not self.target.alive:
            self.active = False
            return
        
        direction = self.target.position - self.position
        distance = direction.length()
        
        # Hit the target if close enough or at same position
        if distance <= self.speed:
            # Apply damage based on tower type
            if self.tower_type == "freeze":
                # Freeze tower: slow effect
                self.target.take_damage(self.damage, slow_effect=0.5, slow_duration=90)  # 1.5 seconds at 60 FPS
            elif self.tower_type == "splash" and self.splash_radius > 0 and all_enemies:
                # Splash tower: AOE damage to all enemies within splash radius
                impact_position = self.target.position
                enemies_hit = 0
                for enemy in all_enemies:
                    if enemy.alive:
                        distance_to_impact = enemy.position.distance_to(impact_position)
                        if distance_to_impact <= self.splash_radius:
                            enemy.take_damage(self.damage)
                            enemies_hit += 1
                # Store for visual effect (optional)
                self.splash_position = impact_position
            else:
                # Single target damage
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
                # Draw splash radius indicator for splash projectiles
                if self.splash_radius > 0:
                    pygame.draw.circle(screen, (255, 100, 0, 100),
                                     (int(self.position.x), int(self.position.y)),
                                     int(self.splash_radius * 0.3), 1)
            elif self.tower_type == "cannon":
                color = DARK_GRAY
            
            pygame.draw.circle(screen, color,
                             (int(self.position.x), int(self.position.y)),
                             self.radius)
