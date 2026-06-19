import asyncio
import json
from typing import Dict, List, Optional
from aiohttp import ClientSession, ClientResponse
import time

class PostRequestHandler:
    def __init__(self):
        self.saved_requests: List[Dict] = []
        self.redirect_map: Dict[str, str] = {}
        self.post_redirects: List[Dict] = []
        
    async def save_redirect_post(self, request_data: Dict) -> Dict:
        saved = {
            'original_request': request_data,
            'timestamp': time.time(),
            'saved': True
        }
        self.saved_requests.append(saved)
        return saved
    
    async def redirect_post_request(self, original_url: str, redirect_url: str, 
                                    payload: Dict) -> Dict:
        redirect_info = {
            'original_url': original_url,
            'redirect_url': redirect_url,
            'payload': payload,
            'timestamp': time.time()
        }
        self.redirect_map[original_url] = redirect_url
        self.post_redirects.append(redirect_info)
        return redirect_info
    
    async def handle_post_request(self, url: str, payload: Dict, 
                                  redirect_to: Optional[str] = None) -> Dict:
        result = {
            'url': url,
            'payload': payload,
            'method': 'POST',
            'timestamp': time.time()
        }
        
        if redirect_to:
            await self.redirect_post_request(url, redirect_to, payload)
            result['redirected_to'] = redirect_to
        
        await self.save_redirect_post(result)
        return result
    
    async def get_all_saved_posts(self) -> List[Dict]:
        return self.saved_requests
    
    async def get_redirect_map(self) -> Dict[str, str]:
        return self.redirect_map
