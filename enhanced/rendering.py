import pygame
import math
import random
from constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS

def draw_agent(agent, boxes, holes, obstacles, screen):
    screen.fill(COLORS['background'])

    for pos in agent.visited_positions:
        alpha = 30
        visited_surface = pygame.Surface((TILE_SIZE-4, TILE_SIZE-4))
        visited_surface.set_alpha(alpha)
        visited_surface.fill(COLORS['visited'])
        screen.blit(visited_surface, (pos[0]*TILE_SIZE+2, pos[1]*TILE_SIZE+2))

    for (x, y) in obstacles:
        pygame.draw.rect(screen, COLORS['obstacle'], (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    for (x, y) in agent.belief_obstacles:
        if (x, y) not in obstacles:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 100 + 155
            color = (min(255, pulse), 0, 0)
            pygame.draw.rect(screen, color, (x*TILE_SIZE+2, y*TILE_SIZE+2, TILE_SIZE-4, TILE_SIZE-4), 2)

    for (x, y), color in holes:
        pygame.draw.circle(screen, COLORS[color], (x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE//2), TILE_SIZE//4)

    for (x, y), color in boxes:
        pygame.draw.rect(screen, COLORS[color], (x*TILE_SIZE+6, y*TILE_SIZE+6, TILE_SIZE-12, TILE_SIZE-12))
        
        if agent.current_task and (x, y) == agent.current_task.box_pos:
            pygame.draw.rect(screen, (255, 255, 255), (x*TILE_SIZE+4, y*TILE_SIZE+4, TILE_SIZE-8, TILE_SIZE-8), 2)
        
        if agent.user_request_target and (x, y) == agent.user_request_target:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.02)) * 100 + 155
            color_pulse = (min(255, pulse), min(255, pulse), 0)
            pygame.draw.rect(screen, color_pulse, (x*TILE_SIZE+2, y*TILE_SIZE+2, TILE_SIZE-4, TILE_SIZE-4), 3)

    if agent.path and len(agent.path) > 1:
        path_points = []
        for pos in agent.path:
            center_x = pos[0] * TILE_SIZE + TILE_SIZE // 2
            center_y = pos[1] * TILE_SIZE + TILE_SIZE // 2
            path_points.append((center_x, center_y))
        
        # Path color for commitment level
        if agent.commitment_intensity > 7:
            path_color = (0, 255, 0)  # Green for high commitment
        elif agent.commitment_intensity > 4:
            path_color = (255, 255, 0)  # Yellow for medium commitment  
        else:
            path_color = (100, 100, 100)  # Gray for low commitment
            
        if len(path_points) > 1:
            pygame.draw.lines(screen, path_color, False, path_points, 2)

    ax, ay = agent.pos
    
    agent_color = COLORS[agent.carrying] if agent.carrying else COLORS['agent']
    
    base_radius = TILE_SIZE // 2
    agent_radius = int(base_radius * agent.agent_size_multiplier)
    
    bounce_y_offset = int(agent.bounce_offset) if agent.bouncing_excitedly else 0
    
    agent_center = (ax*TILE_SIZE + TILE_SIZE//2, ay*TILE_SIZE + TILE_SIZE//2 + bounce_y_offset)
    
    if len(agent.trail_positions) > 1 and agent.commitment_intensity > 7:
        for i, pos in enumerate(agent.trail_positions):
            alpha = int((i / len(agent.trail_positions)) * 150) + 50
            trail_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
            trail_surface.set_alpha(alpha)
            trail_color = (255, 255, 0) if agent.user_request_target else (0, 255, 0)
            pygame.draw.circle(trail_surface, trail_color, (TILE_SIZE//2, TILE_SIZE//2), base_radius//3)
            screen.blit(trail_surface, (pos[0]*TILE_SIZE, pos[1]*TILE_SIZE))
    
    if agent.celebration_timer > 0:
        for i in range(3):
            pulse_radius = agent_radius + int(math.sin((agent.celebration_timer + i*15) * 0.2) * 15) + i*12
            if pulse_radius > 0:
                celebration_color = [(255, 255, 0), (0, 255, 0), (255, 0, 255)][i]
                pygame.draw.circle(screen, celebration_color, agent_center, pulse_radius, 3)
        
        for _ in range(6):
            sparkle_x = agent_center[0] + random.randint(-30, 30)
            sparkle_y = agent_center[1] + random.randint(-30, 30)
            sparkle_size = random.randint(2, 4)
            pygame.draw.circle(screen, (255, 255, 255), (sparkle_x, sparkle_y), sparkle_size)
    
    if agent.giving_up_animation > 0:
        for i in range(2):
            shrink_factor = (agent.giving_up_animation / 120.0) * (1 - i*0.3)
            if shrink_factor > 0:
                shrink_radius = int((agent_radius + i*10) * shrink_factor)
                if shrink_radius > 0:
                    give_up_color = (255, 100, 100)
                    alpha = int(120 * shrink_factor)
                    give_up_surface = pygame.Surface((shrink_radius*2, shrink_radius*2))
                    give_up_surface.set_alpha(alpha)
                    pygame.draw.circle(give_up_surface, give_up_color, (shrink_radius, shrink_radius), shrink_radius, 2)
                    screen.blit(give_up_surface, (agent_center[0]-shrink_radius, agent_center[1]-shrink_radius))

    if (agent.commitment_intensity > 0 and agent.celebration_timer == 0 and 
        agent.giving_up_animation == 0):
        
        for i in range(int(agent.commitment_intensity // 3) + 1):
            ring_radius = agent_radius + 8 + i*6
            ring_thickness = max(2, agent.commitment_intensity // 3)
            
            if agent.commitment_intensity > 8:
                ring_color = (255, 0, 255)  # Purple for extreme commitment
            elif agent.commitment_intensity > 6:  
                ring_color = (255, 255, 0)  # Yellow for high commitment
            elif agent.commitment_intensity > 3:
                ring_color = (0, 255, 0)    # Green for medium commitment
            else:
                ring_color = (100, 100, 255)  # Blue for low commitment
                
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.008)) * 0.2 + 0.8
            pulsed_radius = int(ring_radius * pulse)
            
            pygame.draw.circle(screen, ring_color, agent_center, pulsed_radius, ring_thickness)

    if agent.side_effect_reaction > 0:
        flash_radius = int((agent.side_effect_reaction / 30.0) * 40) + 15
        flash_alpha = int((agent.side_effect_reaction / 30.0) * 150)
        flash_surface = pygame.Surface((flash_radius*2, flash_radius*2))
        flash_surface.set_alpha(flash_alpha)
        
        pygame.draw.circle(flash_surface, (255, 255, 255), (flash_radius, flash_radius), flash_radius, 3)
        screen.blit(flash_surface, (agent_center[0]-flash_radius, agent_center[1]-flash_radius))

    pygame.draw.circle(screen, agent_color, agent_center, max(5, agent_radius))
    
    if agent.carrying:
        carry_border_thickness = max(2, agent_radius // 6)
        pygame.draw.circle(screen, COLORS[agent.carrying], agent_center, agent_radius + 3, carry_border_thickness)
        carry_pulse = abs(math.sin(pygame.time.get_ticks() * 0.015)) * 0.3 + 0.7
        carry_inner_radius = int(agent_radius * carry_pulse * 0.5)
        pygame.draw.circle(screen, COLORS[agent.carrying], agent_center, carry_inner_radius)

    if agent.path and len(agent.path) > 0:
        next_pos = agent.path[0]
        direction_x = next_pos[0] - (agent.pos[0])
        direction_y = next_pos[1] - (agent.pos[1])
        if direction_x != 0 or direction_y != 0:
            length = math.sqrt(direction_x**2 + direction_y**2)
            if length > 0:
                direction_x /= length
                direction_y /= length
                
                arrow_length = agent_radius + 15
                arrow_end = (
                    agent_center[0] + direction_x * arrow_length,
                    agent_center[1] + direction_y * arrow_length
                )
                
                arrow_thickness = max(2, agent.commitment_intensity // 3)
                pygame.draw.line(screen, (255, 255, 255), agent_center, arrow_end, arrow_thickness)
                
                arrow_head_length = 8
                arrow_head_width = 6
                perpendicular_x = -direction_y
                perpendicular_y = direction_x
                
                head1 = (
                    arrow_end[0] - direction_x * arrow_head_length + perpendicular_x * arrow_head_width,
                    arrow_end[1] - direction_y * arrow_head_length + perpendicular_y * arrow_head_width
                )
                head2 = (
                    arrow_end[0] - direction_x * arrow_head_length - perpendicular_x * arrow_head_width,
                    arrow_end[1] - direction_y * arrow_head_length - perpendicular_y * arrow_head_width
                )
                
                pygame.draw.polygon(screen, (255, 255, 255), [arrow_end, head1, head2])

    pygame.display.flip()

def draw_scenario_indicator(screen, scenario_type):
    border_thickness = 8
    
    if scenario_type == "user_request":
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.02)) * 155 + 100
        border_color = (0, int(pulse), 255)
        for i in range(border_thickness):
            pygame.draw.rect(screen, border_color, (i, i, SCREEN_WIDTH-i*2, SCREEN_HEIGHT-i*2), 1)
        
        corner_size = 50
        for corner in [(0,0), (SCREEN_WIDTH-corner_size, 0), (0, SCREEN_HEIGHT-corner_size), (SCREEN_WIDTH-corner_size, SCREEN_HEIGHT-corner_size)]:
            pygame.draw.rect(screen, border_color, (corner[0], corner[1], corner_size, corner_size), 5)
    
    elif scenario_type == "giving_up":
        if pygame.time.get_ticks() % 800 < 400:
            border_color = (255, 0, 0)
            for i in range(border_thickness):
                pygame.draw.rect(screen, border_color, (i, i, SCREEN_WIDTH-i*2, SCREEN_HEIGHT-i*2), 1)
            
            x_size = 40
            x_thickness = 6
            corners = [(20, 20), (SCREEN_WIDTH-60, 20), (20, SCREEN_HEIGHT-60), (SCREEN_WIDTH-60, SCREEN_HEIGHT-60)]
            for corner in corners:
                pygame.draw.line(screen, (255, 0, 0), corner, (corner[0]+x_size, corner[1]+x_size), x_thickness)
                pygame.draw.line(screen, (255, 0, 0), (corner[0]+x_size, corner[1]), (corner[0], corner[1]+x_size), x_thickness)
    
    elif scenario_type == "persistent":
        intensity = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 100 + 155
        border_color = (int(intensity), 0, 255)
        for i in range(border_thickness*2):  
            pygame.draw.rect(screen, border_color, (i, i, SCREEN_WIDTH-i*2, SCREEN_HEIGHT-i*2), 1)
        
        square_size = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 30) + 20
        corners = [(10, 10), (SCREEN_WIDTH-square_size-10, 10), (10, SCREEN_HEIGHT-square_size-10), (SCREEN_WIDTH-square_size-10, SCREEN_HEIGHT-square_size-10)]
        for corner in corners:
            pygame.draw.rect(screen, border_color, (corner[0], corner[1], square_size, square_size), 4)
    
    elif scenario_type == "side_effects":
        if pygame.time.get_ticks() % 200 < 100:
            flash_colors = [(255, 255, 0), (255, 100, 0), (255, 0, 100)]
            border_color = random.choice(flash_colors)
            for i in range(border_thickness//2):
                pygame.draw.rect(screen, border_color, (i*2, i*2, SCREEN_WIDTH-i*4, SCREEN_HEIGHT-i*4), 1)
    
    elif scenario_type == "normal":
        border_color = (0, 100, 0)
        pygame.draw.rect(screen, border_color, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 2)