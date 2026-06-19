import asyncio
from typing import Dict, List, Optional, Tuple
import time
import re

class DataBlock:
    def __init__(self, block_id: str):
        self.block_id = block_id
        self.data: bytes = b''
        self.sequence_position: int = 0
        self.size: int = 0
        self.pattern: Optional[str] = None
        self.found_at: Optional[float] = None
        
class DataBlockSequence:
    def __init__(self):
        self.found_blocks: Dict[str, DataBlock] = {}
        self.block_sequences: Dict[str, List[str]] = {}
        self.sequence_history: List[Dict] = []
        
    async def find_data_blocks(self, data: bytes, pattern: bytes) -> List[DataBlock]:
        found = []
        offset = 0
        
        while True:
            pos = data.find(pattern, offset)
            if pos == -1:
                break
                
            block_id = f"block_{pos}_{int(time.time())}"
            block = DataBlock(block_id)
            block.data = data[pos:pos+len(pattern)]
            block.sequence_position = pos
            block.size = len(pattern)
            block.pattern = pattern.hex()
            block.found_at = time.time()
            
            self.found_blocks[block_id] = block
            found.append(block)
            
            offset = pos + len(pattern)
        
        return found
    
    async def detect_block_sequence(self, block_ids: List[str]) -> List[str]:
        sequence = []
        
        for block_id in block_ids:
            if block_id in self.found_blocks:
                block = self.found_blocks[block_id]
                sequence.append(block_id)
        
        return sequence
    
    async def get_sequence_at_location(self, location: int) -> Optional[List[DataBlock]]:
        blocks_at_location = []
        
        for block_id, block in self.found_blocks.items():
            if block.sequence_position == location:
                blocks_at_location.append(block)
        
        return blocks_at_location if blocks_at_location else None
    
    async def get_total_found_blocks(self) -> int:
        return len(self.found_blocks)
    
    def get_found_block(self, block_id: str) -> Optional[DataBlock]:
        return self.found_blocks.get(block_id)
