import pygame
import sys
import random
from constants import GRID_WIDTH, GRID_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
from agent import Agent
from rendering import draw_agent, draw_scenario_indicator

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

def run_audio_simulation():
    
    environment = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    obstacles = set()
    while len(obstacles) < 70:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos != (0, 0):
            obstacles.add(pos)
            environment[pos[1]][pos[0]] = 1

    boxes, holes = [], []

    def spawn_box_hole():
        from constants import all_possible_colors
        active_colors = {color for _, color in boxes + holes}
        available_colors = [c for c in all_possible_colors if c not in active_colors]
        if not available_colors:
            return

        spawn_count = min(2, len(available_colors))
        for _ in range(spawn_count):
            color = available_colors.pop(0)

            for container, others in [(boxes, holes), (holes, boxes)]:
                attempts = 0
                while attempts < 50:
                    pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                    if (environment[pos[1]][pos[0]] == 0 and
                            pos not in [b[0] for b in boxes] and
                            pos not in [h[0] for h in holes] and
                            pos != (0, 0)):
                        container.append((pos, color))
                        break
                    attempts += 1

    spawn_box_hole()

    agent = Agent((0, 0), environment)
    
    scenario_timer = 0
    current_scenario = "normal"
    scenario_duration = 35000  
    
    scenarios = [
        "normal",           
        "persistent",     
        "giving_up",        
        "side_effects"      
    ]
    scenario_index = 0

    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    scenario_index = (scenario_index + 1) % len(scenarios)
                    current_scenario = scenarios[scenario_index]
                    scenario_timer = current_time
                elif event.key == pygame.K_r:
                    if boxes:
                        box_color = random.choice([color for _, color in boxes])
                        agent.handle_user_request_behavior(box_color)
                        current_scenario = "user_request"
                elif event.key == pygame.K_c:
                    agent.cancel_user_request_behavior()
                    current_scenario = "giving_up"

        if current_time - scenario_timer > scenario_duration:
            scenario_index = (scenario_index + 1) % len(scenarios)
            current_scenario = scenarios[scenario_index]
            scenario_timer = current_time

        scenario_time = current_time - scenario_timer
        
        if current_scenario == "user_request":
            if scenario_time < 1000 and boxes and not agent.user_request_target:
                box_color = random.choice([color for _, color in boxes])
                agent.handle_user_request_behavior(box_color)
                
        elif current_scenario == "persistent":
            if agent.current_task and scenario_time > 3000:
                task_pos = agent.current_task.box_pos
                surrounding_positions = [
                    (task_pos[0] + dx, task_pos[1] + dy) 
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]
                    if (0 <= task_pos[0] + dx < GRID_WIDTH and 
                        0 <= task_pos[1] + dy < GRID_HEIGHT)
                ]
                for i, pos in enumerate(surrounding_positions):
                    if i < 6 and pos not in obstacles:
                        agent.belief_obstacles.add(pos)
                        
        elif current_scenario == "giving_up":
            if scenario_time < 500:
                agent.persistence_attempts = 12  
                agent.show_giving_up_through_behavior()
                
        elif current_scenario == "side_effects":
            if scenario_time % 2500 < 100: 
                agent.show_side_effect_reaction()
                if agent.pos[0] > 0:
                    agent.belief_obstacles.add((agent.pos[0]-1, agent.pos[1]))

        if current_time % 30000 < 100: 
            old_box_count = len(boxes)
            spawn_box_hole()
            if len(boxes) > old_box_count:
                agent.bouncing_excitedly = True
                agent.hesitation_timer = 20  

        agent.update_intelligence(boxes, holes)
        agent.execute_movement()
        agent.handle_pickup(boxes)
        agent.handle_drop(holes)

        draw_agent(agent, boxes, holes, obstacles, screen)
        
        draw_scenario_indicator(screen, current_scenario)
        
        clock.tick(12) 

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Intention agent")
    run_audio_simulation()