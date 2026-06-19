import base64
import json
from typing import Dict, List, Any, Optional
import time

class PayloadDecoder:
    @staticmethod
    def decode_base64(encoded: str) -> str:
        try:
            decoded = base64.b64decode(encoded).decode('utf-8')
            return decoded
        except Exception as e:
            print(f"Decode error: {e}")
            return ""
    
    @staticmethod
    def decode_json(encoded: str) -> Optional[Dict]:
        try:
            decoded = json.loads(encoded)
            return decoded
        except Exception as e:
            print(f"JSON decode error: {e}")
            return None

class PayloadEncoder:
    @staticmethod
    def encode_base64(data: str) -> str:
        try:
            encoded = base64.b64encode(data.encode('utf-8')).decode('utf-8')
            return encoded
        except Exception as e:
            print(f"Encode error: {e}")
            return ""
    
    @staticmethod
    def encode_json(data: Dict) -> str:
        try:
            encoded = json.dumps(data)
            return encoded
        except Exception as e:
            print(f"JSON encode error: {e}")
            return ""

class PayloadMachine:
    def __init__(self):
        self.decoder = PayloadDecoder()
        self.encoder = PayloadEncoder()
        self.instruction_history: List[Dict] = []
        
    async def decode_payload(self, payload: str, encoding: str = 'base64') -> Optional[str]:
        if encoding == 'base64':
            return self.decoder.decode_base64(payload)
        elif encoding == 'json':
            decoded = self.decoder.decode_json(payload)
            if decoded:
                return json.dumps(decoded)
        return None
    
    async def recode_payload(self, data: Any, target_encoding: str = 'base64') -> Optional[str]:
        if target_encoding == 'base64':
            if isinstance(data, dict):
                data_str = json.dumps(data)
            else:
                data_str = str(data)
            return self.encoder.encode_base64(data_str)
        elif target_encoding == 'json':
            if isinstance(data, dict):
                return self.encoder.encode_json(data)
        return None
    
    async def process_instruction(self, instruction: Dict) -> Dict:
        result = {
            'instruction': instruction,
            'processed_at': time.time(),
            'success': False
        }
        
        if 'payload' in instruction:
            encoding = instruction.get('encoding', 'base64')
            decoded = await self.decode_payload(instruction['payload'], encoding)
            
            if decoded:
                result['decoded_payload'] = decoded
                result['success'] = True
                
                if 'recode_to' in instruction:
                    recoded = await self.recode_payload(decoded, instruction['recode_to'])
                    result['recoded_payload'] = recoded
        
        self.instruction_history.append(result)
        return result
    
    async def process_post_instruction(self, payload: str, instruction_type: str = 'post') -> Dict:
        instruction = {
            'type': instruction_type,
            'payload': payload,
            'encoding': 'base64',
            'recode_to': 'json'
        }
        return await self.process_instruction(instruction)
    
    def get_instruction_history(self) -> List[Dict]:
        return self.instruction_history
