import pygame
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from enemy import Enemy
from tower import Tower
from projectile import Projectile
from utility import TimeWarp
from barrier import Barrier

STRAIGHT_PATH = [(50, SCREEN_HEIGHT // 2), (SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2)]
ENEMY_TYPES = [
    "basic",
    "fast",
    "tank",
    "shielded",
    "splitter",
    "air",
    "summoner",
    "flying_fortress",
    "decoy",
    "swarm",
    "boss"
]
TOWER_TYPES = ["arrow", "cannon", "laser", "freeze", "splash", "sniper", "drone_swarm", "railgun", "flamethrower", "poison", "economy"]


class TestMode:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense Test Mode - Sandbox")
        self.clock = pygame.time.Clock()
        self.enemies = []
        self.projectiles = []
        self.towers = []
        self.time_warps = []
        self.barriers = []
        self.selected_enemy = 0
        self.selected_tower = 0
        self.lives = 100
        self.money = 999999
        self.wave_number = 1
        self.mode_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.grid_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.draw_grid_overlay()
        # Initialize grid for tower placement tracking
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def draw_grid_overlay(self):
        self.grid_overlay.fill((0, 0, 0, 0))
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.grid_overlay, LIGHT_GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.grid_overlay, LIGHT_GRAY, (0, y), (SCREEN_WIDTH, y), 1)

    def spawn_enemy(self):
        enemy_type = ENEMY_TYPES[self.selected_enemy]
        enemy = Enemy(STRAIGHT_PATH, enemy_type)
        self.enemies.append(enemy)

    def place_tower(self, grid_pos):
        grid_x, grid_y = grid_pos
        # Check if cell is already occupied
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            if self.grid[grid_y][grid_x] is None:
                tower_type = TOWER_TYPES[self.selected_tower]
                tower = Tower(grid_x, grid_y, tower_type)
                self.towers.append(tower)
                self.grid[grid_y][grid_x] = tower
                return True
        return False
    
    def place_barrier(self, grid_pos):
        grid_x, grid_y = grid_pos
        # Check if cell is already occupied
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            if self.grid[grid_y][grid_x] is None:
                barrier = Barrier(grid_x, grid_y)
                self.barriers.append(barrier)
                self.grid[grid_y][grid_x] = barrier
                return True
        return False

    def spawn_time_warp(self, pos):
        warp = TimeWarp(*pos)
        self.time_warps.append(warp)

    def handle_input(self):
        keys_pressed = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # Enemy selection
                elif event.key == pygame.K_RIGHT:
                    self.selected_enemy = (self.selected_enemy + 1) % len(ENEMY_TYPES)
                elif event.key == pygame.K_LEFT:
                    self.selected_enemy = (self.selected_enemy - 1) % len(ENEMY_TYPES)
                # Tower selection
                elif event.key == pygame.K_UP:
                    self.selected_tower = (self.selected_tower + 1) % len(TOWER_TYPES)
                elif event.key == pygame.K_DOWN:
                    self.selected_tower = (self.selected_tower - 1) % len(TOWER_TYPES)
                # Spawn enemy
                elif event.key == pygame.K_SPACE:
                    self.spawn_enemy()
                # Spawn multiple enemies (useful for testing)
                elif event.key == pygame.K_m:
                    for _ in range(5):
                        self.spawn_enemy()
                # Place time warp at mouse position
                elif event.key == pygame.K_t:
                    self.spawn_time_warp(pygame.mouse.get_pos())
                # Clear all enemies
                elif event.key == pygame.K_c:
                    self.enemies.clear()
                # Reset test
                elif event.key == pygame.K_r:
                    self.enemies.clear()
                    self.projectiles.clear()
                    self.towers.clear()
                    self.time_warps.clear()
                    self.barriers.clear()
                    self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
                    self.lives = 100
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                grid_x = mx // GRID_SIZE
                grid_y = my // GRID_SIZE
                
                if event.button == 1:  # Left click - place tower
                    self.place_tower((grid_x, grid_y))
                elif event.button == 3:  # Right click - place barrier
                    self.place_barrier((grid_x, grid_y))

    def update_entities(self):
        # Update time warps
        for warp in self.time_warps[:]:
            if not warp.update():
                self.time_warps.remove(warp)
        
        # Update barriers - enemies damage them
        for barrier in self.barriers[:]:
            if not barrier.alive:
                self.barriers.remove(barrier)
                grid_x, grid_y = barrier.grid_x, barrier.grid_y
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    self.grid[grid_y][grid_x] = None
        
        # Get active enemies for targeting
        enemy_list = [e for e in self.enemies if e.alive and not e.reached_end]
        
        # Update towers and handle spawning/income
        for tower in self.towers:
            projectile = tower.update(enemy_list)
            if projectile:
                if isinstance(projectile, list):
                    self.projectiles.extend(projectile)
                else:
                    self.projectiles.append(projectile)
            
            # Handle economy tower income
            if getattr(tower, "is_economy", False):
                if not hasattr(tower, "income_timer"):
                    tower.income_timer = 0
                tower.income_timer += 1
                if tower.income_timer >= getattr(tower, "income_interval", 60):
                    self.money += getattr(tower, "income_amount", 5)
                    tower.income_timer = 0
            
            # Handle drone tower spawning
            if getattr(tower, "is_drone_tower", False):
                if not hasattr(tower, "drone_spawn_timer"):
                    tower.drone_spawn_timer = 0
                tower.drone_spawn_timer += 1
                if tower.drone_spawn_timer >= getattr(tower, "drone_spawn_delay", 300):
                    # Spawn drone projectile
                    if enemy_list:
                        import random
                        target = random.choice(enemy_list)
                        from projectile import Projectile
                        drone = Projectile(tower.x, tower.y, target, tower.damage, "drone")
                        self.projectiles.append(drone)
                    tower.drone_spawn_timer = 0
        
        # Update enemies
        for enemy in self.enemies[:]:
            if enemy.alive and not enemy.reached_end:
                enemy.update()
                # Check if enemy reached end
                if enemy.reached_end:
                    self.lives -= 1
            # Remove dead or finished enemies
            if not enemy.alive or enemy.reached_end:
                if enemy in enemy_list:
                    enemy_list.remove(enemy)
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.active:
                self.projectiles.remove(projectile)

    def draw_path(self):
        pygame.draw.lines(self.screen, DARK_GRAY, False, STRAIGHT_PATH, 4)

    def draw_entities(self):
        # Draw towers
        for tower in self.towers:
            tower.draw(self.screen)
        # Draw barriers
        for barrier in self.barriers:
            if barrier.alive:
                barrier.draw(self.screen)
        # Draw time warps
        for warp in self.time_warps:
            warp.draw(self.screen)
        # Draw enemies
        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(self.screen)
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)

    def draw_ui(self):
        # Title and stats
        title = self.mode_font.render("TEST MODE - SANDBOX", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))
        
        stats = self.small_font.render(f"Lives: {self.lives}  |  Money: ${self.money}  |  Enemies: {len([e for e in self.enemies if e.alive])}  |  Towers: {len(self.towers)}", True, WHITE)
        self.screen.blit(stats, (10, 40))
        
        # Instructions on the left
        instructions = [
            f"ENEMY: {ENEMY_TYPES[self.selected_enemy].upper()}",
            "← → : Change Enemy",
            "SPACE: Spawn 1",
            "M: Spawn 5",
            "",
            f"TOWER: {TOWER_TYPES[self.selected_tower].upper()}",
            "↑ ↓ : Change Tower",
            "LEFT CLICK: Place Tower",
            "",
            "RIGHT CLICK: Place Barrier",
            "T: Place Time Warp",
            "C: Clear Enemies",
            "R: Reset All",
            "ESC: Quit"
        ]
        y_offset = 70
        for text in instructions:
            if text == "":
                y_offset += 10
                continue
            color = LIGHT_GRAY if text.startswith(" ") or ":" in text else WHITE
            rendered = self.small_font.render(text, True, color)
            self.screen.blit(rendered, (10, y_offset))
            y_offset += 20

    def run(self):
        while True:
            self.handle_input()
            self.update_entities()
            self.screen.fill(BLACK)
            self.screen.blit(self.grid_overlay, (0, 0))
            self.draw_path()
            self.draw_entities()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    TestMode().run()
