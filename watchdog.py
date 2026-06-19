import asyncio
import time
from typing import Dict, Optional, Callable
import random

class WatchdogUpdate:
    def __init__(self):
        self.detected_updates: Dict[str, Dict] = {}
        self.update_callbacks: Dict[str, Callable] = {}
        self.last_check_time: float = time.time()
        self.check_interval: float = 1.0
        
    async def check_for_updates(self, system_state: Dict) -> Dict:
        current_time = time.time()
        update_detected = False
        update_info = {
            'detected': False,
            'timestamp': current_time,
            'changes': []
        }
        
        if 'version' in system_state:
            if 'last_version' not in self.detected_updates:
                self.detected_updates['last_version'] = system_state['version']
            elif self.detected_updates['last_version'] != system_state['version']:
                update_detected = True
                update_info['changes'].append({
                    'type': 'version_change',
                    'old': self.detected_updates['last_version'],
                    'new': system_state['version']
                })
                self.detected_updates['last_version'] = system_state['version']
        
        if 'config_hash' in system_state:
            if 'last_config_hash' not in self.detected_updates:
                self.detected_updates['last_config_hash'] = system_state['config_hash']
            elif self.detected_updates['last_config_hash'] != system_state['config_hash']:
                update_detected = True
                update_info['changes'].append({
                    'type': 'config_change',
                    'old_hash': self.detected_updates['last_config_hash'],
                    'new_hash': system_state['config_hash']
                })
                self.detected_updates['last_config_hash'] = system_state['config_hash']
        
        if update_detected:
            update_info['detected'] = True
            await self.trigger_update_callbacks(update_info)
        
        self.last_check_time = current_time
        return update_info
    
    async def register_callback(self, callback_id: str, callback: Callable):
        self.update_callbacks[callback_id] = callback
    
    async def trigger_update_callbacks(self, update_info: Dict):
        for callback_id, callback in self.update_callbacks.items():
            try:
                await callback(update_info)
            except Exception as e:
                print(f"Callback error for {callback_id}: {e}")
    
    async def start_monitoring(self, system_state_getter: Callable):
        while True:
            system_state = await system_state_getter()
            await self.check_for_updates(system_state)
            await asyncio.sleep(self.check_interval)
