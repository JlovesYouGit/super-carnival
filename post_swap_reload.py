import asyncio
from typing import Dict, Optional, Callable
from aiohttp import ClientSession
import time

class PostSwapReload:
    def __init__(self):
        self.active_swaps: Dict[str, Dict] = {}
        self.swap_attempts: Dict[str, int] = {}
        self.max_attempts = 10
        self.accepted_codes = ['0', '00', '000', '0000', '00000']
        
    async def swap_request(self, request_id: str, original_url: str, 
                          new_url: str, payload: Dict) -> Dict:
        swap_info = {
            'request_id': request_id,
            'original_url': original_url,
            'new_url': new_url,
            'payload': payload,
            'swapped_at': time.time(),
            'status': 'swapped'
        }
        self.active_swaps[request_id] = swap_info
        return swap_info
    
    async def reload_request(self, request_id: str, url: str, 
                            payload: Dict) -> Optional[Dict]:
        if request_id not in self.active_swaps:
            return None
            
        reload_info = {
            'request_id': request_id,
            'url': url,
            'payload': payload,
            'reloaded_at': time.time(),
            'status': 'reloaded'
        }
        
        if request_id not in self.swap_attempts:
            self.swap_attempts[request_id] = 0
        self.swap_attempts[request_id] += 1
        
        return reload_info
    
    async def check_accept(self, response_code: str) -> bool:
        return response_code in self.accepted_codes
    
    async def process_until_accept(self, request_id: str, url: str, 
                                   payload: Dict, swap_callback: Callable) -> Dict:
        attempts = 0
        result = {
            'request_id': request_id,
            'accepted': False,
            'attempts': 0,
            'final_code': None
        }
        
        while attempts < self.max_attempts:
            attempts += 1
            result['attempts'] = attempts
            
            swapped = await swap_callback(request_id, url, payload)
            response_code = str(swapped.get('response_code', ''))
            
            if await self.check_accept(response_code):
                result['accepted'] = True
                result['final_code'] = response_code
                result['completed_at'] = time.time()
                break
                
            await asyncio.sleep(0.1)
            
        return result
    
    async def handle_post_swap(self, request_id: str, original_url: str, 
                             new_url: str, payload: Dict) -> Dict:
        await self.swap_request(request_id, original_url, new_url, payload)
        
        async def swap_callback(rid, url, pay):
            return await self.reload_request(rid, url, pay)
        
        result = await self.process_until_accept(request_id, new_url, payload, swap_callback)
        return result
    
    async def is_permitted(self, code: str) -> bool:
        return await self.check_accept(code)
    
    def get_swap_status(self, request_id: str) -> Optional[Dict]:
        return self.active_swaps.get(request_id)
