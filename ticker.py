import time
from typing import Dict, Optional

class Ticker:
    def __init__(self):
        self.current_value: int = 0
        self.ticker_history: Dict[int, Dict] = {}
        self.tick_count: int = 0
        
    def set_value(self, value: int) -> int:
        self.current_value = value
        self.tick_count += 1
        self.ticker_history[self.tick_count] = {
            'value': value,
            'timestamp': time.time()
        }
        return self.current_value
    
    def get_value(self) -> int:
        return self.current_value
    
    def set_minus_nine(self) -> int:
        return self.set_value(-9)
    
    def increment(self) -> int:
        return self.set_value(self.current_value + 1)
    
    def decrement(self) -> int:
        return self.set_value(self.current_value - 1)
    
    def get_history(self) -> Dict[int, Dict]:
        return self.ticker_history
    
    def get_tick_count(self) -> int:
        return self.tick_count
    
    def reset(self) -> int:
        self.current_value = 0
        self.tick_count = 0
        self.ticker_history.clear()
        return self.current_value
