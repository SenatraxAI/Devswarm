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


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    from main import coordinator
    
    await websocket.accept()
    
    try:
        # Send initial connection message with agent data
        agent_data = []
        if coordinator and coordinator.is_ready:
            for name, agent in coordinator.agents.items():
                agent_data.append({
                    "name": name,
                    "role": agent.role,
                    "status": agent.session.status
                })
        
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "DevSwarm backend connected",
            "agents": agent_data
        })
        
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "user_message":
                # Process the user message
                message_text = data.get("message", "")
                
                # Route message to agents
                if coordinator and coordinator.is_ready:
                    routing_info = await coordinator.process_user_message(message_text)
                    
                    # Send routing confirmation back
                    await websocket.send_json({
                        "type": "message_routed",
                        "mentioned_agents": routing_info["mentioned_agents"],
                        "routing_strategy": routing_info["routing_strategy"]
                    })
                    
                    #Broadcast user message to chat
                    await websocket.send_json({
                        "type": "agent_message",
                        "data": {
                            "agent": "You",
                            "message": message_text,
                            "messageType": "user",
                            "timestamp": data.get("timestamp", 0)
                        }
                    })
                    
                    # TODO: Trigger agent responses (Phase 2 - Phi-4 integration)
                    # For now, send acknowledgment from mentioned agents
                    for agent_name in routing_info["mentioned_agents"]:
                        await websocket.send_json({
                            "type": "agent_status",
                            "data": {
                                "agent": agent_name,
                                "status": "thinking",
                                "message": f"Processing your message..."
                            }
                        })
            else:
                # Echo back for unknown types
                await websocket.send_json({
                    "type": "response",
                    "data": data
                })
            
    except WebSocketDisconnect:
        print("Client disconnected from WebSocket")

