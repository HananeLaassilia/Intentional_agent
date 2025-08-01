from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Set
from enum import Enum
import time
import heapq

class TaskState(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentMode(Enum):
    EXPLORING = "exploring"
    PATHFINDING = "pathfinding"
    COLLECTING = "collecting"
    DELIVERING = "delivering"
    IDLE = "idle"

@dataclass
class Task:
    priority: float
    box_pos: Tuple[int, int]
    box_color: str
    hole_pos: Tuple[int, int]
    estimated_steps: int
    state: TaskState = TaskState.PENDING
    created_time: float = field(default_factory=time.time)
    attempts: int = 0
    
    def __lt__(self, other):
        return self.priority < other.priority

@dataclass
class PerformanceMetrics:
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_steps_taken: int = 0
    total_distance_traveled: float = 0.0
    efficiency_score: int = 0
    consecutive_successes: int = 0
    average_task_completion_time: float = 0.0
    pathfinding_cache_hits: int = 0
    pathfinding_cache_misses: int = 0
    
    @property
    def success_rate(self) -> float:
        total = self.tasks_completed + self.tasks_failed
        return (self.tasks_completed / total * 100) if total > 0 else 0.0
    
    @property
    def steps_per_task(self) -> float:
        return (self.total_steps_taken / self.tasks_completed) if self.tasks_completed > 0 else 0.0

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: Dict = {}
        self.access_order: List = []
    
    def get(self, key) -> Optional[List]:
        if key in self.cache:
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key, value: List):
        if key in self.cache:
            self.access_order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        
        self.cache[key] = value
        self.access_order.append(key)
    
    def clear(self):
        self.cache.clear()
        self.access_order.clear()

@dataclass
class GameState:
    boxes: List[Tuple[Tuple[int, int], str]] = field(default_factory=list)
    holes: List[Tuple[Tuple[int, int], str]] = field(default_factory=list)
    obstacles: Set[Tuple[int, int]] = field(default_factory=set)
    agent_pos: Tuple[int, int] = (0, 0)
    agent_carrying: Optional[str] = None
    
    def get_free_positions(self, grid_width: int, grid_height: int) -> Set[Tuple[int, int]]:
        occupied = self.obstacles.copy()
        occupied.update(pos for pos, _ in self.boxes)
        occupied.update(pos for pos, _ in self.holes)
        occupied.add(self.agent_pos)
        
        return {(x, y) for x in range(grid_width) for y in range(grid_height) 
                if (x, y) not in occupied}

def calculate_path_efficiency(path: List[Tuple[int, int]], start: Tuple[int, int], goal: Tuple[int, int]) -> float:
    if not path:
        return 0.0
    
    manhattan_dist = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    actual_dist = len(path) - 1  
    
    return (manhattan_dist / actual_dist) if actual_dist > 0 else 1.0

def heuristic_with_obstacles(pos: Tuple[int, int], goal: Tuple[int, int], obstacles: Set[Tuple[int, int]]) -> float:
    base_distance = abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    penalty = 0
    if base_distance > 0:
        dx = 1 if goal[0] > pos[0] else -1 if goal[0] < pos[0] else 0
        dy = 1 if goal[1] > pos[1] else -1 if goal[1] < pos[1] else 0
        
        check_x, check_y = pos[0] + dx, pos[1] + dy
        steps_checked = 0
        while (check_x != goal[0] or check_y != goal[1]) and steps_checked < 3:
            if (check_x, check_y) in obstacles:
                penalty += 2
            check_x += dx if check_x != goal[0] else 0
            check_y += dy if check_y != goal[1] else 0
            steps_checked += 1
    
    return base_distance + penalty