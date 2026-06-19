import asyncio
from typing import Dict, List, Optional, Tuple
import time
import hashlib

class SpatialRule:
    def __init__(self, rule_id: str):
        self.rule_id = rule_id
        self.hash_value: str = ''
        self.found_state: str = ''
        self.physics_state: str = ''
        self.block_movement_allowed: bool = True
        self.created_at: time.time()

class SpatialHashRules:
    def __init__(self):
        self.rules: Dict[str, SpatialRule] = {}
        self.spatial_states: Dict[str, str] = {}
        self.rule_history: List[Dict] = []
        
    async def create_spatial_rule(self, rule_id: str, hash_value: str, found_state: str, physics_state: str) -> SpatialRule:
        rule = SpatialRule(rule_id)
        rule.hash_value = hash_value
        rule.found_state = found_state
        rule.physics_state = physics_state
        
        self.rules[rule_id] = rule
        self.spatial_states[hash_value] = physics_state
        
        return rule
    
    async def check_movement_allowed(self, block_hash: str, current_state: str) -> bool:
        # Check if movement is allowed under spatial hash rules
        for rule_id, rule in self.rules.items():
            if rule.hash_value == block_hash:
                if rule.found_state == current_state:
                    return rule.block_movement_allowed
        
        # Default: allow movement
        return True
    
    async def move_block_under_rule(self, block_id: str, block_hash: str, current_state: str) -> bool:
        allowed = await self.check_movement_allowed(block_hash, current_state)
        
        if allowed:
            self.rule_history.append({
                'block_id': block_id,
                'block_hash': block_hash,
                'current_state': current_state,
                'movement_allowed': allowed,
                'moved_at': time.time()
            })
        
        return allowed
    
    async def apply_spatial_rule(self, rule_id: str, block_data: bytes) -> bool:
        if rule_id not in self.rules:
            return False
            
        rule = self.rules[rule_id]
        
        # Calculate hash of block data
        block_hash = hashlib.sha256(block_data).hexdigest()
        
        # Check if hash matches rule
        if block_hash == rule.hash_value:
            return True
        
        return False
    
    async def get_physics_state(self, hash_value: str) -> Optional[str]:
        return self.spatial_states.get(hash_value)
    
    async def update_physics_state(self, hash_value: str, new_state: str):
        self.spatial_states[hash_value] = new_state
        
    def get_rule(self, rule_id: str) -> Optional[SpatialRule]:
        return self.rules.get(rule_id)
