# How to Run the Tower Defense Game

## Installation

1. Install Python 3.8 or higher
2. Install pygame:
```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python game_src/main.py
```

Or from the game_src directory:
```bash
cd game_src
python main.py
```

## How to Play

### Objective
Defend the path from enemies! Survive 10 waves to win.

### Controls
- **SPACE**: Start game / Pause/Unpause
- **ESC**: Deselect tower type or selected tower
- **R**: Restart game (on game over/victory screen)
- **Mouse**: Click to select and place towers

### Game Mechanics

1. **Placing Towers**
   - Click on a tower button at the top (Arrow, Cannon, or Laser)
   - Move your mouse over the grid (a ghost tower will appear)
   - Click on a valid cell (green outline) to place the tower
   - Green cells are buildable, red cells are blocked

2. **Tower Types**
   - **Arrow Tower ($100)**: Fast fire rate, low damage, cheap
   - **Cannon Tower ($200)**: Slow fire rate, high damage
   - **Laser Tower ($300)**: Very fast fire rate, medium damage, longest range

3. **Upgrading Towers**
   - Click on a placed tower to select it
   - Click the "Upgrade" button to improve its stats
   - Towers can be upgraded up to level 3
   - Each upgrade increases damage, range, and fire rate

4. **Selling Towers**
   - Select a tower
   - Click the "Sell" button to get 75% of your investment back

5. **Enemy Types**
   - **Basic (Red)**: Normal speed and health, 20 gold reward
   - **Fast (Yellow)**: High speed, low health, 15 gold reward
   - **Tank (Dark Gray)**: Slow speed, high health, 50 gold reward

6. **Resources**
   - Starting money: $500
   - Starting lives: 20
   - Gain money by killing enemies
   - Lose lives when enemies reach the end of the path

7. **Waves**
   - Click "Next Wave" to start the next wave
   - Waves get progressively harder with more and tougher enemies
   - Survive all 10 waves to win!

## Game Structure

The game is organized into several modules in the `game_src/` folder:

- `game_src/main.py`: Entry point for the game
- `game_src/game.py`: Main game loop and state management
- `game_src/config.py`: Game configuration constants
- `game_src/enemy.py`: Enemy classes and behaviors
- `game_src/tower.py`: Tower classes and behaviors
- `game_src/projectile.py`: Projectile/bullet system
- `game_src/wave.py`: Wave spawning system
- `game_src/ui.py`: User interface elements
- `game_src/test_game.py`: Test suite

## Tips

- Place towers at corners where enemies spend more time in range
- Arrow towers are cheap and good for early waves
- Laser towers have the longest range but are expensive
- Upgrade your towers to handle stronger enemies
- Don't forget to start the next wave when ready!
