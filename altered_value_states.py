import asyncio
from typing import Dict, List, Optional, Any
import time

class AlteredValue:
    def __init__(self, value_id: str):
        self.value_id = value_id
        self.original_value: Any = None
        self.altered_value: Any = None
        self.is_none_moving: bool = False
        self.is_altered_state: bool = False
        self.last_updated: Optional[float] = None
        self.update_count: int = 0
        
class AlteredValueStates:
    def __init__(self):
        self.altered_values: Dict[str, AlteredValue] = {}
        self.state_history: List[Dict] = []
        
    async def create_value(self, value_id: str, original_value: Any) -> AlteredValue:
        altered_value = AlteredValue(value_id)
        altered_value.original_value = original_value
        altered_value.altered_value = original_value
        
        self.altered_values[value_id] = altered_value
        return altered_value
    
    async def update_value(self, value_id: str, new_value: Any) -> bool:
        if value_id not in self.altered_values:
            return False
            
        altered = self.altered_values[value_id]
        
        # Check if value is actually changing
        if altered.altered_value != new_value:
            altered.altered_value = new_value
            altered.last_updated = time.time()
            altered.update_count += 1
            
            # If value holds and updates, constant is not defined as none moving but altered value states
            altered.is_none_moving = False
            altered.is_altered_state = True
            
            self.state_history.append({
                'value_id': value_id,
                'original_value': altered.original_value,
                'altered_value': new_value,
                'updated_at': time.time()
            })
        
        return True
    
    async def check_if_none_moving(self, value_id: str) -> bool:
        if value_id in self.altered_values:
            return self.altered_values[value_id].is_none_moving
        return False
    
    async def check_if_altered_state(self, value_id: str) -> bool:
        if value_id in self.altered_values:
            return self.altered_values[value_id].is_altered_state
        return False
    
    async def get_value_difference(self, value_id: str) -> Optional[Any]:
        if value_id in self.altered_values:
            altered = self.altered_values[value_id]
            return altered.altered_value - altered.original_value if isinstance(altered.altered_value, (int, float)) else None
        return None
    
    async def reset_to_original(self, value_id: str) -> bool:
        if value_id not in self.altered_values:
            return False
            
        altered = self.altered_values[value_id]
        altered.altered_value = altered.original_value
        altered.is_altered_state = False
        altered.is_none_moving = True
        
        return True
    
    def get_altered_value(self, value_id: str) -> Optional[AlteredValue]:
        return self.altered_values.get(value_id)
