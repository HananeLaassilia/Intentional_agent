import pygame
import sys
import random
from constants import GRID_WIDTH, GRID_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
from agent import IntelligentAgent
from rendering import draw_enhanced

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

def run_intelligent_simulation():
    max_duration = 120_000
    start_time = pygame.time.get_ticks()
    generation_interval = 10000
    last_generation = start_time

    obstacles = set()
    while len(obstacles) < 80:
        pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        if pos != (0, 0):
            obstacles.add(pos)

    boxes, holes = [], []

    def spawn_box_hole():
        from constants import all_possible_colors
        active_colors = {color for _, color in boxes + holes}
        available_colors = [c for c in all_possible_colors if c not in active_colors]
        if not available_colors:
            return

        spawn_count = min(4, len(available_colors))
        for _ in range(spawn_count):
            color = available_colors.pop(0)

            for container, others in [(boxes, holes), (holes, boxes)]:
                attempts = 0
                while attempts < 50:
                    pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
                    if pos not in obstacles and pos not in [b[0] for b in boxes] and pos not in [h[0] for h in holes]:
                        container.append((pos, color))
                        break
                    attempts += 1

    spawn_box_hole()
    agent = IntelligentAgent((0, 0))

    while True:
        now = pygame.time.get_ticks()
        if now - start_time > max_duration:
            agent.thought = f"Done. Score: {agent.efficiency_score}"
            draw_enhanced(agent, boxes, holes, obstacles, screen)
            pygame.time.delay(5000)
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if now - last_generation > generation_interval:
            spawn_box_hole()
            last_generation = now
            agent.thought = "New targets spawned."

        agent.update_intelligence(boxes, holes, obstacles)
        agent.execute_movement()
        agent.handle_pickup(boxes)
        agent.handle_drop(holes)

        draw_enhanced(agent, boxes, holes, obstacles, screen)
        clock.tick(8)
