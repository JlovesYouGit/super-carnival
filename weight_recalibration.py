import asyncio
import numpy as np
from typing import Dict, List, Optional
import time
import json

class WeightRecalibrationCycle:
    def __init__(self, cycle_id: str):
        self.cycle_id = cycle_id
        self.original_weights: Dict[str, float] = {}
        self.recalibrated_weights: Dict[str, float] = {}
        self.calibration_factor: float = 1.0
        self.cycle_count: int = 0
        self.created_at = time.time()
        
    def to_dict(self) -> Dict:
        return {
            'cycle_id': self.cycle_id,
            'original_weights': self.original_weights,
            'recalibrated_weights': self.recalibrated_weights,
            'calibration_factor': self.calibration_factor,
            'cycle_count': self.cycle_count,
            'created_at': self.created_at
        }

class WeightRecalibration:
    def __init__(self):
        self.cycles: Dict[str, WeightRecalibrationCycle] = {}
        self.calibration_history: List[Dict] = []
        
    async def create_cycle(self, cycle_id: str, original_weights: Dict[str, float]) -> WeightRecalibrationCycle:
        cycle = WeightRecalibrationCycle(cycle_id)
        cycle.original_weights = original_weights.copy()
        self.cycles[cycle_id] = cycle
        return cycle
    
    async def recalibrate_weights(self, cycle_id: str, target_weights: Dict[str, float]) -> Dict:
        if cycle_id not in self.cycles:
            return {'error': 'Cycle not found'}
            
        cycle = self.cycles[cycle_id]
        recalibrated = {}
        
        for key, original_value in cycle.original_weights.items():
            if key in target_weights:
                target_value = target_weights[key]
                recalibrated[key] = original_value + (target_value - original_value) * cycle.calibration_factor
            else:
                recalibrated[key] = original_value
                
        cycle.recalibrated_weights = recalibrated
        cycle.cycle_count += 1
        
        return {
            'cycle_id': cycle_id,
            'recalibrated_weights': recalibrated,
            'cycle_count': cycle.cycle_count
        }
    
    async def calibrate_cycle(self, cycle_id: str, calibration_factor: float):
        if cycle_id in self.cycles:
            self.cycles[cycle_id].calibration_factor = calibration_factor
            
    async def run_calibration_cycle(self, cycle_id: str, iterations: int = 10) -> Dict:
        results = []
        
        for i in range(iterations):
            calibration_factor = 1.0 - (i / iterations) * 0.5
            await self.calibrate_cycle(cycle_id, calibration_factor)
            
            result = await self.recalibrate_weights(cycle_id, self.cycles[cycle_id].original_weights)
            results.append(result)
            
            self.calibration_history.append({
                'cycle_id': cycle_id,
                'iteration': i,
                'calibration_factor': calibration_factor,
                'timestamp': time.time()
            })
            
        return {
            'cycle_id': cycle_id,
            'total_iterations': iterations,
            'results': results
        }
    
    async def replicate_original_pattern(self, cycle_id: str) -> bool:
        if cycle_id not in self.cycles:
            return False
            
        cycle = self.cycles[cycle_id]
        cycle.recalibrated_weights = cycle.original_weights.copy()
        return True
    
    def get_cycle(self, cycle_id: str) -> Optional[WeightRecalibrationCycle]:
        return self.cycles.get(cycle_id)
    
    def get_calibration_history(self) -> List[Dict]:
        return self.calibration_history
