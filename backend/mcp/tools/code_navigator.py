"""
Code Navigator - AST-based project structure analysis
Provides high-level understanding without executing code
"""
import ast
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import json


class CodeNavigator:
    """
    Analyze project structure using AST
    Safe analysis without code execution
    """
    
    def __init__(self):
        self.analysis_cache = {}
    
    async def get_project_structure(
        self,
        dir_path: Optional[str] = None,
        max_depth: int = 3,
        file_path: Optional[str] = None,
        path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate project structure tree
        
        Args:
            dir_path: Project directory
            max_depth: Maximum depth to traverse
            
        Returns:
            {
                "success": bool,
                "structure": dict,
                "stats": dict
            }
        """
        # Handle aliases
        dir_path = dir_path or file_path or path
        try:
            path = Path(dir_path)
            if not path.exists():
                return {"success": False, "error": "Directory not found"}
            
            structure = self._build_tree(path, max_depth)
            stats = self._calculate_stats(structure)
            
            return {
                "success": True,
                "structure": structure,
                "stats": stats
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def analyze_imports(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Extract and analyze import statements
        
        Args:
            file_path: Python file to analyze
            
        Returns:
            {
                "success": bool,
                "imports": list,
                "from_imports": list
            }
        """
        try:
            path = Path(file_path)
            if not path.exists() or path.suffix != '.py':
                return {"success": False, "error": "Invalid Python file"}
            
            code = path.read_text()
            tree = ast.parse(code)
            
            imports = []
            from_imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        from_imports.append(f"{module}.{alias.name}")
            
            return {
                "success": True,
                "imports": imports,
                "from_imports": from_imports,
                "total": len(imports) + len(from_imports)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def find_definition(
        self,
        symbol: str,
        project_dir: str,
        symbol_type: str = "any"  # function, class, any
    ) -> Dict[str, Any]:
        """
        Find symbol definition in project
        
        Args:
            symbol: Symbol name to find
            project_dir: Project directory to search
            symbol_type: Type filter (function, class, any)
            
        Returns:
            {
                "success": bool,
                "results": list of {file, line, type}
            }
        """
        try:
            results = []
            project_path = Path(project_dir)
            
            for py_file in project_path.rglob("*.py"):
                try:
                    code = py_file.read_text()
                    tree = ast.parse(code)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name == symbol:
                            if symbol_type in ["function", "any"]:
                                results.append({
                                    "file": str(py_file.relative_to(project_path)),
                                    "line": node.lineno,
                                    "type": "function"
                                })
                        elif isinstance(node, ast.ClassDef) and node.name == symbol:
                            if symbol_type in ["class", "any"]:
                                results.append({
                                    "file": str(py_file.relative_to(project_path)),
                                    "line": node.lineno,
                                    "type": "class"
                                })
                except:
                    continue
            
            return {
                "success": True,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_call_graph(
        self,
        file_path: str,
        function_name: str
    ) -> Dict[str, Any]:
        """
        Build call graph for a function
        
        Args:
            file_path: File containing function
            function_name: Function to analyze
            
        Returns:
            {
                "success": bool,
                "calls": list,
                "called_by": list (if available)
            }
        """
        try:
            path = Path(file_path)
            code = path.read_text()
            tree = ast.parse(code)
            
            # Find function node
            target_function = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    target_function = node
                    break
            
            if not target_function:
                return {"success": False, "error": f"Function {function_name} not found"}
            
            # Extract function calls
            calls = []
            for node in ast.walk(target_function):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        calls.append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        calls.append(f"{node.func.value.id if isinstance(node.func.value, ast.Name) else '...'}.{node.func.attr}")
            
            return {
                "success": True,
                "function": function_name,
                "calls": list(set(calls)),
                "count": len(set(calls))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _build_tree(self, path: Path, max_depth: int, current_depth: int = 0) -> Dict:
        """Recursively build directory tree"""
        if current_depth >= max_depth:
            return {"name": path.name, "type": "directory", "truncated": True}
        
        if path.is_file():
            return {
                "name": path.name,
                "type": "file",
                "size": path.stat().st_size
            }
        
        children = []
        try:
            for item in sorted(path.iterdir()):
                # Skip hidden and common ignore patterns
                if item.name.startswith('.') or item.name in ['node_modules', '__pycache__', 'venv']:
                    continue
                children.append(self._build_tree(item, max_depth, current_depth + 1))
        except PermissionError:
            pass
        
        return {
            "name": path.name,
            "type": "directory",
            "children": children
        }
    
    def _calculate_stats(self, structure: Dict) -> Dict:
        """Calculate project statistics"""
        stats = {"files": 0, "directories": 0, "total_size": 0}
        
        def count(node):
            if node["type"] == "file":
                stats["files"] += 1
                stats["total_size"] += node.get("size", 0)
            elif node["type"] == "directory":
                stats["directories"] += 1
                for child in node.get("children", []):
                    count(child)
        
        count(structure)
        return stats


# Tool schemas
CODE_NAVIGATOR_STRUCTURE_SCHEMA = {
    "name": "analyze_project_structure",
    "description": "Get project directory structure",
    "parameters": {
        "dir_path": {"type": "string", "required": True},
        "max_depth": {"type": "integer", "required": False}
    }
}

CODE_NAVIGATOR_IMPORTS_SCHEMA = {
    "name": "analyze_imports",
    "description": "Extract imports from Python file",
    "parameters": {
        "file_path": {"type": "string", "required": True}
    }
}

CODE_NAVIGATOR_FIND_SCHEMA = {
    "name": "find_definition",
    "description": "Find function/class definition in project",
    "parameters": {
        "symbol": {"type": "string", "required": True},
        "project_dir": {"type": "string", "required": True},
        "symbol_type": {"type": "string", "required": False}
    }
}
