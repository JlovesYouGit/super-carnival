import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple
import time

class NeuralMatchDetector:
    def __init__(self):
        self.match_threshold: float = 0.95
        self.neural_patterns: Dict[str, np.ndarray] = {}
        self.match_history: List[Dict] = []
        
    def create_pattern_vector(self, data: List[float]) -> np.ndarray:
        return np.array(data, dtype=np.float32)
    
    async def add_pattern(self, pattern_id: str, data: List[float]):
        vector = self.create_pattern_vector(data)
        self.neural_patterns[pattern_id] = vector
        
    async def detect_match(self, pattern_id: str, target_data: List[float]) -> Tuple[bool, float]:
        if pattern_id not in self.neural_patterns:
            return False, 0.0
            
        pattern_vector = self.neural_patterns[pattern_id]
        target_vector = self.create_pattern_vector(target_data)
        
        similarity = self.calculate_similarity(pattern_vector, target_vector)
        is_match = similarity >= self.match_threshold
        
        match_record = {
            'pattern_id': pattern_id,
            'similarity': similarity,
            'is_match': is_match,
            'timestamp': time.time()
        }
        self.match_history.append(match_record)
        
        return is_match, similarity
    
    def calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        if len(vec1) != len(vec2):
            min_len = min(len(vec1), len(vec2))
            vec1 = vec1[:min_len]
            vec2 = vec2[:min_len]
            
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    async def indicate_exact(self, pattern_id: str, target_data: List[float]) -> bool:
        is_match, similarity = await self.detect_match(pattern_id, target_data)
        return is_match and similarity > 0.99
    
    def set_match_threshold(self, threshold: float):
        self.match_threshold = threshold
        
    def get_match_history(self) -> List[Dict]:
        return self.match_history
