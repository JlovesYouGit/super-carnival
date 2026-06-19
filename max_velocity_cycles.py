import asyncio
from typing import Dict, List, Optional, Callable
import time

class VelocityCycle:
    def __init__(self, cycle_id: str):
        self.cycle_id = cycle_id
        self.velocity: float = 1.0
        self.max_velocity: float = 1000.0
        self.cycle_count: int = 0
        self.errors_ignored: int = 0
        self.is_running: bool = False
        self.cycle_task: Optional[asyncio.Task] = None
        
class MaxVelocityCycles:
    def __init__(self):
        self.cycles: Dict[str, VelocityCycle] = {}
        self.cycle_callbacks: Dict[str, List[Callable]] = {}
        self.is_running: bool = False
        
    async def create_cycle(self, cycle_id: str, max_velocity: float = 1000.0) -> VelocityCycle:
        cycle = VelocityCycle(cycle_id)
        cycle.max_velocity = max_velocity
        self.cycles[cycle_id] = cycle
        return cycle
    
    async def start_cycle(self, cycle_id: str, cycle_function: Callable):
        if cycle_id not in self.cycles:
            return
            
        cycle = self.cycles[cycle_id]
        cycle.is_running = True
        cycle.cycle_task = asyncio.create_task(self._run_cycle(cycle_id, cycle_function))
    
    async def _run_cycle(self, cycle_id: str, cycle_function: Callable):
        while cycle_id in self.cycles and self.cycles[cycle_id].is_running:
            cycle = self.cycles[cycle_id]
            
            try:
                # Execute cycle function at max velocity
                await cycle_function(cycle_id)
                cycle.cycle_count += 1
                
                # Calculate delay based on velocity (lower delay = higher velocity)
                delay = max(0.001, 1.0 / cycle.max_velocity)
                await asyncio.sleep(delay)
                
            except Exception as e:
                # Ignore errors as requested
                cycle.errors_ignored += 1
                continue
    
    async def stop_cycle(self, cycle_id: str):
        if cycle_id in self.cycles:
            self.cycles[cycle_id].is_running = False
            if self.cycles[cycle_id].cycle_task:
                self.cycles[cycle_id].cycle_task.cancel()
    
    async def set_velocity(self, cycle_id: str, velocity: float):
        if cycle_id in self.cycles:
            self.cycles[cycle_id].velocity = min(velocity, self.cycles[cycle_id].max_velocity)
    
    async def get_cycle_stats(self, cycle_id: str) -> Optional[Dict]:
        if cycle_id in self.cycles:
            cycle = self.cycles[cycle_id]
            return {
                'cycle_id': cycle_id,
                'velocity': cycle.velocity,
                'max_velocity': cycle.max_velocity,
                'cycle_count': cycle.cycle_count,
                'errors_ignored': cycle.errors_ignored,
                'is_running': cycle.is_running
            }
        return None
    
    def get_cycle(self, cycle_id: str) -> Optional[VelocityCycle]:
        return self.cycles.get(cycle_id)
