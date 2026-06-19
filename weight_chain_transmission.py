import asyncio
from typing import Dict, List, Optional, Any
import time

class ChainNode:
    def __init__(self, node_id: str, position: int):
        self.node_id = node_id
        self.position = position
        self.weight_data: Optional[Dict] = None
        self.received_weight: float = 0.0
        self.transmitted_weight: float = 0.0
        self.processed: bool = False
        
class WeightChainTransmission:
    def __init__(self):
        self.chains: Dict[str, List[ChainNode]] = {}
        self.weight_data_store: Dict[str, Dict] = {}
        self.transmission_history: List[Dict] = []
        
    async def create_chain(self, chain_id: str, node_count: int) -> List[ChainNode]:
        nodes = []
        for i in range(node_count):
            node = ChainNode(f"node_{chain_id}_{i}", i)
            nodes.append(node)
        
        self.chains[chain_id] = nodes
        return nodes
    
    async def transmit_weight_data(self, chain_id: str, weight_data: Dict, 
                                   start_node: int = 0) -> bool:
        if chain_id not in self.chains:
            return False
            
        chain = self.chains[chain_id]
        
        # Store weight data
        data_id = f"weight_{chain_id}_{int(time.time())}"
        self.weight_data_store[data_id] = weight_data
        
        # Transmit through entire chain
        for i in range(start_node, len(chain)):
            node = chain[i]
            node.weight_data = weight_data.copy()
            node.received_weight = weight_data.get('weight', 1.0)
            node.transmitted_weight = node.received_weight
            node.processed = True
            
            self.transmission_history.append({
                'chain_id': chain_id,
                'node_id': node.node_id,
                'position': i,
                'weight_received': node.received_weight,
                'weight_transmitted': node.transmitted_weight,
                'processed_at': time.time()
            })
        
        return True
    
    async def get_chain_weight_at_position(self, chain_id: str, position: int) -> Optional[float]:
        if chain_id not in self.chains:
            return None
            
        chain = self.chains[chain_id]
        if 0 <= position < len(chain):
            return chain[position].transmitted_weight
        return None
    
    async def get_total_chain_weight(self, chain_id: str) -> float:
        if chain_id not in self.chains:
            return 0.0
            
        chain = self.chains[chain_id]
        total_weight = sum(node.transmitted_weight for node in chain)
        return total_weight
    
    async def check_weight_persistence(self, chain_id: str) -> bool:
        if chain_id not in self.chains:
            return False
            
        chain = self.chains[chain_id]
        return all(node.processed for node in chain)
    
    async def get_weight_data(self, chain_id: str) -> Optional[Dict]:
        if chain_id not in self.chains or not self.chains[chain_id]:
            return None
            
        return self.chains[chain_id][0].weight_data
    
    def get_chain(self, chain_id: str) -> Optional[List[ChainNode]]:
        return self.chains.get(chain_id)
