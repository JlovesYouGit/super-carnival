import asyncio
from typing import Dict, List, Optional, Tuple
import time
import random

class RearrangedPattern:
    def __init__(self, pattern_id: str):
        self.pattern_id = pattern_id
        self.original_sequence: List[bytes] = []
        self.rearranged_sequence: List[bytes] = []
        self.external_source: str = ''
        self.rearranged_at: Optional[float] = None
        
class MultiRearrangePatterns:
    def __init__(self):
        self.patterns: Dict[str, RearrangedPattern] = {}
        self.rearrange_history: List[Dict] = {}
        
    async def create_pattern(self, pattern_id: str, original_sequence: List[bytes], external_source: str) -> RearrangedPattern:
        pattern = RearrangedPattern(pattern_id)
        pattern.original_sequence = original_sequence.copy()
        pattern.external_source = external_source
        
        self.patterns[pattern_id] = pattern
        return pattern
    
    async def rearrange_pattern(self, pattern_id: str, rearrangement_type: str = 'random') -> bool:
        if pattern_id not in self.patterns:
            return False
            
        pattern = self.patterns[pattern_id]
        
        if rearrangement_type == 'random':
            pattern.rearranged_sequence = pattern.original_sequence.copy()
            random.shuffle(pattern.rearranged_sequence)
        elif rearrangement_type == 'reverse':
            pattern.rearranged_sequence = pattern.original_sequence[::-1]
        elif rearrangement_type == 'rotate':
            pattern.rearranged_sequence = pattern.original_sequence[1:] + [pattern.original_sequence[0]]
        
        pattern.rearranged_at = time.time()
        
        self.rearrange_history.append({
            'pattern_id': pattern_id,
            'rearrangement_type': rearrangement_type,
            'external_source': pattern.external_source,
            'rearranged_at': time.time()
        })
        
        return True
    
    async def handle_external_patterns(self, external_patterns: List[Tuple[str, List[bytes]]]) -> List[RearrangedPattern]:
        handled = []
        
        for source, sequence in external_patterns:
            pattern_id = f"pattern_{source}_{int(time.time())}"
            pattern = await self.create_pattern(pattern_id, sequence, source)
            await self.rearrange_pattern(pattern_id, 'random')
            handled.append(pattern)
        
        return handled
    
    async def get_rearranged_sequence(self, pattern_id: str) -> Optional[List[bytes]]:
        if pattern_id in self.patterns:
            return self.patterns[pattern_id].rearranged_sequence
        return None
    
    async def compare_sequences(self, pattern_id: str) -> Optional[Dict]:
        if pattern_id not in self.patterns:
            return None
            
        pattern = self.patterns[pattern_id]
        
        return {
            'pattern_id': pattern_id,
            'original_length': len(pattern.original_sequence),
            'rearranged_length': len(pattern.rearranged_sequence),
            'is_different': pattern.original_sequence != pattern.rearranged_sequence,
            'external_source': pattern.external_source
        }
    
    def get_pattern(self, pattern_id: str) -> Optional[RearrangedPattern]:
        return self.patterns.get(pattern_id)
