import asyncio
from typing import Dict, List, Optional, Any
import time

from signal_metric import SignalMetricSystem
from state_transition import StateTransitionSystem
from negative_positive_skip import NegativePositiveSkip
from weight_chain_transmission import WeightChainTransmission
from data_metric_learning import DataMetricLearning
from endpoint_edit_integration import EndpointEditIntegration
from nine_chain_fraction import NineChainFractionProcessor

class SignalStateIntegration:
    def __init__(self):
        self.signal_metrics = SignalMetricSystem()
        self.state_transitions = StateTransitionSystem()
        self.negative_positive_skip = NegativePositiveSkip()
        self.weight_chain = WeightChainTransmission()
        self.data_learning = DataMetricLearning()
        self.endpoint_edit = EndpointEditIntegration()
        self.nine_chain_processor = NineChainFractionProcessor()
        
        self.integration_history: List[Dict] = []
        self.system_initialized = False
        
    async def initialize(self):
        await self.state_transitions.create_transition("main_transition")
        await self.negative_positive_skip.create_transition("main_zone_transition")
        await self.weight_chain.create_chain("main_chain", node_count=5)
        await self.endpoint_edit.initialize()
        self.system_initialized = True
        print("Signal State Integration System initialized")
        
    async def process_signal_metric(self, signal_id: str, metric_value: float) -> Dict:
        # Measure signal metric
        signal = await self.signal_metrics.measure_signal(signal_id, metric_value)
        
        # Check for negative stays
        has_negative_stays = await self.signal_metrics.check_negative_stays(signal_id)
        
        # Process zone transition
        zone_result = await self.negative_positive_skip.transition_zone(signal_id, metric_value)
        zone_transitioned, zone_message, skipped_state_1 = zone_result
        
        # Determine state transition based on zone
        if skipped_state_1:
            # Skip state 1, go directly to state 2
            state_result = await self.state_transitions.transition_state("main_transition", 2, skip_allowed=True)
        else:
            # Normal state progression
            current_state = await self.state_transitions.get_current_state("main_transition") or 0
            next_state = min(current_state + 1, 2)
            state_result = await self.state_transitions.transition_state("main_transition", next_state)
        
        state_transitioned, state_message = state_result
        
        # Check if state 1 is persistent and has weight
        current_state = await self.state_transitions.get_current_state("main_transition")
        if current_state == 1:
            await self.state_transitions.set_persistent("main_transition", True)
            state_weight = await self.state_transitions.get_state_weight("main_transition") or 0.0
            state_weight += 1.0
            await self.state_transitions.add_weight("main_transition", state_weight)
            
            # Transmit weight data through entire chain
            weight_data = {
                'weight': state_weight,
                'source_state': 1,
                'persistent': True,
                'timestamp': time.time()
            }
            await self.weight_chain.transmit_weight_data("main_chain", weight_data)
        
        # Learn from metric (off case handling)
        is_off_case = metric_value < 0 and zone_transitioned
        learned_metric = await self.data_learning.learn_from_metric(signal_id, metric_value, is_off_case)
        
        # Format output to avoid raw binary representation
        formatted_value = self._format_metric_value(metric_value)
        
        result = {
            'signal_id': signal_id,
            'metric_value': formatted_value,
            'has_negative_stays': has_negative_stays,
            'zone_transitioned': zone_transitioned,
            'skipped_state_1': skipped_state_1,
            'state_transitioned': state_transitioned,
            'current_state': current_state,
            'state_weight': await self.state_transitions.get_state_weight("main_transition"),
            'chain_weight': await self.weight_chain.get_total_chain_weight("main_chain"),
            'learned_confidence': learned_metric.confidence,
            'is_off_case_learned': learned_metric.off_case_learned,
            'timestamp': time.time()
        }
        
        self.integration_history.append(result)
        
        return result
    
    def _format_metric_value(self, metric_value: float) -> Dict:
        """Format metric value to avoid raw binary representation"""
        # Convert to proper decimal representation
        if isinstance(metric_value, (int, float)):
            return {
                'decimal': float(metric_value),
                'fraction': metric_value if abs(metric_value) < 1 else metric_value / (10 ** len(str(int(abs(metric_value))))),
                'is_negative': metric_value < 0,
                'magnitude': abs(metric_value)
            }
        return {'decimal': 0.0, 'fraction': 0.0, 'is_negative': False, 'magnitude': 0.0}
    
    async def process_signal_sequence(self, signal_id: str, metric_values: List[float]) -> Dict:
        if not self.system_initialized:
            await self.initialize()
            
        results = []
        
        for value in metric_values:
            result = await self.process_signal_metric(signal_id, value)
            results.append(result)
        
        # Get final state
        final_state = await self.state_transitions.get_current_state("main_transition")
        total_weight = await self.weight_chain.get_total_chain_weight("main_chain")
        
        return {
            'signal_id': signal_id,
            'metric_count': len(metric_values),
            'final_state': final_state,
            'total_chain_weight': total_weight,
            'results': results,
            'processed_at': time.time()
        }
    
    async def get_integration_status(self) -> Dict:
        return {
            'initialized': self.system_initialized,
            'signal_count': len(self.signal_metrics.signals),
            'transition_count': len(self.state_transitions.transitions),
            'zone_transition_count': len(self.negative_positive_skip.transitions),
            'chain_count': len(self.weight_chain.chains),
            'learned_metric_count': len(self.data_learning.learned_metrics),
            'endpoint_edit_status': self.endpoint_edit.get_system_status(),
            'current_state': await self.state_transitions.get_current_state("main_transition"),
            'total_chain_weight': await self.weight_chain.get_total_chain_weight("main_chain"),
            'timestamp': time.time()
        }
