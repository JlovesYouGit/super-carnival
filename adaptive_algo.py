import asyncio
from typing import Dict, List, Optional, Tuple
import time
import numpy as np

class PatternFlow:
    def __init__(self, flow_id: str):
        self.flow_id = flow_id
        self.pattern_sequence: List[Dict] = []
        self.flow_velocity: float = 1.0
        self.adaptation_rate: float = 0.1
        self.detected_at: Optional[float] = None

class AdaptiveAlgo:
    def __init__(self):
        self.pattern_flows: Dict[str, PatternFlow] = {}
        self.adaptation_history: List[Dict] = []
        self.codebase_patterns: Dict[str, List[float]] = {}
        
    async def detect_pattern_flow(self, flow_id: str, pattern_data: List[float]) -> PatternFlow:
        flow = PatternFlow(flow_id)
        flow.pattern_sequence = [{'value': val, 'timestamp': time.time()} for val in pattern_data]
        flow.detected_at = time.time()
        flow.flow_velocity = self._calculate_velocity(pattern_data)
        
        self.pattern_flows[flow_id] = flow
        
        self.adaptation_history.append({
            'flow_id': flow_id,
            'pattern_length': len(pattern_data),
            'velocity': flow.flow_velocity,
            'detected_at': time.time()
        })
        
        return flow
    
    def _calculate_velocity(self, pattern_data: List[float]) -> float:
        if len(pattern_data) < 2:
            return 1.0
            
        # Calculate rate of change
        changes = []
        for i in range(1, len(pattern_data)):
            change = abs(pattern_data[i] - pattern_data[i-1])
            changes.append(change)
            
        avg_change = sum(changes) / len(changes) if changes else 0.0
        velocity = 1.0 / (1.0 + avg_change)
        
        return velocity
    
    async def adapt_to_codebase(self, flow_id: str, codebase_id: str) -> Tuple[bool, float]:
        if flow_id not in self.pattern_flows or codebase_id not in self.codebase_patterns:
            return False, 0.0
            
        flow = self.pattern_flows[flow_id]
        codebase_pattern = self.codebase_patterns[codebase_id]
        
        # Calculate adaptation match
        flow_pattern = [p['value'] for p in flow.pattern_sequence]
        match_score = self._calculate_pattern_match(flow_pattern, codebase_pattern)
        
        # Adapt flow velocity based on match
        if match_score > 0.8:
            flow.adaptation_rate = 0.05  # Slow adaptation for high match
        else:
            flow.adaptation_rate = 0.2  # Fast adaptation for low match
        
        flow.flow_velocity *= (1 + flow.adaptation_rate * match_score)
        
        return match_score > 0.7, match_score
    
    def _calculate_pattern_match(self, pattern1: List[float], pattern2: List[float]) -> float:
        if not pattern1 or not pattern2:
            return 0.0
            
        # Normalize patterns to same length
        min_len = min(len(pattern1), len(pattern2))
        p1 = pattern1[:min_len]
        p2 = pattern2[:min_len]
        
        # Calculate correlation
        if len(p1) == 0:
            return 0.0
            
        mean1 = sum(p1) / len(p1)
        mean2 = sum(p2) / len(p2)
        
        numerator = sum((x - mean1) * (y - mean2) for x, y in zip(p1, p2))
        denominator = (sum((x - mean1) ** 2 for x in p1) ** 0.5) * (sum((y - mean2) ** 2 for y in p2) ** 0.5)
        
        if denominator == 0:
            return 0.0
            
        correlation = numerator / denominator
        return (correlation + 1) / 2  # Normalize to 0-1
    
    async def register_codebase_pattern(self, codebase_id: str, pattern: List[float]):
        self.codebase_patterns[codebase_id] = pattern
        
    async def catch_same_pattern_flow(self, target_flow_id: str, source_pattern: List[float]) -> Optional[PatternFlow]:
        # Detect flow from source pattern
        detected_flow = await self.detect_pattern_flow(target_flow_id, source_pattern)
        
        # Try to match with existing codebase patterns
        best_match = None
        best_score = 0.0
        
        for codebase_id in self.codebase_patterns:
            is_match, score = await self.adapt_to_codebase(target_flow_id, codebase_id)
            if score > best_score:
                best_score = score
                best_match = codebase_id
        
        if best_match and best_score > 0.8:
            return detected_flow
            
        return None
    
    async def adaptive_learning(self, flow_id: str, new_pattern_data: List[float]):
        if flow_id not in self.pattern_flows:
            await self.detect_pattern_flow(flow_id, new_pattern_data)
        else:
            flow = self.pattern_flows[flow_id]
            flow.pattern_sequence.extend([{'value': val, 'timestamp': time.time()} for val in new_pattern_data])
            flow.flow_velocity = self._calculate_velocity([p['value'] for p in flow.pattern_sequence])
    
    def get_pattern_flow(self, flow_id: str) -> Optional[PatternFlow]:
        return self.pattern_flows.get(flow_id)
    
    def get_adaptation_history(self) -> List[Dict]:
        return self.adaptation_history.copy()
