"""
Project Routes - API endpoints for managing multi-agent project workspaces
Handles project creation, listing, and metadata management
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import uuid
from datetime import datetime
import os

router = APIRouter(prefix="/projects", tags=["projects"])

DATA_DIR = Path("data/events")

def get_project_metadata(project_id: str) -> Dict[str, Any]:
    """Helper to read project metadata"""
    meta_path = DATA_DIR / project_id / "metadata.json"
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    
    # Return default if not found or corrupt
    return {
        "id": project_id,
        "name": project_id.capitalize(),
        "description": "No description provided",
        "created_at": datetime.now().timestamp(),
        "status": "active",
        "tags": []
    }

@router.get("/")
async def list_projects():
    """List all available project workspaces"""
    projects = []
    if not DATA_DIR.exists():
        return {"projects": []}

    for item in DATA_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            event_file = item / "events.jsonl"
            metadata = get_project_metadata(item.name)
            
            # Estimate activity based on events.jsonl
            last_active = metadata.get("created_at")
            if event_file.exists():
                last_active = os.path.getmtime(event_file)

            projects.append({
                "id": item.name,
                "name": metadata.get("name", item.name),
                "description": metadata.get("description", ""),
                "last_active": last_active,
                "created_at": metadata.get("created_at"),
                "status": metadata.get("status", "active")
            })
    
    # Sort by last active (newest first)
    projects.sort(key=lambda x: x["last_active"], reverse=True)
    return {"success": True, "projects": projects}

@router.post("/")
async def create_project(data: Dict[str, Any]):
    """Create a new project workspace"""
    name = data.get("name", "New Project")
    project_id = str(uuid.uuid4())[:8] # Short clean IDs
    
    project_dir = DATA_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    
    metadata = {
        "id": project_id,
        "name": name,
        "description": data.get("description", ""),
        "created_at": datetime.now().timestamp(),
        "status": "active",
        "tags": data.get("tags", [])
    }
    
    with open(project_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
        
    # Initialize empty events file
    (project_dir / "events.jsonl").touch()
    
    return {"success": True, "project": metadata}

@router.get("/{project_id}")
async def get_project(project_id: str):
    """Get detailed metadata for a project"""
    project_dir = DATA_DIR / project_id
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")
        
    metadata = get_project_metadata(project_id)
    
    # Add stats
    event_file = project_dir / "events.jsonl"
    event_count = 0
    if event_file.exists():
        with open(event_file, "r", encoding="utf-8") as f:
            event_count = sum(1 for line in f if line.strip())
            
    metadata["stats"] = {
        "event_count": event_count,
        "last_active": os.path.getmtime(event_file) if event_count > 0 else metadata["created_at"]
    }
    
    return {"success": True, "project": metadata}

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Archive/Delete project (for now just archive by renaming folder)"""
    project_dir = DATA_DIR / project_id
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Simple archive for now
    archive_dir = DATA_DIR / f".archived_{project_id}_{int(datetime.now().timestamp())}"
    os.rename(project_dir, archive_dir)
    
    return {"success": True, "message": f"Project {project_id} archived"}

# --- Branching & Checkpoints ---

@router.get("/{project_id}/branches")
async def list_branches(project_id: str):
    """List all unique branches in a project"""
    from storage.event_log import EventLog
    log = EventLog(project_id=project_id)
    
    # We query the SQLite index for unique branch names
    query = "SELECT DISTINCT branch_name FROM events WHERE project_id = ?"
    with log.indexer.conn_factory() as conn: # I noticed I should expose a conn_factory or just use a query helper
        cursor = conn.cursor()
        cursor.execute(query, (project_id,))
        branches = [row[0] for row in cursor.fetchall()]
    
    if not branches:
        branches = ["main"]
        
    return {"success": True, "branches": branches}

@router.post("/{project_id}/branches")
async def create_branch(project_id: str, data: Dict[str, Any]):
    """Create a new branch (checkpoint) from a parent event"""
    branch_name = data.get("name")
    parent_event_id = data.get("parent_event_id")
    
    if not branch_name:
        raise HTTPException(status_code=400, detail="Branch name required")
        
    from storage.event_log import EventLog, EventType
    log = EventLog(project_id=project_id)
    
    # Create the branch-start event
    log.append_event(
        event_type=EventType.TEAM_DECISION,
        agent="System",
        payload={
            "action": "CREATE_BRANCH",
            "branch_name": branch_name,
            "parent_event_id": parent_event_id
        },
        branch_name=branch_name,
        parent_events=[parent_event_id] if parent_event_id else []
    )
    
    return {"success": True, "message": f"Branch '{branch_name}' created"}

@router.post("/{project_id}/branches/switch")
async def switch_branch(project_id: str, data: Dict[str, Any]):
    """Switch the current active branch for the project session"""
    branch_name = data.get("name", "main")
    # This might need to update a persistent 'active_branch' in metadata.json
    
    metadata = get_project_metadata(project_id)
    metadata["active_branch"] = branch_name
    
    project_dir = DATA_DIR / project_id
    with open(project_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
        
    return {"success": True, "active_branch": branch_name}
