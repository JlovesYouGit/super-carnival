import asyncio
import json
from typing import Dict, List, Optional
from aiohttp import ClientSession
import time

class ExternalHTTPSLogger:
    def __init__(self, log_endpoint: str):
        self.endpoint_url = log_endpoint
        self.session: Optional[ClientSession] = None
        self.log_buffer: List[Dict] = []
        self.buffer_size = 100
        
    async def initialize(self):
        connector = self.session.connector if self.session else None
        self.session = ClientSession(connector=connector)
        
    async def close(self):
        if self.session:
            await self.session.close()
            
    async def log_endpoint(self, endpoint_data: Dict) -> bool:
        log_entry = {
            'endpoint': endpoint_data,
            'timestamp': time.time(),
            'source': 'external_network'
        }
        
        self.log_buffer.append(log_entry)
        
        if len(self.log_buffer) >= self.buffer_size:
            await self.flush_buffer()
            
        return True
    
    async def flush_buffer(self) -> bool:
        if not self.log_buffer:
            return False
            
        try:
            payload = {
                'logs': self.log_buffer,
                'count': len(self.log_buffer),
                'flushed_at': time.time()
            }
            
            headers = {'Content-Type': 'application/json'}
            
            async with self.session.post(
                self.endpoint_url,
                json=payload,
                headers=headers,
                ssl=False
            ) as response:
                if response.status == 200:
                    self.log_buffer.clear()
                    return True
                    
        except Exception as e:
            print(f"Logging error: {e}")
            
        return False
    
    async def log_external_host(self, host: str, verification_code: str, 
                                endpoint: str) -> Dict:
        endpoint_data = {
            'host': host,
            'verification_code': verification_code,
            'endpoint': endpoint,
            'logged_via_https': True
        }
        
        await self.log_endpoint(endpoint_data)
        return endpoint_data
    
    async def get_buffer_status(self) -> Dict:
        return {
            'buffer_size': len(self.log_buffer),
            'max_buffer_size': self.buffer_size,
            'needs_flush': len(self.log_buffer) >= self.buffer_size
        }
