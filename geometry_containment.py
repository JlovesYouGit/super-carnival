import asyncio
from typing import Dict, List, Optional, Tuple
import time
import numpy as np

class GeometryShape:
    def __init__(self, shape_id: str):
        self.shape_id = shape_id
        self.vertices: List[Tuple[float, float, float]] = []
        self.pipeline_source: str = ''
        self.contained: bool = False
        self.locked: bool = False
        self.created_at: time.time()

class GeometryContainment:
    def __init__(self):
        self.shapes: Dict[str, GeometryShape] = {}
        self.containment_history: List[Dict] = {}
        
    async def create_shape_from_pipeline(self, shape_id: str, pipeline_data: bytes, pipeline_source: str) -> GeometryShape:
        shape = GeometryShape(shape_id)
        shape.pipeline_source = pipeline_source
        
        # Extract vertices from pipeline data
        vertices = self._extract_vertices_from_data(pipeline_data)
        shape.vertices = vertices
        
        self.shapes[shape_id] = shape
        return shape
    
    def _extract_vertices_from_data(self, data: bytes) -> List[Tuple[float, float, float]]:
        vertices = []
        
        # Simple vertex extraction from byte data
        for i in range(0, len(data) - 11, 12):
            if i + 12 <= len(data):
                x = float.fromhex(data[i:i+4].hex())
                y = float.fromhex(data[i+4:i+8].hex())
                z = float.fromhex(data[i+8:i+12].hex())
                vertices.append((x, y, z))
        
        return vertices
    
    async def lock_geometry(self, shape_id: str) -> bool:
        if shape_id not in self.shapes:
            return False
            
        self.shapes[shape_id].locked = True
        return True
    
    async def contain_shape(self, shape_id: str) -> bool:
        if shape_id not in self.shapes:
            return False
            
        shape = self.shapes[shape_id]
        
        # Perfectly re-arrange to avoid geometry error
        if shape.vertices:
            # Normalize vertices to prevent rendering errors
            normalized = self._normalize_vertices(shape.vertices)
            shape.vertices = normalized
            shape.contained = True
            
            self.containment_history.append({
                'shape_id': shape_id,
                'pipeline_source': shape.pipeline_source,
                'contained_at': time.time()
            })
        
        return True
    
    def _normalize_vertices(self, vertices: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        if not vertices:
            return vertices
            
        # Find bounds
        x_vals = [v[0] for v in vertices]
        y_vals = [v[1] for v in vertices]
        z_vals = [v[2] for v in vertices]
        
        x_min, x_max = min(x_vals), max(x_vals)
        y_min, y_max = min(y_vals), max(y_vals)
        z_min, z_max = min(z_vals), max(z_vals)
        
        # Normalize to unit cube
        normalized = []
        for x, y, z in vertices:
            norm_x = (x - x_min) / (x_max - x_min) if x_max != x_min else 0.5
            norm_y = (y - y_min) / (y_max - y_min) if y_max != y_min else 0.5
            norm_z = (z - z_min) / (z_max - z_min) if z_max != z_min else 0.5
            normalized.append((norm_x, norm_y, norm_z))
        
        return normalized
    
    async def apply_perfectly(self, shape_id: str) -> bool:
        if shape_id not in self.shapes:
            return False
            
        shape = self.shapes[shape_id]
        
        # Ensure shape is contained and locked
        await self.contain_shape(shape_id)
        await self.lock_geometry(shape_id)
        
        return True
    
    async def get_shape_vertices(self, shape_id: str) -> Optional[List[Tuple[float, float, float]]]:
        if shape_id in self.shapes:
            return self.shapes[shape_id].vertices
        return None
    
    def get_shape(self, shape_id: str) -> Optional[GeometryShape]:
        return self.shapes.get(shape_id)
