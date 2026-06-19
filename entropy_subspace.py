import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple
import time
import hashlib
import random

class EntropySubspace:
    def __init__(self):
        self.subspaces: Dict[str, Dict] = {}
        self.entropy_values: Dict[str, List[float]] = []
        self.total_entropy: float = 0.0
        
    async def create_subspace(self, subspace_id: str, dimensions: int) -> Dict:
        subspace = {
            'subspace_id': subspace_id,
            'dimensions': dimensions,
            'entropy_pool': [],
            'created_at': time.time()
        }
        self.subspaces[subspace_id] = subspace
        return subspace
    
    async def calculate_entropy(self, data: List[float]) -> float:
        if not data:
            return 0.0
            
        data_array = np.array(data)
        probabilities = np.abs(data_array) / np.sum(np.abs(data_array))
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return entropy
    
    async def extract_entropy_from_subspace(self, subspace_id: str) -> Optional[float]:
        if subspace_id not in self.subspaces:
            return None
            
        subspace = self.subspaces[subspace_id]
        if not subspace['entropy_pool']:
            return 0.0
            
        entropy = await self.calculate_entropy(subspace['entropy_pool'])
        self.total_entropy += entropy
        return entropy
    
    async def add_to_subspace(self, subspace_id: str, value: float):
        if subspace_id in self.subspaces:
            self.subspaces[subspace_id]['entropy_pool'].append(value)
            
    async def reproduce_data_extraction(self, subspace_id: str, elapsed_time: float) -> Dict:
        total_entropy = await self.extract_entropy_from_subspace(subspace_id)
        
        extraction = {
            'subspace_id': subspace_id,
            'total_entropy': total_entropy,
            'elapsed_time': elapsed_time,
            'extraction_rate': total_entropy / elapsed_time if elapsed_time > 0 else 0,
            'timestamp': time.time()
        }
        
        return extraction
    
    def get_total_entropy(self) -> float:
        return self.total_entropy
    
    def get_subspace_info(self, subspace_id: str) -> Optional[Dict]:
        return self.subspaces.get(subspace_id)
