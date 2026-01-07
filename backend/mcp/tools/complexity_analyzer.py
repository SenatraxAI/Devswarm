"""
Complexity Analyzer - Code complexity metrics
Measures cyclomatic complexity, cognitive complexity, coupling/cohesion
"""
import ast
from typing import Dict, Any, List
from pathlib import Path


class ComplexityAnalyzer:
    """
    Code complexity measurement tool
    Identifies high-complexity functions and technical debt
    """
    
    def __init__(self):
        self.analysis_history = []
    
    async def analyze_complexity(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Analyze code complexity
        
        Args:
            file_path: Python file to analyze
            
        Returns:
            {
                "success": bool,
                "functions": list,
                "avg_complexity": float,
                "high_complexity_count": int
            }
        """
        try:
            path = Path(file_path)
            if not path.exists() or path.suffix != '.py':
                return {"success": False, "error": "Invalid Python file"}
            
            code = path.read_text()
            tree = ast.parse(code)
            
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    cognitive = self._calculate_cognitive_complexity(node)
                    lines = self._count_lines(node)
                    
                    risk = self._assess_risk(complexity, cognitive, lines)
                    
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "cyclomatic": complexity,
                        "cognitive": cognitive,
                        "lines": lines,
                        "risk": risk
                    })
            
            # Calculate summary metrics
            if functions:
                avg_complexity = sum(f["cyclomatic"] for f in functions) / len(functions)
                high_complexity_count = sum(1 for f in functions if f["risk"] in ["HIGH", "CRITICAL"])
            else:
                avg_complexity = 0
                high_complexity_count = 0
            
            result = {
                "success": True,
                "file": file_path,
                "functions": functions,
                "total_functions": len(functions),
                "avg_complexity": round(avg_complexity, 2),
                "high_complexity_count": high_complexity_count
            }
            
            # Record in history
            self.analysis_history.append({
                "file": file_path,
                "avg_complexity": avg_complexity,
                "high_risk": high_complexity_count
            })
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate cyclomatic complexity
        Counts decision points: if, for, while, and, or, except
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            # Boolean operators
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            # Exception handling
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            # Comprehensions
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1
        
        return complexity
    
    def _calculate_cognitive_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate cognitive complexity
        Accounts for nesting depth
        """
        cognitive = 0
        
        def walk_with_depth(node, depth=0):
            nonlocal cognitive
            
            for child in ast.iter_child_nodes(node):
                # Increment for control structures
                if isinstance(child, (ast.If, ast.While, ast.For)):
                    cognitive += 1 + depth  # Base + nesting penalty
                    walk_with_depth(child, depth + 1)
                elif isinstance(child, ast.BoolOp):
                    cognitive += len(child.values) - 1
                    walk_with_depth(child, depth)
                else:
                    walk_with_depth(child, depth)
        
        walk_with_depth(node)
        return cognitive
    
    def _count_lines(self, node: ast.FunctionDef) -> int:
        """Count lines in function"""
        if hasattr(node, 'end_lineno'):
            return node.end_lineno - node.lineno + 1
        return 10  # Default estimate
    
    def _assess_risk(self, cyclomatic: int, cognitive: int, lines: int) -> str:
        """Assess complexity risk level"""
        # Critical: Very high complexity
        if cyclomatic > 20 or cognitive > 30 or lines > 200:
            return "CRITICAL"
        # High: High complexity
        elif cyclomatic > 10 or cognitive > 15 or lines > 100:
            return "HIGH"
        # Medium: Moderate complexity
        elif cyclomatic > 5 or cognitive > 8 or lines > 50:
            return "MEDIUM"
        # Low: Simple function
        else:
            return "LOW"
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """Get recent analysis history"""
        return self.analysis_history[-limit:]


# Tool schema
COMPLEXITY_ANALYZE_SCHEMA = {
    "name": "analyze_complexity",
    "description": "Analyze code complexity metrics",
    "parameters": {
        "file_path": {"type": "string", "required": True}
    }
}
