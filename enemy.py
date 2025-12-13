"""
Enemy classes for tower defense game
"""
import pygame
import math
from config import *

class Enemy:
    """Base enemy class"""
    def __init__(self, waypoints, enemy_type="basic"):
        self.waypoints = waypoints
        self.waypoint_index = 0
        self.position = pygame.math.Vector2(waypoints[0])
        
        # Enemy type determines stats
        if enemy_type == "basic":
            self.max_health = 100
            self.speed = 2
            self.reward = 20
            self.color = RED
            self.radius = 15
        elif enemy_type == "fast":
            self.max_health = 50
            self.speed = 4
            self.reward = 15
            self.color = YELLOW
            self.radius = 12
        elif enemy_type == "tank":
            self.max_health = 300
            self.speed = 1
            self.reward = 50
            self.color = DARK_GRAY
            self.radius = 20
        
        self.health = self.max_health
        self.alive = True
        self.reached_end = False
        
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
        else:
            direction = direction.normalize()
            self.position += direction * self.speed
    
    def take_damage(self, damage):
        """Reduce enemy health"""
        self.health -= damage
        if self.health <= 0:
            self.alive = False
    
    def draw(self, screen):
        """Draw enemy with health bar"""
        if not self.alive:
            return
        
        # Draw enemy circle
        pygame.draw.circle(screen, self.color, 
                          (int(self.position.x), int(self.position.y)), 
                          self.radius)
        
        # Draw health bar
        health_bar_width = 30
        health_bar_height = 5
        health_percentage = self.health / self.max_health
        
        # Health bar background (red)
        health_bar_x = int(self.position.x - health_bar_width / 2)
        health_bar_y = int(self.position.y - self.radius - 10)
        pygame.draw.rect(screen, RED, 
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health bar foreground (green)
        pygame.draw.rect(screen, GREEN,
                        (health_bar_x, health_bar_y, 
                         int(health_bar_width * health_percentage), health_bar_height))
    
    def update(self):
        """Update enemy state"""
        if self.alive and not self.reached_end:
            self.move()
