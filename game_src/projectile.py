"""
Projectile classes for tower defense game
"""
import pygame
import math
from config import *

class Projectile:
    """Projectile that moves toward target enemy"""
    def __init__(self, x, y, target, damage, speed, tower_type="arrow", splash_radius=0, piercing=False, poison_dmg=0, poison_dur=0, burn_dmg=0, burn_dur=0):
        self.position = pygame.math.Vector2(x, y)
        self.target = target
        self.damage = damage
        self.speed = speed
        self.active = True
        self.radius = 5
        self.tower_type = tower_type
        self.splash_radius = splash_radius  # AOE damage radius
        self.piercing = piercing  # For railgun
        self.poison_dmg = poison_dmg
        self.poison_dur = poison_dur
        self.burn_dmg = burn_dmg
        self.burn_dur = burn_dur
        self.hit_enemies = []  # For splash damage and piercing
        self.all_enemies = []  # Reference to all enemies for splash damage
        
    def update(self, all_enemies=None):
        """Move projectile toward target"""
        if not self.target.alive:
            self.active = False
            return
        
        direction = self.target.position - self.position
        distance = direction.length()
        
        # Railgun piercing - check for enemies along the path
        if self.piercing and all_enemies and distance > 0:
            for enemy in all_enemies:
                if enemy.alive and enemy not in self.hit_enemies:
                    # Check if enemy is close to projectile path
                    enemy_dist = enemy.position.distance_to(self.position)
                    if enemy_dist <= enemy.radius + 5:
                        enemy.take_damage(self.damage)
                        self.hit_enemies.append(enemy)
        
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
            elif self.tower_type == "poison":
                # Poison tower: DOT effect
                self.target.take_damage(self.damage, poison_dmg=self.poison_dmg, poison_dur=self.poison_dur)
            elif self.tower_type == "flamethrower":
                # Flamethrower: burn DOT
                self.target.take_damage(self.damage, burn_dmg=self.burn_dmg, burn_dur=self.burn_dur)
            elif self.tower_type == "railgun":
                # Railgun: final hit on target
                if self.target not in self.hit_enemies:
                    self.target.take_damage(self.damage)
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
            elif self.tower_type == "drone_swarm":
                color = (150, 150, 200)
            elif self.tower_type == "railgun":
                color = (0, 255, 255)
                # Draw longer projectile for railgun
                self.radius = 7
            elif self.tower_type == "flamethrower":
                color = (255, 69, 0)
            elif self.tower_type == "poison":
                color = (0, 200, 0)
            
            pygame.draw.circle(screen, color,
                             (int(self.position.x), int(self.position.y)),
                             self.radius)
