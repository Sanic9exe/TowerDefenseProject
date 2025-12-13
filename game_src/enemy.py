"""
Enemy classes for tower defense game
"""
import pygame
import math
from config import *

class Enemy:
    """Base enemy class"""
    def __init__(self, waypoints, enemy_type="basic", difficulty_mult=1.0):
        self.waypoints = waypoints
        self.waypoint_index = 0
        self.position = pygame.math.Vector2(waypoints[0])
        self.enemy_type = enemy_type
        
        # Enemy type determines stats
        if enemy_type == "basic":
            self.max_health = int(100 * difficulty_mult)
            self.speed = 2
            self.reward = 20
            self.color = RED
            self.radius = 15
            self.is_air = False
            self.shield = 0
            self.splits = False
        elif enemy_type == "fast":
            self.max_health = int(50 * difficulty_mult)
            self.speed = 4
            self.reward = 15
            self.color = YELLOW
            self.radius = 12
            self.is_air = False
            self.shield = 0
            self.splits = False
        elif enemy_type == "tank":
            self.max_health = int(300 * difficulty_mult)
            self.speed = 1
            self.reward = 50
            self.color = DARK_GRAY
            self.radius = 20
            self.is_air = False
            self.shield = 0
            self.splits = False
        elif enemy_type == "shielded":
            self.max_health = int(80 * difficulty_mult)
            self.speed = 2
            self.reward = 30
            self.color = BLUE
            self.radius = 15
            self.is_air = False
            self.shield = 3  # Blocks 3 hits
            self.splits = False
        elif enemy_type == "splitter":
            self.max_health = int(120 * difficulty_mult)
            self.speed = 1.5
            self.reward = 25
            self.color = (255, 128, 0)  # Orange
            self.radius = 16
            self.is_air = False
            self.shield = 0
            self.splits = True
        elif enemy_type == "air":
            self.max_health = int(60 * difficulty_mult)
            self.speed = 3
            self.reward = 35
            self.color = (100, 200, 255)  # Light blue
            self.radius = 13
            self.is_air = True
            self.shield = 0
            self.splits = False
        elif enemy_type == "boss":
            self.max_health = int(1000 * difficulty_mult)
            self.speed = 0.5
            self.reward = 200
            self.color = (128, 0, 128)  # Purple
            self.radius = 30
            self.is_air = False
            self.shield = 5
            self.splits = False
            self.is_boss = True
            self.shield_regen_timer = 0
            self.shield_regen_delay = 180  # Regen after 3 seconds
        else:
            # Default to basic
            self.max_health = int(100 * difficulty_mult)
            self.speed = 2
            self.reward = 20
            self.color = RED
            self.radius = 15
            self.is_air = False
            self.shield = 0
            self.splits = False
        
        self.health = self.max_health
        self.alive = True
        self.reached_end = False
        self.is_boss = enemy_type == "boss"
        
    def move(self):
        """Move enemy toward next waypoint"""
        if self.waypoint_index >= len(self.waypoints):
            self.reached_end = True
            return
        
        target = pygame.math.Vector2(self.waypoints[self.waypoint_index])
        direction = target - self.position
        distance = direction.length()
        
        if distance <= self.speed:
            self.position = target
            self.waypoint_index += 1
            if self.waypoint_index >= len(self.waypoints):
                self.reached_end = True
        elif distance > 0:
            direction = direction.normalize()
            self.position += direction * self.speed
    
    def take_damage(self, damage):
        """Reduce enemy health, accounting for shields"""
        if self.shield > 0:
            self.shield -= 1
            # Shield blocks damage but still counts as hit
            return False  # Indicates shield absorbed hit
        else:
            self.health -= damage
            if self.health <= 0:
                self.alive = False
            return True  # Indicates damage was dealt
    
    def draw(self, screen):
        """Draw enemy with health bar and shield indicator"""
        if not self.alive:
            return
        
        # Draw enemy circle
        pygame.draw.circle(screen, self.color, 
                          (int(self.position.x), int(self.position.y)), 
                          self.radius)
        
        # Draw shield indicator if present
        if self.shield > 0:
            pygame.draw.circle(screen, BLUE, 
                             (int(self.position.x), int(self.position.y)),
                             self.radius + 3, 2)
        
        # Draw boss indicator
        if self.is_boss:
            pygame.draw.circle(screen, YELLOW,
                             (int(self.position.x), int(self.position.y)),
                             self.radius + 5, 3)
        
        # Draw air unit indicator (wings)
        if self.is_air:
            wing_offset = 8
            pygame.draw.line(screen, WHITE,
                           (int(self.position.x - wing_offset), int(self.position.y)),
                           (int(self.position.x - wing_offset - 5), int(self.position.y - 5)), 2)
            pygame.draw.line(screen, WHITE,
                           (int(self.position.x + wing_offset), int(self.position.y)),
                           (int(self.position.x + wing_offset + 5), int(self.position.y - 5)), 2)
        
        # Draw health bar
        health_bar_width = 30 if not self.is_boss else 50
        health_bar_height = 5
        health_percentage = self.health / self.max_health
        
        # Health bar background (red)
        health_bar_x = int(self.position.x - health_bar_width / 2)
        health_bar_y = int(self.position.y - self.radius - 15)
        pygame.draw.rect(screen, RED, 
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health bar foreground (green)
        if self.max_health > 0:
            pygame.draw.rect(screen, GREEN,
                            (health_bar_x, health_bar_y, 
                             int(health_bar_width * health_percentage), health_bar_height))
    
    def update(self):
        """Update enemy state"""
        if self.alive and not self.reached_end:
            self.move()
            
            # Boss shield regeneration
            if self.is_boss and self.shield < 5:
                self.shield_regen_timer += 1
                if self.shield_regen_timer >= self.shield_regen_delay:
                    self.shield = min(5, self.shield + 1)
                    self.shield_regen_timer = 0
