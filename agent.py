import heapq
import pygame
from collections import deque
from constants import GRID_WIDTH, GRID_HEIGHT
from utils import Task

class IntelligentAgent:
    def __init__(self, start_pos, environment):
        self.pos = start_pos
        self.carrying = None
        self.path = []
        self.visited_positions = set()
        self.failed_attempts = {}
        self.task_queue = []
        self.current_task = None
        self.thought = "Initializing..."
        self.efficiency_score = 0
        self.tasks_completed = 0
        self.true_env = environment  
        self.belief_obstacles = set()  

    def sense(self):
        x, y = self.pos
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if self.true_env[ny][nx] == 1:
                    self.belief_obstacles.add((nx, ny))
                elif (nx, ny) in self.belief_obstacles:
                    self.belief_obstacles.remove((nx, ny))

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
        self.task_queue.clear()
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
        self.sense()

        if not self.carrying and not self.current_task:
            self.evaluate_tasks(boxes, holes)
            self.current_task = self.select_next_task()
            if self.current_task:
                self.thought = f"Target: {self.current_task.box_color} box"
                self.path = self.a_star_pathfind(self.pos, self.current_task.box_pos, self.belief_obstacles)
            else:
                self.thought = "Analyzing..."
        elif self.carrying and not self.path:
            targets = [h for h in holes if h[1] == self.carrying]
            if targets:
                target = min(targets, key=lambda h: self.manhattan_distance(self.pos, h[0]))
                self.path = self.a_star_pathfind(self.pos, target[0], self.belief_obstacles)
                self.thought = f"Delivering {self.carrying}"
        elif not self.path and self.current_task:
            self.thought = "Recalculating..."
            if not self.carrying:
                self.path = self.a_star_pathfind(self.pos, self.current_task.box_pos, self.belief_obstacles)

    def execute_movement(self):
        if self.path:
            next_pos = self.path[0]
            if self.true_env[next_pos[1]][next_pos[0]] == 1:
                self.belief_obstacles.add(next_pos)
                self.path = []
                self.thought = "Obstacle! Updating belief and replanning..."
                return False
            self.pos = self.path.pop(0)
            return True
        return False

    def handle_pickup(self, boxes):
        if self.current_task and self.pos == self.current_task.box_pos:
            for i, (b_pos, b_color) in enumerate(boxes):
                if b_pos == self.current_task.box_pos and b_color == self.current_task.box_color:
                    self.carrying = b_color
                    boxes.pop(i)
                    self.thought = f"Picked up {b_color}"
                    self.efficiency_score += 10
                    return True
        return False

    def handle_drop(self, holes):
        if self.carrying:
            for i, (h_pos, h_color) in enumerate(holes):
                if self.pos == h_pos and h_color == self.carrying:
                    holes.pop(i)
                    self.carrying = None
                    self.current_task = None
                    self.thought = "Dropped off"
                    self.efficiency_score += 20
                    self.tasks_completed += 1
                    return True
        return False
