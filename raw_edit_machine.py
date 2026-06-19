import asyncio
import os
from typing import Dict, List, Optional, Any
import time
import json

class RawEditOperation:
    def __init__(self, operation_id: str, file_path: str, edit_type: str):
        self.operation_id = operation_id
        self.file_path = file_path
        self.edit_type = edit_type  # 'insert', 'replace', 'delete'
        self.position: Optional[int] = None
        old_data: Optional[bytes] = None
        new_data: Optional[bytes] = None
        self.executed = False
        self.created_at = time.time()

class RawEditMachine:
    def __init__(self):
        self.edit_operations: Dict[str, RawEditOperation] = {}
        self.edit_history: List[Dict] = []
        self.active_edits: Dict[str, bool] = {}
        
    async def prepare_raw_edit(self, operation_id: str, file_path: str, edit_type: str, 
                               position: Optional[int] = None, new_data: Optional[bytes] = None) -> RawEditOperation:
        operation = RawEditOperation(operation_id, file_path, edit_type)
        operation.position = position
        operation.new_data = new_data
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                operation.old_data = f.read()
        
        self.edit_operations[operation_id] = operation
        return operation
    
    async def execute_raw_edit(self, operation_id: str) -> bool:
        if operation_id not in self.edit_operations:
            return False
            
        operation = self.edit_operations[operation_id]
        
        try:
            if operation.edit_type == 'insert' and operation.new_data:
                with open(operation.file_path, 'ab') as f:
                    f.write(operation.new_data)
                    
            elif operation.edit_type == 'replace' and operation.new_data:
                with open(operation.file_path, 'wb') as f:
                    f.write(operation.new_data)
                    
            elif operation.edit_type == 'delete':
                if operation.old_data:
                    with open(operation.file_path, 'wb') as f:
                        f.write(operation.old_data[:operation.position] if operation.position else b'')
            
            operation.executed = True
            self.active_edits[operation_id] = True
            
            self.edit_history.append({
                'operation_id': operation_id,
                'file_path': operation.file_path,
                'edit_type': operation.edit_type,
                'executed_at': time.time()
            })
            
            return True
            
        except Exception as e:
            print(f"Edit execution error: {e}")
            return False
    
    async def batch_execute_edits(self, operation_ids: List[str]) -> Dict[str, bool]:
        results = {}
        for op_id in operation_ids:
            results[op_id] = await self.execute_raw_edit(op_id)
        return results
    
    async def automatic_full_raw_edit(self, file_path: str, new_content: bytes) -> bool:
        operation_id = f"auto_{int(time.time())}"
        await self.prepare_raw_edit(operation_id, file_path, 'replace', new_data=new_content)
        return await self.execute_raw_edit(operation_id)
    
    async def undo_edit(self, operation_id: str) -> bool:
        if operation_id not in self.edit_operations:
            return False
            
        operation = self.edit_operations[operation_id]
        
        if operation.old_data:
            undo_id = f"undo_{operation_id}"
            await self.prepare_raw_edit(undo_id, operation.file_path, 'replace', new_data=operation.old_data)
            return await self.execute_raw_edit(undo_id)
            
        return False
    
    def get_operation(self, operation_id: str) -> Optional[RawEditOperation]:
        return self.edit_operations.get(operation_id)
    
    def get_edit_history(self) -> List[Dict]:
        return self.edit_history.copy()
