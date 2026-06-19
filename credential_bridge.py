import asyncio
import json
import os
import sys
from typing import Dict, Optional, Any
import requests

class CredentialBridge:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.api_base = f"http://{self.config['api_server']['host']}:{self.config['api_server']['port']}"
        self.auth_token = None
        self.admin_token = None
        
    def load_config(self) -> Dict:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        return {
            "target": "https://www.tiktok.com/",
            "api_server": {
                "host": "127.0.0.1",
                "port": 8000,
                "admin_password": "admin"
            },
            "xspace_scanner": {
                "target_host": "www.tiktok.com",
                "ports": [80, 443, 8080, 8443, 3000, 5000, 8000, 9000],
                "paths": ["/", "/mirror", "/.well-known/mirror", "/status", "/health", "/api", "/graphql", "/swagger", "/openapi.json"],
                "scan_interval": 300
            },
            "credentials": {
                "main_system_endpoint": "https://www.tiktok.com/",
                "auth_token": None,
                "admin_token": None
            },
            "integration": {
                "main_system_path": "../",
                "enable_bridge": True,
                "auto_scan_on_startup": True
            }
        }
    
    async def authenticate(self) -> bool:
        try:
            response = requests.post(
                f"{self.api_base}/auth/token",
                json={"password": self.config['api_server']['admin_password']},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                self.admin_token = data.get('token') if data.get('role') == 'admin' else None
                return True
        except Exception as e:
            print(f"Authentication error: {e}")
        return False
    
    async def scan_target(self, target: str = None) -> Dict:
        if not self.auth_token:
            await self.authenticate()
        
        scan_target = target or self.config['xspace_scanner']['target_host']
        
        try:
            response = requests.post(
                f"{self.api_base}/xspace/scan",
                json={"target": scan_target},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                }
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Scan error: {e}")
        return {}
    
    async def get_mirrors(self) -> Dict:
        if not self.auth_token:
            await self.authenticate()
        
        try:
            response = requests.get(
                f"{self.api_base}/xspace",
                headers={
                    "Authorization": f"Bearer {self.auth_token}"
                }
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Get mirrors error: {e}")
        return {}
    
    async def retrieve_mirrors_by_hash(self, content_hash: str, threshold: float = 0.8) -> Dict:
        if not self.auth_token:
            await self.authenticate()
        
        try:
            response = requests.post(
                f"{self.api_base}/xspace/retrieve",
                json={"content_hash": content_hash, "threshold": threshold},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                }
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Retrieve mirrors error: {e}")
        return {}
    
    async def get_credentials_for_main(self) -> Dict:
        credentials = {
            "target": self.config['target'],
            "api_endpoint": self.api_base,
            "auth_token": self.auth_token,
            "admin_token": self.admin_token,
            "scan_results": await self.scan_target(),
            "mirrors": await self.get_mirrors()
        }
        return credentials
    
    def save_credentials_to_main(self, credentials: Dict):
        main_config_path = os.path.join(self.config['integration']['main_system_path'], '.env')
        
        with open(main_config_path, 'a') as f:
            f.write(f"\n# Virtual Probe X Credentials\n")
            f.write(f"VIRTUAL_PROBE_API_ENDPOINT={credentials['api_endpoint']}\n")
            f.write(f"VIRTUAL_PROBE_AUTH_TOKEN={credentials['auth_token']}\n")
            f.write(f"VIRTUAL_PROBE_ADMIN_TOKEN={credentials['admin_token']}\n")
            f.write(f"VIRTUAL_PROBE_TARGET={credentials['target']}\n")
    
    async def initialize_bridge(self) -> bool:
        if not await self.authenticate():
            print("Failed to authenticate with virtual probe API")
            return False
        
        if self.config['integration']['auto_scan_on_startup']:
            await self.scan_target()
        
        credentials = await self.get_credentials_for_main()
        self.save_credentials_to_main(credentials)
        
        return True

async def main():
    bridge = CredentialBridge()
    success = await bridge.initialize_bridge()
    
    if success:
        print("Virtual Probe X bridge initialized successfully")
        print(f"API Endpoint: {bridge.api_base}")
        print(f"Target: {bridge.config['target']}")
        print(f"Auth Token: {bridge.auth_token[:20]}..." if bridge.auth_token else "No auth token")
    else:
        print("Failed to initialize Virtual Probe X bridge")

if __name__ == "__main__":
    asyncio.run(main())
