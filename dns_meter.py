import asyncio
import dns.resolver
from typing import Dict, Optional
import time

class DNSBroadcastMeter:
    def __init__(self):
        self.pin_counts: Dict[str, int] = {}
        self.broadcast_points: Dict[str, list] = {}
        self.metered_requests: Dict[str, float] = {}
        
    async def broadcast_await_pin_count(self, domain: str) -> int:
        if domain not in self.pin_counts:
            self.pin_counts[domain] = 0
        self.pin_counts[domain] += 1
        return self.pin_counts[domain]
    
    async def meter_dns_point(self, domain: str, pin_count: int) -> Dict:
        metered_data = {
            'domain': domain,
            'pin_count': pin_count,
            'timestamp': time.time(),
            'metered': True
        }
        self.metered_requests[domain] = time.time()
        return metered_data
    
    async def resolve_domain(self, domain: str) -> Optional[list]:
        try:
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(domain, 'A')
            return [str(rdata) for rdata in answers]
        except Exception as e:
            print(f"DNS resolution error for {domain}: {e}")
            return None
    
    async def process_dns_broadcast(self, domain: str) -> Dict:
        pin_count = await self.broadcast_await_pin_count(domain)
        metered = await self.meter_dns_point(domain, pin_count)
        resolved = await self.resolve_domain(domain)
        
        result = {
            'domain': domain,
            'pin_count': pin_count,
            'metered': metered,
            'resolved_ips': resolved,
            'timestamp': time.time()
        }
        
        if domain not in self.broadcast_points:
            self.broadcast_points[domain] = []
        self.broadcast_points[domain].append(result)
        
        return result
