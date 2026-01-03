"""
Procedural map generation for tower defense game
"""
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE

def generate_random_path(num_waypoints=8):
    """Generate a random winding path from left to right"""
    waypoints = []
    
    # Start from left side
    start_y = random.randint(SCREEN_HEIGHT // 4, 3 * SCREEN_HEIGHT // 4)
    waypoints.append((0, start_y))
    
    # Generate intermediate waypoints
    segment_width = SCREEN_WIDTH // (num_waypoints - 1)
    
    for i in range(1, num_waypoints - 1):
        x = i * segment_width + random.randint(-50, 50)
        # Keep y within bounds and create winding pattern
        if i % 2 == 1:
            y = random.randint(100, SCREEN_HEIGHT // 2 - 50)
        else:
            y = random.randint(SCREEN_HEIGHT // 2 + 50, SCREEN_HEIGHT - 100)
        
        waypoints.append((x, y))
    
    # End on right side
    end_y = random.randint(SCREEN_HEIGHT // 4, 3 * SCREEN_HEIGHT // 4)
    waypoints.append((SCREEN_WIDTH, end_y))
    
    return waypoints

def generate_multi_lane_paths():
    """Generate two separate paths for multi-lane mode"""
    path1 = []
    path2 = []
    
    # Top lane
    start_y1 = random.randint(100, SCREEN_HEIGHT // 3)
    path1.append((0, start_y1))
    
    for i in range(1, 5):
        x = i * (SCREEN_WIDTH // 5)
        y = start_y1 + random.randint(-50, 50)
        y = max(100, min(SCREEN_HEIGHT // 3, y))
        path1.append((x, y))
    
    path1.append((SCREEN_WIDTH, start_y1 + random.randint(-30, 30)))
    
    # Bottom lane
    start_y2 = random.randint(2 * SCREEN_HEIGHT // 3, SCREEN_HEIGHT - 100)
    path2.append((0, start_y2))
    
    for i in range(1, 5):
        x = i * (SCREEN_WIDTH // 5)
        y = start_y2 + random.randint(-50, 50)
        y = max(2 * SCREEN_HEIGHT // 3, min(SCREEN_HEIGHT - 100, y))
        path2.append((x, y))
    
    path2.append((SCREEN_WIDTH, start_y2 + random.randint(-30, 30)))
    
    return path1, path2
