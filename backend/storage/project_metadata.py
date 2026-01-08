"""
Project Metadata - Persists project-specific settings and user identity
Stores metadata in a project-specific JSON file
"""
import json
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
        """Load metadata from disk"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading metadata for {self.project_id}: {e}")
        return {
            "project_name": self.project_id,
            "user_name": "Boss",
            "user_role": "Project Owner",
            "goals": []
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
