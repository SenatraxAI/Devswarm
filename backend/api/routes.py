"""
API Routes for DevSwarm backend
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict

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
