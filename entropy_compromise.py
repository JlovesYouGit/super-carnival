import asyncio
from typing import Dict, List, Optional, Tuple
import time
import hashlib

class CompromisedState:
    def __init__(self, state_id: str):
        self.state_id = state_id
        self.is_compromised: bool = False
        self.entropy_value: float = 0.0
        self.code_changed: bool = False
        self.influence_moved: bool = False
        self.block_structure_moved: bool = False
        self.things_applied: bool = False
        self.detected_at: Optional[float] = None

class EntropyCompromise:
    def __init__(self):
        self.compromised_states: Dict[str, CompromisedState] = {}
        self.compromise_history: List[Dict] = []
        self.entropy_threshold: float = 0.8
        
    async def detect_compromise(self, state_id: str, current_entropy: float, original_entropy: float) -> CompromisedState:
        state = CompromisedState(state_id)
        
        # Check if entire state is compromised
        entropy_change = abs(current_entropy - original_entropy)
        
        if entropy_change > self.entropy_threshold:
            state.is_compromised = True
            state.entropy_value = current_entropy
            state.detected_at = time.time()
            
            # When compromised, entropy value changes it from code
            state.code_changed = True
            
            # Influence of that value has moved entire block structure
            state.influence_moved = True
            state.block_structure_moved = True
            
            # Indicates things have been applied
            state.things_applied = True
        
        self.compromised_states[state_id] = state
        
        self.compromise_history.append({
            'state_id': state_id,
            'is_compromised': state.is_compromised,
            'entropy_change': entropy_change,
            'detected_at': time.time()
        })
        
        return state
    
    async def check_value_holds(self, state_id: str) -> bool:
        if state_id in self.compromised_states:
            return self.compromised_states[state_id].is_compromised
        return False
    
    async def update_constant_state(self, state_id: str, is_altered: bool):
        if state_id in self.compromised_states:
            # If value holds and updates, constant is not defined as none moving but altered value states
            self.compromised_states[state_id].is_compromised = is_altered
    
    async def get_compromise_status(self, state_id: str) -> Optional[Dict]:
        if state_id in self.compromised_states:
            state = self.compromised_states[state_id]
            return {
                'state_id': state_id,
                'is_compromised': state.is_compromised,
                'entropy_value': state.entropy_value,
                'code_changed': state.code_changed,
                'influence_moved': state.influence_moved,
                'block_structure_moved': state.block_structure_moved,
                'things_applied': state.things_applied,
                'detected_at': state.detected_at
            }
        return None
    
    def set_entropy_threshold(self, threshold: float):
        self.entropy_threshold = threshold
        
    def get_compromised_state(self, state_id: str) -> Optional[CompromisedState]:
        return self.compromised_states.get(state_id)
