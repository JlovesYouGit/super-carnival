import asyncio
from typing import Dict, List, Optional
import time
import json

class PersonaCategory:
    def __init__(self, category_id: str, name: str, ego_type: str):
        self.category_id = category_id
        self.name = name
        self.ego_type = ego_type
        self.intellectual_properties: List[str] = []
        self.created_at = time.time()
        
    def to_dict(self) -> Dict:
        return {
            'category_id': self.category_id,
            'name': self.name,
            'ego_type': self.ego_type,
            'intellectual_properties': self.intellectual_properties,
            'created_at': self.created_at
        }

class EmergentPersonaCategories:
    def __init__(self):
        self.categories: Dict[str, PersonaCategory] = {}
        self.intent_pattern_mapping: Dict[str, List[str]] = {}
        self.collective_intellectual_properties: Dict[str, List[str]] = {}
        
    async def create_category(self, category_id: str, name: str, ego_type: str) -> PersonaCategory:
        category = PersonaCategory(category_id, name, ego_type)
        self.categories[category_id] = category
        return category
    
    async def add_intellectual_property(self, category_id: str, property: str):
        if category_id in self.categories:
            self.categories[category_id].intellectual_properties.append(property)
            
    async def map_intent_to_categories(self, intent: str, category_ids: List[str]):
        self.intent_pattern_mapping[intent] = category_ids
        
    async def extract_collective_properties(self, intent: str) -> List[str]:
        category_ids = self.intent_pattern_mapping.get(intent, [])
        collective = []
        
        for cat_id in category_ids:
            if cat_id in self.categories:
                collective.extend(self.categories[cat_id].intellectual_properties)
                
        self.collective_intellectual_properties[intent] = collective
        return collective
    
    def get_categories_by_intent(self, intent: str) -> List[PersonaCategory]:
        category_ids = self.intent_pattern_mapping.get(intent, [])
        return [self.categories[cat_id] for cat_id in category_ids if cat_id in self.categories]
    
    def get_category(self, category_id: str) -> Optional[PersonaCategory]:
        return self.categories.get(category_id)
