TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 15
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT

COLORS = {
    'red': (255, 100, 100),
    'green': (100, 255, 100),
    'blue': (100, 100, 255),
    'yellow': (255, 255, 100),
    'purple': (200, 100, 255),
    'orange': (255, 165, 0),
    'cyan': (0, 255, 255),
    'pink': (255, 105, 180),
    'obstacle': (60, 60, 60),
    'agent': (255, 255, 0),
    'background': (20, 20, 20),
    'visited': (40, 40, 40)
}

all_possible_colors = [
    'red', 'green', 'blue', 'yellow', 'purple', 'orange', 'cyan', 'pink'
]
