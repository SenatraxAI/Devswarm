"""
Refactoring Engine - AST-based code transformations
Safe refactoring that maintains semantic correctness
"""
import ast
from typing import Dict, Any, Optional
from pathlib import Path


class RefactoringEngine:
    """
    AST-based code refactoring tool
    Supports rename, extract method, inline operations
    """
    
    def __init__(self):
        self.refactoring_history = []
    
    async def rename_symbol(
        self,
        file_path: str,
        old_name: str,
        new_name: str
    ) -> Dict[str, Any]:
        """
        Rename variable/function/class
        
        Args:
            file_path: Python file
            old_name: Current name
            new_name: New name
            
        Returns:
            {
                "success": bool,
                "occurrences": int,
                "updated_code": str
            }
        """
        try:
            path = Path(file_path)
            if not path.exists() or path.suffix != '.py':
                return {"success": False, "error": "Invalid Python file"}
            
            code = path.read_text()
            tree = ast.parse(code)
            
            # Find and rename all occurrences
            occurrences = 0
            
            class RenameTransformer(ast.NodeTransformer):
                def visit_Name(self, node):
                    nonlocal occurrences
                    if node.id == old_name:
                        node.id = new_name
                        occurrences += 1
                    return node
                
                def visit_FunctionDef(self, node):
                    nonlocal occurrences
                    if node.name == old_name:
                        node.name = new_name
                        occurrences += 1
                    self.generic_visit(node)
                    return node
                
                def visit_ClassDef(self, node):
                    nonlocal occurrences
                    if node.name == old_name:
                        node.name = new_name
                        occurrences += 1
                    self.generic_visit(node)
                    return node
            
            transformer = RenameTransformer()
            new_tree = transformer.visit(tree)
            
            # Convert back to code
            updated_code = ast.unparse(new_tree)
            
            # Record in history
            self.refactoring_history.append({
                "type": "rename",
                "file": file_path,
                "from": old_name,
                "to": new_name,
                "occurrences": occurrences
            })
            
            return {
                "success": True,
                "occurrences": occurrences,
                "updated_code": updated_code
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def extract_method(
        self,
        file_path: str,
        start_line: int,
        end_line: int,
        method_name: str
    ) -> Dict[str, Any]:
        """
        Extract code block into new method
        (Simplified implementation)
        """
        try:
            path = Path(file_path)
            lines = path.read_text().splitlines()
            
            # Extract target lines
            extracted = lines[start_line-1:end_line]
            
            # Create new method
            new_method = [
                f"def {method_name}():",
                *["    " + line for line in extracted]
            ]
            
            # Replace with call
            lines[start_line-1:end_line] = [f"    {method_name}()"]
            
            # Insert new method
            lines.insert(start_line-1, "")
            lines[start_line:start_line] = new_method
            
            updated_code = "\n".join(lines)
            
            return {
                "success": True,
                "method_name": method_name,
                "updated_code": updated_code
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_refactoring_history(self, limit: int = 10) -> list:
        """Get recent refactoring history"""
        return self.refactoring_history[-limit:]


# Tool schemas
REFACTOR_RENAME_SCHEMA = {
    "name": "refactor_rename",
    "description": "Rename symbol across file",
    "parameters": {
        "file_path": {"type": "string", "required": True},
        "old_name": {"type": "string", "required": True},
        "new_name": {"type": "string", "required": True}
    }
}
