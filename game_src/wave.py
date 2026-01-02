"""
Wave system for spawning enemies
"""
import pygame
import random
from config import *
from enemy import Enemy

class Wave:
    """Manages enemy waves"""
    def __init__(self, wave_number, waypoints, difficulty="normal", is_endless=False):
        self.wave_number = wave_number
        self.waypoints = waypoints
        self.enemies = []
        self.spawn_queue = []
        self.spawn_timer = 0
        self.spawn_delay = 60  # frames between spawns
        self.completed = False
        self.difficulty = difficulty
        self.is_endless = is_endless
        self.is_boss_wave = (wave_number % 5 == 0)  # Boss every 5 waves
        
        # Generate wave based on wave number
        self._generate_wave()
    
    def _generate_wave(self):
        """Generate enemies for this wave"""
        
        # Boss wave
        if self.is_boss_wave:
            self.spawn_queue.append("boss")
            # Add some minions with boss
            minion_count = 5 + self.wave_number // 2
            for _ in range(minion_count):
                self.spawn_queue.append(random.choice(["basic", "fast"]))
            return
        
        # Endless mode with random scaling
        if self.is_endless:
            total_enemies = 10 + self.wave_number * 3
            for _ in range(total_enemies):
                enemy_type = random.choices(
                    ["basic", "fast", "tank", "shielded", "splitter"],
                    weights=[30, 25, 20, 15, 10]
                )[0]
                self.spawn_queue.append(enemy_type)
            # Add air units in hard mode or after wave 10
            if self.difficulty == "hard" or self.wave_number > 10:
                air_count = max(1, self.wave_number // 3)
                for _ in range(air_count):
                    self.spawn_queue.append("air")
            return
        
        # Normal wave difficulty scaling
        basic_count = 5 + self.wave_number * 2
        fast_count = max(0, self.wave_number - 2) * 2
        tank_count = max(0, (self.wave_number - 3) // 2)
        shielded_count = max(0, self.wave_number - 4)
        splitter_count = max(0, (self.wave_number - 5) // 2)
        
        # Add enemies to spawn queue
        for _ in range(basic_count):
            self.spawn_queue.append("basic")
        for _ in range(fast_count):
            self.spawn_queue.append("fast")
        for _ in range(tank_count):
            self.spawn_queue.append("tank")
        for _ in range(shielded_count):
            self.spawn_queue.append("shielded")
        for _ in range(splitter_count):
            self.spawn_queue.append("splitter")
        
        # Add air units after wave 18 in all modes (not just hard mode)
        if self.wave_number >= 18:
            air_count = max(1, (self.wave_number - 17) // 2)
            for _ in range(air_count):
                self.spawn_queue.append("air")
        
        # Add new advanced enemies after wave 18
        if self.wave_number >= 18:
            summoner_count = max(0, (self.wave_number - 18) // 3)
            fortress_count = max(0, (self.wave_number - 20) // 4)
            decoy_count = max(1, (self.wave_number - 18) // 2)
            swarm_count = max(0, (self.wave_number - 19) // 2)
            
            for _ in range(summoner_count):
                self.spawn_queue.append("summoner")
            for _ in range(fortress_count):
                self.spawn_queue.append("flying_fortress")
            for _ in range(decoy_count):
                self.spawn_queue.append("decoy")
            # Swarms spawn in groups
            if swarm_count > 0:
                for _ in range(swarm_count):
                    # Each swarm is 5-10 tiny enemies
                    num_swarm = random.randint(5, 10)
                    for _ in range(num_swarm):
                        self.spawn_queue.append("swarm")
        
        # Shuffle for variety
        random.shuffle(self.spawn_queue)
    
    def update(self, barrier_grid=None):
        """Update wave state and spawn enemies"""
        if self.spawn_queue:
            self.spawn_timer += 1
            # Boss spawns slower
            delay = self.spawn_delay * 3 if self.is_boss_wave and len(self.enemies) == 0 else self.spawn_delay
            if self.spawn_timer >= delay:
                enemy_type = self.spawn_queue.pop(0)
                # Get difficulty multiplier
                diff_mult = DIFFICULTY_MODIFIERS[self.difficulty]["enemy_health"]
                enemy = Enemy(self.waypoints, enemy_type, diff_mult)
                self.enemies.append(enemy)
                self.spawn_timer = 0
        elif not self.enemies:
            self.completed = True
        
        # Update all enemies and handle spawning
        diff_mult = DIFFICULTY_MODIFIERS[self.difficulty]["enemy_health"]
        for enemy in self.enemies[:]:
            if enemy.alive and not enemy.reached_end:
                # Check for time warp effect (passed from game)
                if hasattr(self, 'time_warp_factor') and self.time_warp_factor < 1.0:
                    original_speed = enemy.speed
                    enemy.speed *= self.time_warp_factor
                    enemy.update(barrier_grid)
                    enemy.speed = original_speed
                else:
                    enemy.update(barrier_grid)
                
                # Handle decoy spawning (check flag set in enemy.py)
                if hasattr(enemy, 'should_spawn_decoys') and enemy.should_spawn_decoys:
                    # Spawn 2-3 fake decoys at the real decoy's position
                    import random
                    num_decoys = random.randint(2, 3)
                    for i in range(num_decoys):
                        fake_decoy = Enemy(self.waypoints, "decoy_fake", diff_mult)
                        fake_decoy.position = enemy.position.copy()
                        fake_decoy.waypoint_index = enemy.waypoint_index
                        fake_decoy.parent_decoy = enemy  # Reference to real decoy
                        self.enemies.append(fake_decoy)
                    enemy.should_spawn_decoys = False  # Clear flag
                
                # Handle summoner spawning (timer-based, consolidated here)
                if hasattr(enemy, 'can_summon') and enemy.can_summon:
                    enemy.summon_timer += 1
                    if enemy.summon_timer >= enemy.summon_delay:
                        # Spawn a basic minion at summoner's position
                        minion = Enemy(self.waypoints, "basic", diff_mult * 0.5)
                        minion.position = enemy.position.copy()
                        minion.waypoint_index = enemy.waypoint_index
                        minion.reward = 5  # Lower reward for spawned minions
                        self.enemies.append(minion)
                        enemy.summon_timer = 0
                
                # Handle flying fortress spawning (timer-based, consolidated here)
                if hasattr(enemy, 'spawns_units') and enemy.spawns_units:
                    enemy.spawn_timer += 1
                    if enemy.spawn_timer >= enemy.spawn_delay:
                        # Spawn a tank ground unit below the fortress
                        spawn_unit = Enemy(self.waypoints, "tank", diff_mult * 0.6)
                        spawn_unit.position = enemy.position.copy()
                        spawn_unit.waypoint_index = enemy.waypoint_index
                        spawn_unit.reward = 10  # Lower reward for spawned units
                        spawn_unit.is_air = False  # Ground unit
                        self.enemies.append(spawn_unit)
                        enemy.spawn_timer = 0
    
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
        """Get killed enemies for rewards and handle splitting"""
        dead = [e for e in self.enemies if not e.alive]
        
        # Handle splitting enemies
        diff_mult = DIFFICULTY_MODIFIERS[self.difficulty]["enemy_health"]
        for enemy in dead:
            if enemy.splits:
                # Spawn 2 smaller (basic) enemies at the death position
                for i in range(2):
                    split_enemy = Enemy(self.waypoints, "basic", diff_mult * 0.5)
                    split_enemy.position = enemy.position.copy()
                    split_enemy.waypoint_index = enemy.waypoint_index
                    split_enemy.reward = 5  # Less reward for split enemies
                    self.enemies.append(split_enemy)
            
            # Handle decoy death - kill all fake decoys when real one dies
            if hasattr(enemy, 'is_decoy') and enemy.is_decoy and enemy.is_real:
                for other_enemy in self.enemies[:]:
                    if (hasattr(other_enemy, 'is_decoy') and other_enemy.is_decoy and 
                        not other_enemy.is_real and hasattr(other_enemy, 'parent_decoy') and 
                        other_enemy.parent_decoy == enemy):
                        other_enemy.alive = False
        
        # Remove dead enemies from list
        self.enemies = [e for e in self.enemies if e.alive]
        return dead
