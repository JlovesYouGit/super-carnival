import asyncio
from typing import Dict, List, Optional, Tuple
import time
import numpy as np

class LearnedMetric:
    def __init__(self, metric_id: str):
        self.metric_id = metric_id
        self.learned_values: List[float] = []
        self.learned_patterns: Dict[str, float] = {}
        self.confidence: float = 0.0
        self.last_learned: Optional[float] = None
        self.off_case_learned: bool = False
        
    def add_learned_value(self, value: float):
        self.learned_values.append(value)
        self.last_learned = value
        
    def update_confidence(self, confidence: float):
        self.confidence = confidence

class DataMetricLearning:
    def __init__(self):
        self.learned_metrics: Dict[str, LearnedMetric] = {}
        self.learning_history: List[Dict] = []
        self.off_case_patterns: Dict[str, List[float]] = {}
        self.learning_rate: float = 0.1
        
    async def learn_from_metric(self, metric_id: str, value: float, is_off_case: bool = False) -> LearnedMetric:
        if metric_id not in self.learned_metrics:
            self.learned_metrics[metric_id] = LearnedMetric(metric_id)
        
        metric = self.learned_metrics[metric_id]
        metric.add_learned_value(value)
        
        if is_off_case:
            metric.off_case_learned = True
            if metric_id not in self.off_case_patterns:
                self.off_case_patterns[metric_id] = []
            self.off_case_patterns[metric_id].append(value)
        
        # Update confidence based on learning
        if len(metric.learned_values) > 1:
            variance = np.var(metric.learned_values)
            metric.update_confidence(1.0 / (1.0 + variance))
        
        self.learning_history.append({
            'metric_id': metric_id,
            'value': value,
            'is_off_case': is_off_case,
            'confidence': metric.confidence,
            'learned_at': time.time()
        })
        
        return metric
    
    async def predict_from_learning(self, metric_id: str) -> Optional[float]:
        if metric_id not in self.learned_metrics:
            return None
            
        metric = self.learned_metrics[metric_id]
        if not metric.learned_values:
            return None
            
        # Simple prediction: average of learned values
        return sum(metric.learned_values) / len(metric.learned_values)
    
    async def get_off_case_pattern(self, metric_id: str) -> Optional[List[float]]:
        return self.off_case_patterns.get(metric_id)
    
    async def check_off_case_learned(self, metric_id: str) -> bool:
        if metric_id in self.learned_metrics:
            return self.learned_metrics[metric_id].off_case_learned
        return False
    
    async def apply_learning_to_state(self, metric_id: str, current_state: int) -> Tuple[int, float]:
        if metric_id not in self.learned_metrics:
            return current_state, 0.0
            
        metric = self.learned_metrics[metric_id]
        predicted = await self.predict_from_learning(metric_id)
        
        if predicted is None:
            return current_state, 0.0
        
        # Apply learning to state transition
        if predicted > 0.5:
            new_state = min(current_state + 1, 2)
        else:
            new_state = max(current_state - 1, 0)
        
        confidence = metric.confidence
        
        return new_state, confidence
    
    def set_learning_rate(self, rate: float):
        self.learning_rate = rate
        
    def get_learned_metric(self, metric_id: str) -> Optional[LearnedMetric]:
        return self.learned_metrics.get(metric_id)
