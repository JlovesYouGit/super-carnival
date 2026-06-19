import asyncio
from typing import Dict, List, Optional
import time
import json

class ServerUpdateOrder:
    def __init__(self):
        self.update_queue: List[Dict] = []
        self.update_history: Dict[str, Dict] = {}
        self.current_order: int = 0
        self.recode_instructions: Dict[str, str] = {}
        
    async def add_update(self, server_id: str, update_data: Dict) -> Dict:
        update_order = {
            'server_id': server_id,
            'update_data': update_data,
            'order': self.current_order,
            'queued_at': time.time(),
            'status': 'queued'
        }
        self.update_queue.append(update_order)
        self.current_order += 1
        return update_order
    
    async def process_update(self, server_id: str) -> Optional[Dict]:
        for i, update in enumerate(self.update_queue):
            if update['server_id'] == server_id and update['status'] == 'queued':
                update['status'] = 'processing'
                update['processing_started'] = time.time()
                return update
        return None
    
    async def complete_update(self, server_id: str, result: Dict) -> Dict:
        for update in self.update_queue:
            if update['server_id'] == server_id:
                update['status'] = 'completed'
                update['completed_at'] = time.time()
                update['result'] = result
                self.update_history[server_id] = update
                return update
        return {}
    
    async def recode_server(self, server_id: str, recode_instruction: str) -> Dict:
        recode_data = {
            'server_id': server_id,
            'recode_instruction': recode_instruction,
            'recoded_at': time.time(),
            'status': 'recoded'
        }
        self.recode_instructions[server_id] = recode_instruction
        return recode_data
    
    async def get_update_order(self, server_id: str) -> Optional[int]:
        for update in self.update_queue:
            if update['server_id'] == server_id:
                return update['order']
        return None
    
    async def process_queue(self) -> List[Dict]:
        processed = []
        for update in self.update_queue:
            if update['status'] == 'queued':
                await self.process_update(update['server_id'])
                processed.append(update)
        return processed
    
    async def update_via_recode(self, server_id: str, update_data: Dict, 
                                recode_instruction: str) -> Dict:
        await self.add_update(server_id, update_data)
        await self.recode_server(server_id, recode_instruction)
        
        result = {
            'server_id': server_id,
            'update_data': update_data,
            'recode_instruction': recode_instruction,
            'updated_via_recode': True,
            'timestamp': time.time()
        }
        
        await self.complete_update(server_id, result)
        return result
    
    def get_update_history(self) -> Dict[str, Dict]:
        return self.update_history
    
    def get_queue_status(self) -> Dict:
        return {
            'queue_length': len(self.update_queue),
            'pending': len([u for u in self.update_queue if u['status'] == 'queued']),
            'processing': len([u for u in self.update_queue if u['status'] == 'processing']),
            'completed': len([u for u in self.update_queue if u['status'] == 'completed'])
        }
