import asyncio
from typing import Dict, List, Optional, Set
import time
import random

class WordInterwindSpace:
    def __init__(self, space_id: str, space_type: str):
        self.space_id = space_id
        self.space_type = space_type  # 'endpoint' or 'user'
        self.words: Set[str] = set()
        self.word_frequencies: Dict[str, int] = {}
        self.file_types: Dict[str, List[str]] = {}
        self.created_at = time.time()

class WordInterwindSystem:
    def __init__(self):
        self.endpoint_spaces: Dict[str, WordInterwindSpace] = {}
        self.user_spaces: Dict[str, WordInterwindSpace] = {}
        self.interwind_mappings: Dict[str, List[str]] = {}
        
    async def create_endpoint_space(self, space_id: str, file_types: List[str]) -> WordInterwindSpace:
        space = WordInterwindSpace(space_id, 'endpoint')
        space.file_types = {ft: [] for ft in file_types}
        self.endpoint_spaces[space_id] = space
        return space
    
    async def create_user_space(self, space_id: str, file_types: List[str]) -> WordInterwindSpace:
        space = WordInterwindSpace(space_id, 'user')
        space.file_types = {ft: [] for ft in file_types}
        self.user_spaces[space_id] = space
        return space
    
    async def add_words_to_space(self, space_id: str, space_type: str, words: List[str], file_type: str):
        if space_type == 'endpoint':
            space = self.endpoint_spaces.get(space_id)
        else:
            space = self.user_spaces.get(space_id)
            
        if space and file_type in space.file_types:
            for word in words:
                space.words.add(word.lower())
                space.word_frequencies[word.lower()] = space.word_frequencies.get(word.lower(), 0) + 1
                space.file_types[file_type].append(word.lower())
    
    async def calculate_probable_interwind(self, endpoint_space_id: str, user_space_id: str) -> Dict:
        endpoint_space = self.endpoint_spaces.get(endpoint_space_id)
        user_space = self.user_spaces.get(user_space_id)
        
        if not endpoint_space or not user_space:
            return {'error': 'Spaces not found'}
            
        common_words = endpoint_space.words & user_space.words
        total_words = endpoint_space.words | user_space.words
        
        interwind_probability = len(common_words) / len(total_words) if total_words else 0.0
        
        # Calculate file type dispersion
        file_type_matches = {}
        for file_type in endpoint_space.file_types:
            if file_type in user_space.file_types:
                endpoint_words = set(endpoint_space.file_types[file_type])
                user_words = set(user_space.file_types[file_type])
                file_type_matches[file_type] = len(endpoint_words & user_words)
        
        return {
            'endpoint_space_id': endpoint_space_id,
            'user_space_id': user_space_id,
            'interwind_probability': interwind_probability,
            'common_words': list(common_words),
            'file_type_matches': file_type_matches,
            'timestamp': time.time()
        }
    
    async def disperse_words_across_files(self, space_id: str, space_type: str, words: List[str]) -> Dict:
        if space_type == 'endpoint':
            space = self.endpoint_spaces.get(space_id)
        else:
            space = self.user_spaces.get(space_id)
            
        if not space:
            return {'error': 'Space not found'}
            
        dispersion = {}
        for file_type in space.file_types:
            words_per_file = len(words) // len(space.file_types)
            dispersed_words = random.sample(words, min(words_per_file, len(words)))
            await self.add_words_to_space(space_id, space_type, dispersed_words, file_type)
            dispersion[file_type] = len(dispersed_words)
            
        return dispersion
    
    def get_space(self, space_id: str, space_type: str) -> Optional[WordInterwindSpace]:
        if space_type == 'endpoint':
            return self.endpoint_spaces.get(space_id)
        return self.user_spaces.get(space_id)
