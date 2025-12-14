import pygame
import sys
from config import *
from enemy import Enemy
from tower import Tower
from projectile import Projectile
from utility import TimeWarp

STRAIGHT_PATH = [(0, SCREEN_HEIGHT // 2), (SCREEN_WIDTH, SCREEN_HEIGHT // 2)]
ENEMY_TYPES = [
    "basic",
    "fast",
    "tank",
    "shielded",
    "splitter",
    "summoner",
    "flying_fortress",
    "air",
    "boss"
]
TOWER_TYPES = ["arrow", "cannon", "laser", "freeze", "splash", "sniper", "drone", "railgun", "flamethrower", "poison", "economy"]


class TestMode:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense Test Mode")
        self.clock = pygame.time.Clock()
        self.enemies = []
        self.projectiles = []
        self.towers = []
        self.time_warps = []
        self.selected_enemy = 0
        self.selected_tower = 0
        self.mode_font = pygame.font.Font(None, 24)
        self.grid_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.draw_grid_overlay()

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
        tower_type = TOWER_TYPES[self.selected_tower]
        grid_x, grid_y = grid_pos
        tower = Tower(grid_x, grid_y, tower_type)
        self.towers.append(tower)

    def spawn_time_warp(self, pos):
        warp = TimeWarp(*pos)
        self.time_warps.append(warp)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_RIGHT:
                    self.selected_enemy = (self.selected_enemy + 1) % len(ENEMY_TYPES)
                elif event.key == pygame.K_LEFT:
                    self.selected_enemy = (self.selected_enemy - 1) % len(ENEMY_TYPES)
                elif event.key == pygame.K_UP:
                    self.selected_tower = (self.selected_tower + 1) % len(TOWER_TYPES)
                elif event.key == pygame.K_DOWN:
                    self.selected_tower = (self.selected_tower - 1) % len(TOWER_TYPES)
                elif event.key == pygame.K_e:
                    self.spawn_enemy()
                elif event.key == pygame.K_w:
                    self.spawn_time_warp(pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    grid_x = mx // GRID_SIZE
                    grid_y = my // GRID_SIZE
                    self.place_tower((grid_x, grid_y))

    def update_entities(self):
        for warp in self.time_warps[:]:
            if not warp.update():
                self.time_warps.remove(warp)
        enemy_list = [e for e in self.enemies if e.alive and not e.reached_end]
        for tower in self.towers:
            projectile = tower.update(enemy_list)
            if projectile:
                self.projectiles.append(projectile)
            if getattr(tower, "generate_income", False):
                tower.generate_income = False
        for enemy in self.enemies:
            if enemy.alive and not enemy.reached_end:
                enemy.update()
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.active:
                self.projectiles.remove(projectile)

    def draw_path(self):
        pygame.draw.lines(self.screen, DARK_GRAY, False, STRAIGHT_PATH, 4)

    def draw_entities(self):
        for tower in self.towers:
            tower.draw(self.screen)
        for warp in self.time_warps:
            warp.draw(self.screen)
        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(self.screen)
        for projectile in self.projectiles:
            projectile.draw(self.screen)

    def draw_ui(self):
        instructions = [
            f"Enemy: {ENEMY_TYPES[self.selected_enemy]} (Left/Right ➜ cycle, E ➜ spawn)",
            f"Tower: {TOWER_TYPES[self.selected_tower]} (Up/Down ➜ cycle, Click ➜ place)",
            "W ➜ place Time Warp (infinite lives, straight path)",
            "Arrow keys cycle selections, ESC to quit"
        ]
        y_offset = 10
        for text in instructions:
            rendered = self.mode_font.render(text, True, WHITE)
            self.screen.blit(rendered, (10, y_offset))
            y_offset += 24

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
