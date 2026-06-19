import asyncio
import zlib
import hashlib
import json
from typing import Dict, List, Optional, Any
import time

class DataCompressor:
    def __init__(self):
        self.compressed_blocks: Dict[str, Dict] = {}
        self.seeds: Dict[str, str] = {}
        
    def generate_seed(self, data: Any) -> str:
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    async def compress_by_seed(self, data: Any, seed: Optional[str] = None) -> Dict:
        if seed is None:
            seed = self.generate_seed(data)
            
        data_str = json.dumps(data)
        compressed = zlib.compress(data_str.encode())
        
        block = {
            'seed': seed,
            'original_size': len(data_str),
            'compressed_size': len(compressed),
            'compressed_data': compressed.hex(),
            'compression_ratio': len(compressed) / len(data_str),
            'timestamp': time.time()
        }
        
        self.seeds[seed] = block
        return block
    
    async def compress_by_block_type(self, data: Any, block_type: str) -> Dict:
        seed = self.generate_seed(data)
        block = await self.compress_by_seed(data, seed)
        block['block_type'] = block_type
        self.compressed_blocks[block_type] = block
        return block
    
    async def decompress_by_seed(self, seed: str) -> Optional[Any]:
        if seed not in self.seeds:
            return None
            
        block = self.seeds[seed]
        compressed_bytes = bytes.fromhex(block['compressed_data'])
        decompressed = zlib.decompress(compressed_bytes).decode()
        return json.loads(decompressed)
    
    def get_compression_stats(self, seed: str) -> Optional[Dict]:
        if seed in self.seeds:
            block = self.seeds[seed]
            return {
                'original_size': block['original_size'],
                'compressed_size': block['compressed_size'],
                'compression_ratio': block['compression_ratio'],
                'space_saved': block['original_size'] - block['compressed_size']
            }
        return None
