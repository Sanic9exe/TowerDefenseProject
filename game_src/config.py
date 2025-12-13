"""
Game Configuration Constants
"""

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Grid settings
GRID_SIZE = 64
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (34, 139, 34)

# Game settings
STARTING_MONEY = 500
STARTING_LIVES = 20

# Difficulty settings
DIFFICULTY_MODIFIERS = {
    "easy": {"enemy_health": 0.7, "enemy_speed": 0.8, "money_mult": 1.2, "starting_money": 700},
    "normal": {"enemy_health": 1.0, "enemy_speed": 1.0, "money_mult": 1.0, "starting_money": 500},
    "hard": {"enemy_health": 1.5, "enemy_speed": 1.2, "money_mult": 2.0, "starting_money": 400}
}

# Tower costs
TOWER_COSTS = {
    "arrow": 100,
    "cannon": 200,
    "laser": 300,
    "freeze": 250,
    "splash": 350,
    "sniper": 400
}

# Tower targeting modes
TARGETING_MODES = ["closest", "strongest", "weakest", "first", "last", "nearest_exit"]

# Game speed multipliers
SPEED_OPTIONS = [1, 2, 3]

# Path waypoints (x, y) coordinates
PATH_WAYPOINTS = [
    (0, 400),
    (300, 400),
    (300, 200),
    (600, 200),
    (600, 600),
    (900, 600),
    (900, 300),
    (1200, 300)
]
