import heapq
import pygame
import math
import os
import random
from collections import deque
from constants import GRID_WIDTH, GRID_HEIGHT
from utils import Task

class Agent:
    def __init__(self, start_pos, environment):
        self.pos = start_pos
        self.carrying = None
        self.path = []
        self.visited_positions = set()
        self.failed_attempts = {}
        self.task_queue = []
        self.current_task = None
        self.efficiency_score = 0
        self.tasks_completed = 0
        self.true_env = environment  
        self.belief_obstacles = set()
        
        self.commitment_intensity = 0
        self.frustration_level = 0
        self.persistence_attempts = 0
        self.celebration_timer = 0
        self.hesitation_timer = 0
        self.user_request_target = None
        self.giving_up_animation = 0
        self.side_effect_reaction = 0
        
        self.sound_timer = 0
        self.last_sound_type = ""
        
        # Clean movement behavior modifiers
        self.movement_speed = 1
        self.growing_with_determination = False
        self.bouncing_excitedly = False
        self.dramatic_pause = False
        
        # Size and visual modifiers - NO SHAKING OR CHAOS
        self.agent_size_multiplier = 1.0
        self.bounce_offset = 0
        self.trail_positions = []
        
        # Initialize pygame mixer and load audio files
        self.sounds = {}
        self.sound_enabled = False
        self.current_boxes = []
        self.load_audio_files()

    def load_audio_files(self):
        try:
            pygame.mixer.init()
            
            sound_files = {
                'frustration': 'sounds/frustration.wav',
                'celebration': 'sounds/celebration.wav',
            }
            
            loaded_count = 0
            for sound_name, file_path in sound_files.items():
                if os.path.exists(file_path):
                    try:
                        self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                        print(f"✓ Loaded {sound_name}")
                        loaded_count += 1
                    except Exception as e:
                        print(f"✗ Failed to load {file_path}: {e}")
                        self.sounds[sound_name] = None
                else:
                    self.sounds[sound_name] = None
            
            self.sound_enabled = True
            
        except Exception as e:
            self.sound_enabled = False

    def play_sound(self, sound_name, volume=0.7):
        if not self.sound_enabled or self.sound_timer > 0:
            return
        
        if sound_name in self.sounds and self.sounds[sound_name] is not None:
            try:
                sound = self.sounds[sound_name]
                sound.set_volume(volume)
                sound.play()
                self.sound_timer = 15  # Prevent sound spam
            except Exception as e:
                print(f"Failed to play {sound_name}: {e}")
        else:
            print(f"{sound_name} not available")


    def play_frustration_sound(self, level):
        volume = min(1.0, 0.4 + (level * 0.1))
        self.play_sound('frustration', volume)

    def play_celebration_sound(self):
        self.play_sound('celebration', 1.0)  # Full volume!

    
    def show_commitment_through_behavior(self, intensity):
        self.commitment_intensity = min(10, intensity)
        
        if self.commitment_intensity > 7:
            # hign commitment: Agent grows larger and moves faster
            self.agent_size_multiplier = 1.5
            self.movement_speed = 2
            self.growing_with_determination = True
            self.bouncing_excitedly = True
            if len(self.trail_positions) > 8:
                self.trail_positions = self.trail_positions[-8:]
        elif self.commitment_intensity > 4:
            # medium commitment: Slightly larger, normal speed
            self.agent_size_multiplier = 1.2
            self.movement_speed = 1
            self.growing_with_determination = True
            self.bouncing_excitedly = False
        else:
            # low commitment: Smaller, slower
            self.agent_size_multiplier = 0.8
            self.movement_speed = 1
            self.growing_with_determination = False
            self.bouncing_excitedly = False

    def show_persistence_through_behavior(self):
        self.persistence_attempts += 1
        self.frustration_level = min(10, self.persistence_attempts)
        self.show_commitment_through_behavior(self.persistence_attempts + 5)

    def show_obstacle_frustration(self):
        self.play_frustration_sound(self.frustration_level + 3)

    def show_giving_up_through_behavior(self):
        self.giving_up_animation = 120
        self.agent_size_multiplier = 0.3
        self.current_task = None
        self.path = []
        self.commitment_intensity = 0
        self.persistence_attempts = 0
        self.frustration_level = 0

    def show_success_celebration(self):
        self.play_celebration_sound()
        
        self.celebration_timer = 30
        self.agent_size_multiplier = 2.0
        self.bouncing_excitedly = True
        self.commitment_intensity = 0
        self.persistence_attempts = 0
        self.frustration_level = 0

    def show_side_effect_reaction(self):
        self.side_effect_reaction = 30  
        self.dramatic_pause = True

    def handle_user_request_behavior(self, target_box_color):
        for box_pos, box_color in self.current_boxes:
            if box_color == target_box_color:
                self.user_request_target = box_pos
                self.agent_size_multiplier = 1.8
                self.bouncing_excitedly = True
                self.show_commitment_through_behavior(10)
                self.path = []
                self.current_task = None
                self.dramatic_pause = True
                self.hesitation_timer = 20  # Brief pause
                break

    def cancel_user_request_behavior(self):
        if self.user_request_target:
            self.user_request_target = None
            self.show_giving_up_through_behavior()

    def update_visual_effects(self):
        if self.bouncing_excitedly:
            bounce_intensity = 8
            self.bounce_offset = math.sin(pygame.time.get_ticks() * 0.02) * bounce_intensity
        else:
            self.bounce_offset = 0
        
        if len(self.trail_positions) > 0:
            self.trail_positions = self.trail_positions[-10:]

    def sense(self):
        x, y = self.pos
        obstacle_found = False
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if self.true_env[ny][nx] == 1:
                    if (nx, ny) not in self.belief_obstacles:
                        obstacle_found = True
                    self.belief_obstacles.add((nx, ny))
                elif (nx, ny) in self.belief_obstacles:
                    self.belief_obstacles.remove((nx, ny))
        return obstacle_found

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def a_star_pathfind(self, start, goal, obstacles):
        if start == goal:
            return [start]
        path_key = (start, goal)
        if path_key in self.failed_attempts and pygame.time.get_ticks() - self.failed_attempts[path_key] < 5000:
            return []

        heap = [(0, 0, start, [start])]
        visited = set()

        while heap:
            f_score, g_score, current, path = heapq.heappop(heap)
            if current in visited:
                continue
            visited.add(current)
            if current == goal:
                return path

            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = current[0]+dx, current[1]+dy
                neighbor = (nx, ny)
                if (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and
                        neighbor not in obstacles and neighbor not in visited):
                    new_g = g_score + 1
                    h = self.manhattan_distance(neighbor, goal)
                    heapq.heappush(heap, (new_g + h, new_g, neighbor, path + [neighbor]))

        self.failed_attempts[path_key] = pygame.time.get_ticks()
        return []

    def evaluate_tasks(self, boxes, holes):
        self.current_boxes = boxes
        self.task_queue.clear()
        
        if self.user_request_target:
            for box_pos, box_color in boxes:
                if box_pos == self.user_request_target:
                    for hole_pos, hole_color in holes:
                        if hole_color == box_color:
                            self.task_queue.append(Task(0, box_pos, box_color, hole_pos, 0))
                            return
        
        for box_pos, box_color in boxes:
            for hole_pos, hole_color in holes:
                if hole_color == box_color:
                    dist = self.manhattan_distance(self.pos, box_pos) + self.manhattan_distance(box_pos, hole_pos)
                    penalty = 50 if (self.pos, box_pos) in self.failed_attempts else 0
                    self.task_queue.append(Task(dist + penalty, box_pos, box_color, hole_pos, dist))
        self.task_queue.sort(key=lambda t: t.priority)

    def select_next_task(self):
        for i, task in enumerate(self.task_queue):
            if self.a_star_pathfind(self.pos,task.box_pos,self.belief_obstacles):
                return self.task_queue.pop(i)
        return None

    def update_intelligence(self, boxes, holes):
        self.visited_positions.add(self.pos)
        
        if self.sound_timer > 0:
            self.sound_timer -= 1
        
        self.update_visual_effects()
        
        if self.celebration_timer > 0:
            self.celebration_timer -= 1
            self.bouncing_excitedly = True
            return
            
        if self.giving_up_animation > 0:
            self.giving_up_animation -= 1
            shrink_progress = 1.0 - (self.giving_up_animation / 120.0)
            self.agent_size_multiplier = max(0.3, 1.0 - shrink_progress * 0.7)
            return
            
        if self.hesitation_timer > 0:
            self.hesitation_timer -= 1
            self.dramatic_pause = True
            return
            
        if self.side_effect_reaction > 0:
            self.side_effect_reaction -= 1
            return

        self.dramatic_pause = False

        if self.persistence_attempts > 8:
            self.show_giving_up_through_behavior()
            return
            
        if self.tasks_completed > 6:
            self.show_giving_up_through_behavior()
            return

        obstacle_discovered = self.sense()

        if not self.carrying and not self.current_task:
            self.evaluate_tasks(boxes, holes)
            self.current_task = self.select_next_task()
            if self.current_task:
                commitment_level = 10 if self.user_request_target else 6
                self.show_commitment_through_behavior(commitment_level)
                self.path = self.a_star_pathfind(self.pos, self.current_task.box_pos, self.belief_obstacles)
                self.trail_positions.append(self.pos)
            else:
                self.agent_size_multiplier = 0.7
                
        elif self.carrying and not self.path:
            targets = [h for h in holes if h[1] == self.carrying]
            if targets:
                target = min(targets, key=lambda h: self.manhattan_distance(self.pos, h[0]))
                self.path = self.a_star_pathfind(self.pos, target[0], self.belief_obstacles)
                self.show_commitment_through_behavior(self.commitment_intensity + 3)
                self.bouncing_excitedly = True
                
        elif not self.path and self.current_task:
            self.show_persistence_through_behavior()
            if not self.carrying:
                self.path = self.a_star_pathfind(self.pos, self.current_task.box_pos, self.belief_obstacles)

    def execute_movement(self):
        if self.dramatic_pause:
            return False
            
        if not self.path:
            return False

        if self.commitment_intensity > 7:
            self.trail_positions.append(self.pos)

        moves_this_frame = self.movement_speed
        moved = False
        
        for _ in range(moves_this_frame):
            if not self.path:
                break
                
            next_pos = self.path[0]
            
            if self.true_env[next_pos[1]][next_pos[0]] == 1:
                
                self.belief_obstacles.add(next_pos)
                self.path = [] 
                self.show_obstacle_frustration()  
                self.show_persistence_through_behavior()  
                self.show_side_effect_reaction()
                return False

            self.pos = self.path.pop(0)
            moved = True
            
        return moved

    def handle_pickup(self, boxes):
        if self.current_task and self.pos == self.current_task.box_pos:
            for i, (b_pos, b_color) in enumerate(boxes):
                if b_pos == self.current_task.box_pos and b_color == self.current_task.box_color:
                    self.carrying = b_color
                    boxes.pop(i)
                    self.efficiency_score += 10
                    self.side_effect_reaction = 10  
                    return True
        return False

    def handle_drop(self, holes):
        if self.carrying:
            for i, (h_pos, h_color) in enumerate(holes):
                if self.pos == h_pos and h_color == self.carrying:
                    holes.pop(i)
                    carried_color = self.carrying
                    self.carrying = None
                    self.current_task = None
                    self.user_request_target = None
                    self.show_success_celebration()  
                    self.efficiency_score += 20
                    self.tasks_completed += 1
                    return True
        return False