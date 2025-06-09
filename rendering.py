import pygame
from constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS


def draw_enhanced(agent, boxes, holes, obstacles, screen):
    font = pygame.font.SysFont(None, 20)
    title_font = pygame.font.SysFont(None, 24)
    screen.fill(COLORS['background'])
    
    for pos in agent.visited_positions:
        pygame.draw.rect(screen, COLORS['visited'], (pos[0]*TILE_SIZE+2, pos[1]*TILE_SIZE+2, TILE_SIZE-4, TILE_SIZE-4))

    for (x, y) in obstacles:
        pygame.draw.rect(screen, COLORS['obstacle'], (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    for (x, y), color in holes:
        pygame.draw.circle(screen, COLORS[color], (x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE//2), TILE_SIZE//4)

    for (x, y), color in boxes:
        pygame.draw.rect(screen, COLORS[color], (x*TILE_SIZE+6, y*TILE_SIZE+6, TILE_SIZE-12, TILE_SIZE-12))
        if agent.current_task and (x, y) == agent.current_task.box_pos:
            pygame.draw.rect(screen, (255, 255, 255), (x*TILE_SIZE+4, y*TILE_SIZE+4, TILE_SIZE-8, TILE_SIZE-8), 2)

    ax, ay = agent.pos
    agent_color = COLORS[agent.carrying] if agent.carrying else COLORS['agent']
    pygame.draw.circle(screen, agent_color, (ax*TILE_SIZE+TILE_SIZE//2, ay*TILE_SIZE+TILE_SIZE//2), TILE_SIZE//2)

    y_offset = 10
    screen.blit(title_font.render("Intelligent Agent", True, (255, 255, 255)), (10, y_offset))
    y_offset += 30

    stats = [
        f"Tasks Completed: {agent.tasks_completed}",
        f"Carrying: {agent.carrying or 'Nothing'}",
        f"Thought: {agent.thought}"
    ]
    for stat in stats:
        screen.blit(font.render(stat, True, (200, 200, 200)), (10, y_offset))
        y_offset += 20

    pygame.display.flip()
