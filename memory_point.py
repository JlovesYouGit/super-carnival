import asyncio
import json
import os
from typing import Dict, List, Optional
import time

class MemoryPoint:
    def __init__(self, point_id: str):
        self.point_id = point_id
        self.state_data: Dict = {}
        self.weight_states: Dict[str, Dict] = {}
        self.pattern_states: Dict[str, Dict] = {}
        self.created_at = time.time()
        self.saved_at = None
        
    def to_dict(self) -> Dict:
        return {
            'point_id': self.point_id,
            'state_data': self.state_data,
            'weight_states': self.weight_states,
            'pattern_states': self.pattern_states,
            'created_at': self.created_at,
            'saved_at': self.saved_at
        }

class MemoryPointSystem:
    def __init__(self, storage_file: str = "memory_points.json"):
        self.storage_file = storage_file
        self.memory_points: Dict[str, MemoryPoint] = {}
        self.active_point: Optional[str] = None
        self.load_memory_points()
        
    def load_memory_points(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    for point_id, point_data in data.get('memory_points', {}).items():
                        point = MemoryPoint(point_id)
                        point.state_data = point_data.get('state_data', {})
                        point.weight_states = point_data.get('weight_states', {})
                        point.pattern_states = point_data.get('pattern_states', {})
                        point.created_at = point_data.get('created_at', time.time())
                        point.saved_at = point_data.get('saved_at')
                        self.memory_points[point_id] = point
            except Exception as e:
                print(f"Load memory points error: {e}")
    
    def save_memory_points(self):
        try:
            data = {
                'memory_points': {pid: p.to_dict() for pid, p in self.memory_points.items()},
                'active_point': self.active_point,
                'saved_at': time.time()
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Save memory points error: {e}")
    
    async def create_memory_point(self, point_id: str) -> MemoryPoint:
        point = MemoryPoint(point_id)
        self.memory_points[point_id] = point
        self.active_point = point_id
        self.save_memory_points()
        return point
    
    async def save_state_at_point(self, point_id: str, state_data: Dict):
        if point_id in self.memory_points:
            self.memory_points[point_id].state_data = state_data.copy()
            self.memory_points[point_id].saved_at = time.time()
            self.save_memory_points()
    
    async def save_weight_state(self, point_id: str, weight_id: str, weight_data: Dict):
        if point_id in self.memory_points:
            self.memory_points[point_id].weight_states[weight_id] = weight_data.copy()
            self.memory_points[point_id].saved_at = time.time()
            self.save_memory_points()
    
    async def save_pattern_state(self, point_id: str, pattern_id: str, pattern_data: Dict):
        if point_id in self.memory_points:
            self.memory_points[point_id].pattern_states[pattern_id] = pattern_data.copy()
            self.memory_points[point_id].saved_at = time.time()
            self.save_memory_points()
    
    async def load_from_point(self, point_id: str) -> Optional[Dict]:
        if point_id in self.memory_points:
            point = self.memory_points[point_id]
            self.active_point = point_id
            return {
                'point_id': point_id,
                'state_data': point.state_data,
                'weight_states': point.weight_states,
                'pattern_states': point.pattern_states
            }
        return None
    
    async def continue_cycle_at_point(self, point_id: str) -> bool:
        if point_id in self.memory_points:
            self.active_point = point_id
            return True
        return False
    
    def get_memory_point(self, point_id: str) -> Optional[MemoryPoint]:
        return self.memory_points.get(point_id)
    
    def get_active_point(self) -> Optional[str]:
        return self.active_point
