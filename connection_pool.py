import asyncio
from typing import Dict, List, Optional
from aiohttp import ClientSession, TCPConnector
import time

class Connection:
    def __init__(self, connection_id: str, endpoint: str):
        self.connection_id = connection_id
        self.endpoint = endpoint
        self.session: Optional[ClientSession] = None
        self.last_used = time.time()
        self.is_active = False
        
    async def connect(self):
        connector = TCPConnector(limit=100)
        self.session = ClientSession(connector=connector)
        self.is_active = True
        self.last_used = time.time()
        
    async def close(self):
        if self.session:
            await self.session.close()
            self.is_active = False
            
    async def keep_alive(self):
        if self.is_active and self.session:
            self.last_used = time.time()

class ConnectionPool:
    def __init__(self, max_connections: int = 100):
        self.connections: Dict[str, Connection] = {}
        self.max_connections = max_connections
        self.current_load = 0
        self.swap_threshold = 0.8
        
    async def add_connection(self, connection_id: str, endpoint: str) -> Connection:
        if len(self.connections) >= self.max_connections:
            await self.swap_connection()
            
        connection = Connection(connection_id, endpoint)
        await connection.connect()
        self.connections[connection_id] = connection
        self.current_load = len(self.connections) / self.max_connections
        return connection
        
    async def get_connection(self, connection_id: str) -> Optional[Connection]:
        if connection_id in self.connections:
            await self.connections[connection_id].keep_alive()
            return self.connections[connection_id]
        return None
        
    async def swap_connection(self):
        if not self.connections:
            return
            
        oldest_id = min(self.connections.keys(), 
                       key=lambda k: self.connections[k].last_used)
        await self.remove_connection(oldest_id)
        
    async def remove_connection(self, connection_id: str):
        if connection_id in self.connections:
            await self.connections[connection_id].close()
            del self.connections[connection_id]
            self.current_load = len(self.connections) / self.max_connections
            
    async def auto_swap(self):
        while self.current_load > self.swap_threshold:
            await self.swap_connection()
            
    async def keep_connections_alive(self):
        tasks = []
        for connection in self.connections.values():
            tasks.append(connection.keep_alive())
        await asyncio.gather(*tasks)
        
    async def get_active_connections(self) -> List[str]:
        return [cid for cid, conn in self.connections.items() if conn.is_active]
        
    async def cleanup_idle(self, idle_threshold: float = 300):
        current_time = time.time()
        to_remove = []
        
        for cid, conn in self.connections.items():
            if current_time - conn.last_used > idle_threshold:
                to_remove.append(cid)
                
        for cid in to_remove:
            await self.remove_connection(cid)
