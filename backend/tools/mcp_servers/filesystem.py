"""
Filesystem MCP Server
Provides file operations: read, write, list, search
"""
from typing import Dict, List, Any
import os
import asyncio
from pathlib import Path
import fnmatch

from tools.mcp_host import MCPServer, MCPTool


class FilesystemMCPServer(MCPServer):
    """MCP Server for filesystem operations"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.workspace_root = Path.cwd()  # Default to current directory
    
    async def connect(self):
        """Connect to filesystem server (no actual connection needed)"""
        self.is_connected = True
    
    async def disconnect(self):
        """Disconnect from filesystem server"""
        self.is_connected = False
    
    async def discover_tools(self) -> List[MCPTool]:
        """Discover available filesystem tools"""
        tools = [
            MCPTool(
                name="fs_read_file",
                description="Read contents of a file",
                schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file"},
                    },
                    "required": ["path"]
                },
                server=self.name
            ),
            MCPTool(
                name="fs_write_file",
                description="Write content to a file",
                schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file"},
                        "content": {"type": "string", "description": "Content to write"},
                    },
                    "required": ["path", "content"]
                },
                server=self.name
            ),
            MCPTool(
                name="fs_list_directory",
                description="List files and directories",
                schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"},
                    },
                    "required": ["path"]
                },
                server=self.name
            ),
            MCPTool(
                name="fs_search_files",
                description="Search for files by pattern",
                schema={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Glob pattern"},
                        "path": {"type": "string", "description": "Search directory"},
                    },
                    "required": ["pattern"]
                },
                server=self.name
            ),
        ]
        
        self.tools = {tool.name: tool for tool in tools}
        return tools
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a filesystem tool"""
        if tool_name == "fs_read_file":
            return await self._read_file(arguments["path"])
        elif tool_name == "fs_write_file":
            return await self._write_file(arguments["path"], arguments["content"])
        elif tool_name == "fs_list_directory":
            return await self._list_directory(arguments["path"])
        elif tool_name == "fs_search_files":
            return await self._search_files(
                arguments["pattern"],
                arguments.get("path", ".")
            )
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_file(self, path: str) -> Dict[str, Any]:
        """Read a file"""
        try:
            file_path = Path(path)
            if not file_path.exists():
                return {"error": f"File not found: {path}"}
            
            content = file_path.read_text(encoding="utf-8")
            return {
                "path": str(file_path),
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write to a file"""
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            return {
                "path": str(file_path),
                "size": len(content),
                "success": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _list_directory(self, path: str) -> Dict[str, Any]:
        """List directory contents"""
        try:
            dir_path = Path(path)
            if not dir_path.exists():
                return {"error": f"Directory not found: {path}"}
            
            items = []
            for item in dir_path.iterdir():
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return {
                "path": str(dir_path),
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _search_files(self, pattern: str, path: str = ".") -> Dict[str, Any]:
        """Search for files matching a pattern"""
        try:
            search_path = Path(path)
            matches = []
            
            for file_path in search_path.rglob(pattern):
                matches.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "is_dir": file_path.is_dir()
                })
            
            return {
                "pattern": pattern,
                "search_path": str(search_path),
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            return {"error": str(e)}
