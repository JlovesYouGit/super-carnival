import asyncio
import json
import hashlib
from typing import Dict, List, Optional
import time
import threading

class CoreLock:
    def __init__(self, lock_id: str):
        self.lock_id = lock_id
        self.lock = threading.Lock()
        self.locked = False
        self.locked_at = None
        
    def acquire(self):
        self.lock.acquire()
        self.locked = True
        self.locked_at = time.time()
        
    def release(self):
        self.lock.release()
        self.locked = False
        self.locked_at = None
        
    def is_locked(self) -> bool:
        return self.locked

class IsolatedJSONLock:
    def __init__(self, filename: str = "isolated_persona_categories.json"):
        self.filename = filename
        self.core_locks: Dict[str, CoreLock] = {}
        self.persona_categories: Dict[str, Dict] = {}
        self.model_weights: Dict[str, Dict] = {}
        self.load_data()
        
    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.persona_categories = data.get('persona_categories', {})
                self.model_weights = data.get('model_weights', {})
        except:
            pass
    
    def save_data(self):
        try:
            data = {
                'persona_categories': self.persona_categories,
                'model_weights': self.model_weights,
                'saved_at': time.time()
            }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Save error: {e}")
    
    def get_core_lock(self, category_id: str) -> CoreLock:
        if category_id not in self.core_locks:
            self.core_locks[category_id] = CoreLock(category_id)
        return self.core_locks[category_id]
    
    async def lock_category(self, category_id: str):
        lock = self.get_core_lock(category_id)
        lock.acquire()
        
    async def unlock_category(self, category_id: str):
        lock = self.get_core_lock(category_id)
        lock.release()
    
    async def add_persona_category(self, category_id: str, category_data: Dict):
        await self.lock_category(category_id)
        try:
            self.persona_categories[category_id] = category_data
            self.save_data()
        finally:
            await self.unlock_category(category_id)
    
    async def lock_model_weights(self, category_id: str, weights: Dict):
        await self.lock_category(category_id)
        try:
            self.model_weights[category_id] = {
                'weights': weights,
                'locked': True,
                'locked_at': time.time()
            }
            self.save_data()
        finally:
            await self.unlock_category(category_id)
    
    def is_category_locked(self, category_id: str) -> bool:
        if category_id in self.core_locks:
            return self.core_locks[category_id].is_locked()
        return False
    
    def get_persona_category(self, category_id: str) -> Optional[Dict]:
        return self.persona_categories.get(category_id)
    
    def get_model_weights(self, category_id: str) -> Optional[Dict]:
        return self.model_weights.get(category_id)
