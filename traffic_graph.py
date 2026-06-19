from typing import Dict, List, Set
import asyncio

class TrafficFlowPoint:
    def __init__(self, point_id: str, endpoint: str):
        self.point_id = point_id
        self.endpoint = endpoint
        self.connections: Set[str] = set()
        self.ping_count: int = 0
        
    def add_connection(self, to_point: str):
        self.connections.add(to_point)
        
    def increment_ping(self):
        self.ping_count += 1

class TrafficFlowGraph:
    def __init__(self):
        self.points: Dict[str, TrafficFlowPoint] = {}
        self.routes: Dict[str, List[str]] = {}
        
    def add_point(self, point_id: str, endpoint: str) -> TrafficFlowPoint:
        point = TrafficFlowPoint(point_id, endpoint)
        self.points[point_id] = point
        return point
    
    def add_connection(self, from_point: str, to_point: str):
        if from_point in self.points and to_point in self.points:
            self.points[from_point].add_connection(to_point)
            
    async def route_through(self, start_point: str, end_point: str) -> List[str]:
        if start_point not in self.points or end_point not in self.points:
            return []
        
        visited = set()
        queue = [[start_point]]
        
        while queue:
            path = queue.pop(0)
            current = path[-1]
            
            if current == end_point:
                return path
            
            if current not in visited:
                visited.add(current)
                for neighbor in self.points[current].connections:
                    new_path = path + [neighbor]
                    queue.append(new_path)
        
        return []
    
    def increment_ping(self, point_id: str):
        if point_id in self.points:
            self.points[point_id].increment_ping()
    
    def get_ping_count(self, point_id: str) -> int:
        if point_id in self.points:
            return self.points[point_id].ping_count
        return 0
    
    def get_all_ping_counts(self) -> Dict[str, int]:
        return {pid: point.ping_count for pid, point in self.points.items()}
