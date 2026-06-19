import asyncio
import json
import os
from typing import Dict, List, Optional
import time
import uuid

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.session_count: int = 0
        self.persistent_file = "sessions_persistent.json"
        self.load_persistent_sessions()
        
    def load_persistent_sessions(self):
        if os.path.exists(self.persistent_file):
            try:
                with open(self.persistent_file, 'r') as f:
                    data = json.load(f)
                    self.sessions = data.get('sessions', {})
                    self.session_count = data.get('session_count', 0)
            except Exception as e:
                print(f"Load persistent sessions error: {e}")
    
    def save_persistent_sessions(self):
        try:
            data = {
                'sessions': self.sessions,
                'session_count': self.session_count,
                'saved_at': time.time()
            }
            with open(self.persistent_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Save persistent sessions error: {e}")
    
    async def create_session(self, user_id: str) -> Dict:
        session_id = str(uuid.uuid4())
        self.session_count += 1
        
        session = {
            'session_id': session_id,
            'user_id': user_id,
            'created_at': time.time(),
            'last_activity': time.time(),
            'status': 'active',
            'data': {},
            'interference_count': 0
        }
        
        self.sessions[session_id] = session
        self.save_persistent_sessions()
        
        return session
    
    async def update_session(self, session_id: str, data: Dict) -> bool:
        if session_id not in self.sessions:
            return False
            
        self.sessions[session_id]['data'].update(data)
        self.sessions[session_id]['last_activity'] = time.time()
        self.save_persistent_sessions()
        
        return True
    
    async def increment_interference(self, session_id: str) -> int:
        if session_id not in self.sessions:
            return 0
            
        self.sessions[session_id]['interference_count'] += 1
        self.save_persistent_sessions()
        
        return self.sessions[session_id]['interference_count']
    
    def get_session_count(self) -> int:
        return len(self.sessions)
    
    def get_total_session_count(self) -> int:
        return self.session_count
    
    def is_count_exceeding_one(self) -> bool:
        return self.get_session_count() > 1
    
    def get_all_sessions(self) -> Dict[str, Dict]:
        return self.sessions
    
    async def close_session(self, session_id: str) -> bool:
        if session_id not in self.sessions:
            return False
            
        self.sessions[session_id]['status'] = 'closed'
        self.sessions[session_id]['closed_at'] = time.time()
        self.save_persistent_sessions()
        
        return True
