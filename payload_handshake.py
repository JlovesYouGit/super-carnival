import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any
import time

class PayloadHandshake:
    def __init__(self):
        self.active_handshakes: Dict[str, Dict] = {}
        self.handshake_tokens: Dict[str, str] = {}
        self.data_traversal_paths: Dict[str, List] = {}
        
    async def create_handshake(self, payload: Dict, target_endpoint: str) -> str:
        handshake_id = str(uuid.uuid4())
        token = self._generate_token(handshake_id, payload)
        
        handshake = {
            'handshake_id': handshake_id,
            'token': token,
            'payload': payload,
            'target_endpoint': target_endpoint,
            'created_at': time.time(),
            'status': 'pending'
        }
        
        self.active_handshakes[handshake_id] = handshake
        self.handshake_tokens[token] = handshake_id
        
        return handshake_id
    
    def _generate_token(self, handshake_id: str, payload: Dict) -> str:
        import hashlib
        payload_str = json.dumps(payload, sort_keys=True)
        combined = f"{handshake_id}:{payload_str}:{time.time()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    async def complete_handshake(self, handshake_id: str, response_data: Dict) -> Dict:
        if handshake_id not in self.active_handshakes:
            return {'error': 'Handshake not found'}
            
        handshake = self.active_handshakes[handshake_id]
        handshake['status'] = 'completed'
        handshake['completed_at'] = time.time()
        handshake['response_data'] = response_data
        
        return handshake
    
    async def traverse_data(self, handshake_id: str, data_path: List[str]) -> Optional[Any]:
        if handshake_id not in self.active_handshakes:
            return None
            
        handshake = self.active_handshakes[handshake_id]
        data = handshake['payload']
        
        for key in data_path:
            if isinstance(data, dict) and key in data:
                data = data[key]
            elif isinstance(data, list) and key.isdigit():
                idx = int(key)
                if idx < len(data):
                    data = data[idx]
            else:
                return None
                
        return data
    
    async def update_external_parameter(self, handshake_id: str, param_name: str, param_value: Any) -> bool:
        if handshake_id not in self.active_handshakes:
            return False
            
        handshake = self.active_handshakes[handshake_id]
        
        if 'external_parameters' not in handshake:
            handshake['external_parameters'] = {}
            
        handshake['external_parameters'][param_name] = param_value
        return True
    
    def get_handshake_status(self, handshake_id: str) -> Optional[Dict]:
        return self.active_handshakes.get(handshake_id)
