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
    "sniper": 400,
    "drone": 500,
    "railgun": 600,
    "flamethrower": 300,
    "poison": 350,
    "economy": 400
}

# Tower targeting modes
TARGETING_MODES = ["closest", "strongest", "weakest", "first", "last", "nearest_exit"]

# Game speed multipliers
SPEED_OPTIONS = [1, 2, 3]

# Barrier settings
BARRIER_COST = 50
MAX_BARRIERS = 10  # Maximum number of barriers in hard mode

# Game modes
GAME_MODES = ["normal", "endless", "multi_lane", "path_randomizer", "one_life", "reverse"]

# Utility settings
TIME_WARP_COST = 150
TIME_WARP_DURATION = 180  # 3 seconds at 60 FPS
TIME_WARP_RADIUS = 120
TIME_WARP_SLOW = 0.3  # Slows to 30% speed

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

# Alternative paths for multi-lane mode
PATH_WAYPOINTS_TOP = [
    (0, 200),
    (400, 200),
    (400, 100),
    (800, 100),
    (800, 300),
    (1200, 300)
]

PATH_WAYPOINTS_BOTTOM = [
    (0, 600),
    (400, 600),
    (400, 700),
    (800, 700),
    (800, 500),
    (1200, 500)
]
