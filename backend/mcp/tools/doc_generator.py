"""
Documentation Generator - Auto-generate docs from code
Extracts docstrings, function signatures, and creates markdown/HTML documentation
"""
import ast
from typing import Dict, Any, List, Optional
from pathlib import Path
import json


class DocumentationGenerator:
    """
    Auto-generate project documentation
    Supports Python, JavaScript/TypeScript
    Output formats: Markdown, HTML
    """
    
    def __init__(self):
        self.generation_history = []
        
    def get_schema(self, tool_name: str) -> Optional[Dict]:
        """Get schema for documentation tools"""
        if tool_name == "generate_documentation":
            return DOC_GENERATOR_SCHEMA
        return None
    
    async def generate_docs(
        self,
        project_dir: str,
        output_format: str = "markdown",
        include_private: bool = False
    ) -> Dict[str, Any]:
        """
        Generate documentation for project
        
        Args:
            project_dir: Project root directory
            output_format: Output format (markdown, html)
            include_private: Include private members
            
        Returns:
            {
                "success": bool,
                "documentation": str,
                "files_processed": int
            }
        """
        try:
            project_path = Path(project_dir)
            
            # Collect all Python files
            python_files = list(project_path.rglob("*.py"))
            
            # Skip common directories
            python_files = [
                f for f in python_files
                if not any(part in f.parts for part in ['__pycache__', 'venv', 'node_modules', '.git'])
            ]
            
            print(f"📚 Generating documentation for {len(python_files)} files...")
            
            # Extract documentation
            modules = []
            for file_path in python_files:
                module_doc = self._extract_module_docs(file_path, include_private)
                if module_doc:
                    modules.append(module_doc)
            
            # Generate output
            if output_format == "markdown":
                documentation = self._generate_markdown(modules, project_path.name)
            elif output_format == "html":
                documentation = self._generate_html(modules, project_path.name)
            else:
                return {"success": False, "error": f"Unsupported format: {output_format}"}
            
            # Record in history
            self.generation_history.append({
                "project": project_dir,
                "files": len(python_files),
                "format": output_format
            })
            
            return {
                "success": True,
                "documentation": documentation,
                "files_processed": len(python_files),
                "modules": len(modules)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_module_docs(self, file_path: Path, include_private: bool) -> Optional[Dict]:
        """Extract documentation from a Python module"""
        try:
            code = file_path.read_text(encoding='utf-8')
            tree = ast.parse(code)
            
            # Module docstring
            module_docstring = ast.get_docstring(tree)
            
            # Extract classes and functions
            classes = []
            functions = []
            
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    if not include_private and node.name.startswith('_'):
                        continue
                    classes.append(self._extract_class_docs(node, include_private))
                
                elif isinstance(node, ast.FunctionDef):
                    if not include_private and node.name.startswith('_'):
                        continue
                    functions.append(self._extract_function_docs(node))
            
            if not (classes or functions):
                return None
            
            return {
                "name": file_path.stem,
                "path": str(file_path),
                "docstring": module_docstring or "",
                "classes": classes,
                "functions": functions
            }
            
        except Exception:
            return None
    
    def _extract_class_docs(self, node: ast.ClassDef, include_private: bool) -> Dict:
        """Extract documentation from a class"""
        methods = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if not include_private and item.name.startswith('_') and item.name != '__init__':
                    continue
                methods.append(self._extract_function_docs(item))
        
        return {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "methods": methods,
            "bases": [self._get_name(base) for base in node.bases]
        }
    
    def _extract_function_docs(self, node: ast.FunctionDef) -> Dict:
        """Extract documentation from a function"""
        # Extract parameters
        params = []
        for arg in node.args.args:
            param_info = {"name": arg.arg}
            if arg.annotation:
                param_info["type"] = self._get_annotation(arg.annotation)
            params.append(param_info)
        
        # Extract return type
        return_type = None
        if node.returns:
            return_type = self._get_annotation(node.returns)
        
        return {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "params": params,
            "return_type": return_type,
            "is_async": isinstance(node, ast.AsyncFunctionDef)
        }
    
    def _get_name(self, node) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "Unknown"
    
    def _get_annotation(self, node) -> str:
        """Get type annotation as string"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return f"{self._get_annotation(node.value)}[{self._get_annotation(node.slice)}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return "Any"
    
    def _generate_markdown(self, modules: List[Dict], project_name: str) -> str:
        """Generate Markdown documentation"""
        lines = [
            f"# {project_name} Documentation",
            "",
            "Auto-generated API documentation",
            "",
            "## Table of Contents",
            ""
        ]
        
        # TOC
        for module in modules:
            lines.append(f"- [{module['name']}](#{module['name'].lower()})")
        
        lines.extend(["", "---", ""])
        
        # Module documentation
        for module in modules:
            lines.extend([
                f"## {module['name']}",
                "",
                module['docstring'],
                ""
            ])
            
            # Classes
            for cls in module['classes']:
                lines.extend([
                    f"### class `{cls['name']}`",
                    "",
                    cls['docstring'],
                    ""
                ])
                
                # Methods
                for method in cls['methods']:
                    params_str = ", ".join(p['name'] for p in method['params'])
                    async_prefix = "async " if method['is_async'] else ""
                    lines.extend([
                        f"#### {async_prefix}`{method['name']}({params_str})`",
                        "",
                        method['docstring'],
                        ""
                    ])
            
            # Functions
            for func in module['functions']:
                params_str = ", ".join(p['name'] for p in func['params'])
                async_prefix = "async " if func['is_async'] else ""
                lines.extend([
                    f"### {async_prefix}`{func['name']}({params_str})`",
                    "",
                    func['docstring'],
                    ""
                ])
        
        return "\n".join(lines)
    
    def _generate_html(self, modules: List[Dict], project_name: str) -> str:
        """Generate HTML documentation"""
        # Simple HTML template
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{project_name} Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
        pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; }}
        code {{ background: #e8e8e8; padding: 2px 5px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>{project_name} Documentation</h1>
    <p>Auto-generated API documentation</p>
"""
        
        for module in modules:
            html += f"<h2>{module['name']}</h2>\n"
            html += f"<p>{module['docstring']}</p>\n"
            
            for cls in module['classes']:
                html += f"<h3>class {cls['name']}</h3>\n"
                html += f"<p>{cls['docstring']}</p>\n"
        
        html += "</body>\n</html>"
        return html
    
    def get_generation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent documentation generation history"""
        return self.generation_history[-limit:]


# Tool schema
DOC_GENERATOR_SCHEMA = {
    "name": "generate_documentation",
    "description": "Auto-generate project documentation",
    "parameters": {
        "project_dir": {"type": "string", "required": True},
        "output_format": {"type": "string", "required": False},
        "include_private": {"type": "boolean", "required": False}
    }
}
