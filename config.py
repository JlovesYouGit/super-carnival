import os
from dotenv import load_dotenv
from typing import Optional

class Config:
    def __init__(self):
        load_dotenv()
        self.dummy_http_endpoint = os.getenv('DUMMY_HTTP_ENDPOINT', 'https://www.tiktok.com/')
        self.external_log_endpoint = os.getenv('EXTERNAL_LOG_ENDPOINT', 'https://www.tiktok.com/api/log')
        self.verification_code_length = int(os.getenv('VERIFICATION_CODE_LENGTH', '5'))
        self.max_connections = int(os.getenv('MAX_CONNECTIONS', '100'))
        self.connection_timeout = int(os.getenv('CONNECTION_TIMEOUT', '30'))
        
        # Virtual Probe X credentials
        self.virtual_probe_api_endpoint = os.getenv('VIRTUAL_PROBE_API_ENDPOINT', 'http://127.0.0.1:8000')
        self.virtual_probe_auth_token = os.getenv('VIRTUAL_PROBE_AUTH_TOKEN', None)
        self.virtual_probe_admin_token = os.getenv('VIRTUAL_PROBE_ADMIN_TOKEN', None)
        self.virtual_probe_target = os.getenv('VIRTUAL_PROBE_TARGET', 'https://www.tiktok.com/')
        
    def get_dummy_http_endpoint(self) -> str:
        return self.dummy_http_endpoint
    
    def get_external_log_endpoint(self) -> str:
        return self.external_log_endpoint
    
    def get_verification_code_length(self) -> int:
        return self.verification_code_length
    
    def get_max_connections(self) -> int:
        return self.max_connections
    
    def get_connection_timeout(self) -> int:
        return self.connection_timeout
    
    def set_dummy_http_endpoint(self, endpoint: str):
        self.dummy_http_endpoint = endpoint
        os.environ['DUMMY_HTTP_ENDPOINT'] = endpoint
    
    def get_virtual_probe_api_endpoint(self) -> str:
        return self.virtual_probe_api_endpoint
    
    def get_virtual_probe_auth_token(self) -> Optional[str]:
        return self.virtual_probe_auth_token
    
    def get_virtual_probe_admin_token(self) -> Optional[str]:
        return self.virtual_probe_admin_token
    
    def get_virtual_probe_target(self) -> str:
        return self.virtual_probe_target
