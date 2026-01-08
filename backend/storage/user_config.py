
import json
from pathlib import Path
from typing import Dict, Any

class UserConfig:
    """
    Manages global user configuration (Profile, Preferences).
    Stored in data/user_profile.json
    """
    def __init__(self, storage_path: str = "data/user_profile.json"):
        self.path = Path(storage_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading user profile: {e}")
        
        # Default profile
        return {
            "name": "Boss",
            "role": "Lead Developer",
            "company": "DevSwarm AI",
            "bio": "Building the future of autonomous engineering.",
            "preferences": {
                "theme": "dark",
                "natural_grammar": True,
                "agent_style": "professional_casual"
            }
        }

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"⚠️ Error saving user profile: {e}")

    def update(self, **kwargs):
        self.data.update(kwargs)
        self.save()

    def get_all(self) -> Dict[str, Any]:
        return self.data
