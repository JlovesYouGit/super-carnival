from typing import Dict, List
import time

class AllowlistItem:
    def __init__(self, item_id: str, class_name: str, order: int):
        self.item_id = item_id
        self.class_name = class_name
        self.order = order
        self.timestamp = time.time()
        
    def to_dict(self) -> Dict:
        return {
            'item_id': self.item_id,
            'class_name': self.class_name,
            'order': self.order,
            'timestamp': self.timestamp
        }

class AllowlistManager:
    def __init__(self):
        self.items: Dict[str, AllowlistItem] = {}
        self.class_counts: Dict[str, int] = {}
        self.order_counter: int = 0
        
    def add_item(self, item_id: str, class_name: str) -> AllowlistItem:
        self.order_counter += 1
        item = AllowlistItem(item_id, class_name, self.order_counter)
        self.items[item_id] = item
        
        if class_name not in self.class_counts:
            self.class_counts[class_name] = 0
        self.class_counts[class_name] += 1
        
        return item
    
    def get_class_order_count(self, class_name: str) -> int:
        return self.class_counts.get(class_name, 0)
    
    def get_item_order(self, item_id: str) -> int:
        if item_id in self.items:
            return self.items[item_id].order
        return 0
    
    def get_all_class_counts(self) -> Dict[str, int]:
        return self.class_counts
    
    def get_items_by_class(self, class_name: str) -> List[AllowlistItem]:
        return [item for item in self.items.values() 
                if item.class_name == class_name]
    
    def is_allowed(self, item_id: str) -> bool:
        return item_id in self.items
