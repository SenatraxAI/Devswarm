"""
Project Routes - API endpoints for project management
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
from storage.project_manager import ProjectManager
import subprocess

router = APIRouter(prefix="/projects", tags=["projects"])
project_manager = ProjectManager()

class ProjectOpenRequest(BaseModel):
    path: str
    name: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    root_path: str
    last_accessed: float
    created_at: Optional[float] = None

@router.get("", response_model=List[ProjectResponse])
async def list_projects():
    """List all registered projects"""
    return project_manager.list_projects()

@router.post("/open", response_model=ProjectResponse)
async def open_project(req: ProjectOpenRequest):
    """Register and open a local project folder"""
    try:
        project = project_manager.open_project(req.path, req.name)
        return project
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pick")
async def pick_folder():
    """Triggers native OS folder picker with PowerShell bridge"""
    powershell_cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Add-Type -AssemblyName System.Windows.Forms; "
        "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
        "$f.Description = 'Select Project Folder'; "
        "if($f.ShowDialog() -eq 'OK'){ $f.SelectedPath }"
    ]
    
    try:
        # Run PS command and capture output
        result = subprocess.run(powershell_cmd, capture_output=True, text=True, check=True)
        path = result.stdout.strip()
        
        if not path:
            return {"status": "cancelled"}
            
        return {"status": "success", "path": path}
    except Exception as e:
        print(f"❌ Picker Error: {e}")
        raise HTTPException(status_code=500, detail=f"Native picker failed: {str(e)}")

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get project details"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/{project_id}/touch")
async def touch_project(project_id: str):
    """Update last accessed timestamp"""
    project_manager.update_project_access(project_id)
    return {"status": "success"}
