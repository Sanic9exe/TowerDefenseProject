"""
Main game class that manages game state and logic
"""
import pygame
import sys
from config import *
from enemy import Enemy
from tower import Tower
from projectile import Projectile
from wave import Wave
from ui import UI
from barrier import Barrier
from utility import TimeWarp
from map_generator import generate_random_path, generate_multi_lane_paths
from ai_controller import AITowerController

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense - Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.fullscreen = False  # Fullscreen toggle state
        
        # Game settings
        self.difficulty = "normal"  # easy, normal, hard
        self.game_mode = "normal"  # normal, endless, multi_lane
        self.game_speed = 1  # 1x, 2x, 3x
        self.current_paths = [PATH_WAYPOINTS]  # List of paths (for multi-lane)
        
        # Game state
        self.state = "mode_select"  # mode_select, menu, playing, paused, game_over, victory
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        self.wave_number = 0
        self.total_waves = 10  # QOL: selectable wave count (default 10)
        
        # Game objects
        self.towers = []
        self.projectiles = []
        self.barriers = []  # Buildable barriers (hard mode)
        self.time_warps = []  # Time warp utilities
        self.current_wave = None
        self.current_waves = []  # Multiple waves for multi-lane
        self.ui = UI()
        self.selected_tower = None
        self.placing_barrier = False  # For barrier placement mode
        self.placing_time_warp = False  # For time warp placement
        
        # Grid for tower placement
        self.grid = [[None for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        self._mark_path_cells()
        
        # Reverse Mode specific attributes
        self.reverse_state = "planning"  # planning, ai_placing, wave_active, wave_complete
        self.reverse_budget = 500  # Player budget for spawning enemies
        self.reverse_queue = []  # Queued enemies to spawn
        self.reverse_score = 0  # Enemies that reached the end
        self.reverse_spawned = 0  # Total enemies spawned this wave
        self.reverse_spawn_timer = 0  # Timer for spawning queued enemies
        self.ai_controller = None  # Will be initialized when reverse mode starts
        
    def _mark_path_cells(self):
        """Mark grid cells that are part of the path(s) using Bresenham's line algorithm"""
        # Mark all paths in current_paths
        for path_waypoints in self.current_paths:
            for i in range(len(path_waypoints) - 1):
                start = path_waypoints[i]
                end = path_waypoints[i + 1]
                
                # Use Bresenham's line algorithm to mark all cells along the path
                x1, y1 = int(start[0] // GRID_SIZE), int(start[1] // GRID_SIZE)
                x2, y2 = int(end[0] // GRID_SIZE), int(end[1] // GRID_SIZE)
                
                # Bresenham's line algorithm
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                sx = 1 if x1 < x2 else -1
                sy = 1 if y1 < y2 else -1
                err = dx - dy
                
                x, y = x1, y1
                while True:
                    # Mark current cell and adjacent cells for path width
                    for offset_x in range(-1, 2):
                        for offset_y in range(-1, 2):
                            gx, gy = x + offset_x, y + offset_y
                            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                                self.grid[gx][gy] = "path"
                    
                    if x == x2 and y == y2:
                        break
                    
                    e2 = 2 * err
                    if e2 > -dy:
                        err -= dy
                        x += sx
                    if e2 < dx:
                        err += dx
                        y += sy
    
    def _setup_game_mode(self):
        """Set up paths based on game mode"""
        if self.game_mode == "endless" or self.game_mode == "path_randomizer":
            # Generate random path for endless and path randomizer modes
            self.current_paths = [generate_random_path()]
        elif self.game_mode == "multi_lane":
            # Generate two paths for multi-lane mode
            path1, path2 = generate_multi_lane_paths()
            self.current_paths = [path1, path2]
        elif self.game_mode == "reverse":
            # Reverse mode: use default path
            self.current_paths = [PATH_WAYPOINTS]
            # Initialize AI controller
            path_cells = []
            for gx in range(GRID_WIDTH):
                for gy in range(GRID_HEIGHT):
                    if self.grid[gx][gy] == "path":
                        path_cells.append((gx, gy))
            self.ai_controller = AITowerController(self.grid, path_cells)
            self.reverse_state = "planning"
            self.reverse_budget = 500
            self.reverse_queue = []
            self.reverse_score = 0
        else:
            # Use default path for normal/one_life mode
            self.current_paths = [PATH_WAYPOINTS]
        
        # Re-mark path cells
        self.grid = [[None for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        self._mark_path_cells()
    
    def start_next_wave(self):
        """Start the next wave"""
        # Reverse mode doesn't use this - wave starts when player commits enemies
        if self.game_mode == "reverse":
            self.wave_number += 1
            self.reverse_state = "planning"
            return
        
        if self.game_mode == "multi_lane":
            # Multi-lane: check if all waves completed
            all_completed = all(w.completed for w in self.current_waves) if self.current_waves else True
            if all_completed:
                self.wave_number += 1
                self.current_waves = []
                # Create a wave for each path
                for path in self.current_paths:
                    wave = Wave(self.wave_number, path, self.difficulty, False)
                    self.current_waves.append(wave)
        else:
            # Single path mode
            if self.current_wave is None or self.current_wave.completed:
                self.wave_number += 1
                is_endless = (self.game_mode == "endless")
                
                # Path randomizer: generate new path each wave
                if self.game_mode == "path_randomizer":
                    self.current_paths = [generate_random_path()]
                    # Re-mark path cells
                    self.grid = [[None if not isinstance(cell, Tower) else cell 
                                 for cell in row] for row in self.grid]
                    self._mark_path_cells()
                
                # Use the appropriate path
                path = self.current_paths[0]
                self.current_wave = Wave(self.wave_number, path, self.difficulty, is_endless)
        
        # Unlock new towers at certain waves
        if self.wave_number >= 3 and "freeze" not in self.ui.unlocked_towers:
            self.ui.unlocked_towers.add("freeze")
        if self.wave_number >= 5 and "splash" not in self.ui.unlocked_towers:
            self.ui.unlocked_towers.add("splash")
        if self.wave_number >= 7 and "sniper" not in self.ui.unlocked_towers:
            self.ui.unlocked_towers.add("sniper")
        # New advanced towers unlock later
        if self.wave_number >= 10 and "flamethrower" not in self.ui.unlocked_towers:
            self.ui.unlocked_towers.add("flamethrower")
        if self.wave_number >= 12 and "poison" not in self.ui.unlocked_towers:
            self.ui.unlocked_towers.add("poison")
        if self.wave_number >= 15 and "drone_swarm" not in self.ui.unlocked_towers:
            self.ui.unlocked_towers.add("drone_swarm")
        if self.wave_number >= 18 and "railgun" not in self.ui.unlocked_towers:
            self.ui.unlocked_towers.add("railgun")
        if self.wave_number >= 20 and "economy" not in self.ui.unlocked_towers:
            self.ui.unlocked_towers.add("economy")
    
    def handle_events(self):
        """Handle pygame events"""
        mouse_pos = pygame.mouse.get_pos()
        self.ui.update_button_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # F8 toggles fullscreen at all times
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F8:
                self.fullscreen = not self.fullscreen
                if self.fullscreen:
                    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                else:
                    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                continue
            
            if self.state == "mode_select":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:  # Easy mode
                        self.difficulty = "easy"
                        self.money = DIFFICULTY_MODIFIERS["easy"]["starting_money"]
                        self.state = "menu"
                    elif event.key == pygame.K_2:  # Normal mode
                        self.difficulty = "normal"
                        self.state = "menu"
                    elif event.key == pygame.K_3:  # Hard mode
                        self.difficulty = "hard"
                        self.money = DIFFICULTY_MODIFIERS["hard"]["starting_money"]
                        self.state = "menu"
                    elif event.key == pygame.K_e:  # Endless mode
                        self.game_mode = "endless"
                        self.state = "menu"
                    elif event.key == pygame.K_m:  # Multi-lane mode
                        self.game_mode = "multi_lane"
                        self.state = "menu"
                    elif event.key == pygame.K_p:  # Path randomizer mode
                        self.game_mode = "path_randomizer"
                        self.state = "menu"
                    elif event.key == pygame.K_o:  # One life mode
                        self.game_mode = "one_life"
                        self.lives = 1  # Only one life!
                        self.money = STARTING_MONEY * 3  # Triple starting money
                        self.state = "menu"
                    elif event.key == pygame.K_r:  # Reverse mode
                        self.game_mode = "reverse"
                        self.state = "menu"
            
            elif self.state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self._setup_game_mode()  # Setup paths based on mode
                        self.state = "playing"
                        self.start_next_wave()
                    # QOL: Select wave count (number keys 1-9 for 10-90 waves in increments of 10)
                    elif event.key >= pygame.K_1 and event.key <= pygame.K_9 and self.game_mode != "endless":
                        self.total_waves = (event.key - pygame.K_0) * 10
            
            elif self.state == "playing":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_click(mouse_pos)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.state = "paused"
                    elif event.key == pygame.K_ESCAPE:
                        self.ui.selected_tower_type = None
                        self.selected_tower = None
            
            elif self.state == "paused":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.state = "playing"
            
            elif self.state == "game_over" or self.state == "victory":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.__init__()
        
        return True
    
    def _handle_click(self, pos):
        """Handle mouse clicks"""
        # Reverse Mode specific handling
        if self.game_mode == "reverse":
            self._handle_reverse_click(pos)
            return
        
        # Check tower selection buttons (only unlocked towers)
        for tower_type, button in self.ui.tower_buttons.items():
            if button.is_clicked(pos) and tower_type in self.ui.unlocked_towers:
                if self.money >= TOWER_COSTS[tower_type]:
                    self.ui.selected_tower_type = tower_type
                    self.selected_tower = None
                return
        
        # Check next wave button
        if self.ui.next_wave_button.is_clicked(pos):
            if self.current_wave is None or self.current_wave.completed:
                self.start_next_wave()
            return
        
        # Check pause button
        if self.ui.pause_button.is_clicked(pos):
            self.state = "paused"
            return
        
        # Check speed button
        if self.ui.speed_button.is_clicked(pos):
            current_index = SPEED_OPTIONS.index(self.game_speed)
            self.game_speed = SPEED_OPTIONS[(current_index + 1) % len(SPEED_OPTIONS)]
            self.ui.speed_button.text = f"Speed: {self.game_speed}x"
            return
        
        # Check barrier button (all modes now)
        if self.ui.barrier_button.is_clicked(pos):
            if self.money >= BARRIER_COST and len(self.barriers) < MAX_BARRIERS:
                self.placing_barrier = True
                self.ui.selected_tower_type = None
                self.selected_tower = None
            return
        
        # Check auto-start button
        if self.ui.auto_start_button.is_clicked(pos):
            self.ui.auto_start_waves = not self.ui.auto_start_waves
            self.ui.auto_start_button.text = f"Auto: {'ON' if self.ui.auto_start_waves else 'OFF'}"
            return
        
        # Check time warp button
        if self.ui.timewarp_button.is_clicked(pos):
            if self.money >= TIME_WARP_COST:
                self.placing_time_warp = True
                self.ui.selected_tower_type = None
                self.selected_tower = None
                self.placing_barrier = False
            return
        
        # Check tower action buttons if tower is selected
        if self.selected_tower:
            if self.ui.upgrade_button.is_clicked(pos):
                if self.selected_tower.level < 3 and self.money >= self.selected_tower.upgrade_cost:
                    cost = self.selected_tower.upgrade()
                    if cost:
                        self.money -= cost
                return
            
            if self.ui.sell_button.is_clicked(pos):
                self.money += self.selected_tower.get_sell_value()
                self.towers.remove(self.selected_tower)
                self.grid[self.selected_tower.grid_x][self.selected_tower.grid_y] = None
                self.selected_tower = None
                return
            
            if self.ui.target_button.is_clicked(pos):
                self.selected_tower.cycle_targeting_mode()
                return
        
        # Check grid for tower/barrier placement or selection
        grid_x = pos[0] // GRID_SIZE
        grid_y = pos[1] // GRID_SIZE
        
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            # Place time warp
            if self.placing_time_warp:
                # Place at center of clicked cell
                warp_x = grid_x * GRID_SIZE + GRID_SIZE // 2
                warp_y = grid_y * GRID_SIZE + GRID_SIZE // 2
                time_warp = TimeWarp(warp_x, warp_y)
                self.time_warps.append(time_warp)
                self.money -= TIME_WARP_COST
                self.placing_time_warp = False
            # Place barrier
            elif self.placing_barrier:
                if self._can_place_barrier(grid_x, grid_y):
                    barrier = Barrier(grid_x, grid_y)
                    self.barriers.append(barrier)
                    self.grid[grid_x][grid_y] = barrier
                    self.money -= BARRIER_COST
                    self.placing_barrier = False
            # Place tower
            elif self.ui.selected_tower_type:
                if self._can_place_tower(grid_x, grid_y):
                    cost = TOWER_COSTS[self.ui.selected_tower_type]
                    if self.money >= cost:
                        tower = Tower(grid_x, grid_y, self.ui.selected_tower_type)
                        self.towers.append(tower)
                        self.grid[grid_x][grid_y] = tower
                        self.money -= cost
                        self.ui.selected_tower_type = None
            # Select tower
            else:
                cell = self.grid[grid_x][grid_y]
                if isinstance(cell, Tower):
                    # Deselect all towers
                    for tower in self.towers:
                        tower.selected = False
                    # Select clicked tower
                    cell.selected = True
                    self.selected_tower = cell
                else:
                    # Deselect all towers
                    for tower in self.towers:
                        tower.selected = False
                    self.selected_tower = None
    
    def _handle_reverse_click(self, pos):
        """Handle clicks in Reverse Mode"""
        # Check enemy spawn buttons (planning phase only)
        if self.reverse_state == "planning":
            for enemy_type, button in self.ui.enemy_buttons.items():
                if button.is_clicked(pos):
                    cost = ENEMY_SPAWN_COSTS.get(enemy_type, 0)
                    if self.reverse_budget >= cost and len(self.reverse_queue) < 20:
                        self.reverse_queue.append(enemy_type)
                        # Don't deduct yet - deduct when committing
                    return
            
            # Check commit button
            if self.ui.reverse_commit_button.is_clicked(pos):
                if self.reverse_queue:
                    # Calculate total cost
                    total_cost = sum(ENEMY_SPAWN_COSTS.get(et, 0) for et in self.reverse_queue)
                    if self.reverse_budget >= total_cost:
                        self.reverse_budget -= total_cost
                        self.reverse_state = "ai_placing"
                return
            
            # Check clear button
            if self.ui.reverse_clear_button.is_clicked(pos):
                self.reverse_queue.clear()
                return
        
        # Check next wave button (wave_complete phase only)
        if self.reverse_state == "wave_complete":
            if self.ui.reverse_next_wave_button.is_clicked(pos):
                # Check victory/defeat
                if self.reverse_score >= 20:
                    self.state = "victory"
                elif self.wave_number >= 10:
                    if self.reverse_score >= 10:
                        self.state = "victory"
                    else:
                        self.state = "game_over"
                else:
                    # Start next wave
                    self.wave_number += 1
                    self.reverse_state = "planning"
                    self.reverse_queue.clear()
                return
        
        # Check speed button (always available)
        if self.ui.speed_button.is_clicked(pos):
            current_index = SPEED_OPTIONS.index(self.game_speed)
            self.game_speed = SPEED_OPTIONS[(current_index + 1) % len(SPEED_OPTIONS)]
            self.ui.speed_button.text = f"Speed: {self.game_speed}x"
            return
    
    def _can_place_tower(self, grid_x, grid_y):
        """Check if tower can be placed at position"""
        if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y < 0 or grid_y >= GRID_HEIGHT:
            return False
        # Can only place on empty cells (not path, not occupied)
        cell = self.grid[grid_x][grid_y]
        return cell is None
    
    def _can_place_barrier(self, grid_x, grid_y):
        """Check if barrier can be placed at position (only on path)"""
        if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y < 0 or grid_y >= GRID_HEIGHT:
            return False
        # Check if this position is on the path (was marked as path initially)
        # We need to check if it's a path cell and not occupied
        cell = self.grid[grid_x][grid_y]
        # Can place if cell is exactly "path" (not occupied by tower or barrier)
        if cell == "path":
            return True
        # Also check if this position is geometrically on any path using point-to-line distance
        # This handles cases where path marking might have issues
        for path_waypoints in self.current_paths:
            for i in range(len(path_waypoints) - 1):
                start = path_waypoints[i]
                end = path_waypoints[i + 1]
                
                # Convert grid position to pixel position (center of cell)
                px = (grid_x + 0.5) * GRID_SIZE
                py = (grid_y + 0.5) * GRID_SIZE
                
                # Calculate distance from point to line segment
                x1, y1 = start[0], start[1]
                x2, y2 = end[0], end[1]
                
                # Vector from start to end
                dx = x2 - x1
                dy = y2 - y1
                
                # If start == end, just check distance to point
                if dx == 0 and dy == 0:
                    dist = ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
                else:
                    # Parameter t for closest point on line segment
                    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
                    # Closest point on line segment
                    closest_x = x1 + t * dx
                    closest_y = y1 + t * dy
                    # Distance from point to closest point
                    dist = ((px - closest_x) ** 2 + (py - closest_y) ** 2) ** 0.5
                
                # If within path width (40px + some tolerance)
                if dist <= 50:  # PATH_WIDTH is 40, adding tolerance
                    # On path, check if not occupied
                    return cell == "path"
        return False
    
    def update(self):
        """Update game state"""
        if self.state != "playing":
            return
        
        # Apply game speed multiplier
        for _ in range(self.game_speed):
            self._update_game_logic()
    
    def _update_game_logic(self):
        """Core game update logic (can be called multiple times for speed)"""
        # Handle Reverse Mode separately
        if self.game_mode == "reverse":
            self._update_reverse_mode()
            return
        
        # Update economy towers - generate passive income
        for tower in self.towers:
            if hasattr(tower, 'is_economy') and tower.is_economy:
                tower.income_timer += 1
                if tower.income_timer >= tower.income_interval:
                    self.money += tower.income_amount
                    tower.income_timer = 0
        
        # Update waves (single or multi-lane)
        waves_to_update = self.current_waves if self.game_mode == "multi_lane" else ([self.current_wave] if self.current_wave else [])
        
        # Update time warps
        for time_warp in self.time_warps[:]:
            if not time_warp.update():
                self.time_warps.remove(time_warp)
        
        for wave in waves_to_update:
            if wave:
                # Apply time warp effects to enemies in wave
                for time_warp in self.time_warps:
                    for enemy in wave.get_active_enemies():
                        if time_warp.affects_enemy(enemy):
                            enemy.speed *= time_warp.slow_factor
                
                wave.update(self.grid)  # Pass grid so enemies can check for barriers
                
                # Reset enemy speeds after update
                for time_warp in self.time_warps:
                    for enemy in wave.get_active_enemies():
                        if time_warp.affects_enemy(enemy):
                            enemy.speed /= time_warp.slow_factor
                
                # Check for escaped enemies
                escaped = wave.get_escaped_enemies()
                for enemy in escaped:
                    # Decoy fakes only take half a life
                    if hasattr(enemy, 'is_decoy_fake') and enemy.is_decoy_fake:
                        self.lives -= 0.5
                    else:
                        self.lives -= 1
                    
                    if self.lives <= 0:
                        self.state = "game_over"
                
                # Check for killed enemies
                dead = wave.get_dead_enemies()
                for enemy in dead:
                    # Apply money multiplier
                    money_mult = DIFFICULTY_MODIFIERS[self.difficulty]["money_mult"]
                    self.money += int(enemy.reward * money_mult)
        
        # Check for victory/wave completion
        if self.game_mode == "multi_lane":
            all_completed = all(w.completed for w in self.current_waves)
            if self.wave_number >= self.total_waves and all_completed:
                self.state = "victory"
        elif self.game_mode in ["normal", "path_randomizer", "one_life"] and self.current_wave:
            if self.wave_number >= self.total_waves and self.current_wave.completed:
                self.state = "victory"
        elif self.game_mode == "endless" and self.current_wave and self.current_wave.completed:
            # Auto-start next wave in endless mode
            self.start_next_wave()
        
        # Auto-start waves if enabled (non-endless modes)
        if self.ui.auto_start_waves and self.game_mode not in ["endless", "reverse"]:
            if self.game_mode == "multi_lane":
                if all(w.completed for w in self.current_waves):
                    self.start_next_wave()
            elif self.current_wave and self.current_wave.completed:
                self.start_next_wave()
        
        # Get all active enemies from all waves
        all_active_enemies = []
        for wave in waves_to_update:
            if wave:
                all_active_enemies.extend(wave.get_active_enemies())
        
        # Update towers and create projectiles
        for tower in self.towers:
            result = tower.update(all_active_enemies)
            
            # Handle different return types from tower.update()
            if result is not None:
                if isinstance(result, int):
                    # Economy tower returned income
                    self.money += result
                elif isinstance(result, list):
                    # Drone/Flamethrower returned multiple projectiles
                    self.projectiles.extend(result)
                else:
                    # Normal tower returned single projectile
                    self.projectiles.append(result)
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(all_active_enemies)  # Pass enemies for splash damage
            if not projectile.active:
                self.projectiles.remove(projectile)
        
        # Update barriers - remove dead ones
        for barrier in self.barriers[:]:
            if not barrier.alive:
                # Remove dead barriers from grid
                self.grid[barrier.grid_x][barrier.grid_y] = "path"
                self.barriers.remove(barrier)
    
    def _update_reverse_mode(self):
        """Update logic specifically for Reverse Mode"""
        if self.reverse_state == "planning":
            # Planning phase - player is queuing enemies
            # No automatic updates, waiting for player to commit
            pass
        
        elif self.reverse_state == "ai_placing":
            # AI is placing towers
            if self.ai_controller:
                self.ai_controller.update_budget(self.wave_number)
                # AI places towers
                actions = self.ai_controller.place_towers()
                for action_type, data in actions:
                    if action_type == "place_tower":
                        grid_x, grid_y = data["grid_pos"]
                        tower_type = data["type"]
                        tower = Tower(grid_x, grid_y, tower_type)
                        self.towers.append(tower)
                        self.grid[grid_x][grid_y] = tower
            
            # Transition to wave active
            self.reverse_state = "wave_active"
            self.reverse_spawned = 0
            self.reverse_spawn_timer = 0
            # Start wave with empty enemies (we'll spawn manually)
            self.current_wave = Wave(self.wave_number, self.current_paths[0], self.difficulty)
            self.current_wave.enemies = []  # Clear auto-generated enemies
        
        elif self.reverse_state == "wave_active":
            # Spawn enemies from queue
            if self.reverse_queue and self.reverse_spawned < len(self.reverse_queue):
                self.reverse_spawn_timer += 1
                if self.reverse_spawn_timer >= 30:  # Spawn every 0.5 seconds
                    enemy_type = self.reverse_queue[self.reverse_spawned]
                    if enemy_type == "swarm":
                        # Spawn 5 swarm units
                        for _ in range(5):
                            enemy = Enemy(enemy_type, self.current_paths[0], self.difficulty)
                            self.current_wave.enemies.append(enemy)
                    else:
                        enemy = Enemy(enemy_type, self.current_paths[0], self.difficulty)
                        self.current_wave.enemies.append(enemy)
                    
                    self.reverse_spawned += 1
                    self.reverse_spawn_timer = 0
            
            # Update wave
            if self.current_wave:
                self.current_wave.update(self.grid)
                
                # Check for escaped enemies (player earns money)
                escaped = self.current_wave.get_escaped_enemies()
                for enemy in escaped:
                    self.reverse_score += 1
                    # Award money based on enemy type
                    if enemy.enemy_type in ENEMY_REWARDS:
                        self.reverse_budget += ENEMY_REWARDS[enemy.enemy_type]
                
                # Update towers and projectiles
                all_active_enemies = self.current_wave.get_active_enemies()
                
                for tower in self.towers:
                    result = tower.update(all_active_enemies)
                    if result is not None:
                        if isinstance(result, list):
                            self.projectiles.extend(result)
                        elif not isinstance(result, int):
                            self.projectiles.append(result)
                
                for projectile in self.projectiles[:]:
                    projectile.update(all_active_enemies)
                    if not projectile.active:
                        self.projectiles.remove(projectile)
                
                # Check if wave is complete
                if self.current_wave.completed:
                    self.reverse_state = "wave_complete"
        
        elif self.reverse_state == "wave_complete":
            # Wave finished, prepare for next wave
            # Waiting for player to start next wave
            pass
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(LIGHT_GREEN)
        
        # Draw grid lines
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))
        
        # Draw path
        self._draw_path()
        
        if self.state == "mode_select":
            self._draw_mode_select()
        elif self.state == "menu":
            self._draw_menu()
        elif self.state == "playing":
            self._draw_game()
        elif self.state == "paused":
            self._draw_game()
            self._draw_pause_overlay()
        elif self.state == "game_over":
            self._draw_game()
            self._draw_game_over()
        elif self.state == "victory":
            self._draw_game()
            self._draw_victory()
        
        pygame.display.flip()
    
    def _draw_path(self):
        """Draw the path(s)"""
        # Draw all paths
        for path_waypoints in self.current_paths:
            for i in range(len(path_waypoints) - 1):
                start = path_waypoints[i]
                end = path_waypoints[i + 1]
                pygame.draw.line(self.screen, BROWN, start, end, 40)
    
    def _draw_mode_select(self):
        """Draw mode/difficulty selection screen"""
        title = self.ui.font_large.render("TOWER DEFENSE - ENHANCED", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Difficulty selection
        diff_title = self.ui.font_medium.render("Select Difficulty:", True, BLACK)
        self.screen.blit(diff_title, (SCREEN_WIDTH // 2 - 150, 200))
        
        difficulties = [
            ("1 - Easy", "More money, weaker enemies", GREEN),
            ("2 - Normal", "Standard experience", YELLOW),
            ("3 - Hard", "Double money, tough enemies, air units", RED)
        ]
        
        y_pos = 250
        for key, desc, color in difficulties:
            text = self.ui.font_medium.render(key, True, color)
            desc_text = self.ui.font_small.render(desc, True, BLACK)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - 150, y_pos))
            self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - 100, y_pos + 30))
            y_pos += 80
        
        # Game mode selection
        mode_title = self.ui.font_medium.render("Special Modes:", True, BLUE)
        self.screen.blit(mode_title, (SCREEN_WIDTH // 2 - 100, 520))
        
        endless_text = self.ui.font_small.render("E - Endless Mode (Random path, infinite waves)", True, BLACK)
        self.screen.blit(endless_text, (SCREEN_WIDTH // 2 - 180, 555))
        
        multi_text = self.ui.font_small.render("M - Multi-Lane Mode (Defend 2 paths!)", True, BLACK)
        self.screen.blit(multi_text, (SCREEN_WIDTH // 2 - 150, 585))
        
        path_text = self.ui.font_small.render("P - Path Randomizer (New path each wave!)", True, BLACK)
        self.screen.blit(path_text, (SCREEN_WIDTH // 2 - 160, 615))
        
        one_life_text = self.ui.font_small.render("O - One Life Mode (1 life, 3x money!)", True, BLACK)
        self.screen.blit(one_life_text, (SCREEN_WIDTH // 2 - 150, 645))
        
        reverse_text = self.ui.font_small.render("R - Reverse Mode (Control enemies vs AI towers!)", True, GREEN)
        self.screen.blit(reverse_text, (SCREEN_WIDTH // 2 - 170, 675))
    
    def _draw_menu(self):
        """Draw menu screen"""
        title = self.ui.font_large.render("TOWER DEFENSE", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)
        
        # Show selected mode and difficulty
        mode_text = f"Mode: {self.game_mode.title()} | Difficulty: {self.difficulty.title()}"
        mode_display = self.ui.font_medium.render(mode_text, True, BLUE)
        mode_rect = mode_display.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(mode_display, mode_rect)
        
        # QOL: Show wave count selection for non-endless modes
        if self.game_mode != "endless":
            wave_text = f"Total Waves: {self.total_waves} (Press 1-9 to change: 10-90 waves)"
            wave_display = self.ui.font_small.render(wave_text, True, BLACK)
            wave_rect = wave_display.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
            self.screen.blit(wave_display, wave_rect)
        
        instructions = self.ui.font_medium.render("Press SPACE to Start", True, BLACK)
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(instructions, inst_rect)
        
        if self.game_mode == "normal" or self.game_mode == "multi_lane" or self.game_mode == "path_randomizer" or self.game_mode == "one_life":
            info_text = f"Defend the path! Survive {self.total_waves} waves to win!"
            if self.game_mode == "path_randomizer":
                info_text = f"Path changes each wave! Survive {self.total_waves} waves!"
            elif self.game_mode == "one_life":
                info_text = f"ONE LIFE ONLY! But 3x money! Survive {self.total_waves} waves!"
            info = self.ui.font_small.render(info_text, True, BLACK)
        elif self.game_mode == "reverse":
            info = self.ui.font_small.render("Spawn enemies and get them through! AI defends with towers.", True, BLACK)
        else:
            info = self.ui.font_small.render("Survive as long as you can!", True, BLACK)
        info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(info, info_rect)
    
    def _draw_game(self):
        """Draw game elements"""
        # Handle Reverse Mode drawing separately
        if self.game_mode == "reverse":
            self._draw_reverse_game()
            return
        
        # Draw time warps (behind everything)
        for time_warp in self.time_warps:
            time_warp.draw(self.screen)
        
        # Draw barriers
        for barrier in self.barriers:
            barrier.draw(self.screen)
        
        # Draw towers
        for tower in self.towers:
            tower.draw(self.screen)
        
        # Draw enemies (from all waves)
        if self.game_mode == "multi_lane":
            for wave in self.current_waves:
                wave.draw(self.screen)
        elif self.current_wave:
            self.current_wave.draw(self.screen)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Draw UI
        self.ui.draw_hud(self.screen, self.money, self.lives, self.wave_number, 
                        self.game_mode, self.difficulty)
        self.ui.draw_tower_buttons(self.screen, self.money)
        # Barrier and time warp now available in all modes
        self.ui.draw_control_buttons(self.screen)
        
        # Draw selected tower info
        if self.selected_tower:
            self.ui.draw_tower_info(self.screen, self.selected_tower, self.money)
        
        # Draw tower ghost
        if self.ui.selected_tower_type:
            mouse_pos = pygame.mouse.get_pos()
            grid_x = mouse_pos[0] // GRID_SIZE
            grid_y = mouse_pos[1] // GRID_SIZE
            valid = self._can_place_tower(grid_x, grid_y)
            self.ui.draw_tower_ghost(self.screen, self.ui.selected_tower_type, 
                                    grid_x, grid_y, valid)
        
        # Draw barrier ghost
        if self.placing_barrier:
            mouse_pos = pygame.mouse.get_pos()
            grid_x = mouse_pos[0] // GRID_SIZE
            grid_y = mouse_pos[1] // GRID_SIZE
            valid = self._can_place_barrier(grid_x, grid_y)
            # Draw semi-transparent filled square with border (like towers)
            ghost_surface = pygame.Surface((GRID_SIZE - 10, GRID_SIZE - 10))
            ghost_surface.set_alpha(128)
            ghost_surface.fill((139, 69, 19))  # Brown color for barrier
            self.screen.blit(ghost_surface, (grid_x * GRID_SIZE + 5, grid_y * GRID_SIZE + 5))
            # Draw colored border
            ghost_color = GREEN if valid else RED
            pygame.draw.rect(self.screen, ghost_color, 
                           (grid_x * GRID_SIZE + 5, grid_y * GRID_SIZE + 5,
                            GRID_SIZE - 10, GRID_SIZE - 10), 3)
        
        # Draw time warp ghost
        if self.placing_time_warp:
            mouse_pos = pygame.mouse.get_pos()
            # Draw radius indicator
            pygame.draw.circle(self.screen, (100, 100, 255), mouse_pos, TIME_WARP_RADIUS, 2)
            pygame.draw.circle(self.screen, (50, 50, 200), mouse_pos, 10)
    
    def _draw_reverse_game(self):
        """Draw Reverse Mode game elements"""
        # Draw towers (AI controlled)
        for tower in self.towers:
            tower.draw(self.screen)
        
        # Draw enemies (player's)
        if self.current_wave:
            self.current_wave.draw(self.screen)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Draw Reverse Mode UI
        ai_budget = self.ai_controller.budget if self.ai_controller else 0
        self.ui.draw_reverse_ui(
            self.screen,
            self.reverse_state,
            self.reverse_budget,
            self.reverse_queue,
            self.reverse_score,
            self.wave_number,
            ai_budget
        )
        
        # Draw speed button (always available)
        self.ui.speed_button.draw(self.screen)
    
    def _draw_pause_overlay(self):
        """Draw pause overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        text = self.ui.font_large.render("PAUSED", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        
        hint = self.ui.font_small.render("Press SPACE to continue", True, WHITE)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(hint, hint_rect)
    
    def _draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        text = self.ui.font_large.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        
        wave_text = self.ui.font_medium.render(f"You reached wave {self.wave_number}", True, WHITE)
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(wave_text, wave_rect)
        
        hint = self.ui.font_small.render("Press R to restart", True, WHITE)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(hint, hint_rect)
    
    def _draw_victory(self):
        """Draw victory screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        text = self.ui.font_large.render("VICTORY!", True, YELLOW)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        
        congrats = self.ui.font_medium.render("You defended the path!", True, WHITE)
        congrats_rect = congrats.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(congrats, congrats_rect)
        
        hint = self.ui.font_small.render("Press R to restart", True, WHITE)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(hint, hint_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
