"""
Filesystem Tool - Enhanced file operations with safety controls
Provides read, write, search, and directory operations
"""
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import fnmatch


class FilesystemTool:
    """
    Safe filesystem operations for agents
    Respects access boundaries and implements safety controls
    """
    
    def __init__(self, allowed_paths: Optional[List[str]] = None):
        """
        Initialize filesystem tool
        
        Args:
            allowed_paths: List of allowed directory paths (default: current project)
        """
        self.allowed_paths = allowed_paths or [os.getcwd()]
        self.operation_history = []
    
    def _is_path_allowed(self, path: str) -> bool:
        """Check if path is within allowed boundaries"""
        abs_path = os.path.abspath(path)
        
        for allowed in self.allowed_paths:
            allowed_abs = os.path.abspath(allowed)
            if abs_path.startswith(allowed_abs):
                return True
        
        return False
    
    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read file contents
        
        Args:
            file_path: Path to file
            
        Returns:
            {
                "success": bool,
                "content": str,
                "encoding": str,
                "size": int
            }
        """
        if not self._is_path_allowed(file_path):
            return {
                "success": False,
                "error": f"Access denied: {file_path} outside allowed paths"
            }
        
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {"success": False, "error": "File not found"}
            
            if not path.is_file():
                return {"success": False, "error": "Path is not a file"}
            
            # Read with UTF-8 encoding
            content = path.read_text(encoding='utf-8')
            size = path.stat().st_size
            
            self.operation_history.append({
                "operation": "read",
                "path": file_path,
                "success": True
            })
            
            return {
                "success": True,
                "content": content,
                "encoding": "utf-8",
                "size": size,
                "path": file_path
            }
            
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "File is not UTF-8 encoded (binary file?)"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def write_file(
        self,
        file_path: str,
        content: str,
        create_dirs: bool = True
    ) -> Dict[str, Any]:
        """
        Write content to file
        
        Args:
            file_path: Path to file
            content: Content to write
            create_dirs: Create parent directories if missing
            
        Returns:
            {
                "success": bool,
                "bytes_written": int
            }
        """
        if not self._is_path_allowed(file_path):
            return {
                "success": False,
                "error": f"Access denied: {file_path} outside allowed paths"
            }
        
        try:
            path = Path(file_path)
            
            # Create parent directories if needed
            if create_dirs and not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            path.write_text(content, encoding='utf-8')
            size = path.stat().st_size
            
            self.operation_history.append({
                "operation": "write",
                "path": file_path,
                "success": True
            })
            
            return {
                "success": True,
                "bytes_written": size,
                "path": file_path
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_directory(
        self,
        dir_path: str,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        List directory contents
        
        Args:
            dir_path: Directory path
            recursive: Recursively list subdirectories
            
        Returns:
            {
                "success": bool,
                "files": list,
                "directories": list
            }
        """
        if not self._is_path_allowed(dir_path):
            return {
                "success": False,
                "error": f"Access denied: {dir_path} outside allowed paths"
            }
        
        try:
            path = Path(dir_path)
            
            if not path.exists():
                return {"success": False, "error": "Directory not found"}
            
            if not path.is_dir():
                return {"success": False, "error": "Path is not a directory"}
            
            files = []
            directories = []
            
            if recursive:
                # Recursive listing
                for item in path.rglob("*"):
                    rel_path = str(item.relative_to(path))
                    if item.is_file():
                        files.append({
                            "path": rel_path,
                            "size": item.stat().st_size
                        })
                    elif item.is_dir():
                        directories.append(rel_path)
            else:
                # Single level
                for item in path.iterdir():
                    if item.is_file():
                        files.append({
                            "name": item.name,
                            "size": item.stat().st_size
                        })
                    elif item.is_dir():
                        directories.append(item.name)
            
            return {
                "success": True,
                "files": files,
                "directories": directories,
                "path": dir_path
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_files(
        self,
        dir_path: str,
        pattern: str,
        content_search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for files
        
        Args:
            dir_path: Directory to search
            pattern: Filename pattern (glob)
            content_search: Optional text to search within files
            
        Returns:
            {
                "success": bool,
                "matches": list
            }
        """
        if not self._is_path_allowed(dir_path):
            return {
                "success": False,
                "error": f"Access denied: {dir_path} outside allowed paths"
            }
        
        try:
            path = Path(dir_path)
            
            if not path.exists():
                return {"success": False, "error": "Directory not found"}
            
            matches = []
            
            # Search by filename pattern
            for item in path.rglob(pattern):
                if item.is_file():
                    match_info = {
                        "path": str(item.relative_to(path)),
                        "size": item.stat().st_size
                    }
                    
                    # Optional content search
                    if content_search:
                        try:
                            content = item.read_text(encoding='utf-8')
                            if content_search in content:
                                matches.append(match_info)
                        except:
                            pass  # Skip files that can't be read
                    else:
                        matches.append(match_info)
            
            return {
                "success": True,
                "matches": matches,
                "count": len(matches)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_directory(
        self,
        dir_path: str
    ) -> Dict[str, Any]:
        """Create directory (including parents)"""
        if not self._is_path_allowed(dir_path):
            return {
                "success": False,
                "error": f"Access denied: {dir_path} outside allowed paths"
            }
        
        try:
            path = Path(dir_path)
            path.mkdir(parents=True, exist_ok=True)
            
            return {
                "success": True,
                "path": dir_path
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Tool schemas
FILESYSTEM_READ_SCHEMA = {
    "name": "fs_read_file",
    "description": "Read contents of a file",
    "parameters": {
        "file_path": {
            "type": "string",
            "description": "Path to file",
            "required": True
        }
    }
}

FILESYSTEM_WRITE_SCHEMA = {
    "name": "fs_write_file",
    "description": "Write content to a file",
    "parameters": {
        "file_path": {"type": "string", "required": True},
        "content": {"type": "string", "required": True},
        "create_dirs": {"type": "boolean", "required": False}
    }
}

FILESYSTEM_LIST_SCHEMA = {
    "name": "fs_list_directory",
    "description": "List directory contents",
    "parameters": {
        "dir_path": {"type": "string", "required": True},
        "recursive": {"type": "boolean", "required": False}
    }
}

FILESYSTEM_SEARCH_SCHEMA = {
    "name": "fs_search_files",
    "description": "Search for files by pattern",
    "parameters": {
        "dir_path": {"type": "string", "required": True},
        "pattern": {"type": "string", "required": True},
        "content_search": {"type": "string", "required": False}
    }
}
