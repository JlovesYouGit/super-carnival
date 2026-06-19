import asyncio
from typing import Dict, List, Optional, Any
import time
import struct

class RawNumericalData:
    def __init__(self, data_id: str):
        self.data_id = data_id
        self.raw_bytes: bytes = b''
        self.numerical_values: List[float] = []
        self.expected_pattern: Optional[List[float]] = None
        self.captured_at: time.time = time.time()
        self.is_expected: bool = False

class RawDataCapture:
    def __init__(self):
        self.captured_data: Dict[str, RawNumericalData] = {}
        self.capture_history: List[Dict] = []
        self.pattern_expectations: Dict[str, List[float]] = {}
        
    async def capture_raw_data(self, data_id: str, raw_bytes: bytes) -> RawNumericalData:
        data = RawNumericalData(data_id)
        data.raw_bytes = raw_bytes
        data.numerical_values = self._extract_numerical_values(raw_bytes)
        
        # Check if matches expected pattern
        if data_id in self.pattern_expectations:
            expected = self.pattern_expectations[data_id]
            data.expected_pattern = expected
            data.is_expected = self._matches_expected_pattern(data.numerical_values, expected)
        
        self.captured_data[data_id] = data
        
        self.capture_history.append({
            'data_id': data_id,
            'byte_count': len(raw_bytes),
            'numerical_count': len(data.numerical_values),
            'is_expected': data.is_expected,
            'captured_at': time.time()
        })
        
        return data
    
    def _extract_numerical_values(self, raw_bytes: bytes) -> List[float]:
        values = []
        
        # Try to extract as floats (4 bytes each)
        for i in range(0, len(raw_bytes) - 3, 4):
            try:
                value = struct.unpack('f', raw_bytes[i:i+4])[0]
                values.append(value)
            except:
                pass
                
        return values
    
    def _matches_expected_pattern(self, actual: List[float], expected: List[float]) -> bool:
        if len(actual) != len(expected):
            return False
            
        for a, e in zip(actual, expected):
            if abs(a - e) > 0.001:
                return False
                
        return True
    
    async def set_expected_pattern(self, data_id: str, pattern: List[float]):
        self.pattern_expectations[data_id] = pattern
        
    async def machine_catch_raw_data(self, data_id: str, raw_bytes: bytes) -> Dict:
        captured = await self.capture_raw_data(data_id, raw_bytes)
        
        return {
            'data_id': data_id,
            'captured': True,
            'is_expected': captured.is_expected,
            'numerical_values': captured.numerical_values[:10],
            'total_values': len(captured.numerical_values),
            'timestamp': time.time()
        }
    
    async def compare_to_expected(self, data_id: str) -> Optional[Dict]:
        if data_id not in self.captured_data:
            return None
            
        data = self.captured_data[data_id]
        
        return {
            'data_id': data_id,
            'is_expected': data.is_expected,
            'expected_pattern': data.expected_pattern,
            'actual_pattern': data.numerical_values[:10] if data.numerical_values else [],
            'match_count': sum(1 for a, e in zip(data.numerical_values, data.expected_pattern) if abs(a - e) < 0.001) if data.expected_pattern else 0
        }
    
    def get_captured_data(self, data_id: str) -> Optional[RawNumericalData]:
        return self.captured_data.get(data_id)
    
    def get_capture_history(self) -> List[Dict]:
        return self.capture_history.copy()
