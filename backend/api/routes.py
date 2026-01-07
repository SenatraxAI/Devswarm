"""
API routes for DevSwarm
Handles user requests and agent communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
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
                    # Log user message event
                    coordinator.event_log.append_event(
                        event_type=EventType.USER_MESSAGE,
                        agent="User",
                        payload={"message": message_text},
                        metadata={"session_id": data.get("timestamp", 0)}
                    )
                    
                    routing_info = await coordinator.process_user_message(message_text)
                    
                    # Send routing confirmation back
                    await websocket.send_json({
                        "type": "message_routed",
                        "mentioned_agents": routing_info["mentioned_agents"],
                        "routing_strategy": routing_info["routing_strategy"]
                    })
                    
                    # Broadcast user message to chat
                    await websocket.send_json({
                        "type": "agent_message",
                        "data": {
                            "agent": "You",
                            "message": message_text,
                            "messageType": "user",
                            "timestamp": data.get("timestamp", 0)
                        }
                    })
                    
                    # Generate responses from agents that should be notified
                    # (mentioned_agents if @ present, or Sarah if no @)
                    agents_to_notify = routing_info.get("should_notify", routing_info["mentioned_agents"])
                    
                    for agent_name in agents_to_notify:
                        # Update agent status to thinking
                        await websocket.send_json({
                            "type": "agent_status",
                            "data": {
                                "agent": agent_name,
                                "status": "thinking",
                                "message": "Processing your message..."
                            }
                        })
                        
                        # Get agent and generate response
                        agent = coordinator.agents.get(agent_name)
                        if agent:
                            try:
                                # Process message with streaming
                                response = await agent.process_message(message_text, websocket)
                                
                                # Send complete response
                                await websocket.send_json({
                                    "type": "agent_message",
                                    "data": {
                                        "agent": agent_name,
                                        "message": response,
                                        "messageType": "agent",
                                        "timestamp": data.get("timestamp", 0) + 1000
                                    }
                                })
                                
                                # Check if agent @mentioned other agents in response
                                from orchestration.mention_parser import MentionParser
                                parser = MentionParser()
                                follow_up_mentions = parser.extract_mentions(response)
                                
                                if follow_up_mentions:
                                    # Agent is calling other agents!
                                    print(f"🔗 {agent_name} mentioned: {follow_up_mentions}")
                                    
                                    # Trigger responses from mentioned agents
                                    for mentioned_agent in follow_up_mentions:
                                        if mentioned_agent in coordinator.agents:
                                            await websocket.send_json({
                                                "type": "agent_status",
                                                "data": {
                                                    "agent": mentioned_agent,
                                                    "status": "thinking",
                                                    "message": f"Responding to {agent_name}..."
                                                }
                                            })
                                            
                                            # Get the mentioned agent
                                            follow_up_agent = coordinator.agents[mentioned_agent]
                                            
                                            # Build context: "AGENT: Sarah mentioned you: {response}"
                                            follow_up_message = f"🔗 {agent_name} mentioned you: {response}"
                                            
                                            try:
                                                follow_up_response = await follow_up_agent.process_message(
                                                    follow_up_message, 
                                                    websocket
                                                )
                                                
                                                await websocket.send_json({
                                                    "type": "agent_message",
                                                    "data": {
                                                        "agent": mentioned_agent,
                                                        "message": follow_up_response,
                                                        "messageType": "agent",
                                                        "timestamp": data.get("timestamp", 0) + 2000
                                                    }
                                                })
                                                
                                                await websocket.send_json({
                                                    "type": "agent_status",
                                                    "data": {
                                                        "agent": mentioned_agent,
                                                        "status": "idle",
                                                        "message": ""
                                                    }
                                                })
                                            except Exception as e:
                                                print(f"❌ Error in follow-up from {mentioned_agent}: {e}")
                                
                                # Update status to idle
                                await websocket.send_json({
                                    "type": "agent_status",
                                    "data": {
                                        "agent": agent_name,
                                        "status": "idle",
                                        "message": ""
                                    }
                                })
                            except Exception as e:
                                # Send error
                                await websocket.send_json({
                                    "type": "agent_message",
                                    "data": {
                                        "agent": agent_name,
                                        "message": f"❌ Error: {str(e)}",
                                        "messageType": "error",
                                        "timestamp": data.get("timestamp", 0) + 1000
                                    }
                                })
                                
                                await websocket.send_json({
                                    "type": "agent_status",
                                    "data": {
                                        "agent": agent_name,
                                        "status": "error",
                                        "message": str(e)
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

