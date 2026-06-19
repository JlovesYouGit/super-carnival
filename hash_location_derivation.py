import asyncio
from typing import Dict, List, Optional, Tuple
import time
import hashlib

class HashLocation:
    def __init__(self, location_id: str):
        self.location_id = location_id
        self.hash_position: int = 0
        self.internal_block: bytes = b''
        self.numerical_count: int = 0
        self.structured_params: Dict = {}
        self.derived_at: Optional[float] = None

class HashLocationDerivation:
    def __init__(self):
        self.locations: Dict[str, HashLocation] = {}
        self.derivation_history: List[Dict] = []
        
    async def derive_location_from_hash(self, location_id: str, internal_block: bytes, 
                                       structured_params: Dict) -> HashLocation:
        location = HashLocation(location_id)
        location.internal_block = internal_block
        location.structured_params = structured_params
        
        # Derive hash position from internal block
        block_hash = hashlib.sha256(internal_block).hexdigest()
        hash_position = int(block_hash[:8], 16) % len(internal_block)
        location.hash_position = hash_position
        
        # Calculate entire numerical count of structured fetched params
        location.numerical_count = self._calculate_numerical_count(structured_params)
        
        location.derived_at = time.time()
        
        self.locations[location_id] = location
        
        self.derivation_history.append({
            'location_id': location_id,
            'hash_position': hash_position,
            'numerical_count': location.numerical_count,
            'derived_at': time.time()
        })
        
        return location
    
    def _calculate_numerical_count(self, structured_params: Dict) -> int:
        """Calculate entire numerical count of structured fetched params"""
        count = 0
        
        def count_numerical_values(obj):
            nonlocal count
            if isinstance(obj, (int, float)):
                count += 1
            elif isinstance(obj, dict):
                for value in obj.values():
                    count_numerical_values(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_numerical_values(item)
        
        count_numerical_values(structured_params)
        return count
    
    async def get_endpoint_data_return(self, location_id: str) -> Optional[Dict]:
        """Endpoint data returns the entire numerical count of structured fetched params"""
        if location_id not in self.locations:
            return None
        
        location = self.locations[location_id]
        
        return {
            'location_id': location_id,
            'hash_position': location.hash_position,
            'internal_block_size': len(location.internal_block),
            'numerical_count': location.numerical_count,
            'structured_params': location.structured_params,
            'derived_at': location.derived_at
        }
    
    def get_location(self, location_id: str) -> Optional[HashLocation]:
        return self.locations.get(location_id)
