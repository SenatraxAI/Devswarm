"""
MCP Configuration Loader
Loads MCP server configurations from mcp_servers.json
Supports dynamic MCP server addition via config file
"""
import json
import os
from pathlib import Path
from typing import Dict, Any


class MCPConfig:
    """
    Load and manage MCP server configurations
    Allows adding new MCP servers without code changes
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize MCP Config
        
        Args:
            config_path: Path to mcp_servers.json (default: mcp/mcp_servers.json)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "mcp_servers.json"
        
        self.config_path = Path(config_path)
        self.servers = {}
        self._load_config()
    
    def _load_config(self):
        """Load MCP server configurations from JSON file"""
        if not self.config_path.exists():
            print(f"⚠️  MCP config not found: {self.config_path}")
            return
        
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            
            self.servers = data.get("mcp_servers", {})
            
            # Filter enabled servers
            enabled_count = sum(1 for s in self.servers.values() if s.get("enabled", False))
            print(f"📋 MCP Config loaded: {enabled_count}/{len(self.servers)} servers enabled")
            
        except Exception as e:
            print(f"❌ Failed to load MCP config: {e}")
    
    def get_enabled_servers(self) -> Dict[str, Any]:
        """Get all enabled MCP servers"""
        return {
            name: config
            for name, config in self.servers.items()
            if config.get("enabled", False)
        }
    
    def get_server_config(self, server_name: str) -> Dict[str, Any]:
        """Get configuration for a specific server"""
        return self.servers.get(server_name, {})
    
    def is_server_enabled(self, server_name: str) -> bool:
        """Check if a server is enabled"""
        server = self.servers.get(server_name, {})
        return server.get("enabled", False)
    
    def resolve_env_vars(self, config: Dict) -> Dict:
        """
        Resolve environment variable references in config
        Replaces ${VAR_NAME} with actual env var values
        """
        resolved = {}
        
        for key, value in config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]  # Remove ${ and }
                resolved[key] = os.getenv(env_var, "")
            elif isinstance(value, dict):
                resolved[key] = self.resolve_env_vars(value)
            else:
                resolved[key] = value
        
        return resolved
    
    def add_server_runtime(self, name: str, config: Dict):
        """
        Add a new MCP server at runtime
        (Won't persist to file, only in-memory)
        """
        self.servers[name] = config
        print(f"✅ Added MCP server: {name}")
    
    def reload_config(self):
        """Reload configuration from file"""
        self._load_config()
