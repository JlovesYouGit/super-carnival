import asyncio
from typing import Dict, List, Optional
import time

class AbnormalSequence:
    def __init__(self, sequence_id: str):
        self.sequence_id = sequence_id
        self.sequence_data: List = []
        self.abnormality_score: float = 0.0
        self.detected_at: Optional[float] = None
        self.fixed: bool = False
        self.fixed_at: Optional[float] = None
        
    def to_dict(self) -> Dict:
        return {
            'sequence_id': self.sequence_id,
            'sequence_data': self.sequence_data,
            'abnormality_score': self.abnormality_score,
            'detected_at': self.detected_at,
            'fixed': self.fixed,
            'fixed_at': self.fixed_at
        }

class FixProtocol:
    def __init__(self, protocol_value: float = 50.0):
        self.protocol_value = protocol_value
        self.abnormal_sequences: Dict[str, AbnormalSequence] = {}
        self.fix_history: List[Dict] = []
        
    async def detect_abnormal_sequence(self, sequence_id: str, sequence_data: List) -> bool:
        abnormal = AbnormalSequence(sequence_id)
        abnormal.sequence_data = sequence_data.copy()
        abnormal.detected_at = time.time()
        
        abnormality_score = await self._calculate_abnormality_score(sequence_data)
        abnormal.abnormality_score = abnormality_score
        
        if abnormality_score > self.protocol_value:
            self.abnormal_sequences[sequence_id] = abnormal
            return True
            
        return False
    
    async def _calculate_abnormality_score(self, sequence_data: List) -> float:
        if not sequence_data:
            return 0.0
            
        score = 0.0
        for i in range(len(sequence_data) - 1):
            if isinstance(sequence_data[i], (int, float)) and isinstance(sequence_data[i+1], (int, float)):
                diff = abs(sequence_data[i] - sequence_data[i+1])
                score += diff
                
        return score / len(sequence_data) if sequence_data else 0.0
    
    async def apply_self_effect(self, sequence_id: str) -> Dict:
        if sequence_id not in self.abnormal_sequences:
            return {'error': 'Sequence not found'}
            
        abnormal = self.abnormal_sequences[sequence_id]
        
        if abnormal.abnormality_score >= self.protocol_value:
            abnormal.fixed = True
            abnormal.fixed_at = time.time()
            
            self_effect = {
                'sequence_id': sequence_id,
                'self_effect_applied': True,
                'protocol_value': self.protocol_value,
                'abnormality_score': abnormal.abnormality_score,
                'fixed_at': abnormal.fixed_at
            }
            
            self.fix_history.append(self_effect)
            return self_effect
            
        return {'error': 'Abnormality score below threshold'}
    
    async def lock_state_to_weight_class(self, sequence_id: str, weight_class_id: str) -> Dict:
        if sequence_id not in self.abnormal_sequences:
            return {'error': 'Sequence not found'}
            
        abnormal = self.abnormal_sequences[sequence_id]
        
        if abnormal.fixed:
            return {
                'sequence_id': sequence_id,
                'weight_class_id': weight_class_id,
                'state_locked': True,
                'locked_at': time.time(),
                'query_space_experiences': abnormal.sequence_data
            }
            
        return {'error': 'Sequence not fixed yet'}
    
    def get_abnormal_sequence(self, sequence_id: str) -> Optional[AbnormalSequence]:
        return self.abnormal_sequences.get(sequence_id)
    
    def get_fix_history(self) -> List[Dict]:
        return self.fix_history
    
    def set_protocol_value(self, value: float):
        self.protocol_value = value
