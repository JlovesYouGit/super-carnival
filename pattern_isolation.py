import asyncio
from typing import Dict, List, Optional, Set
import time
import random

class PatternGraph:
    def __init__(self):
        self.patterns: Dict[str, Dict] = {}
        self.connections: Dict[str, Set[str]] = {}
        self.intent_patterns: Dict[str, List] = {}
        
    def add_pattern(self, pattern_id: str, pattern_data: Dict):
        self.patterns[pattern_id] = {
            'id': pattern_id,
            'data': pattern_data,
            'created_at': time.time(),
            'isolated': False
        }
        
    def add_connection(self, from_pattern: str, to_pattern: str):
        if from_pattern not in self.connections:
            self.connections[from_pattern] = set()
        self.connections[from_pattern].add(to_pattern)
        
    def add_intent_pattern(self, intent: str, pattern_ids: List[str]):
        self.intent_patterns[intent] = pattern_ids
        
    def get_patterns_by_intent(self, intent: str) -> List[str]:
        return self.intent_patterns.get(intent, [])

class PatternIsolation:
    def __init__(self):
        self.pattern_graph = PatternGraph()
        self.isolated_patterns: Dict[str, Dict] = {}
        self.value_influences: Dict[str, float] = {}
        self.deterministic_intervals: Dict[str, float] = {}
        self.max_duration: float = 100.0
        
    async def selective_isolation(self, intent: str, time_frame: float) -> List[str]:
        pattern_ids = self.pattern_graph.get_patterns_by_intent(intent)
        isolated = []
        
        for pattern_id in pattern_ids:
            if await self.should_isolate(pattern_id, time_frame):
                await self.isolate_pattern(pattern_id)
                isolated.append(pattern_id)
                
        return isolated
    
    async def should_isolate(self, pattern_id: str, time_frame: float) -> bool:
        if pattern_id not in self.pattern_graph.patterns:
            return False
            
        influence = self.value_influences.get(pattern_id, 0.0)
        interval = self.deterministic_intervals.get(pattern_id, 1.0)
        
        if influence > 0.5 and time_frame < self.max_duration:
            return True
            
        return False
    
    async def isolate_pattern(self, pattern_id: str):
        if pattern_id in self.pattern_graph.patterns:
            pattern = self.pattern_graph.patterns[pattern_id]
            pattern['isolated'] = True
            pattern['isolated_at'] = time.time()
            self.isolated_patterns[pattern_id] = pattern.copy()
            
    async def detect_value_influence(self, pattern_id: str, value: float) -> float:
        influence = abs(value) / (abs(value) + 1.0)
        self.value_influences[pattern_id] = influence
        return influence
    
    async def set_deterministic_interval(self, pattern_id: str, interval: float):
        self.deterministic_intervals[pattern_id] = interval
        
    def get_isolated_patterns(self) -> Dict[str, Dict]:
        return self.isolated_patterns
