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
        elif enemy_type == "summoner":
            self.max_health = int(200 * difficulty_mult)
            self.speed = 1
            self.reward = 80
            self.color = (200, 50, 200)  # Magenta
            self.radius = 18
            self.is_air = False
            self.shield = 0
            self.splits = False
            self.is_summoner = True
            self.can_summon = True
            self.summon_timer = 0
            self.summon_delay = 180  # Spawn every 3 seconds
        elif enemy_type == "flying_fortress":
            self.max_health = int(500 * difficulty_mult)
            self.speed = 0.7
            self.reward = 150
            self.color = (100, 100, 200)  # Light blue-gray
            self.radius = 25
            self.is_air = True
            self.shield = 0
            self.splits = False
            self.is_fortress = True
            self.spawns_units = True
            self.spawn_timer = 0
            self.spawn_delay = 240  # Spawn ground units every 4 seconds
        elif enemy_type == "decoy":
            self.max_health = int(80 * difficulty_mult)
            self.speed = 2.5
            self.reward = 40
            self.color = (255, 192, 203)  # Pink
            self.radius = 14
            self.is_air = False
            self.shield = 0
            self.splits = False
            self.is_decoy = True
            self.is_real = True  # Only one will be real
            self.decoy_split_chance = 0.3  # 30% chance per hit
            self.decoys_spawned = False
        elif enemy_type == "decoy_fake":
            # Fake decoy enemy
            self.max_health = int(1 * difficulty_mult)  # Dies in one hit
            self.speed = 2.5
            self.reward = 0
            self.color = (255, 192, 203, 128)  # Semi-transparent pink
            self.radius = 14
            self.is_air = False
            self.shield = 0
            self.splits = False
            self.is_decoy = True
            self.is_real = False
            self.decoy_split_chance = 0
            self.decoys_spawned = True
            self.parent_decoy = None  # Reference to the real decoy
        elif enemy_type == "swarm":
            self.max_health = int(10 * difficulty_mult)
            self.speed = 3
            self.reward = 5
            self.color = (150, 75, 0)  # Brown
            self.radius = 8
            self.is_air = False
            self.shield = 0
            self.splits = False
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
        self.is_summoner = hasattr(self, 'is_summoner') and self.is_summoner
        self.is_fortress = hasattr(self, 'is_fortress') and self.is_fortress
        self.is_decoy = hasattr(self, 'is_decoy') and self.is_decoy
        self.slow_effect = 1.0  # Multiplier for speed (1.0 = normal, 0.5 = half speed)
        self.slow_timer = 0  # Duration of slow effect
        self.poison_damage = 0  # DOT from poison
        self.poison_timer = 0  # Duration of poison effect
        self.burn_damage = 0  # DOT from flamethrower
        self.burn_timer = 0  # Duration of burn effect
        
    def move(self, barrier_grid=None):
        """Move enemy toward next waypoint, checking for barriers"""
        if self.waypoint_index >= len(self.waypoints):
            self.reached_end = True
            return
        
        target = pygame.math.Vector2(self.waypoints[self.waypoint_index])
        direction = target - self.position
        distance = direction.length()
        
        # Apply slow effect to speed
        effective_speed = self.speed * self.slow_effect
        
        if distance <= effective_speed:
            # Check if next waypoint cell has a barrier
            next_x = int(target.x // GRID_SIZE)
            next_y = int(target.y // GRID_SIZE)
            
            if barrier_grid and 0 <= next_x < len(barrier_grid) and 0 <= next_y < len(barrier_grid[0]):
                barrier = barrier_grid[next_x][next_y]
                if isinstance(barrier, type(self)) and hasattr(barrier, 'alive'):  # Check if it's a Barrier object
                    # Barrier blocks movement, damage it instead
                    barrier.take_damage(effective_speed * 2)  # Damage based on speed
                    return  # Don't move
            
            self.position = target
            self.waypoint_index += 1
            if self.waypoint_index >= len(self.waypoints):
                self.reached_end = True
        elif distance > 0:
            # Check if moving to next position would hit a barrier
            direction_norm = direction.normalize()
            next_pos = self.position + direction_norm * effective_speed
            next_grid_x = int(next_pos.x // GRID_SIZE)
            next_grid_y = int(next_pos.y // GRID_SIZE)
            
            if barrier_grid and 0 <= next_grid_x < len(barrier_grid) and 0 <= next_grid_y < len(barrier_grid[0]):
                barrier = barrier_grid[next_grid_x][next_grid_y]
                # Check if it's a Barrier object (has alive attribute)
                if barrier is not None and not isinstance(barrier, str) and hasattr(barrier, 'alive') and barrier.alive:
                    # Hit a barrier, damage it instead of moving
                    barrier.take_damage(effective_speed * 2)
                    return  # Don't move
            
            self.position += direction_norm * effective_speed
    
    def take_damage(self, damage, slow_effect=None, slow_duration=0, poison_dmg=0, poison_dur=0, burn_dmg=0, burn_dur=0):
        """Reduce enemy health, accounting for shields and apply effects"""
        # Check for decoy split on hit
        if self.is_decoy and self.is_real and not self.decoys_spawned:
            import random
            if random.random() < self.decoy_split_chance:
                self.decoys_spawned = True
                # Will spawn decoys in wave update
                self.should_spawn_decoys = True
        
        if self.shield > 0:
            self.shield -= 1
            # Shield blocks damage but still counts as hit
            return False  # Indicates shield absorbed hit
        else:
            self.health -= damage
            if self.health <= 0:
                self.alive = False
            
            # Apply slow effect if provided (from freeze tower)
            if slow_effect is not None and slow_duration > 0:
                self.slow_effect = slow_effect
                self.slow_timer = slow_duration
            
            # Apply poison DOT
            if poison_dmg > 0 and poison_dur > 0:
                self.poison_damage = poison_dmg
                self.poison_timer = poison_dur
            
            # Apply burn DOT
            if burn_dmg > 0 and burn_dur > 0:
                self.burn_damage = burn_dmg
                self.burn_timer = burn_dur
            
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
    
    def update(self, barrier_grid=None):
        """Update enemy state"""
        if self.alive and not self.reached_end:
            self.move(barrier_grid)
            
            # Update slow effect timer
            if self.slow_timer > 0:
                self.slow_timer -= 1
                if self.slow_timer <= 0:
                    self.slow_effect = 1.0  # Reset to normal speed
            
            # Apply poison DOT
            if self.poison_timer > 0:
                self.health -= self.poison_damage
                self.poison_timer -= 1
                if self.health <= 0:
                    self.alive = False
            
            # Apply burn DOT
            if self.burn_timer > 0:
                self.health -= self.burn_damage
                self.burn_timer -= 1
                if self.health <= 0:
                    self.alive = False
            
            # Summoner spawning
            if self.is_summoner and hasattr(self, 'summon_timer'):
                self.summon_timer += 1
                if self.summon_timer >= self.summon_delay:
                    self.summon_timer = 0
                    self.should_summon = True  # Flag for wave to spawn minion
            
            # Flying Fortress spawning
            if self.is_fortress and hasattr(self, 'spawn_timer'):
                self.spawn_timer += 1
                if self.spawn_timer >= self.spawn_delay:
                    self.spawn_timer = 0
                    self.should_spawn_ground = True  # Flag for wave to spawn ground unit
            
            # Boss shield regeneration
            if self.is_boss and self.shield < 5:
                self.shield_regen_timer += 1
                if self.shield_regen_timer >= self.shield_regen_delay:
                    self.shield = min(5, self.shield + 1)
                    self.shield_regen_timer = 0
