import asyncio
from typing import Dict, List, Optional, Tuple
import time

class ZoneTransition:
    def __init__(self, transition_id: str):
        self.transition_id = transition_id
        self.current_zone: str = 'negative'  # 'negative', 'positive'
        self.skipped_state_1: bool = False
        self.transition_path: List[str] = []
        self.zone_history: List[Tuple[str, float]] = []
        self.transitioned_at: Optional[float] = None

class NegativePositiveSkip:
    def __init__(self):
        self.transitions: Dict[str, ZoneTransition] = {}
        self.skip_history: List[Dict] = []
        self.zone_threshold: float = 0.0
        
    async def create_transition(self, transition_id: str) -> ZoneTransition:
        transition = ZoneTransition(transition_id)
        transition.zone_history.append(('negative', time.time()))
        self.transitions[transition_id] = transition
        return transition
    
    async def transition_zone(self, transition_id: str, value: float) -> Tuple[bool, str, bool]:
        if transition_id not in self.transitions:
            return False, "Transition not found", False
            
        transition = self.transitions[transition_id]
        old_zone = transition.current_zone
        
        # Determine new zone
        new_zone = 'positive' if value >= self.zone_threshold else 'negative'
        
        # Check for negative to positive transition
        if old_zone == 'negative' and new_zone == 'positive':
            # Skip state 1
            transition.skipped_state_1 = True
            transition.transition_path = ['negative', 'positive']  # Direct skip
            skip_message = "Skipped state 1 in negative->positive transition"
        else:
            transition.transition_path = [old_zone, new_zone]
            skip_message = "Normal zone transition"
        
        # Update zone
        transition.current_zone = new_zone
        transition.transitioned_at = time.time()
        transition.zone_history.append((new_zone, time.time()))
        
        self.skip_history.append({
            'transition_id': transition_id,
            'from_zone': old_zone,
            'to_zone': new_zone,
            'skipped_state_1': transition.skipped_state_1,
            'value': value,
            'transitioned_at': time.time()
        })
        
        return True, skip_message, transition.skipped_state_1
    
    async def check_skip_occurred(self, transition_id: str) -> bool:
        if transition_id in self.transitions:
            return self.transitions[transition_id].skipped_state_1
        return False
    
    async def get_transition_path(self, transition_id: str) -> Optional[List[str]]:
        if transition_id in self.transitions:
            return self.transitions[transition_id].transition_path
        return None
    
    def set_zone_threshold(self, threshold: float):
        self.zone_threshold = threshold
        
    def get_transition(self, transition_id: str) -> Optional[ZoneTransition]:
        return self.transitions.get(transition_id)
