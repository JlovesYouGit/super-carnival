import asyncio
import aiohttp
from typing import Dict, List, Optional
import re
from urllib.parse import urlparse

class DomainFetcher:
    def __init__(self):
        self.fetched_domains: Dict[str, Dict] = {}
        self.fetch_history: List[Dict] = []
        
    async def fetch_domain_from_endpoint(self, endpoint_url: str) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint_url, ssl=False) as response:
                    content = await response.text()
                    
                    # Extract domain from endpoint URL
                    parsed = urlparse(endpoint_url)
                    domain = parsed.netloc
                    
                    # Extract additional domain information from content
                    subdomains = self._extract_subdomains(content)
                    ip_addresses = self._extract_ip_addresses(content)
                    
                    domain_info = {
                        'endpoint_url': endpoint_url,
                        'domain': domain,
                        'subdomains': subdomains,
                        'ip_addresses': ip_addresses,
                        'status_code': response.status,
                        'content_length': len(content),
                        'fetched_at': asyncio.get_event_loop().time()
                    }
                    
                    self.fetched_domains[domain] = domain_info
                    self.fetch_history.append({
                        'domain': domain,
                        'endpoint': endpoint_url,
                        'fetched_at': domain_info['fetched_at']
                    })
                    
                    return domain_info
                    
        except Exception as e:
            return {
                'endpoint_url': endpoint_url,
                'error': str(e),
                'fetched_at': asyncio.get_event_loop().time()
            }
    
    def _extract_subdomains(self, content: str) -> List[str]:
        # Extract subdomains from content using regex
        subdomain_pattern = r'\b([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'
        matches = re.findall(subdomain_pattern, content)
        # Filter out main domain and duplicates
        unique_subdomains = list(set(matches))
        return unique_subdomains
    
    def _extract_ip_addresses(self, content: str) -> List[str]:
        # Extract IP addresses from content
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        matches = re.findall(ip_pattern, content)
        # Filter out invalid IPs and duplicates
        valid_ips = []
        for ip in matches:
            parts = ip.split('.')
            if all(0 <= int(part) <= 255 for part in parts):
                valid_ips.append(ip)
        return list(set(valid_ips))
    
    async def fetch_multiple_domains(self, endpoints: List[str]) -> Dict[str, Dict]:
        results = {}
        
        for endpoint in endpoints:
            result = await self.fetch_domain_from_endpoint(endpoint)
            domain = result.get('domain', endpoint)
            results[domain] = result
            
        return results
    
    def get_fetched_domain(self, domain: str) -> Optional[Dict]:
        return self.fetched_domains.get(domain)
    
    def get_all_fetched_domains(self) -> Dict[str, Dict]:
        return self.fetched_domains.copy()
