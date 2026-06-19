import asyncio
from typing import Dict, List, Optional, Any
import time
import struct
import hashlib

class RayByte:
    def __init__(self, byte_id: str):
        self.byte_id = byte_id
        self.raw_bytes: bytes = b''
        self.ray_signature: Optional[str] = None
        self.output_changes: List[Dict] = []
        self.processed_at: Optional[float] = None

class RayByteProcessor:
    def __init__(self):
        self.ray_bytes: Dict[str, RayByte] = {}
        self.processing_history: List[Dict] = []
        self.entropy_base: float = 0.0
        
    async def process_ray_byte_output(self, byte_id: str, raw_bytes: bytes, entropy_base: float) -> RayByte:
        ray = RayByte(byte_id)
        ray.raw_bytes = raw_bytes
        ray.ray_signature = self._calculate_ray_signature(raw_bytes)
        ray.processed_at = time.time()
        
        # Apply changes based on entropy
        changes = await self._apply_entropy_changes(raw_bytes, entropy_base)
        ray.output_changes = changes
        
        self.ray_bytes[byte_id] = ray
        
        self.processing_history.append({
            'byte_id': byte_id,
            'signature': ray.ray_signature,
            'changes_applied': len(changes),
            'entropy_base': entropy_base,
            'processed_at': time.time()
        })
        
        return ray
    
    def _calculate_ray_signature(self, raw_bytes: bytes) -> str:
        return hashlib.sha256(raw_bytes).hexdigest()[:16]
    
    async def _apply_entropy_changes(self, raw_bytes: bytes, entropy: float) -> List[Dict]:
        changes = []
        byte_array = bytearray(raw_bytes)
        
        # Fast through using entropy base
        for i in range(len(byte_array)):
            if entropy > 0.5:
                # Apply change based on entropy
                change_factor = entropy * (i % 10) / 10.0
                original = byte_array[i]
                byte_array[i] = int((original + change_factor * 255) % 256)
                
                changes.append({
                    'position': i,
                    'original': original,
                    'modified': byte_array[i],
                    'change_factor': change_factor
                })
        
        return changes
    
    async def fast_through_entropy(self, byte_id: str, target_entropy: float) -> bytes:
        if byte_id not in self.ray_bytes:
            return b''
            
        ray = self.ray_bytes[byte_id]
        modified = await self._apply_entropy_changes(ray.raw_bytes, target_entropy)
        
        # Reconstruct bytes with changes
        byte_array = bytearray(ray.raw_bytes)
        for change in modified:
            byte_array[change['position']] = change['modified']
            
        return bytes(byte_array)
    
    async def get_outputted_ray_bytes(self, byte_id: str) -> Optional[bytes]:
        if byte_id in self.ray_bytes:
            return await self.fast_through_entropy(byte_id, self.entropy_base)
        return None
    
    async def set_entropy_base(self, entropy: float):
        self.entropy_base = entropy
        
    def get_ray_byte(self, byte_id: str) -> Optional[RayByte]:
        return self.ray_bytes.get(byte_id)
    
    def get_processing_history(self) -> List[Dict]:
        return self.processing_history.copy()
