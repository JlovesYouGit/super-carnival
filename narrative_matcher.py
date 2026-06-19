import asyncio
from typing import Dict, List, Optional, Tuple
import time
import re

class NarrativeCodeStructure:
    def __init__(self, structure_id: str):
        self.structure_id = structure_id
        self.code_blocks: List[Dict] = []
        self.word_patterns: Dict[str, List[str]] = {}
        self.syntax_tree: Dict = {}
        self.created_at = time.time()

class NarrativeMatcher:
    def __init__(self):
        self.structures: Dict[str, NarrativeCodeStructure] = {}
        self.pattern_matches: Dict[str, List[Dict]] = {}
        
    async def analyze_code_structure(self, code: str, structure_id: str) -> NarrativeCodeStructure:
        structure = NarrativeCodeStructure(structure_id)
        
        # Extract code blocks
        code_blocks = re.findall(r'(\w+|\s+|[^\w\s])', code)
        structure.code_blocks = [{'type': 'token', 'value': block} for block in code_blocks]
        
        # Extract word patterns
        words = re.findall(r'\b[a-zA-Z_]\w*\b', code)
        structure.word_patterns['identifiers'] = words
        
        # Build simple syntax tree
        structure.syntax_tree = {
            'root': 'code',
            'children': [
                {'type': 'identifiers', 'count': len(words)},
                {'type': 'tokens', 'count': len(code_blocks)}
            ]
        }
        
        self.structures[structure_id] = structure
        return structure
    
    async def match_narrative_to_code(self, narrative: str, code_structure_id: str) -> Tuple[bool, float]:
        if code_structure_id not in self.structures:
            return False, 0.0
            
        structure = self.structures[code_structure_id]
        narrative_words = re.findall(r'\b\w+\b', narrative.lower())
        code_words = structure.word_patterns.get('identifiers', [])
        
        # Calculate match score
        narrative_set = set(narrative_words)
        code_set = set([w.lower() for w in code_words])
        
        if not narrative_set or not code_set:
            return False, 0.0
            
        overlap = len(narrative_set & code_set)
        total = len(narrative_set | code_set)
        match_score = overlap / total if total > 0 else 0.0
        
        match_record = {
            'narrative': narrative[:100],
            'code_structure_id': code_structure_id,
            'match_score': match_score,
            'timestamp': time.time()
        }
        
        if code_structure_id not in self.pattern_matches:
            self.pattern_matches[code_structure_id] = []
        self.pattern_matches[code_structure_id].append(match_record)
        
        return match_score > 0.7, match_score
    
    async def find_best_match(self, narrative: str) -> Optional[Tuple[str, float]]:
        best_match = None
        best_score = 0.0
        
        for structure_id in self.structures:
            is_match, score = await self.match_narrative_to_code(narrative, structure_id)
            if score > best_score:
                best_score = score
                best_match = (structure_id, score)
                
        return best_match
    
    def get_structure(self, structure_id: str) -> Optional[NarrativeCodeStructure]:
        return self.structures.get(structure_id)
    
    def get_pattern_matches(self, structure_id: str) -> List[Dict]:
        return self.pattern_matches.get(structure_id, [])
