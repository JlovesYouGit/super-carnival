import asyncio
from typing import Dict, List, Optional, Tuple
import time

class BlockRatio:
    def __init__(self, ratio_id: str):
        self.ratio_id = ratio_id
        self.found_block_size: int = 0
        self.swapped_block_size: int = 0
        self.ratio_value: float = 50.0
        self.applied: bool = False
        self.calculated_at: Optional[float] = None
        
class Ratio50_0:
    def __init__(self):
        self.ratios: Dict[str, BlockRatio] = {}
        self.ratio_history: List[Dict] = []
        self.target_ratio: float = 50.0
        
    async def calculate_ratio(self, ratio_id: str, found_size: int, swapped_size: int) -> BlockRatio:
        ratio = BlockRatio(ratio_id)
        ratio.found_block_size = found_size
        ratio.swapped_block_size = swapped_size
        
        # Calculate ratio based on 50.0 target
        if found_size > 0:
            ratio.ratio_value = (swapped_size / found_size) * self.target_ratio
        else:
            ratio.ratio_value = self.target_ratio
        
        ratio.calculated_at = time.time()
        self.ratios[ratio_id] = ratio
        
        self.ratio_history.append({
            'ratio_id': ratio_id,
            'found_size': found_size,
            'swapped_size': swapped_size,
            'ratio_value': ratio.ratio_value,
            'calculated_at': time.time()
        })
        
        return ratio
    
    async def apply_ratio(self, ratio_id: str) -> bool:
        if ratio_id not in self.ratios:
            return False
            
        self.ratios[ratio_id].applied = True
        return True
    
    async def adjust_blocks_to_ratio(self, ratio_id: str) -> Tuple[int, int]:
        if ratio_id not in self.ratios:
            return 0, 0
            
        ratio = self.ratios[ratio_id]
        
        # Adjust swapped block size to match 50.0 ratio
        target_swapped_size = int(ratio.found_block_size * (self.target_ratio / 100.0))
        
        return ratio.found_block_size, target_swapped_size
    
    async def get_ratio_value(self, ratio_id: str) -> Optional[float]:
        if ratio_id in self.ratios:
            return self.ratios[ratio_id].ratio_value
        return None
    
    async def is_ratio_applied(self, ratio_id: str) -> bool:
        if ratio_id in self.ratios:
            return self.ratios[ratio_id].applied
        return False
    
    def set_target_ratio(self, ratio: float):
        self.target_ratio = ratio
        
    def get_ratio(self, ratio_id: str) -> Optional[BlockRatio]:
        return self.ratios.get(ratio_id)
