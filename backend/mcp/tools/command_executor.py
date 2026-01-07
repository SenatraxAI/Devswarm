"""
Command Executor - Safe command execution for agents
Implements whitelist validation and dangerous pattern blocking
"""
import asyncio
import subprocess
from typing import Dict, Any, List,  Optional
from pathlib import Path


class CommandExecutor:
    """
    Safe command execution with security controls
    Enables agents to run builds, tests, and installations
    """
    
    # Allowed commands (whitelist)
    ALLOWED_COMMANDS = {
        # Python
        "python", "python3", "pip", "pip3", "pytest", "mypy", "ruff",
        # Node.js
        "node", "npm", "npx", "yarn", "pnpm", "jest",
        # Build tools
        "make", "cmake", "cargo",
        # Version control
        "git",
        # Containers
        "docker", "docker-compose",
        # Utilities
        "ls", "cat", "grep", "find", "echo"
    }
    
    # Dangerous patterns (always blocked)
    BLOCKED_PATTERNS = [
        "rm -rf /",          # Recursive delete root
        "rm -rf .",
        "rm -rf *",
        "> /dev/null",       # Output redirection tricks
        "curl | bash",       # Pipe to shell
        "wget | sh",
        "eval",              # Code evaluation
        "exec",              
        "sudo",              # Privilege escalation
        "su ",
        "chmod 777",         # Dangerous permissions
        "chown",
        ";",                 # Command chaining
        "&&",
        "||",
        "|"                  # Piping (too risky)
    ]
    
    DEFAULT_TIMEOUT = 30  # seconds
    MAX_OUTPUT_SIZE = 10000  # characters
    
    def __init__(self):
        self.execution_history = []
    
    async def execute(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """
        Execute a command safely
        
        Args:
            command: Command to execute
            cwd: Working directory (optional)
            timeout: Execution timeout in seconds
            
        Returns:
            {
                "success": bool,
                "exit_code": int,
                "stdout": str,
                "stderr": str,
                "command": str,
                "error": str (if failed)
            }
        """
        # Validate command
        validation_error = self._validate_command(command)
        if validation_error:
            return {
                "success": False,
                "error": validation_error,
                "command": command
            }
        
        # Validate working directory
        if cwd:
            cwd_path = Path(cwd)
            if not cwd_path.exists():
                return {
                    "success": False,
                    "error": f"Working directory does not exist: {cwd}",
                    "command": command
                }
        
        # Execute command
        try:
            print(f"🔧 Executing: {command}")
            if cwd:
                print(f"   Working directory: {cwd}")
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            # Wait with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": f"Command timed out after {timeout}s",
                    "command": command
                }
            
            # Decode output
            stdout_str = stdout.decode('utf-8', errors='replace')
            stderr_str = stderr.decode('utf-8', errors='replace')
            
            # Truncate if too large
            if len(stdout_str) > self.MAX_OUTPUT_SIZE:
                stdout_str = stdout_str[:self.MAX_OUTPUT_SIZE] + "\n... (truncated)"
            
            if len(stderr_str) > self.MAX_OUTPUT_SIZE:
                stderr_str = stderr_str[:self.MAX_OUTPUT_SIZE] + "\n... (truncated)"
            
            # Record execution
            self.execution_history.append({
                "command": command,
                "exit_code": process.returncode,
                "success": process.returncode == 0
            })
            
            return {
                "success": process.returncode == 0,
                "exit_code": process.returncode,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "command": command
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    def _validate_command(self, command: str) -> Optional[str]:
        """
        Validate command against whitelist and blocklist
        
        Returns:
            Error message if invalid, None if valid
        """
        # Check for blocked patterns
        command_lower = command.lower()
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in command_lower:
                return f"Blocked: Command contains dangerous pattern '{pattern}'"
        
        # Extract base command
        parts = command.strip().split()
        if not parts:
            return "Empty command"
        
        base_command = parts[0]
        
        # Check whitelist
        if base_command not in self.ALLOWED_COMMANDS:
            return f"Blocked: '{base_command}' not in allowed commands list"
        
        return None
    
    def get_allowed_commands(self) -> List[str]:
        """Get list of allowed commands"""
        return sorted(self.ALLOWED_COMMANDS)
    
    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent command execution history"""
        return self.execution_history[-limit:]


# Tool schema for MCP registration
COMMAND_EXECUTOR_SCHEMA = {
    "name": "execute_command",
    "description": "Execute a command safely with security controls",
    "parameters": {
        "command": {
            "type": "string",
            "description": "Command to execute",
            "required": True
        },
        "cwd": {
            "type": "string",
            "description": "Working directory (optional)",
            "required": False
        },
        "timeout": {
            "type": "integer",
            "description": "Timeout in seconds (default: 30)",
            "required": False
        }
    }
}
