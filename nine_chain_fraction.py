import asyncio
from typing import Dict, List, Optional, Tuple
import time

class NineChainFraction:
    def __init__(self, chain_id: str):
        self.chain_id = chain_id
        self.fractions: List[float] = []
        self.chain_length: int = 9
        self.processed_values: List[Dict] = []
        self.normalized_chain: List[float] = []
        self.created_at: time.time()

class NineChainFractionProcessor:
    def __init__(self):
        self.chains: Dict[str, NineChainFraction] = {}
        self.processing_history: List[Dict] = []
        
    async def create_nine_chain(self, chain_id: str, raw_values: List[float]) -> NineChainFraction:
        chain = NineChainFraction(chain_id)
        
        # Process raw values into fractions below 1
        for value in raw_values:
            if abs(value) >= 1:
                # Convert to fraction below 1
                fraction = value / (10 ** len(str(int(abs(value)))))
            else:
                fraction = abs(value)
            
            chain.fractions.append(fraction)
            
            processed_value = {
                'original': value,
                'fraction': fraction,
                'is_below_one': fraction < 1,
                'magnitude': abs(fraction)
            }
            chain.processed_values.append(processed_value)
        
        # Ensure exactly 9 elements in the chain
        while len(chain.fractions) < 9:
            chain.fractions.append(0.0)
            chain.processed_values.append({'original': 0.0, 'fraction': 0.0, 'is_below_one': True, 'magnitude': 0.0})
        
        chain.fractions = chain.fractions[:9]
        chain.processed_values = chain.processed_values[:9]
        
        # Normalize the chain
        chain.normalized_chain = self._normalize_chain(chain.fractions)
        
        self.chains[chain_id] = chain
        
        self.processing_history.append({
            'chain_id': chain_id,
            'chain_length': len(chain.fractions),
            'normalized': True,
            'processed_at': time.time()
        })
        
        return chain
    
    def _normalize_chain(self, fractions: List[float]) -> List[float]:
        """Normalize fractions to maintain chain integrity"""
        if not fractions:
            return []
        
        total = sum(fractions)
        if total == 0:
            return fractions
        
        # Normalize to maintain relative proportions
        normalized = [f / total for f in fractions]
        return normalized
    
    async def process_chain_fraction(self, chain_id: str, position: int, value: float) -> Dict:
        if chain_id not in self.chains:
            return {'error': 'Chain not found'}
        
        chain = self.chains[chain_id]
        
        if position < 0 or position >= 9:
            return {'error': 'Invalid position (must be 0-8)'}
        
        # Convert to fraction below 1
        if abs(value) >= 1:
            fraction = value / (10 ** len(str(int(abs(value)))))
        else:
            fraction = abs(value)
        
        # Update chain at position
        chain.fractions[position] = fraction
        chain.processed_values[position] = {
            'original': value,
            'fraction': fraction,
            'is_below_one': fraction < 1,
            'magnitude': abs(fraction)
        }
        
        # Renormalize chain
        chain.normalized_chain = self._normalize_chain(chain.fractions)
        
        return {
            'chain_id': chain_id,
            'position': position,
            'fraction': fraction,
            'normalized_chain': chain.normalized_chain,
            'updated_at': time.time()
        }
    
    async def get_chain_summary(self, chain_id: str) -> Optional[Dict]:
        if chain_id not in self.chains:
            return None
        
        chain = self.chains[chain_id]
        
        return {
            'chain_id': chain_id,
            'fractions': chain.fractions,
            'normalized_chain': chain.normalized_chain,
            'chain_length': len(chain.fractions),
            'total_fraction': sum(chain.fractions),
            'average_fraction': sum(chain.fractions) / len(chain.fractions) if chain.fractions else 0,
            'processed_values': chain.processed_values,
            'created_at': chain.created_at
        }
    
    def get_chain(self, chain_id: str) -> Optional[NineChainFraction]:
        return self.chains.get(chain_id)
