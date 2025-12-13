"""
UI elements for tower defense game
"""
import pygame
from config import *

class Button:
    """Simple button class"""
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
        
    def draw(self, screen):
        """Draw button"""
        color = LIGHT_GRAY if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        font = pygame.font.Font(None, 20)
        font_height = font.get_height()
        
        # Handle multiline text
        lines = self.text.split('\n')
        total_height = len(lines) * font_height
        y_offset = self.rect.centery - (total_height // 2)
        
        for line in lines:
            text_surface = font.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(self.rect.centerx, y_offset + font_height // 2))
            screen.blit(text_surface, text_rect)
            y_offset += font_height
    
    def is_clicked(self, pos):
        """Check if button is clicked"""
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        """Update hover state"""
        self.hover = self.rect.collidepoint(pos)

class UI:
    """Game UI manager"""
    def __init__(self):
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 24)
        
        # Tower selection buttons (3 rows with smaller buttons for 11 towers)
        self.tower_buttons = {
            # Row 1 - Original 3
            "arrow": Button(20, 20, 70, 45, f"Arrow\n${TOWER_COSTS['arrow']}", DARK_GREEN),
            "cannon": Button(100, 20, 70, 45, f"Cannon\n${TOWER_COSTS['cannon']}", DARK_GRAY),
            "laser": Button(180, 20, 70, 45, f"Laser\n${TOWER_COSTS['laser']}", BLUE),
            "freeze": Button(260, 20, 70, 45, f"Freeze\n${TOWER_COSTS['freeze']}", (100, 200, 255)),
            # Row 2 - Next 4
            "splash": Button(20, 75, 70, 45, f"Splash\n${TOWER_COSTS['splash']}", (255, 100, 0)),
            "sniper": Button(100, 75, 70, 45, f"Sniper\n${TOWER_COSTS['sniper']}", (50, 50, 50)),
            "flamethrower": Button(180, 75, 70, 45, f"Flame\n${TOWER_COSTS['flamethrower']}", (255, 50, 0)),
            "poison": Button(260, 75, 70, 45, f"Poison\n${TOWER_COSTS['poison']}", (100, 255, 0)),
            # Row 3 - Advanced 3
            "drone_swarm": Button(20, 130, 70, 45, f"Drone\n${TOWER_COSTS['drone_swarm']}", (150, 150, 255)),
            "railgun": Button(100, 130, 70, 45, f"Rail\n${TOWER_COSTS['railgun']}", (200, 200, 255)),
            "economy": Button(180, 130, 70, 45, f"Econ\n${TOWER_COSTS['economy']}", (255, 215, 0))
        }
        
        # Control buttons
        self.next_wave_button = Button(SCREEN_WIDTH - 150, 20, 130, 40, "Next Wave", GREEN)
        self.pause_button = Button(SCREEN_WIDTH - 150, 70, 130, 40, "Pause", GRAY)
        self.speed_button = Button(SCREEN_WIDTH - 150, 120, 130, 40, "Speed: 1x", YELLOW)
        self.barrier_button = Button(SCREEN_WIDTH - 150, 170, 130, 40, "Barrier\n$50", BROWN)
        self.auto_start_button = Button(SCREEN_WIDTH - 150, 220, 130, 40, "Auto: OFF", (200, 200, 0))
        self.timewarp_button = Button(SCREEN_WIDTH - 150, 270, 130, 40, "TimeWarp\n$150", (100, 100, 255))
        
        # Tower action buttons (shown when tower selected) - repositioned lower
        self.upgrade_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 140, 130, 35, "Upgrade", GREEN)
        self.sell_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100, 130, 35, "Sell", RED)
        self.target_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 60, 130, 35, "Target", BLUE)
        
        self.selected_tower_type = None
        self.unlocked_towers = {"arrow", "cannon", "laser"}  # Start with basic towers
        self.auto_start_waves = False  # QOL: auto-start toggle
        
    def draw_hud(self, screen, money, lives, wave_number, game_mode="normal", difficulty="normal"):
        """Draw HUD elements"""
        # Money display
        money_text = self.font_medium.render(f"Money: ${money}", True, YELLOW)
        screen.blit(money_text, (20, SCREEN_HEIGHT - 40))
        
        # Lives display
        lives_text = self.font_medium.render(f"Lives: {lives}", True, RED)
        screen.blit(lives_text, (200, SCREEN_HEIGHT - 40))
        
        # Wave display
        wave_text = self.font_medium.render(f"Wave: {wave_number}", True, WHITE)
        screen.blit(wave_text, (380, SCREEN_HEIGHT - 40))
        
        # Difficulty and mode display
        mode_color = GREEN if game_mode == "endless" else WHITE
        mode_text = self.font_small.render(f"{game_mode.title()} | {difficulty.title()}", True, mode_color)
        screen.blit(mode_text, (550, SCREEN_HEIGHT - 35))
    
    def draw_tower_buttons(self, screen, money):
        """Draw tower selection buttons (only unlocked ones)"""
        for tower_type, button in self.tower_buttons.items():
            if tower_type in self.unlocked_towers:
                button.draw(screen)
                if self.selected_tower_type == tower_type:
                    pygame.draw.rect(screen, YELLOW, button.rect, 4)
            else:
                # Draw locked tower button
                pygame.draw.rect(screen, DARK_GRAY, button.rect)
                pygame.draw.rect(screen, BLACK, button.rect, 2)
                lock_font = pygame.font.Font(None, 24)
                lock_text = lock_font.render("🔒", True, BLACK)
                screen.blit(lock_text, (button.rect.centerx - 10, button.rect.centery - 10))
    
    def draw_control_buttons(self, screen, show_barrier=False):
        """Draw control buttons"""
        self.next_wave_button.draw(screen)
        self.pause_button.draw(screen)
        self.speed_button.draw(screen)
        if show_barrier:
            self.barrier_button.draw(screen)
    
    def draw_tower_info(self, screen, tower, money):
        """Draw selected tower information and action buttons"""
        # Info panel background - taller to fit stats above buttons
        panel_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 260, 160, 240)
        pygame.draw.rect(screen, LIGHT_GRAY, panel_rect)
        pygame.draw.rect(screen, BLACK, panel_rect, 2)
        
        # Tower stats - moved higher up
        y_offset = SCREEN_HEIGHT - 250
        stats = [
            f"Level: {tower.level}",
            f"Damage: {tower.damage}",
            f"Range: {tower.range}",
            f"Type: {tower.tower_type}",
            f"Target: {tower.targeting_mode[:6]}"
        ]
        
        for stat in stats:
            text = self.font_small.render(stat, True, BLACK)
            screen.blit(text, (SCREEN_WIDTH - 170, y_offset))
            y_offset += 22
        
        # Buttons below stats (repositioned to avoid overlap)
        # Upgrade button
        if tower.level < 3:
            self.upgrade_button.text = f"Upgrade\n${tower.upgrade_cost}"
            self.upgrade_button.color = GREEN if money >= tower.upgrade_cost else GRAY
            self.upgrade_button.draw(screen)
        
        # Sell button
        self.sell_button.text = f"Sell\n${tower.get_sell_value()}"
        self.sell_button.draw(screen)
        
        # Target mode button
        self.target_button.text = f"Target"
        self.target_button.draw(screen)
    
    def draw_tower_ghost(self, screen, tower_type, grid_x, grid_y, valid):
        """Draw ghost tower at mouse position"""
        tower_colors = {
            "arrow": DARK_GREEN, 
            "cannon": DARK_GRAY, 
            "laser": BLUE,
            "freeze": (100, 200, 255),
            "splash": (255, 100, 0),
            "sniper": (50, 50, 50)
        }
        
        if tower_type in tower_colors:
            color = GREEN if valid else RED
            alpha = 128
            ghost_surface = pygame.Surface((GRID_SIZE - 20, GRID_SIZE - 20))
            ghost_surface.set_alpha(alpha)
            
            ghost_surface.fill(tower_colors[tower_type])
            
            screen.blit(ghost_surface, (grid_x * GRID_SIZE + 10, grid_y * GRID_SIZE + 10))
            pygame.draw.rect(screen, color, 
                           (grid_x * GRID_SIZE + 10, grid_y * GRID_SIZE + 10,
                            GRID_SIZE - 20, GRID_SIZE - 20), 2)
    
    def update_button_hover(self, mouse_pos):
        """Update hover states for all buttons"""
        for button in self.tower_buttons.values():
            button.update_hover(mouse_pos)
        self.next_wave_button.update_hover(mouse_pos)
        self.pause_button.update_hover(mouse_pos)
        self.speed_button.update_hover(mouse_pos)
        self.barrier_button.update_hover(mouse_pos)
        self.upgrade_button.update_hover(mouse_pos)
        self.sell_button.update_hover(mouse_pos)
        self.target_button.update_hover(mouse_pos)
