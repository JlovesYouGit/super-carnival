from typing import Dict, List
import time

class PingDirective:
    def __init__(self, directive_id: str, ping_count: int, action: str):
        self.directive_id = directive_id
        self.ping_count = ping_count
        self.action = action
        self.timestamp = time.time()
        
    def to_dict(self) -> Dict:
        return {
            'directive_id': self.directive_id,
            'ping_count': self.ping_count,
            'action': self.action,
            'timestamp': self.timestamp
        }

class PingDirectiveClass:
    def __init__(self, class_name: str):
        self.class_name = class_name
        self.directives: Dict[int, PingDirective] = {}
        
    def add_directive(self, ping_count: int, action: str) -> PingDirective:
        directive_id = f"{self.class_name}_{ping_count}"
        directive = PingDirective(directive_id, ping_count, action)
        self.directives[ping_count] = directive
        return directive
    
    def get_directive(self, ping_count: int) -> PingDirective:
        return self.directives.get(ping_count)
    
    def get_all_directives(self) -> Dict[int, PingDirective]:
        return self.directives

class PingDirectiveManager:
    def __init__(self):
        self.classes: Dict[str, PingDirectiveClass] = {}
        
    def add_class(self, class_name: str) -> PingDirectiveClass:
        if class_name not in self.classes:
            self.classes[class_name] = PingDirectiveClass(class_name)
        return self.classes[class_name]
    
    def add_directive(self, class_name: str, ping_count: int, action: str) -> PingDirective:
        if class_name not in self.classes:
            self.add_class(class_name)
        return self.classes[class_name].add_directive(ping_count, action)
    
    def get_directive_by_ping(self, ping_count: int) -> PingDirective:
        for class_obj in self.classes.values():
            directive = class_obj.get_directive(ping_count)
            if directive:
                return directive
        return None
    
    def get_all_classes(self) -> Dict[str, PingDirectiveClass]:
        return self.classes
