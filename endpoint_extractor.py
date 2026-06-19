import asyncio
import json
import hashlib
from typing import Dict, List, Optional, Any
from aiohttp import ClientSession
import time
import os

class EndpointDataStructureExtractor:
    def __init__(self):
        self.extracted_structures: Dict[str, Dict] = {}
        self.sequence_cache: Dict[str, List] = {}
        self.internal_dir = "E:/DOWNLOADs/derived-spacial"
        
    async def extract_from_endpoint(self, endpoint_url: str) -> Optional[Dict]:
        try:
            async with ClientSession() as session:
                async with session.get(endpoint_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        structure = self.analyze_structure(data)
                        self.extracted_structures[endpoint_url] = structure
                        return structure
        except Exception as e:
            print(f"Extraction error: {e}")
        return None
    
    def analyze_structure(self, data: Any) -> Dict:
        structure = {
            'type': type(data).__name__,
            'hash': hashlib.sha256(str(data).encode()).hexdigest()[:16],
            'timestamp': time.time()
        }
        
        if isinstance(data, dict):
            structure['keys'] = list(data.keys())
            structure['nested_structure'] = {k: self.analyze_structure(v) for k, v in data.items()}
        elif isinstance(data, list):
            structure['length'] = len(data)
            if data:
                structure['item_structure'] = self.analyze_structure(data[0])
        elif isinstance(data, (int, float, str, bool)):
            structure['value'] = data
            
        return structure
    
    async def derive_sequence(self, structure: Dict) -> List:
        if structure is None:
            return []
        sequence = []
        self._flatten_structure(structure, sequence)
        return sequence
    
    def _flatten_structure(self, structure: Dict, sequence: List):
        if structure is None:
            return
        if 'keys' in structure:
            sequence.extend(structure['keys'])
        if 'nested_structure' in structure:
            for key, nested in structure['nested_structure'].items():
                sequence.append(key)
                self._flatten_structure(nested, sequence)
        if 'value' in structure:
            sequence.append(structure['value'])
            
    async def scan_internal_dir(self) -> Dict[str, Any]:
        dir_info = {
            'path': self.internal_dir,
            'exists': os.path.exists(self.internal_dir),
            'files': [],
            'code_execution_points': []
        }
        
        if dir_info['exists']:
            for root, dirs, files in os.walk(self.internal_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        dir_info['files'].append(file_path)
                        dir_info['code_execution_points'].append({
                            'file': file_path,
                            'hash': self._file_hash(file_path)
                        })
                        
        return dir_info
    
    def _file_hash(self, file_path: str) -> str:
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    async def update_endpoint_based_on_internal(self, endpoint_url: str) -> Dict:
        dir_info = await self.scan_internal_dir()
        structure = await self.extract_from_endpoint(endpoint_url)
        sequence = await self.derive_sequence(structure) if structure else []
        
        update_info = {
            'endpoint': endpoint_url,
            'internal_dir_info': dir_info,
            'extracted_structure': structure,
            'derived_sequence': sequence,
            'timestamp': time.time()
        }
        
        return update_info
