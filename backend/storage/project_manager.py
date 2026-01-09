"""
Project Manager - Maintains the registry of projects and their root paths
Stores data in data/projects.json
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
import uuid

class ProjectManager:
    """
    Manages the list of projects known to DevSwarm.
    Maps project IDs to absolute filesystem paths.
    """
    def __init__(self, data_dir: str = "data"):
        self.registry_file = Path(data_dir) / "projects.json"
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.projects: Dict[str, Dict[str, Any]] = self._load()

    def _load(self) -> Dict[str, Dict[str, Any]]:
        """Load project registry from disk"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading project registry: {e}")
        return {
            "default": {
                "name": "DevSwarm Core",
                "root_path": os.getcwd(),
                "last_accessed": time.time(),
                "id": "default"
            }
        }

    def save(self):
        """Save project registry to disk"""
        try:
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(self.projects, f, indent=4)
        except Exception as e:
            print(f"⚠️ Error saving project registry: {e}")

    def list_projects(self) -> List[Dict[str, Any]]:
        """Return list of projects sorted by last accessed"""
        return sorted(
            self.projects.values(),
            key=lambda x: x.get("last_accessed", 0),
            reverse=True
        )

    def open_project(self, path: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Register or update a project by its root path
        """
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Path does not exist: {abs_path}")
        
        # Check if project already exists
        for p_id, p_data in self.projects.items():
            if p_data.get("root_path") == abs_path:
                p_data["last_accessed"] = time.time()
                self.save()
                return p_data

        # Create new project
        p_id = str(uuid.uuid4())[:8]
        project_name = name or os.path.basename(abs_path) or "Unnamed Project"
        
        project_data = {
            "id": p_id,
            "name": project_name,
            "root_path": abs_path,
            "last_accessed": time.time(),
            "created_at": time.time()
        }
        
        self.projects[p_id] = project_data
        self.save()
        self.projects[p_id] = project_data
        self.save()
        return project_data

    def create_project(self, parent_path: str, name: str) -> Dict[str, Any]:
        """Create a new project directory and register it"""
        abs_parent = os.path.abspath(parent_path)
        if not os.path.exists(abs_parent):
             raise FileNotFoundError(f"Parent path does not exist: {abs_parent}")
            
        project_path = os.path.join(abs_parent, name)
        
        # Create directory
        try:
            os.makedirs(project_path, exist_ok=False)
        except FileExistsError:
            raise FileExistsError(f"Directory already exists: {project_path}")
            
        # Register as open project
        return self.open_project(project_path, name)

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project details by ID"""
        return self.projects.get(project_id)

    def update_project_access(self, project_id: str):
        """Update last accessed timestamp"""
        if project_id in self.projects:
            self.projects[project_id]["last_accessed"] = time.time()
            self.save()
