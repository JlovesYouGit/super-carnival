import asyncio
import time
from typing import Dict, Optional, List
import statistics

class PayloadTravelTime:
    def __init__(self):
        self.travel_times: List[float] = []
        self.detected_traffic_times: List[float] = []
        self.optimization_factor: float = 1.0
        
    async def record_payload_travel(self, payload_id: str, travel_time: float) -> Dict:
        self.travel_times.append(travel_time)
        return {
            'payload_id': payload_id,
            'travel_time': travel_time,
            'timestamp': time.time()
        }
    
    async def record_detected_traffic(self, traffic_id: str, travel_time: float) -> Dict:
        self.detected_traffic_times.append(travel_time)
        return {
            'traffic_id': traffic_id,
            'travel_time': travel_time,
            'timestamp': time.time()
        }
    
    async def get_average_payload_time(self) -> Optional[float]:
        if not self.travel_times:
            return None
        return statistics.mean(self.travel_times)
    
    async def get_average_traffic_time(self) -> Optional[float]:
        if not self.detected_traffic_times:
            return None
        return statistics.mean(self.detected_traffic_times)
    
    async def is_faster_than_traffic(self) -> bool:
        payload_avg = await self.get_average_payload_time()
        traffic_avg = await self.get_average_traffic_time()
        
        if payload_avg is None or traffic_avg is None:
            return False
        
        return payload_avg < traffic_avg
    
    async def optimize_velocity(self) -> float:
        payload_avg = await self.get_average_payload_time()
        traffic_avg = await self.get_average_traffic_time()
        
        if payload_avg is None or traffic_avg is None:
            return 1.0
        
        if payload_avg >= traffic_avg:
            self.optimization_factor = traffic_avg / payload_avg * 0.9
        else:
            self.optimization_factor = 1.0
        
        return self.optimization_factor
    
    async def get_optimized_travel_time(self, base_time: float) -> float:
        await self.optimize_velocity()
        return base_time * self.optimization_factor
    
    def get_optimization_factor(self) -> float:
        return self.optimization_factor
