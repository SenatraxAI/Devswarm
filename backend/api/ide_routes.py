"""
IDE Routes - Specialized endpoints for the professional IDE interface
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
from storage.project_manager import ProjectManager

router = APIRouter(prefix="/ide", tags=["ide"])
project_manager = ProjectManager()

class FileNode(BaseModel):
    name: str
    path: str
    type: str  # 'file' or 'directory'
    size: Optional[int] = None
    children: Optional[List['FileNode']] = None

FileNode.update_forward_refs()

@router.get("/{project_id}/files", response_model=List[FileNode])
async def list_project_files(project_id: str, path: str = "."):
    """List files in a project directory recursively or shallowly"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    root_path = Path(project["root_path"])
    target_path = root_path / path
    
    if not target_path.exists() or not target_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid directory path")
    
    nodes = []
    try:
        for item in target_path.iterdir():
            # Skip hidden files and __pycache__
            if item.name.startswith('.') or item.name == "__pycache__":
                continue
                
            nodes.append({
                "name": item.name,
                "path": item.relative_to(root_path).as_posix(),
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Sort: directories first, then alphabetical
    return sorted(nodes, key=lambda x: (x["type"] != "directory", x["name"].lower()))

@router.get("/{project_id}/file-content")
async def get_file_content(project_id: str, path: str):
    """Read file content for the code editor"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    file_path = Path(project["root_path"]) / path
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        content = file_path.read_text(encoding='utf-8')
        return {"content": content, "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

class SaveFileRequest(BaseModel):
    content: str

@router.post("/{project_id}/save-file")
async def save_file(project_id: str, path: str, request: SaveFileRequest):
    """Save editor content to disk"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    file_path = Path(project["root_path"]) / path
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(request.content, encoding='utf-8')
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
