import asyncio
import hashlib
import json
from typing import Dict, List, Optional, Tuple
import time
import re

class SHA256DecodeRecode:
    def __init__(self):
        self.word_sequences: Dict[str, List[str]] = {}
        self.hash_mappings: Dict[str, str] = {}
        self.decode_cache: Dict[str, str] = {}
        self.recode_cache: Dict[str, str] = {}
        
    def encode_word_sequence(self, words: List[str]) -> str:
        word_string = ' '.join(words)
        hash_value = hashlib.sha256(word_string.encode()).hexdigest()
        self.hash_mappings[hash_value] = word_string
        return hash_value
    
    def decode_word_sequence(self, hash_value: str) -> Optional[str]:
        if hash_value in self.decode_cache:
            return self.decode_cache[hash_value]
            
        if hash_value in self.hash_mappings:
            decoded = self.hash_mappings[hash_value]
            self.decode_cache[hash_value] = decoded
            return decoded
            
        return None
    
    def recode_word_sequence(self, original_hash: str, new_words: List[str]) -> str:
        new_hash = self.encode_word_sequence(new_words)
        self.recode_cache[original_hash] = new_hash
        return new_hash
    
    async def match_endpoint_sequence(self, endpoint_words: List[str], target_words: List[str]) -> Tuple[bool, float]:
        endpoint_hash = self.encode_word_sequence(endpoint_words)
        target_hash = self.encode_word_sequence(target_words)
        
        if endpoint_hash == target_hash:
            return True, 1.0
            
        # Calculate similarity based on word overlap
        endpoint_set = set(endpoint_words)
        target_set = set(target_words)
        
        if not endpoint_set or not target_set:
            return False, 0.0
            
        overlap = len(endpoint_set & target_set)
        total = len(endpoint_set | target_set)
        similarity = overlap / total if total > 0 else 0.0
        
        return similarity > 0.8, similarity
    
    async def decode_narrative_structure(self, narrative: str) -> Dict:
        words = re.findall(r'\b\w+\b', narrative.lower())
        sentences = re.split(r'[.!?]+', narrative)
        
        structure = {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'unique_words': len(set(words)),
            'word_sequence_hash': self.encode_word_sequence(words),
            'sentences': [s.strip() for s in sentences if s.strip()],
            'words': words
        }
        
        return structure
    
    async def recode_narrative(self, original_hash: str, new_narrative: str) -> str:
        new_structure = await self.decode_narrative_structure(new_narrative)
        return self.recode_word_sequence(original_hash, new_structure['words'])
    
    def get_hash_mapping(self, hash_value: str) -> Optional[str]:
        return self.hash_mappings.get(hash_value)
    
    def get_all_mappings(self) -> Dict[str, str]:
        return self.hash_mappings.copy()
