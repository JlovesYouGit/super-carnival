import asyncio
from typing import Dict, List, Optional
import time
import math

class NanoSequence:
    def __init__(self, sequence_id: str):
        self.sequence_id = sequence_id
        self.nano_chunks: List[bytes] = []
        self.split_pattern: Optional[str] = None
        self.reconstructed: bytes = b''
        self.created_at: time.time()

class NanoSequenceSplitter:
    def __init__(self):
        self.nano_sequences: Dict[str, NanoSequence] = {}
        self.split_history: List[Dict] = []
        self.nano_size: int = 64  # 64 bytes per nano chunk
        
    async def split_into_nano_sequences(self, sequence_id: str, raw_data: bytes, 
                                         split_pattern: str = 'uniform') -> NanoSequence:
        nano_seq = NanoSequence(sequence_id)
        nano_seq.split_pattern = split_pattern
        
        if split_pattern == 'uniform':
            # Split into uniform nano chunks
            for i in range(0, len(raw_data), self.nano_size):
                chunk = raw_data[i:i+self.nano_size]
                nano_seq.nano_chunks.append(chunk)
                
        elif split_pattern == 'variable':
            # Split into variable sized nano chunks
            chunk_size = self.nano_size
            offset = 0
            while offset < len(raw_data):
                # Vary chunk size based on position
                chunk_size = self.nano_size + (offset % 32)
                chunk = raw_data[offset:offset+chunk_size]
                nano_seq.nano_chunks.append(chunk)
                offset += chunk_size
                
        elif split_pattern == 'entropy':
            # Split based on entropy patterns
            chunk_size = self.nano_size
            offset = 0
            while offset < len(raw_data):
                # Calculate local entropy to determine chunk size
                local_entropy = self._calculate_local_entropy(raw_data, offset, chunk_size)
                chunk_size = int(self.nano_size * (1 + local_entropy))
                chunk = raw_data[offset:offset+chunk_size]
                nano_seq.nano_chunks.append(chunk)
                offset += chunk_size
        
        self.nano_sequences[sequence_id] = nano_seq
        
        self.split_history.append({
            'sequence_id': sequence_id,
            'split_pattern': split_pattern,
            'chunk_count': len(nano_seq.nano_chunks),
            'total_bytes': len(raw_data),
            'split_at': time.time()
        })
        
        return nano_seq
    
    def _calculate_local_entropy(self, data: bytes, offset: int, window_size: int) -> float:
        window = data[offset:offset+window_size]
        if not window:
            return 0.0
            
        # Calculate entropy from boolean/raw_data incoming bytes values
        # Convert bytes to boolean representation (bits)
        boolean_values = []
        for byte in window:
            # Convert each byte to 8 boolean bits
            for bit_pos in range(8):
                boolean_bit = (byte >> bit_pos) & 1
                boolean_values.append(boolean_bit)
        
        if not boolean_values:
            return 0.0
        
        # Calculate entropy based on boolean bit distribution
        true_count = sum(boolean_values)
        false_count = len(boolean_values) - true_count
        total = len(boolean_values)
        
        if total == 0:
            return 0.0
        
        # Shannon entropy calculation for boolean values
        entropy = 0.0
        if true_count > 0:
            p_true = true_count / total
            entropy -= p_true * math.log2(p_true) if p_true > 0 else 0
        if false_count > 0:
            p_false = false_count / total
            entropy -= p_false * math.log2(p_false) if p_false > 0 else 0
        
        return entropy / 8.0  # Normalize to 0-1 range
    
    async def reconstruct_from_nano(self, sequence_id: str) -> Optional[bytes]:
        if sequence_id not in self.nano_sequences:
            return None
            
        nano_seq = self.nano_sequences[sequence_id]
        reconstructed = b''.join(nano_seq.nano_chunks)
        nano_seq.reconstructed = reconstructed
        
        return reconstructed
    
    async def get_nano_chunk(self, sequence_id: str, chunk_index: int) -> Optional[bytes]:
        if sequence_id not in self.nano_sequences:
            return None
            
        nano_seq = self.nano_sequences[sequence_id]
        if 0 <= chunk_index < len(nano_seq.nano_chunks):
            return nano_seq.nano_chunks[chunk_index]
            
        return None
    
    async def split_spectrum_data(self, spectrum_data: List[float]) -> List[NanoSequence]:
        sequences = []
        
        # Convert spectrum to bytes
        raw_data = bytes([int(x * 255) for x in spectrum_data])
        
        # Split into multiple nano sequences
        sequence_count = 4
        chunk_size = len(raw_data) // sequence_count
        
        for i in range(sequence_count):
            seq_id = f"nano_seq_{i}_{int(time.time())}"
            chunk = raw_data[i*chunk_size:(i+1)*chunk_size]
            nano_seq = await self.split_into_nano_sequences(seq_id, chunk, 'entropy')
            sequences.append(nano_seq)
            
        return sequences
    
    def set_nano_size(self, size: int):
        self.nano_size = size
        
    def get_nano_sequence(self, sequence_id: str) -> Optional[NanoSequence]:
        return self.nano_sequences.get(sequence_id)
    
    def get_split_history(self) -> List[Dict]:
        return self.split_history.copy()
