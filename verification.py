import random
from typing import Dict, Optional
import time

class VerificationCodeGenerator:
    def __init__(self, code_length: int = 5):
        self.code_length = code_length
        self.generated_codes: Dict[str, str] = {}
        
    def generate_code(self) -> str:
        code = ''.join([str(random.randint(0, 9)) for _ in range(self.code_length)])
        return code
    
    def generate_for_host(self, host: str) -> str:
        code = self.generate_code()
        self.generated_codes[host] = code
        return code
    
    def verify_code(self, host: str, code: str) -> bool:
        return self.generated_codes.get(host) == code
    
    def get_code_for_host(self, host: str) -> Optional[str]:
        return self.generated_codes.get(host)
    
    def regenerate_for_host(self, host: str) -> str:
        return self.generate_for_host(host)
    
    def remove_host(self, host: str):
        if host in self.generated_codes:
            del self.generated_codes[host]

class ExternalHostVerifier:
    def __init__(self, code_length: int = 5):
        self.generator = VerificationCodeGenerator(code_length)
        self.verified_hosts: Dict[str, Dict] = {}
        
    async def register_host(self, host: str) -> Dict:
        code = self.generator.generate_for_host(host)
        verification_data = {
            'host': host,
            'verification_code': code,
            'timestamp': time.time(),
            'verified': False
        }
        self.verified_hosts[host] = verification_data
        return verification_data
    
    async def verify_host(self, host: str, code: str) -> bool:
        if self.generator.verify_code(host, code):
            self.verified_hosts[host]['verified'] = True
            self.verified_hosts[host]['verified_at'] = time.time()
            return True
        return False
    
    async def is_verified(self, host: str) -> bool:
        return self.verified_hosts.get(host, {}).get('verified', False)
    
    async def get_verification_data(self, host: str) -> Optional[Dict]:
        return self.verified_hosts.get(host)
    
    async def regenerate_code(self, host: str) -> str:
        new_code = self.generator.regenerate_for_host(host)
        self.verified_hosts[host]['verification_code'] = new_code
        self.verified_hosts[host]['verified'] = False
        return new_code
