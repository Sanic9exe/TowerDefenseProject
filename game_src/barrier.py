"""
Buildable barriers for path extension in tower defense game
"""
import pygame
from config import *

class Barrier:
    """Buildable barrier that enemies can damage"""
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.position = pygame.math.Vector2(grid_x * GRID_SIZE + GRID_SIZE // 2,
                                            grid_y * GRID_SIZE + GRID_SIZE // 2)
        self.max_health = 300  # Buffed from 200
        self.health = self.max_health
        self.alive = True
        self.cost = 50
        self.color = BROWN
        
    def take_damage(self, damage):
        """Barrier takes damage from enemies"""
        self.health -= damage
        if self.health <= 0:
            self.alive = False
    
    def draw(self, screen):
        """Draw barrier with health bar"""
        if not self.alive:
            return
        
        # Draw barrier
        barrier_rect = pygame.Rect(self.grid_x * GRID_SIZE + 5,
                                   self.grid_y * GRID_SIZE + 5,
                                   GRID_SIZE - 10, GRID_SIZE - 10)
        
        # Color fades from brown to red as health decreases
        health_percent = self.health / self.max_health
        barrier_color = (
            int(BROWN[0] + (RED[0] - BROWN[0]) * (1 - health_percent)),
            int(BROWN[1] * health_percent),
            int(BROWN[2] * health_percent)
        )
        pygame.draw.rect(screen, barrier_color, barrier_rect)
        pygame.draw.rect(screen, BLACK, barrier_rect, 2)
        
        # Draw health bar
        health_bar_width = GRID_SIZE - 10
        health_bar_height = 4
        health_percentage = self.health / self.max_health
        
        # Health bar background (red)
        health_bar_x = int(self.position.x - health_bar_width / 2)
        health_bar_y = int(self.position.y + GRID_SIZE // 2 - 15)
        pygame.draw.rect(screen, RED, 
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health bar foreground (green)
        pygame.draw.rect(screen, GREEN,
                        (health_bar_x, health_bar_y, 
                         int(health_bar_width * health_percentage), health_bar_height))
        
        # Draw "wall" icon
        font = pygame.font.Font(None, 24)
        text = font.render("█", True, BLACK)
        screen.blit(text, (self.position.x - 6, self.position.y - 12))
