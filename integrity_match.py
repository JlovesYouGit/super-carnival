import asyncio
import hashlib
from typing import Dict, List, Optional, Tuple
import time

class IntegrityMatch:
    def __init__(self):
        self.integrity_records: Dict[str, Dict] = {}
        self.match_history: List[Dict] = []
        self.target_integrity: float = 100.0
        
    def calculate_integrity(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    
    async def verify_integrity(self, data: bytes, expected_hash: str) -> Tuple[bool, float]:
        actual_hash = self.calculate_integrity(data)
        match = actual_hash == expected_hash
        integrity_percent = 100.0 if match else 0.0
        
        return match, integrity_percent
    
    async def match_both_sides(self, side_a_data: bytes, side_b_data: bytes) -> Tuple[bool, float]:
        hash_a = self.calculate_integrity(side_a_data)
        hash_b = self.calculate_integrity(side_b_data)
        
        match = hash_a == hash_b
        integrity_percent = 100.0 if match else 0.0
        
        record = {
            'hash_a': hash_a,
            'hash_b': hash_b,
            'match': match,
            'integrity_percent': integrity_percent,
            'timestamp': time.time()
        }
        
        self.match_history.append(record)
        
        return match, integrity_percent
    
    async def ensure_100_integrity(self, side_a_data: bytes, side_b_data: bytes) -> Dict:
        is_match, integrity = await self.match_both_sides(side_a_data, side_b_data)
        
        result = {
            'integrity_achieved': integrity == 100.0,
            'integrity_percent': integrity,
            'is_match': is_match,
            'timestamp': time.time()
        }
        
        if integrity < 100.0:
            result['action_required'] = 'resync_data'
        else:
            result['action_required'] = 'none'
            
        return result
    
    async def track_integrity_record(self, record_id: str, data: bytes, metadata: Dict = None):
        integrity_hash = self.calculate_integrity(data)
        
        self.integrity_records[record_id] = {
            'record_id': record_id,
            'integrity_hash': integrity_hash,
            'metadata': metadata or {},
            'created_at': time.time()
        }
    
    async def verify_record_integrity(self, record_id: str, current_data: bytes) -> Tuple[bool, float]:
        if record_id not in self.integrity_records:
            return False, 0.0
            
        expected_hash = self.integrity_records[record_id]['integrity_hash']
        return await self.verify_integrity(current_data, expected_hash)
    
    def set_target_integrity(self, target: float):
        self.target_integrity = target
        
    def get_integrity_record(self, record_id: str) -> Optional[Dict]:
        return self.integrity_records.get(record_id)
    
    def get_match_history(self) -> List[Dict]:
        return self.match_history.copy()
