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
        
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
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
        
        # Tower selection buttons
        self.tower_buttons = {
            "arrow": Button(20, 20, 100, 60, f"Arrow\n${TOWER_COSTS['arrow']}", DARK_GREEN),
            "cannon": Button(130, 20, 100, 60, f"Cannon\n${TOWER_COSTS['cannon']}", DARK_GRAY),
            "laser": Button(240, 20, 100, 60, f"Laser\n${TOWER_COSTS['laser']}", BLUE)
        }
        
        # Control buttons
        self.next_wave_button = Button(SCREEN_WIDTH - 150, 20, 130, 40, "Next Wave", GREEN)
        self.pause_button = Button(SCREEN_WIDTH - 150, 70, 130, 40, "Pause", GRAY)
        
        # Tower action buttons (shown when tower selected)
        self.upgrade_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 120, 130, 40, "Upgrade", GREEN)
        self.sell_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 70, 130, 40, "Sell", RED)
        
        self.selected_tower_type = None
        
    def draw_hud(self, screen, money, lives, wave_number):
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
    
    def draw_tower_buttons(self, screen, money):
        """Draw tower selection buttons"""
        for tower_type, button in self.tower_buttons.items():
            button.draw(screen)
            if self.selected_tower_type == tower_type:
                pygame.draw.rect(screen, YELLOW, button.rect, 4)
    
    def draw_control_buttons(self, screen):
        """Draw control buttons"""
        self.next_wave_button.draw(screen)
        self.pause_button.draw(screen)
    
    def draw_tower_info(self, screen, tower, money):
        """Draw selected tower information and action buttons"""
        # Info panel background
        panel_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 200, 160, 180)
        pygame.draw.rect(screen, LIGHT_GRAY, panel_rect)
        pygame.draw.rect(screen, BLACK, panel_rect, 2)
        
        # Tower stats
        y_offset = SCREEN_HEIGHT - 190
        stats = [
            f"Level: {tower.level}",
            f"Damage: {tower.damage}",
            f"Range: {tower.range}",
            f"Type: {tower.tower_type}"
        ]
        
        for stat in stats:
            text = self.font_small.render(stat, True, BLACK)
            screen.blit(text, (SCREEN_WIDTH - 170, y_offset))
            y_offset += 25
        
        # Upgrade button
        if tower.level < 3:
            self.upgrade_button.text = f"Upgrade ${tower.upgrade_cost}"
            self.upgrade_button.color = GREEN if money >= tower.upgrade_cost else GRAY
            self.upgrade_button.draw(screen)
        
        # Sell button
        self.sell_button.text = f"Sell ${tower.get_sell_value()}"
        self.sell_button.draw(screen)
    
    def draw_tower_ghost(self, screen, tower_type, grid_x, grid_y, valid):
        """Draw ghost tower at mouse position"""
        if tower_type in ["arrow", "cannon", "laser"]:
            color = GREEN if valid else RED
            alpha = 128
            ghost_surface = pygame.Surface((GRID_SIZE - 20, GRID_SIZE - 20))
            ghost_surface.set_alpha(alpha)
            
            tower_colors = {"arrow": DARK_GREEN, "cannon": DARK_GRAY, "laser": BLUE}
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
        self.upgrade_button.update_hover(mouse_pos)
        self.sell_button.update_hover(mouse_pos)
