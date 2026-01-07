"""
Security Scanner - Static analysis for vulnerability detection
Identifies common security issues via pattern matching and AST analysis
"""
import re
import ast
from typing import Dict, Any, List, Optional
from pathlib import Path
from enum import Enum


class Severity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SecurityScanner:
    """
    Static security analysis tool
    Detects: SQL injection, XSS, hardcoded secrets, command injection
    """
    
    # Regex patterns for vulnerability detection
    PATTERNS = {
        "sql_injection": {
            "patterns": [
                r'execute\s*\(["\'].*\+.*["\']',  # String concatenation
                r'cursor\.execute.*%.*%',          # Old-style formatting
                r'f"SELECT.*{.*}"',                # f-string in SQL
            ],
            "severity": Severity.CRITICAL,
            "description": "Potential SQL injection via string concatenation"
        },
        "command_injection": {
            "patterns": [
                r'os\.system\s*\(.*\+',
                r'subprocess\.(call|run|Popen)\s*\(.*shell\s*=\s*True',
            ],
            "severity": Severity.CRITICAL,
            "description": "Command injection via shell execution"
        },
        "xss": {
            "patterns": [
                r'innerHTML\s*=',
                r'dangerouslySetInnerHTML',
                r'document\.write\s*\(',
            ],
            "severity": Severity.HIGH,
            "description": "Potential XSS via unsafe HTML rendering"
        },
        "hardcoded_secrets": {
            "patterns": [
                r'password\s*=\s*["\'][^"\']{8,}["\']',
                r'api_key\s*=\s*["\'][a-zA-Z0-9]{20,}["\']',
                r'secret\s*=\s*["\'][^"\']{8,}["\']',
                r'token\s*=\s*["\'][a-zA-Z0-9]{20,}["\']',
            ],
            "severity": Severity.HIGH,
            "description": "Hardcoded secret detected"
        },
        "path_traversal": {
            "patterns": [
                r'open\s*\([^)]*\+',
                r'os\.path\.join\s*\([^)]*input',
            ],
            "severity": Severity.HIGH,
            "description": "Path traversal via user input"
        },
        "weak_crypto": {
            "patterns": [
                r'md5\s*\(',
                r'sha1\s*\(',
                r'DES',
            ],
            "severity": Severity.MEDIUM,
            "description": "Weak cryptographic algorithm"
        }
    }
    
    def __init__(self):
        self.scan_history = []
    
    async def scan_file(
        self,
        file_path: str,
        scan_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Scan file for security vulnerabilities
        
        Args:
            file_path: Path to file
            scan_types: Specific vulnerability types to check (None = all)
            
        Returns:
            {
                "success": bool,
                "vulnerabilities": list,
                "summary": dict
            }
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": "File not found"}
            
            # Read file content
            content = path.read_text(encoding='utf-8')
            
            # Detect vulnerabilities
            vulnerabilities = []
            
            # Pattern-based detection
            for vuln_type, config in self.PATTERNS.items():
                if scan_types and vuln_type not in scan_types:
                    continue
                
                for pattern in config["patterns"]:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        vulnerabilities.append({
                            "type": vuln_type,
                            "severity": config["severity"].value,
                            "description": config["description"],
                            "line": line_num,
                            "code": match.group(0)[:100]  # Truncate long matches
                        })
            
            # AST-based checks (Python only)
            if path.suffix == '.py':
                ast_vulns = self._ast_analysis(content, path.name)
                vulnerabilities.extend(ast_vulns)
            
            # Generate summary
            summary = {
                "total": len(vulnerabilities),
                "critical": sum(1 for v in vulnerabilities if v["severity"] == "CRITICAL"),
                "high": sum(1 for v in vulnerabilities if v["severity"] == "HIGH"),
                "medium": sum(1 for v in vulnerabilities if v["severity"] == "MEDIUM"),
                "low": sum(1 for v in vulnerabilities if v["severity"] == "LOW")
            }
            
            # Record in history
            self.scan_history.append({
                "file": file_path,
                "vulnerabilities": len(vulnerabilities),
                "critical": summary["critical"]
            })
            
            return {
                "success": True,
                "file": file_path,
                "vulnerabilities": vulnerabilities,
                "summary": summary
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _ast_analysis(self, code: str, filename: str) -> List[Dict]:
        """AST-based security checks"""
        vulnerabilities = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for eval/exec usage
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec']:
                            vulnerabilities.append({
                                "type": "dangerous_function",
                                "severity": Severity.CRITICAL.value,
                                "description": f"Use of dangerous function: {node.func.id}",
                                "line": node.lineno,
                                "code": f"{node.func.id}(...)"
                            })
                
                # Check for assert usage (can be disabled with -O)
                if isinstance(node, ast.Assert):
                    vulnerabilities.append({
                        "type": "assert_security",
                        "severity": Severity.LOW.value,
                        "description": "Assert statements disabled in optimized mode",
                        "line": node.lineno,
                        "code": "assert ..."
                    })
        
        except SyntaxError:
            pass  # Skip files with syntax errors
        
        return vulnerabilities
    
    async def scan_project(
        self,
        project_dir: str,
        file_patterns: List[str] = ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx"]
    ) -> Dict[str, Any]:
        """
        Scan entire project directory
        
        Args:
            project_dir: Project root directory
            file_patterns: File patterns to scan
            
        Returns:
            {
                "success": bool,
                "files_scanned": int,
                "total_vulnerabilities": int,
                "files_with_issues": list
            }
        """
        try:
            project_path = Path(project_dir)
            all_vulnerabilities = []
            files_scanned = 0
            
            for pattern in file_patterns:
                for file_path in project_path.rglob(pattern):
                    # Skip common ignore directories
                    if any(part in file_path.parts for part in ['node_modules', '__pycache__', '.git', 'venv']):
                        continue
                    
                    result = await self.scan_file(str(file_path))
                    if result["success"] and result.get("vulnerabilities"):
                        all_vulnerabilities.append({
                            "file": str(file_path.relative_to(project_path)),
                            "vulnerabilities": result["vulnerabilities"],
                            "summary": result["summary"]
                        })
                    
                    files_scanned += 1
            
            total_vulns = sum(f["summary"]["total"] for f in all_vulnerabilities)
            
            return {
                "success": True,
                "files_scanned": files_scanned,
                "total_vulnerabilities": total_vulns,
                "files_with_issues": all_vulnerabilities
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_scan_history(self, limit: int = 10) -> List[Dict]:
        """Get recent scan history"""
        return self.scan_history[-limit:]


# Tool schemas
SECURITY_SCAN_FILE_SCHEMA = {
    "name": "scan_security",
    "description": "Scan file for security vulnerabilities",
    "parameters": {
        "file_path": {"type": "string", "required": True},
        "scan_types": {"type": "array", "required": False}
    }
}

SECURITY_SCAN_PROJECT_SCHEMA = {
    "name": "scan_project_security",
    "description": "Scan entire project for vulnerabilities",
    "parameters": {
        "project_dir": {"type": "string", "required": True},
        "file_patterns": {"type": "array", "required": False}
    }
}
