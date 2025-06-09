from dataclasses import dataclass
from typing import Tuple

@dataclass
class Task:
    priority: float
    box_pos: Tuple[int, int]
    box_color: str
    hole_pos: Tuple[int, int]
    estimated_steps: int
