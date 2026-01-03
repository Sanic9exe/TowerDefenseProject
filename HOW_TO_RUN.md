# How to Run the Tower Defense Game - Enhanced Edition

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

### Game Modes
When you start, you'll select a difficulty and game mode:
- **Easy (Press 1)**: Enemies have 70% health, you start with $700
- **Normal (Press 2)**: Standard experience, start with $500
- **Hard (Press 3)**: Enemies have 150% health, earn 2x money, includes air units, unlock barriers
- **Endless (Press E)**: Infinite waves with random map generation, survive as long as possible!
- **Multi-Lane (Press M)**: Defend TWO paths simultaneously, ultimate challenge!

### Controls
- **SPACE**: Start game / Pause/Unpause
- **ESC**: Deselect tower type or selected tower
- **R**: Restart game (on game over/victory screen)
- **Mouse**: Click to select, place, and interact with towers
- **1/2/3**: Select difficulty at start screen
- **E**: Select Endless mode (random map)
- **M**: Select Multi-Lane mode (2 paths)

### Game Mechanics

1. **Placing Towers**
   - Click on an unlocked tower button (top of screen)
   - Move your mouse over the grid (a ghost tower will appear)
   - Click on a valid cell (green outline) to place the tower
   - Green cells are buildable, red cells are blocked

2. **Tower Types** (unlock progressively)
   - **Arrow Tower ($100)**: Fast fire rate, low damage, good starter
   - **Cannon Tower ($200)**: Slow fire rate, high damage
   - **Laser Tower ($300)**: Very fast, medium damage, can hit air units
   - **Freeze Tower ($250)**: Unlocks wave 3, slows enemies
   - **Splash Tower ($350)**: Unlocks wave 5, area damage
   - **Sniper Tower ($400)**: Unlocks wave 7, long range, can hit air

3. **Tower Management**
   - Click on a placed tower to select it
   - **Upgrade** button: Improve stats (up to level 3)
   - **Sell** button: Get money back (full refund within 5 seconds if not fired)
   - **Target** button: Cycle targeting modes
   - Each upgrade increases damage, range, and fire rate

4. **Targeting Modes** (NEW!)
   - **Closest**: Target nearest enemy to tower (default)
   - **Strongest**: Target enemy with most health
   - **Weakest**: Target enemy with least health
   - **First**: Target enemy furthest along path
   - **Last**: Target enemy at start of path
   - **Nearest Exit**: Target enemy closest to end
   - Click "Target" button on selected tower to cycle modes

5. **Selling Towers** (ENHANCED!)
   - **Full Refund**: Sell within 5 seconds of placing (if tower hasn't fired)
   - **90% Refund**: Sell tower that has never fired
   - **75% Refund**: Standard refund rate

6. **Enemy Types** (EXPANDED!)
   - **Basic (Red)**: Normal speed and health, 20 gold
   - **Fast (Yellow)**: High speed, low health, 15 gold
   - **Tank (Dark Gray)**: Slow speed, high health, 50 gold
   - **Shielded (Blue)**: Has shield that blocks 3 hits, 30 gold
   - **Splitter (Orange)**: Splits into 2 smaller enemies on death, 25 gold
   - **Air (Light Blue)**: Flies over path, needs anti-air towers, 35 gold (Hard mode)
   - **Boss (Purple)**: Every 5 waves, massive health, regenerating shields, 200 gold

7. **Resources**
   - Starting money: Varies by difficulty ($400-$700)
   - Starting lives: 20
   - Gain money by killing enemies (2x in Hard mode)
   - Lose lives when enemies reach the end of the path

8. **Waves**
   - Click "Next Wave" to start the next wave
   - Click "Speed" button to toggle 1x/2x/3x game speed
   - Waves get progressively harder with more and tougher enemies
   - Boss waves every 5 waves!
   - **Normal Mode**: Survive 10 waves to win
   - **Endless Mode**: Waves continue forever with random map, see how long you last!
   - **Multi-Lane Mode**: Defend 2 paths simultaneously for 10 waves

9. **Barriers** (Hard Mode Only)
   - Click "Barrier" button ($50 each)
   - Place on the path to block enemies
   - Maximum of 10 barriers
   - Enemies damage barriers (200 HP each)
   - Use to extend enemy path or create choke points

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

## Strategy Tips

### General Tips
- Place towers at corners where enemies spend more time in range
- Arrow towers are cheap and good for early waves
- Save money for the boss waves (every 5 waves)
- Use the "Sell" feature within 5 seconds to reposition misplaced towers
- Upgrade strategic towers rather than building many weak ones
- Use fast-forward (2x/3x speed) when confident to speed through waves

### Targeting Strategy
- Use "Strongest" targeting for boss enemies
- Use "Nearest Exit" targeting to prevent enemies from escaping
- Use "Weakest" targeting to eliminate enemies quickly for money
- Mix targeting modes across different towers for optimal coverage

### Enemy-Specific Tips
- **Shielded enemies**: Need multiple hits, focus fire with several towers
- **Splitter enemies**: Can overwhelm you, kill them early or far from exit
- **Air units**: Require Laser or Sniper towers (can't be hit by others)
- **Boss enemies**: Shields regenerate! Focus fire to break shields quickly

### Mode-Specific Tips
- **Easy**: Great for learning, experiment with tower combinations
- **Normal**: Balanced, requires good tower placement and upgrades
- **Hard**: Air units + barriers! Build Laser/Sniper towers, use barriers strategically, 2x money
- **Endless**: Random maps each time! Prioritize upgrades and adaptability
- **Multi-Lane**: Split your defense! Place towers between paths to cover both lanes

### Animation Features
- **Tower Rotation**: Watch barrels turn to track enemies
- **Recoil Effect**: Towers visually recoil when firing
- **Charge Effect**: Laser and Sniper show charging animations
- Visual feedback helps you understand tower behavior
