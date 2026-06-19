import asyncio
import time
from typing import Dict, Optional
from watchdog import WatchdogUpdate
from ticker import Ticker
from delay_order import DelayOrderRepeater
from payload_velocity import PayloadTravelTime
from entropy_velocity import MachineProcessEntropy

class WatchdogRule:
    def __init__(self):
        self.watchdog = WatchdogUpdate()
        self.ticker = Ticker()
        self.delay_repeater = DelayOrderRepeater()
        self.payload_velocity = PayloadTravelTime()
        self.entropy_velocity = MachineProcessEntropy()
        
        self.rule_active: bool = True
        self.rule_executions: int = 0
        self.last_execution_time: Optional[float] = None
        
    async def initialize(self):
        await self.watchdog.register_callback('ticker_rule', self.execute_rule)
        
    async def execute_rule(self, update_info: Dict) -> Dict:
        if not update_info.get('detected'):
            return {'rule_triggered': False}
            
        self.rule_executions += 1
        execution_start = time.time()
        
        result = {
            'rule_triggered': True,
            'execution_id': self.rule_executions,
            'steps': []
        }
        
        # Step 1: Set ticker to -9
        ticker_value = self.ticker.set_minus_nine()
        result['steps'].append({
            'step': 1,
            'action': 'set_ticker_minus_nine',
            'value': ticker_value,
            'timestamp': time.time()
        })
        
        # Step 2: Set under delay order instruction repeater
        instruction_id = f"rule_instruction_{self.rule_executions}"
        delay_ms = int(self.entropy_velocity.get_velocity_multiplier() * 100)
        instruction = {
            'rule_execution': self.rule_executions,
            'ticker_value': ticker_value,
            'entropy_multiplier': self.entropy_velocity.get_velocity_multiplier()
        }
        
        await self.delay_repeater.add_instruction(instruction_id, delay_ms, instruction)
        await self.delay_repeater.repeat_instruction(instruction_id, repeat_times=3)
        
        result['steps'].append({
            'step': 2,
            'action': 'delay_order_repeater',
            'instruction_id': instruction_id,
            'delay_ms': delay_ms,
            'repeat_count': 3,
            'timestamp': time.time()
        })
        
        # Step 3: Optimize payload travel time to be faster than detected traffic
        is_faster = await self.payload_velocity.is_faster_than_traffic()
        optimization_factor = await self.payload_velocity.optimize_velocity()
        
        result['steps'].append({
            'step': 3,
            'action': 'payload_velocity_optimization',
            'is_faster_than_traffic': is_faster,
            'optimization_factor': optimization_factor,
            'timestamp': time.time()
        })
        
        # Step 4: Add entropy to increase velocity
        base_velocity = 1.0
        increased_velocity = await self.entropy_velocity.apply_entropy_velocity(base_velocity)
        
        result['steps'].append({
            'step': 4,
            'action': 'entropy_velocity_increase',
            'base_velocity': base_velocity,
            'increased_velocity': increased_velocity,
            'velocity_multiplier': self.entropy_velocity.get_velocity_multiplier(),
            'timestamp': time.time()
        })
        
        # Step 5: Get entropy from machine process
        process_entropy = await self.entropy_velocity.collect_process_entropy()
        
        result['steps'].append({
            'step': 5,
            'action': 'machine_process_entropy',
            'entropy_value': process_entropy,
            'process_metrics': self.entropy_velocity.get_process_metrics(),
            'timestamp': time.time()
        })
        
        self.last_execution_time = time.time()
        result['execution_time'] = self.last_execution_time - execution_start
        result['completed_at'] = self.last_execution_time
        
        return result
    
    async def monitor_system(self, system_state_getter):
        await self.watchdog.start_monitoring(system_state_getter)
    
    def get_ticker_value(self) -> int:
        return self.ticker.get_value()
    
    def get_rule_status(self) -> Dict:
        return {
            'rule_active': self.rule_active,
            'rule_executions': self.rule_executions,
            'last_execution_time': self.last_execution_time,
            'ticker_value': self.ticker.get_value(),
            'velocity_multiplier': self.entropy_velocity.get_velocity_multiplier(),
            'payload_optimization_factor': self.payload_velocity.get_optimization_factor()
        }
    
    async def record_payload_travel(self, payload_id: str, travel_time: float):
        await self.payload_velocity.record_payload_travel(payload_id, travel_time)
    
    async def record_traffic_travel(self, traffic_id: str, travel_time: float):
        await self.payload_velocity.record_detected_traffic(traffic_id, travel_time)
