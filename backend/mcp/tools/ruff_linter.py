"""
Ruff Linter - Fast Python code quality tool
Integrates Ruff for linting and formatting
"""
import asyncio
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class RuffLinter:
    """
    Python code quality via Ruff
    10-100x faster than Flake8/Black
    """
    
    def __init__(self):
        self.lint_history = []
        self.description = "Lint and format Python code with Ruff"

    def get_schema(self, tool_name: str) -> Optional[Dict]:
        """Get schema for a specific ruff operation"""
        mapping = {
            "lint_python": RUFF_LINTER_SCHEMA, # Registry name is lint_python
            "ruff_lint": RUFF_LINTER_SCHEMA,
            "ruff_format": RUFF_FORMAT_SCHEMA
        }
        return mapping.get(tool_name)
    
    async def lint(
        self,
        file_path: str,
        fix: bool = False
    ) -> Dict[str, Any]:
        """
        Lint a Python file with Ruff
        
        Args:
            file_path: Path to Python file
            fix: Whether to auto-fix issues
            
        Returns:
            {
                "success": bool,
                "violations": list,
                "fixed": int (if fix=True),
                "file_path": str
            }
        """
        # Validate file exists
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        if not file_path.endswith('.py'):
            return {
                "success": False,
                "error": "Not a Python file"
            }
        
        # Build command
        cmd_parts = ["ruff", "check"]
        if fix:
            cmd_parts.append("--fix")
        cmd_parts.extend(["--output-format", "json", file_path])
        
        command = " ".join(cmd_parts)
        
        # Execute
        try:
            print(f"🔍 Linting: {file_path}")
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Parse JSON output
            if stdout:
                violations = json.loads(stdout.decode('utf-8'))
            else:
                violations = []
            
            # Count fixed if applicable
            fixed_count = 0
            if fix and stderr:
                # Ruff outputs fix summary to stderr
                stderr_text = stderr.decode('utf-8')
                if "fixed" in stderr_text.lower():
                    # Parse fixed count from output
                    # Format: "Fixed X errors"
                    import re
                    match = re.search(r'Fixed (\d+)', stderr_text)
                    if match:
                        fixed_count = int(match.group(1))
            
            result = {
                "success": True,
                "violations": violations,
                "file_path": file_path,
                "violation_count": len(violations)
            }
            
            if fix:
                result["fixed"] = fixed_count
            
            # Record in history
            self.lint_history.append({
                "file": file_path,
                "violations": len(violations),
                "fixed": fixed_count if fix else 0
            })
            
            return result
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Failed to parse Ruff output"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def format(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Format a Python file with Ruff
        
        Args:
            file_path: Path to Python file
            
        Returns:
            {
                "success": bool,
                "formatted": bool,
                "file_path": str
            }
        """
        # Validate file
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # Execute format
        try:
            print(f"✨ Formatting: {file_path}")
            
            process = await asyncio.create_subprocess_shell(
                f"ruff format {file_path}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Check if file was changed
            output = stdout.decode('utf-8') if stdout else ""
            formatted = "1 file reformatted" in output or "reformatted" in output.lower()
            
            return {
                "success": True,
                "formatted": formatted,
                "file_path": file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_installation(self) -> bool:
        """Check if Ruff is installed"""
        try:
            process = await asyncio.create_subprocess_shell(
                "ruff --version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            return process.returncode == 0
            
        except:
            return False
    
    def get_lint_history(self, limit: int = 10) -> List[Dict]:
        """Get recent linting history"""
        return self.lint_history[-limit:]


# Tool schema for MCP registration
RUFF_LINTER_SCHEMA = {
    "name": "ruff_lint",
    "description": "Lint Python code with Ruff (fast Python linter)",
    "parameters": {
        "file_path": {
            "type": "string",
            "description": "Path to Python file",
            "required": True
        },
        "fix": {
            "type": "boolean",
            "description": "Auto-fix violations (default: false)",
            "required": False
        }
    }
}

RUFF_FORMAT_SCHEMA = {
    "name": "ruff_format",
    "description": "Format Python code with Ruff formatter",
    "parameters": {
        "file_path": {
            "type": "string",
            "description": "Path to Python file",
            "required": True
        }
    }
}
