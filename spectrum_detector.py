import asyncio
from typing import Dict, List, Optional, Tuple
import time
import numpy as np

class SpectrumSignal:
    def __init__(self, signal_id: str):
        self.signal_id = signal_id
        self.locations: List[Dict] = []
        self.raw_data: bytes = b''
        self.digital_spectrum: List[float] = []
        self.detected_at: Optional[float] = None
        self.awaiting_entry: bool = False

class MultiLocationSpectrumDetector:
    def __init__(self):
        self.detected_signals: Dict[str, SpectrumSignal] = {}
        self.active_sessions: Dict[str, List[str]] = {}
        self.detection_history: List[Dict] = []
        
    async def detect_spectrum_signal(self, signal_id: str, raw_data: bytes, locations: List[Dict]) -> SpectrumSignal:
        signal = SpectrumSignal(signal_id)
        signal.raw_data = raw_data
        signal.locations = locations
        signal.digital_spectrum = self._analyze_digital_spectrum(raw_data)
        signal.detected_at = time.time()
        
        self.detected_signals[signal_id] = signal
        
        self.detection_history.append({
            'signal_id': signal_id,
            'location_count': len(locations),
            'spectrum_length': len(signal.digital_spectrum),
            'detected_at': time.time()
        })
        
        return signal
    
    def _analyze_digital_spectrum(self, raw_data: bytes) -> List[float]:
        # Convert raw bytes to digital spectrum
        spectrum = []
        for byte in raw_data:
            spectrum.append(byte / 255.0)
        return spectrum
    
    async def permit_entry_from_signal(self, signal_id: str, session_id: str) -> bool:
        if signal_id not in self.detected_signals:
            return False
            
        signal = self.detected_signals[signal_id]
        signal.awaiting_entry = True
        
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = []
        self.active_sessions[session_id].append(signal_id)
        
        return True
    
    async def check_awaiting_signals(self, session_id: str) -> List[str]:
        if session_id not in self.active_sessions:
            return []
            
        awaiting = []
        for signal_id in self.active_sessions[session_id]:
            if signal_id in self.detected_signals:
                if self.detected_signals[signal_id].awaiting_entry:
                    awaiting.append(signal_id)
                    
        return awaiting
    
    async def get_multi_location_spectrum(self, signal_id: str) -> Optional[Dict]:
        if signal_id not in self.detected_signals:
            return None
            
        signal = self.detected_signals[signal_id]
        
        return {
            'signal_id': signal_id,
            'locations': signal.locations,
            'spectrum_data': signal.digital_spectrum[:100],
            'total_spectrum_points': len(signal.digital_spectrum),
            'detected_at': signal.detected_at
        }
    
    async def process_raw_digital_data(self, raw_data: bytes) -> List[SpectrumSignal]:
        signals = []
        
        # Split raw data into potential signals
        chunk_size = 1024
        for i in range(0, len(raw_data), chunk_size):
            chunk = raw_data[i:i+chunk_size]
            signal_id = f"spectrum_{i}_{int(time.time())}"
            
            locations = [
                {'location_id': f"loc_{i}", 'offset': i, 'size': len(chunk)},
                {'location_id': f"loc_{i+1}", 'offset': i + chunk_size, 'size': 0}
            ]
            
            signal = await self.detect_spectrum_signal(signal_id, chunk, locations)
            signals.append(signal)
            
        return signals
    
    def get_detected_signal(self, signal_id: str) -> Optional[SpectrumSignal]:
        return self.detected_signals.get(signal_id)
    
    def get_active_sessions(self) -> Dict[str, List[str]]:
        return self.active_sessions.copy()
