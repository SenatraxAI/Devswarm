"""
API routes for DevSwarm
Handles user requests and agent communication
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel
from orchestration.coordinator import AgentCoordinator
from storage.event_log import EventType

router = APIRouter()


class UserRequest(BaseModel):
    """User request model"""
    message: str
    context: Dict = {}


class ChatMessage(BaseModel):
    """Chat message from user"""
    message: str
    timestamp: int


class AgentResponse(BaseModel):
    """Agent response model"""
    agent: str
    message: str
    status: str


class ToolExecutionRequest(BaseModel):
    """Tool execution request"""
    tool_name: str
    arguments: Dict
    agent_name: str = "system"


@router.post("/request")
async def process_request(request: UserRequest):
    """Process a user request through the agent team"""
    # TODO: Connect to actual coordinator
    return {
        "status": "received",
        "message": request.message,
        "agents_activated": ["Sarah Chen (PM)"]
    }


@router.get("/agents")
async def get_agents():
    """Get list of all agents and their status"""
    # TODO: Connect to actual coordinator
    return {
        "agents": [
            {"name": "Sarah Chen", "role": "PM", "status": "idle"},
            {"name": "Marcus Williams", "role": "Architect", "status": "idle"},
            {"name": "Elena Rodriguez", "role": "Frontend", "status": "idle"},
            {"name": "James Okonkwo", "role": "Backend", "status": "idle"},
            {"name": "Priya Sharma", "role": "DevOps", "status": "idle"},
            {"name": "David Kim", "role": "Security", "status": "idle"},
            {"name": "Aisha Patel", "role": "QA", "status": "idle"},
            {"name": "Oliver Hansen", "role": "Coordinator", "status": "idle"},
        ]
    }


@router.get("/tools")
async def get_tools(agent_name: Optional[str] = None):
    """Get available tools, optionally filtered by agent"""
    from main import mcp_host
    
    if not mcp_host or not mcp_host.is_initialized:
        raise HTTPException(status_code=503, detail="MCP Host not initialized")
    
    tools = mcp_host.get_available_tools(agent_name)
    return {
        "tools": tools,
        "count": len(tools)
    }


@router.get("/tools/{tool_name}")
async def get_tool_schema(tool_name: str):
    """Get schema for a specific tool"""
    from main import mcp_host
    
    if not mcp_host or not mcp_host.is_initialized:
        raise HTTPException(status_code=503, detail="MCP Host not initialized")
    
    schema = mcp_host.get_tool_schema(tool_name)
    if not schema:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    return schema


@router.post("/tools/execute")
async def execute_tool(request: ToolExecutionRequest):
    """Execute a tool"""
    from main import mcp_host
    
    if not mcp_host or not mcp_host.is_initialized:
        raise HTTPException(status_code=503, detail="MCP Host not initialized")
    
    result = await mcp_host.execute_tool(
        request.tool_name,
        request.arguments,
        request.agent_name
    )
    
    return result


@router.post("/chat")
async def process_chat(message: ChatMessage):
    """
    Process a chat message from user with @mention support
    
    Returns routing info and triggers agent processing
    """
    from main import coordinator
    
    if not coordinator or not coordinator.is_ready:
        raise HTTPException(status_code=503, detail="Agent coordinator not ready")
    
    # Process message with @mention routing
    routing_info = await coordinator.process_user_message(message.message)
    
    return {
        "status": "processing",
        "message": message.message,
        "mentioned_agents": routing_info["mentioned_agents"],
        "routing_strategy": routing_info["routing_strategy"],
        "timestamp": message.timestamp
    }




