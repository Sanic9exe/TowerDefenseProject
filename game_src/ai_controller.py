"""
AI Tower Controller for Reverse Mode
Handles automatic tower placement and upgrades
"""

import random
from config import TOWER_COSTS

class AITowerController:
    """AI that places and manages towers in Reverse Mode"""
    
    def __init__(self, grid, path_cells):
        self.grid = grid
        self.path_cells = path_cells
        self.budget = 300  # Starting AI budget
        self.placed_towers = []
        self.wave_number = 1
        
    def update_budget(self, wave_number):
        """Increase AI budget each wave"""
        self.wave_number = wave_number
        # AI gets progressively more budget
        self.budget += 100 + (wave_number * 50)
        
    def get_valid_tower_positions(self):
        """Find all valid positions for tower placement"""
        valid_positions = []
        grid_width = len(self.grid)
        grid_height = len(self.grid[0]) if grid_width > 0 else 0
        
        for x in range(grid_width):
            for y in range(grid_height):
                # Check if cell is empty (not path, not occupied)
                if self.grid[x][y] is None:
                    valid_positions.append((x, y))
        
        return valid_positions
    
    def get_strategic_positions(self, valid_positions):
        """Score positions based on proximity to path"""
        scored_positions = []
        
        for pos in valid_positions:
            px, py = pos
            # Calculate minimum distance to any path cell
            min_dist = float('inf')
            for path_x, path_y in self.path_cells:
                dist = ((px - path_x) ** 2 + (py - path_y) ** 2) ** 0.5
                min_dist = min(min_dist, dist)
            
            # Prefer positions near path but not too close
            if 1 <= min_dist <= 3:  # Ideal range
                score = 10 - min_dist
            else:
                score = max(0, 5 - abs(min_dist - 2))
            
            scored_positions.append((pos, score))
        
        # Sort by score (descending)
        scored_positions.sort(key=lambda x: x[1], reverse=True)
        return [pos for pos, score in scored_positions]
    
    def choose_tower_type(self):
        """Choose tower type based on wave number and budget"""
        affordable_towers = []
        
        for tower_type, cost in TOWER_COSTS.items():
            if cost <= self.budget:
                affordable_towers.append((tower_type, cost))
        
        if not affordable_towers:
            return None
        
        # Early waves: prefer cheap towers
        # Later waves: prefer expensive towers
        if self.wave_number < 5:
            # Prefer arrow, cannon
            priorities = ["arrow", "cannon", "freeze"]
        elif self.wave_number < 10:
            # Add splash, laser
            priorities = ["splash", "laser", "freeze", "cannon"]
        else:
            # Prefer powerful towers
            priorities = ["railgun", "sniper", "drone_swarm", "splash"]
        
        # Try to pick from priorities if affordable
        for priority in priorities:
            for tower_type, cost in affordable_towers:
                if tower_type == priority:
                    return tower_type
        
        # Otherwise, pick random affordable tower
        return random.choice(affordable_towers)[0]
    
    def place_towers(self):
        """AI decision to place towers"""
        actions = []  # List of (action_type, data) tuples
        
        valid_positions = self.get_valid_tower_positions()
        if not valid_positions:
            return actions
        
        strategic_positions = self.get_strategic_positions(valid_positions)
        
        # Try to place multiple towers if budget allows
        attempts = 0
        max_attempts = min(5, len(strategic_positions))
        
        while attempts < max_attempts and self.budget > 100:
            tower_type = self.choose_tower_type()
            if not tower_type:
                break
            
            cost = TOWER_COSTS[tower_type]
            if cost > self.budget:
                break
            
            # Get best available position
            if attempts < len(strategic_positions):
                grid_x, grid_y = strategic_positions[attempts]
                
                # Calculate pixel position (center of grid cell)
                from config import GRID_SIZE
                pixel_x = grid_x * GRID_SIZE + GRID_SIZE // 2
                pixel_y = grid_y * GRID_SIZE + GRID_SIZE // 2
                
                actions.append(("place_tower", {
                    "type": tower_type,
                    "grid_pos": (grid_x, grid_y),
                    "pixel_pos": (pixel_x, pixel_y),
                    "cost": cost
                }))
                
                self.budget -= cost
                self.placed_towers.append({
                    "type": tower_type,
                    "pos": (grid_x, grid_y),
                    "level": 1
                })
            
            attempts += 1
        
        return actions
