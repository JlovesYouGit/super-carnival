import asyncio
from typing import Dict, List, Optional, Set
import time

class PatternTrend:
    def __init__(self, trend_id: str):
        self.trend_id = trend_id
        self.pattern_data: List = []
        self.exhausted: bool = False
        self.exhausted_at: Optional[float] = None
        self.trend_strength: float = 0.0
        self.created_at = time.time()
        
    def to_dict(self) -> Dict:
        return {
            'trend_id': self.trend_id,
            'pattern_data': self.pattern_data,
            'exhausted': self.exhausted,
            'exhausted_at': self.exhausted_at,
            'trend_strength': self.trend_strength,
            'created_at': self.created_at
        }

class PatternTrendScanner:
    def __init__(self):
        self.exhausted_trends: Dict[str, PatternTrend] = {}
        self.unexhausted_trends: Dict[str, PatternTrend] = {}
        self.scan_history: List[Dict] = {}
        
    async def scan_pattern(self, trend_id: str, pattern_data: List) -> PatternTrend:
        trend = PatternTrend(trend_id)
        trend.pattern_data = pattern_data.copy()
        
        is_exhausted = await self._check_exhaustion(pattern_data)
        trend.exhausted = is_exhausted
        
        if is_exhausted:
            trend.exhausted_at = time.time()
            self.exhausted_trends[trend_id] = trend
        else:
            self.unexhausted_trends[trend_id] = trend
            
        trend.trend_strength = await self._calculate_trend_strength(pattern_data)
        
        return trend
    
    async def _check_exhaustion(self, pattern_data: List) -> bool:
        if not pattern_data:
            return True
            
        unique_values = set(pattern_data)
        exhaustion_ratio = len(unique_values) / len(pattern_data) if pattern_data else 0
        
        return exhaustion_ratio < 0.3
    
    async def _calculate_trend_strength(self, pattern_data: List) -> float:
        if not pattern_data:
            return 0.0
            
        if len(pattern_data) < 2:
            return 0.0
            
        strength = 0.0
        for i in range(len(pattern_data) - 1):
            if isinstance(pattern_data[i], (int, float)) and isinstance(pattern_data[i+1], (int, float)):
                change = abs(pattern_data[i+1] - pattern_data[i])
                strength += change
                
        return strength / len(pattern_data)
    
    async def go_through_all_trends(self) -> Dict:
        all_trends = {}
        
        for trend_id, trend in self.exhausted_trends.items():
            all_trends[f"exhausted_{trend_id}"] = trend.to_dict()
            
        for trend_id, trend in self.unexhausted_trends.items():
            all_trends[f"unexhausted_{trend_id}"] = trend.to_dict()
            
        scan_result = {
            'total_trends': len(all_trends),
            'exhausted_count': len(self.exhausted_trends),
            'unexhausted_count': len(self.unexhausted_trends),
            'trends': all_trends,
            'scanned_at': time.time()
        }
        
        self.scan_history[time.time()] = scan_result
        return scan_result
    
    async def reclassify_trend(self, trend_id: str) -> bool:
        if trend_id in self.exhausted_trends:
            trend = self.exhausted_trends[trend_id]
            del self.exhausted_trends[trend_id]
            self.unexhausted_trends[trend_id] = trend
            trend.exhausted = False
            trend.exhausted_at = None
            return True
            
        elif trend_id in self.unexhausted_trends:
            trend = self.unexhausted_trends[trend_id]
            is_exhausted = await self._check_exhaustion(trend.pattern_data)
            
            if is_exhausted:
                del self.unexhausted_trends[trend_id]
                self.exhausted_trends[trend_id] = trend
                trend.exhausted = True
                trend.exhausted_at = time.time()
                return True
                
        return False
    
    def get_exhausted_trends(self) -> Dict[str, PatternTrend]:
        return self.exhausted_trends
    
    def get_unexhausted_trends(self) -> Dict[str, PatternTrend]:
        return self.unexhausted_trends
    
    def get_scan_history(self) -> Dict:
        return self.scan_history
