"""
Comprehensive test suite for tower defense game
"""
import pygame
import sys

# Initialize pygame
pygame.init()

# Import game modules
from config import *
from enemy import Enemy
from tower import Tower
from projectile import Projectile
from wave import Wave
from game import Game
from ui import UI

def test_enemy_system():
    """Test enemy creation and movement"""
    print("Testing Enemy System...")
    
    # Test basic enemy
    enemy = Enemy(PATH_WAYPOINTS, "basic")
    assert enemy.health == 100, "Basic enemy health incorrect"
    assert enemy.speed == 2, "Basic enemy speed incorrect"
    assert enemy.reward == 20, "Basic enemy reward incorrect"
    
    # Test fast enemy
    enemy_fast = Enemy(PATH_WAYPOINTS, "fast")
    assert enemy_fast.health == 50, "Fast enemy health incorrect"
    assert enemy_fast.speed == 4, "Fast enemy speed incorrect"
    
    # Test tank enemy
    enemy_tank = Enemy(PATH_WAYPOINTS, "tank")
    assert enemy_tank.health == 300, "Tank enemy health incorrect"
    assert enemy_tank.speed == 1, "Tank enemy speed incorrect"
    
    # Test enemy movement - move multiple times to ensure movement
    initial_pos = enemy.position.copy()
    for _ in range(10):
        enemy.move()
    assert enemy.position != initial_pos, "Enemy should move"
    
    # Test damage
    enemy.take_damage(30)
    assert enemy.health == 70, "Enemy damage not working"
    enemy.take_damage(100)
    assert not enemy.alive, "Enemy should be dead"
    
    print("✓ Enemy System tests passed")

def test_tower_system():
    """Test tower creation and targeting"""
    print("Testing Tower System...")
    
    # Test arrow tower
    tower = Tower(5, 5, "arrow")
    assert tower.damage == 20, "Arrow tower damage incorrect"
    assert tower.range == 150, "Arrow tower range incorrect"
    assert tower.cost == 100, "Arrow tower cost incorrect"
    
    # Test cannon tower
    tower_cannon = Tower(5, 5, "cannon")
    assert tower_cannon.damage == 60, "Cannon tower damage incorrect"
    assert tower_cannon.cost == 200, "Cannon tower cost incorrect"
    
    # Test laser tower
    tower_laser = Tower(5, 5, "laser")
    assert tower_laser.damage == 15, "Laser tower damage incorrect"
    assert tower_laser.cost == 300, "Laser tower cost incorrect"
    
    # Test tower upgrade
    initial_damage = tower.damage
    cost = tower.upgrade()
    assert tower.level == 2, "Tower level not increased"
    assert tower.damage > initial_damage, "Tower damage not increased"
    assert cost == 150, "Upgrade cost incorrect"
    
    # Test sell value
    sell_value = tower.get_sell_value()
    assert sell_value > 0, "Sell value should be positive"
    
    print("✓ Tower System tests passed")

def test_projectile_system():
    """Test projectile creation and movement"""
    print("Testing Projectile System...")
    
    enemy = Enemy(PATH_WAYPOINTS, "basic")
    projectile = Projectile(100, 100, enemy, 20, 8)
    
    assert projectile.active, "Projectile should be active"
    assert projectile.damage == 20, "Projectile damage incorrect"
    
    # Test projectile update
    initial_pos = projectile.position.copy()
    projectile.update()
    assert projectile.position != initial_pos, "Projectile should move"
    
    print("✓ Projectile System tests passed")

def test_wave_system():
    """Test wave spawning"""
    print("Testing Wave System...")
    
    wave = Wave(1, PATH_WAYPOINTS)
    assert wave.wave_number == 1, "Wave number incorrect"
    assert len(wave.spawn_queue) > 0, "Wave should have enemies to spawn"
    
    # Test wave 2 has more enemies
    wave2 = Wave(2, PATH_WAYPOINTS)
    assert len(wave2.spawn_queue) > len(wave.spawn_queue), "Wave 2 should have more enemies"
    
    print("✓ Wave System tests passed")

def test_game_initialization():
    """Test game initialization"""
    print("Testing Game Initialization...")
    
    game = Game()
    assert game.money == STARTING_MONEY, "Starting money incorrect"
    assert game.lives == STARTING_LIVES, "Starting lives incorrect"
    assert game.wave_number == 0, "Initial wave number should be 0"
    assert len(game.towers) == 0, "Should start with no towers"
    assert game.state == "menu", "Should start in menu state"
    
    print("✓ Game Initialization tests passed")

def test_ui_system():
    """Test UI components"""
    print("Testing UI System...")
    
    ui = UI()
    assert len(ui.tower_buttons) == 3, "Should have 3 tower buttons"
    assert "arrow" in ui.tower_buttons, "Should have arrow tower button"
    assert "cannon" in ui.tower_buttons, "Should have cannon tower button"
    assert "laser" in ui.tower_buttons, "Should have laser tower button"
    
    print("✓ UI System tests passed")

def test_config():
    """Test configuration constants"""
    print("Testing Configuration...")
    
    assert SCREEN_WIDTH == 1200, "Screen width incorrect"
    assert SCREEN_HEIGHT == 800, "Screen height incorrect"
    assert FPS == 60, "FPS incorrect"
    assert STARTING_MONEY == 500, "Starting money incorrect"
    assert STARTING_LIVES == 20, "Starting lives incorrect"
    assert len(PATH_WAYPOINTS) == 8, "Path should have 8 waypoints"
    assert "arrow" in TOWER_COSTS, "Tower costs should include arrow"
    assert TOWER_COSTS["arrow"] == 100, "Arrow tower cost incorrect"
    
    print("✓ Configuration tests passed")

def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*50)
    print("Running Tower Defense Game Test Suite")
    print("="*50 + "\n")
    
    try:
        test_config()
        test_enemy_system()
        test_tower_system()
        test_projectile_system()
        test_wave_system()
        test_game_initialization()
        test_ui_system()
        
        print("\n" + "="*50)
        print("✓ ALL TESTS PASSED!")
        print("="*50)
        return True
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    pygame.quit()
    sys.exit(0 if success else 1)
