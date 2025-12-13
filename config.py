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
