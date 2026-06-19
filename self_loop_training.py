import asyncio
import numpy as np
from typing import Dict, List, Optional
import time
import random

class WeightOrderState:
    def __init__(self, state_id: str):
        self.state_id = state_id
        self.weights: Dict[str, float] = {}
        self.pressure_level: float = 0.0
        self.exposed_experience: float = 0.0
        self.entropy_effect: float = 0.0
        self.created_at = time.time()

class SelfLoopTraining:
    def __init__(self):
        self.weight_orders: Dict[str, List[str]] = {}
        self.states: Dict[str, WeightOrderState] = {}
        self.training_history: List[Dict] = []
        self.pressure_space_threshold: float = 0.8
        
    async def create_weight_order(self, order_id: str, weight_ids: List[str]):
        self.weight_orders[order_id] = weight_ids
        
    async def create_state(self, state_id: str, weights: Dict[str, float]) -> WeightOrderState:
        state = WeightOrderState(state_id)
        state.weights = weights.copy()
        self.states[state_id] = state
        return state
    
    async def apply_pressure_space(self, state_id: str, pressure: float):
        if state_id in self.states:
            self.states[state_id].pressure_level = pressure
            
    async def expose_experience(self, state_id: str, experience: float):
        if state_id in self.states:
            self.states[state_id].exposed_experience = experience
            
    async def apply_random_entropy(self, state_id: str):
        if state_id in self.states:
            entropy = random.uniform(0.0, 1.0)
            self.states[state_id].entropy_effect = entropy
            
    async def self_loop_cycle(self, order_id: str, state_id: str, cycles: int = 100) -> Dict:
        if order_id not in self.weight_orders or state_id not in self.states:
            return {'error': 'Order or state not found'}
            
        state = self.states[state_id]
        weight_ids = self.weight_orders[order_id]
        results = []
        
        for cycle in range(cycles):
            await self.apply_pressure_space(state_id, cycle / cycles)
            await self.expose_experience(state_id, random.uniform(0.5, 1.0))
            await self.apply_random_entropy(state_id)
            
            if state.pressure_level > self.pressure_space_threshold:
                await self._apply_pressure_effect(state, weight_ids)
                
            cycle_result = {
                'cycle': cycle,
                'pressure_level': state.pressure_level,
                'exposed_experience': state.exposed_experience,
                'entropy_effect': state.entropy_effect,
                'weights': state.weights.copy()
            }
            results.append(cycle_result)
            
            self.training_history.append({
                'order_id': order_id,
                'state_id': state_id,
                'cycle': cycle,
                'timestamp': time.time()
            })
            
        return {
            'order_id': order_id,
            'state_id': state_id,
            'total_cycles': cycles,
            'results': results
        }
    
    async def _apply_pressure_effect(self, state: WeightOrderState, weight_ids: List[str]):
        for weight_id in weight_ids:
            if weight_id in state.weights:
                pressure_factor = state.pressure_level * state.entropy_effect
                state.weights[weight_id] *= (1 + pressure_factor * 0.1)
    
    async def force_self_loop(self, order_id: str, state_id: str) -> Dict:
        state = self.states[state_id]
        state.pressure_level = 1.0
        state.exposed_experience = 1.0
        
        return await self.self_loop_cycle(order_id, state_id, cycles=50)
    
    def get_state(self, state_id: str) -> Optional[WeightOrderState]:
        return self.states.get(state_id)
    
    def get_training_history(self) -> List[Dict]:
        return self.training_history
