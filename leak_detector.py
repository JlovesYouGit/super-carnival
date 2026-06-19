import asyncio
from typing import Dict, Optional, Callable
import time

class HandshakeRequestListener:
    def __init__(self):
        self.active_handshakes: Dict[str, Dict] = {}
        self.handshake_callbacks: Dict[str, Callable] = {}
        
    async def register_handshake(self, connection_id: str, callback: Callable = None):
        self.active_handshakes[connection_id] = {
            'status': 'pending',
            'timestamp': time.time()
        }
        if callback:
            self.handshake_callbacks[connection_id] = callback
            
    async def complete_handshake(self, connection_id: str):
        if connection_id in self.active_handshakes:
            self.active_handshakes[connection_id]['status'] = 'completed'
            self.active_handshakes[connection_id]['completed_at'] = time.time()
            
            if connection_id in self.handshake_callbacks:
                await self.handshake_callbacks[connection_id](connection_id)
                
    async def get_handshake_status(self, connection_id: str) -> Optional[str]:
        if connection_id in self.active_handshakes:
            return self.active_handshakes[connection_id]['status']
        return None

class ExternalLeakPingLock:
    def __init__(self):
        self.leaked_connections: Dict[str, Dict] = {}
        self.locked_connections: Dict[str, bool] = {}
        self.handshake_listener = HandshakeRequestListener()
        self.ping_threshold = 10
        
    async def detect_leak(self, connection_id: str, ping_count: int) -> bool:
        if ping_count > self.ping_threshold:
            self.leaked_connections[connection_id] = {
                'ping_count': ping_count,
                'detected_at': time.time(),
                'leaked': True
            }
            return True
        return False
    
    async def lock_connection(self, connection_id: str):
        self.locked_connections[connection_id] = True
        await self.handshake_listener.register_handshake(connection_id)
        
    async def unlock_connection(self, connection_id: str):
        if connection_id in self.locked_connections:
            self.locked_connections[connection_id] = False
            await self.handshake_listener.complete_handshake(connection_id)
            
    async def is_locked(self, connection_id: str) -> bool:
        return self.locked_connections.get(connection_id, False)
    
    async def handle_ping_leak(self, connection_id: str, ping_count: int):
        is_leaked = await self.detect_leak(connection_id, ping_count)
        if is_leaked:
            await self.lock_connection(connection_id)
            return True
        return False
    
    async def process_handshake_request(self, connection_id: str):
        await self.handshake_listener.register_handshake(connection_id)
        await asyncio.sleep(0.1)
        await self.handshake_listener.complete_handshake(connection_id)
