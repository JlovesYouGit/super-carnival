import asyncio
from typing import Dict, List, Optional
import time

class DelayOrderInstruction:
    def __init__(self, instruction_id: str, delay_ms: int, instruction: Dict):
        self.instruction_id = instruction_id
        self.delay_ms = delay_ms
        self.instruction = instruction
        self.created_at = time.time()
        self.executed = False
        
    async def execute(self) -> Dict:
        await asyncio.sleep(self.delay_ms / 1000.0)
        self.executed = True
        return {
            'instruction_id': self.instruction_id,
            'executed_at': time.time(),
            'result': self.instruction
        }

class DelayOrderRepeater:
    def __init__(self):
        self.instructions: Dict[str, DelayOrderInstruction] = {}
        self.repeat_queue: List[Dict] = []
        self.repeat_count: Dict[str, int] = {}
        self.max_repeats: int = 10
        
    async def add_instruction(self, instruction_id: str, delay_ms: int, 
                              instruction: Dict) -> DelayOrderInstruction:
        delay_instruction = DelayOrderInstruction(instruction_id, delay_ms, instruction)
        self.instructions[instruction_id] = delay_instruction
        return delay_instruction
    
    async def execute_instruction(self, instruction_id: str) -> Optional[Dict]:
        if instruction_id in self.instructions:
            return await self.instructions[instruction_id].execute()
        return None
    
    async def add_to_repeat_queue(self, instruction_id: str, repeat_times: int = 1):
        if instruction_id not in self.repeat_count:
            self.repeat_count[instruction_id] = 0
        self.repeat_count[instruction_id] += repeat_times
        
        for _ in range(repeat_times):
            self.repeat_queue.append({
                'instruction_id': instruction_id,
                'queued_at': time.time()
            })
    
    async def process_repeat_queue(self) -> List[Dict]:
        results = []
        while self.repeat_queue:
            queue_item = self.repeat_queue.pop(0)
            instruction_id = queue_item['instruction_id']
            result = await self.execute_instruction(instruction_id)
            if result:
                results.append(result)
        return results
    
    async def repeat_instruction(self, instruction_id: str, repeat_times: int = 1) -> List[Dict]:
        await self.add_to_repeat_queue(instruction_id, repeat_times)
        return await self.process_repeat_queue()
    
    def get_instruction_status(self, instruction_id: str) -> Optional[Dict]:
        if instruction_id in self.instructions:
            return {
                'instruction_id': instruction_id,
                'delay_ms': self.instructions[instruction_id].delay_ms,
                'executed': self.instructions[instruction_id].executed,
                'created_at': self.instructions[instruction_id].created_at
            }
        return None
    
    def get_repeat_count(self, instruction_id: str) -> int:
        return self.repeat_count.get(instruction_id, 0)
