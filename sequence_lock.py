import asyncio
from typing import Dict, List, Optional
import time

class SequenceLockPattern:
    def __init__(self):
        self.locked_sequences: Dict[str, Dict] = {}
        self.pattern_history: List[Dict] = []
        self.repeat_count: Dict[str, int] = {}
        
    async def lock_pattern(self, sequence_id: str, pattern: List[str]) -> Dict:
        lock_info = {
            'sequence_id': sequence_id,
            'pattern': pattern,
            'locked_at': time.time(),
            'status': 'locked',
            'current_step': 0
        }
        self.locked_sequences[sequence_id] = lock_info
        return lock_info
    
    async def unlock_pattern(self, sequence_id: str) -> bool:
        if sequence_id in self.locked_sequences:
            self.locked_sequences[sequence_id]['status'] = 'unlocked'
            self.locked_sequences[sequence_id]['unlocked_at'] = time.time()
            return True
        return False
    
    async def execute_step(self, sequence_id: str, step_data: Dict) -> Dict:
        if sequence_id not in self.locked_sequences:
            return {'error': 'Sequence not found'}
            
        sequence = self.locked_sequences[sequence_id]
        current_step = sequence['current_step']
        pattern = sequence['pattern']
        
        if current_step >= len(pattern):
            return {'error': 'Sequence completed'}
            
        result = {
            'sequence_id': sequence_id,
            'step': current_step,
            'pattern_step': pattern[current_step],
            'step_data': step_data,
            'executed_at': time.time()
        }
        
        sequence['current_step'] += 1
        self.pattern_history.append(result)
        
        return result
    
    async def repeat_sequence(self, sequence_id: str) -> Dict:
        if sequence_id not in self.locked_sequences:
            return {'error': 'Sequence not found'}
            
        if sequence_id not in self.repeat_count:
            self.repeat_count[sequence_id] = 0
        self.repeat_count[sequence_id] += 1
        
        sequence = self.locked_sequences[sequence_id]
        sequence['current_step'] = 0
        sequence['repeated_at'] = time.time()
        
        return {
            'sequence_id': sequence_id,
            'repeat_count': self.repeat_count[sequence_id],
            'reset_at': time.time()
        }
    
    async def lock_and_repeat(self, sequence_id: str, pattern: List[str], 
                             repeat_times: int = 1) -> Dict:
        await self.lock_pattern(sequence_id, pattern)
        
        for _ in range(repeat_times):
            await self.repeat_sequence(sequence_id)
            
        return {
            'sequence_id': sequence_id,
            'pattern': pattern,
            'repeat_times': repeat_times,
            'completed_at': time.time()
        }
    
    def get_sequence_status(self, sequence_id: str) -> Optional[Dict]:
        return self.locked_sequences.get(sequence_id)
    
    def get_pattern_history(self) -> List[Dict]:
        return self.pattern_history
