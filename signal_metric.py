import asyncio
from typing import Dict, List, Optional, Tuple
import time
import numpy as np

class SignalMetric:
    def __init__(self, signal_id: str):
        self.signal_id = signal_id
        self.metric_values: List[float] = []
        self.negative_count: int = 0
        self.positive_count: int = 0
        self.current_state: int = 0
        self.measured_at: Optional[float] = None
        
    def add_metric(self, value: float):
        self.metric_values.append(value)
        if value < 0:
            self.negative_count += 1
        else:
            self.positive_count += 1

class SignalMetricSystem:
    def __init__(self):
        self.signals: Dict[str, SignalMetric] = {}
        self.metric_history: List[Dict] = []
        self.threshold: float = 0.0
        
    async def measure_signal(self, signal_id: str, metric_value: float) -> SignalMetric:
        if signal_id not in self.signals:
            self.signals[signal_id] = SignalMetric(signal_id)
            
        signal = self.signals[signal_id]
        signal.add_metric(metric_value)
        signal.measured_at = time.time()
        
        self.metric_history.append({
            'signal_id': signal_id,
            'metric_value': metric_value,
            'negative_count': signal.negative_count,
            'positive_count': signal.positive_count,
            'measured_at': time.time()
        })
        
        return signal
    
    async def get_signal_metrics(self, signal_id: str) -> Optional[Dict]:
        if signal_id not in self.signals:
            return None
            
        signal = self.signals[signal_id]
        return {
            'signal_id': signal_id,
            'metric_count': len(signal.metric_values),
            'negative_count': signal.negative_count,
            'positive_count': signal.positive_count,
            'current_state': signal.current_state,
            'last_measured': signal.measured_at
        }
    
    async def check_negative_stays(self, signal_id: str) -> bool:
        if signal_id not in self.signals:
            return False
            
        signal = self.signals[signal_id]
        return signal.negative_count > signal.positive_count
    
    def set_threshold(self, threshold: float):
        self.threshold = threshold
        
    def get_signal(self, signal_id: str) -> Optional[SignalMetric]:
        return self.signals.get(signal_id)
