"""
Utility items - Time Warp and other consumables
"""
import pygame
from config import *

class TimeWarp:
    """Time warp utility - slows enemies in an area temporarily"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 150  # Effect radius
        self.duration = 180  # 3 seconds at 60 FPS
        self.timer = 0
        self.active = True
        self.slow_factor = 0.3  # Enemies move at 30% speed
    
    def update(self):
        """Update time warp effect"""
        if self.active:
            self.timer += 1
            if self.timer >= self.duration:
                self.active = False
        return self.active
    
    def affects_enemy(self, enemy):
        """Check if enemy is within time warp radius"""
        if not self.active:
            return False
        
        dx = enemy.position.x - self.x
        dy = enemy.position.y - self.y
        distance = (dx * dx + dy * dy) ** 0.5
        return distance <= self.radius
    
    def draw(self, screen):
        """Draw time warp effect"""
        if self.active:
            # Draw pulsing circle
            pulse = int(10 * (1 + 0.3 * (self.timer % 30) / 30))
            # Outer circle
            pygame.draw.circle(screen, (100, 100, 255), (int(self.x), int(self.y)), self.radius, 2)
            # Inner pulsing circle
            pygame.draw.circle(screen, (150, 150, 255), (int(self.x), int(self.y)), self.radius - pulse, 1)
            # Center indicator
            pygame.draw.circle(screen, (50, 50, 200), (int(self.x), int(self.y)), 10)
