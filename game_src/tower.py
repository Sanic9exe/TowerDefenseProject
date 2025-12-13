"""
Tower classes for tower defense game
"""
import pygame
import math
from config import *
from projectile import Projectile

class Tower:
    """Base tower class"""
    def __init__(self, x, y, tower_type="arrow"):
        self.grid_x = x
        self.grid_y = y
        self.position = pygame.math.Vector2(x * GRID_SIZE + GRID_SIZE // 2,
                                            y * GRID_SIZE + GRID_SIZE // 2)
        self.tower_type = tower_type
        self.level = 1
        
        # Tower type determines stats
        if tower_type == "arrow":
            self.range = 150
            self.damage = 20
            self.fire_rate = 30  # frames between shots
            self.cost = 100
            self.upgrade_cost = 150
            self.color = DARK_GREEN
            self.projectile_speed = 8
        elif tower_type == "cannon":
            self.range = 120
            self.damage = 60
            self.fire_rate = 90
            self.cost = 200
            self.upgrade_cost = 300
            self.color = DARK_GRAY
            self.projectile_speed = 5
        elif tower_type == "laser":
            self.range = 180
            self.damage = 15
            self.fire_rate = 15
            self.cost = 300
            self.upgrade_cost = 450
            self.color = BLUE
            self.projectile_speed = 12
        
        self.cooldown = 0
        self.target = None
        self.selected = False
        
    def find_target(self, enemies):
        """Find closest enemy in range"""
        closest_enemy = None
        min_distance = float('inf')
        
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            distance = self.position.distance_to(enemy.position)
            if distance <= self.range and distance < min_distance:
                min_distance = distance
                closest_enemy = enemy
        
        return closest_enemy
    
    def shoot(self, target):
        """Create a projectile targeting the enemy"""
        if self.cooldown <= 0:
            self.cooldown = self.fire_rate
            return Projectile(self.position.x, self.position.y, 
                            target, self.damage, self.projectile_speed)
        return None
    
    def update(self, enemies):
        """Update tower state and shoot at enemies"""
        if self.cooldown > 0:
            self.cooldown -= 1
        
        # Find and shoot at target
        self.target = self.find_target(enemies)
        if self.target:
            return self.shoot(self.target)
        return None
    
    def upgrade(self):
        """Upgrade tower stats"""
        if self.level < 3:
            self.level += 1
            self.damage = int(self.damage * 1.5)
            self.range = int(self.range * 1.2)
            self.fire_rate = int(self.fire_rate * 0.8)
            old_cost = self.upgrade_cost
            self.upgrade_cost = int(self.upgrade_cost * 1.5)
            return old_cost
        return None
    
    def get_sell_value(self):
        """Get refund value for selling tower"""
        total_cost = self.cost
        # Calculate total investment including upgrades
        upgrade_cost = self.cost * 1.5  # First upgrade cost
        for i in range(1, self.level):
            total_cost += int(upgrade_cost)
            upgrade_cost = upgrade_cost * 1.5
        return int(total_cost * 0.75)
    
    def draw(self, screen):
        """Draw tower and range if selected"""
        # Draw tower
        tower_rect = pygame.Rect(self.grid_x * GRID_SIZE + 10,
                                self.grid_y * GRID_SIZE + 10,
                                GRID_SIZE - 20, GRID_SIZE - 20)
        pygame.draw.rect(screen, self.color, tower_rect)
        
        # Draw border
        border_color = YELLOW if self.selected else BLACK
        pygame.draw.rect(screen, border_color, tower_rect, 2)
        
        # Draw level indicator
        font = pygame.font.Font(None, 20)
        level_text = font.render(str(self.level), True, WHITE)
        screen.blit(level_text, (self.position.x - 5, self.position.y - 10))
        
        # Draw range circle if selected
        if self.selected:
            pygame.draw.circle(screen, YELLOW, 
                             (int(self.position.x), int(self.position.y)),
                             self.range, 2)
