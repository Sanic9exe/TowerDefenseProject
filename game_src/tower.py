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
        self.targeting_mode = "closest"  # Default targeting mode
        self.placed_time = pygame.time.get_ticks()
        self.has_fired = False
        
        # Tower type determines stats
        if tower_type == "arrow":
            self.range = 150
            self.damage = 20
            self.fire_rate = 30  # frames between shots
            self.cost = 100
            self.upgrade_cost = 150
            self.color = DARK_GREEN
            self.projectile_speed = 8
            self.can_hit_air = False
        elif tower_type == "cannon":
            self.range = 120
            self.damage = 60
            self.fire_rate = 90
            self.cost = 200
            self.upgrade_cost = 300
            self.color = DARK_GRAY
            self.projectile_speed = 5
            self.can_hit_air = False
        elif tower_type == "laser":
            self.range = 180
            self.damage = 15
            self.fire_rate = 15
            self.cost = 300
            self.upgrade_cost = 450
            self.color = BLUE
            self.projectile_speed = 12
            self.can_hit_air = True
        elif tower_type == "freeze":
            self.range = 140
            self.damage = 10
            self.fire_rate = 60
            self.cost = 250
            self.upgrade_cost = 375
            self.color = (100, 200, 255)  # Light blue
            self.projectile_speed = 10
            self.can_hit_air = False
            self.slow_effect = 0.5  # Slows enemies by 50%
        elif tower_type == "splash":
            self.range = 100
            self.damage = 40
            self.fire_rate = 100
            self.cost = 350
            self.upgrade_cost = 525
            self.color = (255, 100, 0)  # Orange
            self.projectile_speed = 4
            self.can_hit_air = False
            self.splash_radius = 60
        elif tower_type == "sniper":
            self.range = 250
            self.damage = 100
            self.fire_rate = 120
            self.cost = 400
            self.upgrade_cost = 600
            self.color = (50, 50, 50)  # Dark
            self.projectile_speed = 15
            self.can_hit_air = True
        elif tower_type == "drone":
            self.range = 200
            self.damage = 15
            self.fire_rate = 180  # Low spawn rate for drones
            self.cost = 500
            self.upgrade_cost = 750
            self.color = (150, 150, 200)  # Light purple
            self.projectile_speed = 6
            self.can_hit_air = True
            self.drone_lifetime = 600  # Drones last 10 seconds
        elif tower_type == "railgun":
            self.range = 350  # Ultra-long range
            self.damage = 80
            self.fire_rate = 150  # Long cooldown
            self.cost = 600
            self.upgrade_cost = 900
            self.color = (0, 255, 255)  # Cyan
            self.projectile_speed = 20
            self.can_hit_air = True
            self.piercing = True  # Hits multiple enemies
        elif tower_type == "flamethrower":
            self.range = 80  # Short range
            self.damage = 5  # Low damage per tick
            self.fire_rate = 5  # Continuous damage
            self.cost = 300
            self.upgrade_cost = 450
            self.color = (255, 69, 0)  # Orange-red
            self.projectile_speed = 8
            self.can_hit_air = False
            self.cone_angle = 45  # degrees
            self.dot_duration = 120  # Burn lasts 2 seconds
        elif tower_type == "poison":
            self.range = 150
            self.damage = 3  # Low initial damage
            self.fire_rate = 60
            self.cost = 350
            self.upgrade_cost = 525
            self.color = (0, 200, 0)  # Green
            self.projectile_speed = 7
            self.can_hit_air = False
            self.poison_damage = 2  # Damage per tick
            self.poison_duration = 180  # 3 seconds of DOT
        elif tower_type == "economy":
            self.range = 0  # No attack range
            self.damage = 0
            self.fire_rate = 60  # Generate money every second
            self.cost = 400
            self.upgrade_cost = 600
            self.color = (255, 215, 0)  # Gold
            self.projectile_speed = 0
            self.can_hit_air = False
            self.income_per_cycle = 5  # Generates $5 per second
        
        self.cooldown = 0
        self.target = None
        self.selected = False
        self.rotation_angle = 0  # For visual rotation
        self.target_angle = 0  # Angle to current target
        self.recoil_timer = 0  # For firing recoil animation
        self.charge_timer = 0  # For charge-up animation
        
    def find_target(self, enemies):
        """Find enemy based on targeting mode"""
        valid_enemies = []
        
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            # Check if tower can hit air units
            if enemy.is_air and not self.can_hit_air:
                continue
            
            distance = self.position.distance_to(enemy.position)
            if distance <= self.range:
                valid_enemies.append(enemy)
        
        if not valid_enemies:
            return None
        
        # Select target based on targeting mode
        if self.targeting_mode == "closest":
            return min(valid_enemies, key=lambda e: self.position.distance_to(e.position))
        elif self.targeting_mode == "strongest":
            return max(valid_enemies, key=lambda e: e.health)
        elif self.targeting_mode == "weakest":
            return min(valid_enemies, key=lambda e: e.health)
        elif self.targeting_mode == "first":
            return max(valid_enemies, key=lambda e: e.waypoint_index + 
                      (e.position.distance_to(pygame.math.Vector2(e.waypoints[e.waypoint_index])) 
                       if e.waypoint_index < len(e.waypoints) else 0) / 1000)
        elif self.targeting_mode == "last":
            return min(valid_enemies, key=lambda e: e.waypoint_index + 
                      (e.position.distance_to(pygame.math.Vector2(e.waypoints[e.waypoint_index]))
                       if e.waypoint_index < len(e.waypoints) else 0) / 1000)
        elif self.targeting_mode == "nearest_exit":
            # Calculate how far along the path each enemy is
            return max(valid_enemies, key=lambda e: e.waypoint_index)
        
        return valid_enemies[0] if valid_enemies else None
    
    def shoot(self, target):
        """Create a projectile targeting the enemy"""
        if self.cooldown <= 0:
            self.cooldown = self.fire_rate
            self.has_fired = True
            self.recoil_timer = 10  # Start recoil animation
            
            # Pass splash radius if this is a splash tower
            splash_radius = self.splash_radius if hasattr(self, 'splash_radius') else 0
            return Projectile(self.position.x, self.position.y, 
                            target, self.damage, self.projectile_speed, self.tower_type, splash_radius)
        return None
    
    def update(self, enemies):
        """Update tower state and shoot at enemies"""
        if self.cooldown > 0:
            self.cooldown -= 1
        
        # Update recoil animation
        if self.recoil_timer > 0:
            self.recoil_timer -= 1
        
        # Update charge animation (for laser and sniper)
        if self.tower_type in ["laser", "sniper"]:
            if self.cooldown > self.fire_rate * 0.8:
                self.charge_timer = min(10, self.charge_timer + 1)
            else:
                self.charge_timer = max(0, self.charge_timer - 1)
        
        # Find and shoot at target
        self.target = self.find_target(enemies)
        if self.target:
            # Update rotation to face target
            dx = self.target.position.x - self.position.x
            dy = self.target.position.y - self.position.y
            self.target_angle = math.atan2(dy, dx)
            
            # Smooth rotation
            angle_diff = self.target_angle - self.rotation_angle
            # Normalize angle difference to -pi to pi
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            self.rotation_angle += angle_diff * 0.3  # Smooth rotation speed
            
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
        
        # Full refund if sold within 5 seconds and hasn't fired
        time_since_placed = (pygame.time.get_ticks() - self.placed_time) / 1000.0
        if time_since_placed < 5 and not self.has_fired:
            return total_cost
        # Higher refund if never fired
        elif not self.has_fired:
            return int(total_cost * 0.9)
        # Normal refund
        return int(total_cost * 0.75)
    
    def cycle_targeting_mode(self):
        """Cycle to next targeting mode"""
        current_index = TARGETING_MODES.index(self.targeting_mode)
        self.targeting_mode = TARGETING_MODES[(current_index + 1) % len(TARGETING_MODES)]
    
    def draw(self, screen):
        """Draw tower with animations"""
        # Calculate recoil offset
        recoil_offset = self.recoil_timer if self.recoil_timer > 0 else 0
        
        # Draw tower base
        tower_rect = pygame.Rect(self.grid_x * GRID_SIZE + 10,
                                self.grid_y * GRID_SIZE + 10,
                                GRID_SIZE - 20, GRID_SIZE - 20)
        pygame.draw.rect(screen, self.color, tower_rect)
        
        # Draw border
        border_color = YELLOW if self.selected else BLACK
        pygame.draw.rect(screen, border_color, tower_rect, 2)
        
        # Draw barrel/turret that rotates
        if self.target:
            barrel_length = 15 - recoil_offset  # Recoil effect
            barrel_end_x = self.position.x + math.cos(self.rotation_angle) * barrel_length
            barrel_end_y = self.position.y + math.sin(self.rotation_angle) * barrel_length
            
            # Draw barrel
            pygame.draw.line(screen, BLACK, 
                           (int(self.position.x), int(self.position.y)),
                           (int(barrel_end_x), int(barrel_end_y)), 4)
            
            # Draw barrel tip
            pygame.draw.circle(screen, BLACK, (int(barrel_end_x), int(barrel_end_y)), 3)
        
        # Draw charge effect for laser/sniper
        if self.charge_timer > 0 and self.tower_type in ["laser", "sniper"]:
            charge_color = BLUE if self.tower_type == "laser" else RED
            charge_radius = 5 + self.charge_timer
            pygame.draw.circle(screen, charge_color, 
                             (int(self.position.x), int(self.position.y)),
                             charge_radius, 1)
        
        # Draw level indicator
        font = pygame.font.Font(None, 20)
        level_text = font.render(str(self.level), True, WHITE)
        screen.blit(level_text, (self.position.x - 5, self.position.y - 10))
        
        # Draw targeting mode indicator (first letter) when selected
        if self.selected:
            mode_abbr = self.targeting_mode[0].upper()
            mode_font = pygame.font.Font(None, 16)
            mode_text = mode_font.render(mode_abbr, True, YELLOW)
            screen.blit(mode_text, (self.position.x + 15, self.position.y - 20))
        
        # Draw range circle if selected
        if self.selected:
            pygame.draw.circle(screen, YELLOW, 
                             (int(self.position.x), int(self.position.y)),
                             self.range, 2)
