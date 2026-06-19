import asyncio
from typing import Dict, List, Optional, Callable
import time

class WatchTarget:
    def __init__(self, target_id: str):
        self.target_id = target_id
        self.watch_interval: float = 1.0
        self.is_watching: bool = False
        self.last_checked: Optional[float] = None
        self.check_count: int = 0
        self.alerts: List[Dict] = []
        
class RepeaterWatch:
    def __init__(self):
        self.watch_targets: Dict[str, WatchTarget] = {}
        self.watch_callbacks: Dict[str, List[Callable]] = {}
        self.is_running: bool = False
        self.watch_task: Optional[asyncio.Task] = None
        
    async def add_watch_target(self, target_id: str, watch_interval: float = 1.0) -> WatchTarget:
        target = WatchTarget(target_id)
        target.watch_interval = watch_interval
        self.watch_targets[target_id] = target
        return target
    
    async def start_watching(self, target_id: str):
        if target_id not in self.watch_targets:
            return
            
        target = self.watch_targets[target_id]
        target.is_watching = True
        
        if not self.is_running:
            self.is_running = True
            self.watch_task = asyncio.create_task(self._watch_loop())
    
    async def stop_watching(self, target_id: str):
        if target_id in self.watch_targets:
            self.watch_targets[target_id].is_watching = False
    
    async def _watch_loop(self):
        while self.is_running:
            for target_id, target in self.watch_targets.items():
                if target.is_watching:
                    await self._check_target(target_id)
            
            await asyncio.sleep(0.1)
    
    async def _check_target(self, target_id: str):
        target = self.watch_targets[target_id]
        target.last_checked = time.time()
        target.check_count += 1
        
        # Trigger callbacks
        if target_id in self.watch_callbacks:
            for callback in self.watch_callbacks[target_id]:
                try:
                    await callback(target_id)
                except:
                    pass
    
    async def register_callback(self, target_id: str, callback: Callable):
        if target_id not in self.watch_callbacks:
            self.watch_callbacks[target_id] = []
        self.watch_callbacks[target_id].append(callback)
    
    async def add_alert(self, target_id: str, alert_data: Dict):
        if target_id in self.watch_targets:
            self.watch_targets[target_id].alerts.append({
                'alert_data': alert_data,
                'timestamp': time.time()
            })
    
    async def get_watch_status(self, target_id: str) -> Optional[Dict]:
        if target_id in self.watch_targets:
            target = self.watch_targets[target_id]
            return {
                'target_id': target_id,
                'is_watching': target.is_watching,
                'last_checked': target.last_checked,
                'check_count': target.check_count,
                'alert_count': len(target.alerts)
            }
        return None
    
    async def shutdown(self):
        self.is_running = False
        if self.watch_task:
            self.watch_task.cancel()
            try:
                await self.watch_task
            except:
                pass
    
    def get_watch_target(self, target_id: str) -> Optional[WatchTarget]:
        return self.watch_targets.get(target_id)
