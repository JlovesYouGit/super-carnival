import asyncio
import json
import os
from typing import Dict, List, Optional, Any
import time

class BlockOrderDataFile:
    def __init__(self, filename: str = "block_order_data.json"):
        self.filename = filename
        self.blocks: Dict[str, Dict] = {}
        self.block_order: List[str] = []
        self.parameter_sets: Dict[str, List[Dict]] = {}
        self.recollections: Dict[str, List[Dict]] = {}
        self.load_from_file()
        
    def load_from_file(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.blocks = data.get('blocks', {})
                    self.block_order = data.get('block_order', [])
                    self.parameter_sets = data.get('parameter_sets', {})
                    self.recollections = data.get('recollections', {})
            except Exception as e:
                print(f"Load error: {e}")
    
    def save_to_file(self):
        try:
            data = {
                'blocks': self.blocks,
                'block_order': self.block_order,
                'parameter_sets': self.parameter_sets,
                'recollections': self.recollections,
                'saved_at': time.time()
            }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Save error: {e}")
    
    async def add_block(self, block_id: str, block_data: Dict) -> Dict:
        block = {
            'block_id': block_id,
            'data': block_data,
            'order_position': len(self.block_order),
            'added_at': time.time()
        }
        self.blocks[block_id] = block
        self.block_order.append(block_id)
        self.save_to_file()
        return block
    
    async def add_parameter_set(self, instance_id: str, parameters: Dict):
        if instance_id not in self.parameter_sets:
            self.parameter_sets[instance_id] = []
        self.parameter_sets[instance_id].append({
            'parameters': parameters,
            'timestamp': time.time()
        })
        self.save_to_file()
    
    async def add_recollection(self, instance_id: str, recollection: Dict):
        if instance_id not in self.recollections:
            self.recollections[instance_id] = []
        self.recollections[instance_id].append({
            'recollection': recollection,
            'timestamp': time.time()
        })
        self.save_to_file()
    
    def get_block_order(self) -> List[str]:
        return self.block_order
    
    def get_block(self, block_id: str) -> Optional[Dict]:
        return self.blocks.get(block_id)
    
    def get_parameter_sets(self, instance_id: str) -> List[Dict]:
        return self.parameter_sets.get(instance_id, [])
    
    def get_recollections(self, instance_id: str) -> List[Dict]:
        return self.recollections.get(instance_id, [])
