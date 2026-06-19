import asyncio
from typing import Dict, List, Optional
import time

class SimulatedPatternIteration:
    def __init__(self):
        self.iterations: Dict[str, Dict] = {}
        self.influenced_cycles: Dict[str, List[float]] = {}
        self.cycle_count: int = 100
        
    async def create_iteration(self, iteration_id: str, pattern_data: Dict) -> Dict:
        iteration = {
            'iteration_id': iteration_id,
            'pattern_data': pattern_data,
            'cycle_count': 0,
            'total_elapsed_time': 0.0,
            'created_at': time.time()
        }
        self.iterations[iteration_id] = iteration
        return iteration
    
    async def simulate_iteration(self, iteration_id: str, persona_categories: List[str]) -> Dict:
        if iteration_id not in self.iterations:
            return {'error': 'Iteration not found'}
            
        iteration = self.iterations[iteration_id]
        start_time = time.time()
        
        total_cycles = self.cycle_count * len(persona_categories)
        influenced_values = []
        
        for category in persona_categories:
            for cycle in range(self.cycle_count):
                influence = await self._calculate_influence(cycle, category)
                influenced_values.append(influence)
                
        elapsed_time = time.time() - start_time
        
        iteration['cycle_count'] = total_cycles
        iteration['total_elapsed_time'] = elapsed_time
        iteration['influenced_values'] = influenced_values
        self.influenced_cycles[iteration_id] = influenced_values
        
        return {
            'iteration_id': iteration_id,
            'total_cycles': total_cycles,
            'elapsed_time': elapsed_time,
            'influenced_values': influenced_values[:10],
            'timestamp': time.time()
        }
    
    async def _calculate_influence(self, cycle: int, category: str) -> float:
        import random
        base = 1.0 / (cycle + 1)
        category_factor = hash(category) % 100 / 100.0
        return base * (1 + category_factor) * random.uniform(0.8, 1.2)
    
    async def get_elapsed_time_sum(self, iteration_id: str) -> float:
        if iteration_id in self.iterations:
            return self.iterations[iteration_id]['total_elapsed_time']
        return 0.0
    
    def get_influenced_cycles(self, iteration_id: str) -> List[float]:
        return self.influenced_cycles.get(iteration_id, [])
