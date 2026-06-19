import asyncio
from typing import Dict, List, Optional, Tuple
import time
import hashlib

class ByteLock:
    def __init__(self, lock_id: str, location: int):
        self.lock_id = lock_id
        self.location = location
        self.locked_bytes: bytes = b''
        self.original_bytes: bytes = b''
        self.is_locked: bool = False
        self.locked_at: Optional[float] = None
        
class EndpointByteLock:
    def __init__(self):
        self.byte_locks: Dict[str, ByteLock] = {}
        self.lock_history: List[Dict] = []
        
    async def lock_bytes_at_location(self, lock_id: str, data: bytes, location: int) -> ByteLock:
        byte_lock = ByteLock(lock_id, location)
        
        # Extract bytes at location
        if 0 <= location < len(data):
            byte_lock.original_bytes = data[location:location+1]
            byte_lock.locked_bytes = byte_lock.original_bytes
            byte_lock.is_locked = True
            byte_lock.locked_at = time.time()
        
        self.byte_locks[lock_id] = byte_lock
        
        self.lock_history.append({
            'lock_id': lock_id,
            'location': location,
            'locked_bytes': byte_lock.locked_bytes.hex(),
            'locked_at': time.time()
        })
        
        return byte_lock
    
    async def swap_bytes_at_location(self, lock_id: str, new_bytes: bytes) -> bool:
        if lock_id not in self.byte_locks:
            return False
            
        byte_lock = self.byte_locks[lock_id]
        byte_lock.locked_bytes = new_bytes
        
        self.lock_history.append({
            'lock_id': lock_id,
            'action': 'swap',
            'new_bytes': new_bytes.hex(),
            'swapped_at': time.time()
        })
        
        return True
    
    async def unlock_bytes(self, lock_id: str) -> bool:
        if lock_id not in self.byte_locks:
            return False
            
        self.byte_locks[lock_id].is_locked = False
        return True
    
    async def get_locked_bytes(self, lock_id: str) -> Optional[bytes]:
        if lock_id in self.byte_locks:
            return self.byte_locks[lock_id].locked_bytes
        return None
    
    def get_byte_lock(self, lock_id: str) -> Optional[ByteLock]:
        return self.byte_locks.get(lock_id)
