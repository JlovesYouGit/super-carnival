import asyncio
from typing import Dict, List, Optional, Tuple
import time

class StateTransition:
    def __init__(self, transition_id: str):
        self.transition_id = transition_id
        self.current_state: int = 0
        self.state_history: List[int] = []
        self.transition_times: Dict[Tuple[int, int], float] = {}
        self.weight_accumulated: float = 0.0
        self.is_persistent: bool = False
        self.created_at: time.time()

class StateTransitionSystem:
    def __init__(self):
        self.transitions: Dict[str, StateTransition] = {}
        self.transition_rules: Dict[Tuple[int, int], bool] = {
            (0, 1): True,
            (1, 2): True,
            (0, 2): False  # Direct skip only with negative->positive
        }
        self.transition_history: List[Dict] = []
        
    async def create_transition(self, transition_id: str) -> StateTransition:
        transition = StateTransition(transition_id)
        self.transitions[transition_id] = transition
        return transition
    
    async def transition_state(self, transition_id: str, new_state: int, 
                              skip_allowed: bool = False) -> Tuple[bool, str]:
        if transition_id not in self.transitions:
            return False, "Transition not found"
            
        transition = self.transitions[transition_id]
        old_state = transition.current_state
        transition_key = (old_state, new_state)
        
        # Check if transition is allowed
        if transition_key not in self.transition_rules:
            if not skip_allowed:
                return False, f"Transition {old_state}->{new_state} not allowed"
        
        # Special case: 0->2 only allowed with skip
        if transition_key == (0, 2) and not skip_allowed:
            return False, "Direct 0->2 transition requires skip permission"
        
        # Perform transition
        transition.current_state = new_state
        transition.state_history.append(new_state)
        transition.transition_times[transition_key] = time.time()
        
        self.transition_history.append({
            'transition_id': transition_id,
            'from_state': old_state,
            'to_state': new_state,
            'skip_allowed': skip_allowed,
            'transitioned_at': time.time()
        })
        
        return True, f"Transitioned {old_state}->{new_state}"
    
    async def set_persistent(self, transition_id: str, is_persistent: bool):
        if transition_id in self.transitions:
            self.transitions[transition_id].is_persistent = is_persistent
    
    async def add_weight(self, transition_id: str, weight: float):
        if transition_id in self.transitions:
            self.transitions[transition_id].weight_accumulated += weight
    
    async def get_state_weight(self, transition_id: str) -> Optional[float]:
        if transition_id in self.transitions:
            return self.transitions[transition_id].weight_accumulated
        return None
    
    async def get_current_state(self, transition_id: str) -> Optional[int]:
        if transition_id in self.transitions:
            return self.transitions[transition_id].current_state
        return None
    
    def get_transition(self, transition_id: str) -> Optional[StateTransition]:
        return self.transitions.get(transition_id)
