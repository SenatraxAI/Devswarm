"""
Extended API routes with MCP tool endpoints
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

router = APIRouter()


class UserRequest(BaseModel):
    """User request model"""
    message: str
    context: Dict = {}


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


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "DevSwarm backend connected"
        })
        
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            
            # Echo back for now (TODO: process through coordinator)
            await websocket.send_json({
                "type": "response",
                "data": data
            })
            
    except WebSocketDisconnect:
        print("Client disconnected from WebSocket")
