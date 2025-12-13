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

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = "menu"  # menu, playing, paused, game_over, victory
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        self.wave_number = 0
        
        # Game objects
        self.towers = []
        self.projectiles = []
        self.current_wave = None
        self.ui = UI()
        self.selected_tower = None
        
        # Grid for tower placement
        self.grid = [[None for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        self._mark_path_cells()
        
    def _mark_path_cells(self):
        """Mark grid cells that are part of the path"""
        for i in range(len(PATH_WAYPOINTS) - 1):
            start = PATH_WAYPOINTS[i]
            end = PATH_WAYPOINTS[i + 1]
            
            # Mark cells between waypoints
            x1, y1 = int(start[0] // GRID_SIZE), int(start[1] // GRID_SIZE)
            x2, y2 = int(end[0] // GRID_SIZE), int(end[1] // GRID_SIZE)
            
            if x1 == x2:  # Vertical path
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    if 0 <= x1 < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                        self.grid[x1][y] = "path"
            else:  # Horizontal path
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    if 0 <= x < GRID_WIDTH and 0 <= y1 < GRID_HEIGHT:
                        self.grid[x][y1] = "path"
    
    def start_next_wave(self):
        """Start the next wave"""
        if self.current_wave is None or self.current_wave.completed:
            self.wave_number += 1
            self.current_wave = Wave(self.wave_number, PATH_WAYPOINTS)
    
    def handle_events(self):
        """Handle pygame events"""
        mouse_pos = pygame.mouse.get_pos()
        self.ui.update_button_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.state == "menu":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.state = "playing"
                    self.start_next_wave()
            
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
                    self.state = "menu"
        
        return True
    
    def _handle_click(self, pos):
        """Handle mouse clicks"""
        # Check tower selection buttons
        for tower_type, button in self.ui.tower_buttons.items():
            if button.is_clicked(pos):
                tower_costs = {"arrow": 100, "cannon": 200, "laser": 300}
                if self.money >= tower_costs[tower_type]:
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
        
        # Check grid for tower placement or selection
        grid_x = pos[0] // GRID_SIZE
        grid_y = pos[1] // GRID_SIZE
        
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            # Place tower
            if self.ui.selected_tower_type:
                if self._can_place_tower(grid_x, grid_y):
                    tower_costs = {"arrow": 100, "cannon": 200, "laser": 300}
                    cost = tower_costs[self.ui.selected_tower_type]
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
    
    def _can_place_tower(self, grid_x, grid_y):
        """Check if tower can be placed at position"""
        if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y < 0 or grid_y >= GRID_HEIGHT:
            return False
        return self.grid[grid_x][grid_y] is None
    
    def update(self):
        """Update game state"""
        if self.state != "playing":
            return
        
        # Update current wave
        if self.current_wave:
            self.current_wave.update()
            
            # Check for escaped enemies
            escaped = self.current_wave.get_escaped_enemies()
            for enemy in escaped:
                self.lives -= 1
                if self.lives <= 0:
                    self.state = "game_over"
            
            # Check for killed enemies
            dead = self.current_wave.get_dead_enemies()
            for enemy in dead:
                self.money += enemy.reward
            
            # Check for victory (wave 10 completed)
            if self.wave_number >= 10 and self.current_wave.completed:
                self.state = "victory"
        
        # Update towers and create projectiles
        if self.current_wave:
            active_enemies = self.current_wave.get_active_enemies()
            for tower in self.towers:
                projectile = tower.update(active_enemies)
                if projectile:
                    self.projectiles.append(projectile)
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.active:
                self.projectiles.remove(projectile)
    
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
        
        if self.state == "menu":
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
        """Draw the path"""
        for i in range(len(PATH_WAYPOINTS) - 1):
            start = PATH_WAYPOINTS[i]
            end = PATH_WAYPOINTS[i + 1]
            pygame.draw.line(self.screen, BROWN, start, end, 40)
    
    def _draw_menu(self):
        """Draw menu screen"""
        title = self.ui.font_large.render("TOWER DEFENSE", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)
        
        instructions = self.ui.font_medium.render("Press SPACE to Start", True, BLACK)
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(instructions, inst_rect)
        
        info = self.ui.font_small.render("Defend the path! Survive 10 waves to win!", True, BLACK)
        info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(info, info_rect)
    
    def _draw_game(self):
        """Draw game elements"""
        # Draw towers
        for tower in self.towers:
            tower.draw(self.screen)
        
        # Draw enemies
        if self.current_wave:
            self.current_wave.draw(self.screen)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Draw UI
        self.ui.draw_hud(self.screen, self.money, self.lives, self.wave_number)
        self.ui.draw_tower_buttons(self.screen, self.money)
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
