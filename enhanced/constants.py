TILE_SIZE = 32
GRID_WIDTH = 25
GRID_HEIGHT = 20
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH + 300  # Extra space for enhanced UI
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT
UI_PANEL_WIDTH = 300

# Enhanced color palette with alpha support
COLORS = {
    'red': (255, 100, 100),
    'green': (100, 255, 100),
    'blue': (100, 150, 255),
    'yellow': (255, 255, 100),
    'purple': (200, 100, 255),
    'orange': (255, 165, 0),
    'cyan': (0, 255, 255),
    'pink': (255, 105, 180),
    'lime': (50, 255, 50),
    'magenta': (255, 0, 255),
    'teal': (0, 200, 200),
    'gold': (255, 215, 0),
    
    # UI Colors
    'obstacle': (60, 60, 60),
    'agent': (255, 255, 0),
    'background': (20, 20, 20),
    'visited': (40, 40, 40),
    'path': (100, 100, 255),
    'target_highlight': (255, 255, 255),
    'ui_background': (30, 30, 30),
    'ui_text': (220, 220, 220),
    'ui_highlight': (80, 120, 255),
    'success': (0, 255, 0),
    'warning': (255, 165, 0),
    'error': (255, 50, 50)
}

all_possible_colors = [
    'red', 'green', 'blue', 'yellow', 'purple', 'orange', 
    'cyan', 'pink', 'lime', 'magenta', 'teal', 'gold'
]

# Agent behavior constants
MAX_TASK_QUEUE_SIZE = 50
PATHFIND_CACHE_SIZE = 1000
FAILED_ATTEMPT_COOLDOWN = 3000  # ms
EFFICIENCY_BONUS_MULTIPLIER = 1.2
CONSECUTIVE_SUCCESS_BONUS = 5

# Simulation parameters
DEFAULT_SIMULATION_SPEED = 10
MIN_SIMULATION_SPEED = 1
MAX_SIMULATION_SPEED = 30
OBSTACLE_DENSITY = 0.15  # 15% of grid
INITIAL_PAIRS = 6
MAX_CONCURRENT_PAIRS = 12