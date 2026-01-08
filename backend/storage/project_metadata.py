"""
Project Metadata - Persists project-specific settings and user identity
Stores metadata in a project-specific JSON file
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ProjectMetadata:
    """
    Manages project-specific metadata (User Name, Role, Goals, etc.)
    Stores data in data/events/{project_id}/metadata.json
    """
    def __init__(self, project_id: str = "default", data_dir: str = "data/events"):
        self.project_id = project_id
        self.metadata_file = Path(data_dir) / project_id / "metadata.json"
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load metadata from disk, falling back to global UserConfig"""
        project_data = {}
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    project_data = json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading metadata for {self.project_id}: {e}")
        
        # Load global defaults
        from storage.user_config import UserConfig
        global_config = UserConfig().get_all()
        
        # Merge: Project specific > Global defaults > Hardcoded defaults
        return {
            "project_id": self.project_id,
            "project_name": project_data.get("project_name", self.project_id),
            "root_path": project_data.get("root_path", os.getcwd()),
            "user_name": project_data.get("user_name", global_config.get("name", "Boss")),
            "user_role": project_data.get("user_role", global_config.get("role", "Lead Developer")),
            "user_company": project_data.get("user_company", global_config.get("company", "DevSwarm AI")),
            "goals": project_data.get("goals", []),
            **{k: v for k, v in project_data.items() if k not in ["project_id", "project_name", "root_path", "user_name", "user_role", "user_company", "goals"]}
        }

    def save(self):
        """Save metadata to disk"""
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"⚠️ Error saving metadata for {self.project_id}: {e}")

    def update(self, **kwargs):
        """Update multiple metadata fields"""
        self.data.update(kwargs)
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific metadata value"""
        return self.data.get(key, default)
