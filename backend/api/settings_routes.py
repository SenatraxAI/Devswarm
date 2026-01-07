"""
Settings API Routes
Manage MCP servers, API keys, and tool configurations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
from pathlib import Path

router = APIRouter(prefix="/api/settings", tags=["settings"])


class MCPServerConfig(BaseModel):
    """MCP Server configuration"""
    enabled: bool
    type: str
    transport: Optional[str] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    description: str
    config: Dict[str, Any] = {}


class APIKeyUpdate(BaseModel):
    """API Key update request"""
    key_name: str
    value: str


@router.get("/mcp-servers")
async def get_mcp_servers():
    """Get all MCP server configurations"""
    try:
        config_path = Path("backend/mcp/mcp_servers.json")
        
        if not config_path.exists():
            return {"servers": {}}
        
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        return {"servers": data.get("mcp_servers", {})}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp-servers/{server_name}")
async def update_mcp_server(server_name: str, config: MCPServerConfig):
    """Update or add MCP server configuration"""
    try:
        config_path = Path("backend/mcp/mcp_servers.json")
        
        # Load existing config
        if config_path.exists():
            with open(config_path, 'r') as f:
                data = json.load(f)
        else:
            data = {"mcp_servers": {}}
        
        # Update server config
        data["mcp_servers"][server_name] = config.dict()
        
        # Save
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {"success": True, "message": f"Server '{server_name}' updated"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/mcp-servers/{server_name}")
async def delete_mcp_server(server_name: str):
    """Delete MCP server configuration"""
    try:
        config_path = Path("backend/mcp/mcp_servers.json")
        
        if not config_path.exists():
            raise HTTPException(status_code=404, detail="Config not found")
        
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        if server_name not in data.get("mcp_servers", {}):
            raise HTTPException(status_code=404, detail=f"Server '{server_name}' not found")
        
        # Remove server
        del data["mcp_servers"][server_name]
        
        # Save
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {"success": True, "message": f"Server '{server_name}' deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api-keys")
async def get_api_keys():
    """Get API key status (not actual values for security)"""
    import os
    
    keys = {
        "TAVILY_API_KEY": {
            "configured": bool(os.getenv("TAVILY_API_KEY")),
            "description": "Tavily web search API"
        },
        "SNYK_TOKEN": {
            "configured": bool(os.getenv("SNYK_TOKEN")),
            "description": "Snyk dependency scanner"
        },
        "CONTEXT7_API_KEY": {
            "configured": bool(os.getenv("CONTEXT7_API_KEY")),
            "description": "Context7 documentation lookup"
        },
        "GITHUB_TOKEN": {
            "configured": bool(os.getenv("GITHUB_TOKEN")),
            "description": "GitHub personal access token"
        }
    }
    
    return {"api_keys": keys}


@router.post("/api-keys")
async def update_api_key(update: APIKeyUpdate):
    """Update API key in .env file"""
    try:
        env_path = Path("backend/.env")
        
        # Read existing .env
        env_vars = {}
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        # Update key
        env_vars[update.key_name] = update.value
        
        # Write back
        with open(env_path, 'w') as f:
            f.write("# DevSwarm Environment Variables\n")
            f.write("# Auto-updated via Settings UI\n\n")
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        return {"success": True, "message": f"API key '{update.key_name}' updated"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tool-access")
async def get_tool_access():
    """Get tool access matrix"""
    from mcp.access_control import AccessControl
    
    ac = AccessControl()
    summary = ac.get_tool_usage_summary()
    
    return {"tool_access": summary}


@router.get("/reload")
async def reload_configuration():
    """Reload MCP configuration (restart required for full effect)"""
    try:
        from mcp.mcp_config import MCPConfig
        
        config = MCPConfig()
        config.reload_config()
        
        return {
            "success": True,
            "message": "Configuration reloaded. Restart backend for full effect."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
