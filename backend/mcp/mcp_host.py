"""
MCP Host - Central coordinator for all MCP servers and tool access
Implements hub-and-spoke architecture for tool management
"""
from typing import Dict, List, Any, Optional
import asyncio
from enum import Enum


class TransportType(Enum):
    """Types of MCP server transports"""
    STDIO = "stdio"  # Local servers via stdin/stdout
    SSE = "sse"      # Remote servers via Server-Sent Events


class MCPHost:
    """
    Central coordinator for MCP tool ecosystem
    Manages server connections, tool registry, and access control
    """
    
    def __init__(self):
        """Initialize MCP Host with tool registry, access control, and dynamic config"""
        print("🔧 Initializing MCP Host...")
        
        # Load MCP server configurations
        from mcp.mcp_config import MCPConfig
        self.mcp_config = MCPConfig()
        
        # Initialize tool registry and access control
        from mcp.tool_registry import ToolRegistry
        from mcp.access_control import AccessControl
        
        self.tool_registry = ToolRegistry()
        self.access_control = AccessControl()
        self.servers = {}
        self.is_initialized = True
        
        # All tools from registry are considered "ready"
        print(f"✅ MCP Host initialized with {len(self.tool_registry.list_tools())} tools")
    
    async def connect_server(
        self,
        name: str,
        transport: TransportType,
        config: Dict[str, Any]
    ) -> bool:
        """Connect to an MCP server (SSE/Stdio)"""
        # TODO: Implement external MCP server connection logic
        return False
    
    def set_agent_permissions(self, agent: str, allowed_tools: List[str]):
        """Configure tool access for an agent"""
        self.access_control.set_permissions(agent, allowed_tools)
    
    def can_agent_use_tool(self, agent: str, tool_name: str) -> bool:
        """Check if agent has permission to use tool"""
        return self.access_control.can_use_tool(agent, tool_name)
    
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        agent: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool on behalf of an agent with optional project context
        """
        # Check permissions
        if not self.can_agent_use_tool(agent, tool_name):
            return {
                "success": False,
                "error": f"Agent {agent} not authorized to use {tool_name}"
            }
        
        # Check tool exists (look in tool registry first)
        tool_data = self.tool_registry.get_tool(tool_name)
        if not tool_data:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        # Execute tool
        try:
            tool_impl, method_name = tool_data
            
            # Apply context if provided (e.g. root_path for filesystem)
            if context and hasattr(tool_impl, "set_context"):
                tool_impl.set_context(**context)
            
            # Fetch the method (e.g. search, execute, read_file)
            method = getattr(tool_impl, method_name)
            
            # Execute with unpacked dictionary arguments
            result = await method(**arguments)
            
            # Return result wrapped in success status if not already
            if isinstance(result, dict) and "success" in result:
                return result
                
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            import traceback
            print(f"❌ Tool Execution Error: {e}")
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_tools(self, agent: Optional[str] = None) -> List[Dict]:
        """Get tools available to an agent"""
        tools = []
        all_tool_names = self.tool_registry.list_tools()
        
        for tool_name in all_tool_names:
            if agent and not self.access_control.can_use_tool(agent, tool_name):
                continue
            
            tool_data = self.tool_registry.get_tool(tool_name)
            if tool_data:
                tool_impl, _ = tool_data
                tools.append({
                    "name": tool_name,
                    "description": getattr(tool_impl, "description", f"Tool: {tool_name}")
                })
        
        return tools
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict]:
        """Get schema for a specific tool"""
        tool_data = self.tool_registry.get_tool(tool_name)
        if not tool_data:
            return None
        
        tool_impl, _ = tool_data
        if hasattr(tool_impl, "SCHEMA"):
            return tool_impl.SCHEMA
            
        return {"name": tool_name, "description": getattr(tool_impl, "description", "")}
    
    async def shutdown(self):
        """Shutdown connection"""
        self.is_initialized = False
