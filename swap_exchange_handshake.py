import asyncio
from typing import Dict, List, Optional, Tuple
import time
import hashlib

class SwapExchange:
    def __init__(self, exchange_id: str):
        self.exchange_id = exchange_id
        self.our_block: bytes = b''
        self.their_block: bytes = b''
        self.handshake_token: Optional[str] = None
        self.exchanged: bool = False
        self.cycle_count: int = 0
        self.created_at: time.time()
        
class SwapExchangeHandshake:
    def __init__(self):
        self.exchanges: Dict[str, SwapExchange] = {}
        self.handshake_history: List[Dict] = {}
        
    async def initiate_exchange(self, exchange_id: str, our_block: bytes) -> SwapExchange:
        exchange = SwapExchange(exchange_id)
        exchange.our_block = our_block
        exchange.handshake_token = hashlib.sha256(our_block).hexdigest()[:16]
        
        self.exchanges[exchange_id] = exchange
        
        return exchange
    
    async def complete_exchange(self, exchange_id: str, their_block: bytes) -> bool:
        if exchange_id not in self.exchanges:
            return False
            
        exchange = self.exchanges[exchange_id]
        exchange.their_block = their_block
        exchange.exchanged = True
        exchange.cycle_count += 1
        
        self.handshake_history.append({
            'exchange_id': exchange_id,
            'our_block_size': len(exchange.our_block),
            'their_block_size': len(their_block),
            'exchanged_at': time.time()
        })
        
        return True
    
    async def complete_cycle(self, exchange_id: str) -> bool:
        if exchange_id not in self.exchanges:
            return False
            
        exchange = self.exchanges[exchange_id]
        exchange.cycle_count += 1
        
        return True
    
    async def get_exchanged_blocks(self, exchange_id: str) -> Optional[Tuple[bytes, bytes]]:
        if exchange_id in self.exchanges:
            exchange = self.exchanges[exchange_id]
            return exchange.our_block, exchange.their_block
        return None
    
    async def get_handshake_token(self, exchange_id: str) -> Optional[str]:
        if exchange_id in self.exchanges:
            return self.exchanges[exchange_id].handshake_token
        return None
    
    async def is_exchanged(self, exchange_id: str) -> bool:
        if exchange_id in self.exchanges:
            return self.exchanges[exchange_id].exchanged
        return False
    
    def get_exchange(self, exchange_id: str) -> Optional[SwapExchange]:
        return self.exchanges.get(exchange_id)
