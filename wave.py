"""
Wave system for spawning enemies
"""
import pygame
from config import *
from enemy import Enemy

class Wave:
    """Manages enemy waves"""
    def __init__(self, wave_number, waypoints):
        self.wave_number = wave_number
        self.waypoints = waypoints
        self.enemies = []
        self.spawn_queue = []
        self.spawn_timer = 0
        self.spawn_delay = 60  # frames between spawns
        self.completed = False
        
        # Generate wave based on wave number
        self._generate_wave()
    
    def _generate_wave(self):
        """Generate enemies for this wave"""
        # Wave difficulty scaling
        basic_count = 5 + self.wave_number * 2
        fast_count = max(0, self.wave_number - 2) * 2
        tank_count = max(0, (self.wave_number - 3) // 2)
        
        # Add enemies to spawn queue
        for _ in range(basic_count):
            self.spawn_queue.append("basic")
        for _ in range(fast_count):
            self.spawn_queue.append("fast")
        for _ in range(tank_count):
            self.spawn_queue.append("tank")
    
    def update(self):
        """Update wave state and spawn enemies"""
        if self.spawn_queue:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_delay:
                enemy_type = self.spawn_queue.pop(0)
                enemy = Enemy(self.waypoints, enemy_type)
                self.enemies.append(enemy)
                self.spawn_timer = 0
        elif not self.enemies:
            self.completed = True
        
        # Update all enemies
        for enemy in self.enemies[:]:
            if enemy.alive and not enemy.reached_end:
                enemy.update()
    
    def draw(self, screen):
        """Draw all enemies in wave"""
        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(screen)
    
    def get_active_enemies(self):
        """Get list of alive enemies"""
        return [e for e in self.enemies if e.alive and not e.reached_end]
    
    def get_escaped_enemies(self):
        """Get enemies that reached the end"""
        escaped = [e for e in self.enemies if e.reached_end]
        # Remove escaped enemies from list
        self.enemies = [e for e in self.enemies if not e.reached_end]
        return escaped
    
    def get_dead_enemies(self):
        """Get killed enemies for rewards"""
        dead = [e for e in self.enemies if not e.alive]
        # Remove dead enemies from list
        self.enemies = [e for e in self.enemies if e.alive]
        return dead
