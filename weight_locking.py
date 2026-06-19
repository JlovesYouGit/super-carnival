import asyncio
import numpy as np
from typing import Dict, List, Optional
import time
import json

class ModelWeightClass:
    def __init__(self, class_id: str, query_space: str):
        self.class_id = class_id
        self.query_space = query_space
        self.weights: Dict[str, float] = {}
        self.locked: bool = False
        self.locked_at: Optional[float] = None
        self.experiences: List[Dict] = []
        
    def to_dict(self) -> Dict:
        return {
            'class_id': self.class_id,
            'query_space': self.query_space,
            'weights': self.weights,
            'locked': self.locked,
            'locked_at': self.locked_at,
            'experience_count': len(self.experiences)
        }

class ModelWeightLocking:
    def __init__(self):
        self.weight_classes: Dict[str, ModelWeightClass] = {}
        self.lock_protocol_threshold: float = 50.0
        
    async def create_weight_class(self, class_id: str, query_space: str) -> ModelWeightClass:
        weight_class = ModelWeightClass(class_id, query_space)
        self.weight_classes[class_id] = weight_class
        return weight_class
    
    async def set_weights(self, class_id: str, weights: Dict[str, float]):
        if class_id in self.weight_classes:
            self.weight_classes[class_id].weights = weights.copy()
            
    async def lock_weights(self, class_id: str):
        if class_id in self.weight_classes:
            self.weight_classes[class_id].locked = True
            self.weight_classes[class_id].locked_at = time.time()
            
    async def unlock_weights(self, class_id: str):
        if class_id in self.weight_classes:
            self.weight_classes[class_id].locked = False
            self.weight_classes[class_id].locked_at = None
            
    async def add_experience(self, class_id: str, experience: Dict):
        if class_id in self.weight_classes:
            self.weight_classes[class_id].experiences.append({
                'experience': experience,
                'timestamp': time.time()
            })
            
    async def check_overlap(self, class_id: str, other_class_id: str) -> float:
        if class_id not in self.weight_classes or other_class_id not in self.weight_classes:
            return 0.0
            
        weights1 = self.weight_classes[class_id].weights
        weights2 = self.weight_classes[other_class_id].weights
        
        overlap = 0.0
        common_keys = set(weights1.keys()) & set(weights2.keys())
        
        for key in common_keys:
            overlap += abs(weights1[key] - weights2[key])
            
        return overlap / len(common_keys) if common_keys else 0.0
    
    async def apply_fix_protocol(self, class_id: str, protocol_value: float = 50.0):
        if class_id in self.weight_classes:
            if protocol_value >= self.lock_protocol_threshold:
                await self.lock_weights(class_id)
                return True
        return False
    
    def get_weight_class(self, class_id: str) -> Optional[ModelWeightClass]:
        return self.weight_classes.get(class_id)
    
    def is_locked(self, class_id: str) -> bool:
        if class_id in self.weight_classes:
            return self.weight_classes[class_id].locked
        return False
