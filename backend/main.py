"""
DevSwarm Backend - Main FastAPI Application
Serves as the central orchestrator for the 8-agent team
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import os
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

from api.routes import router
from orchestration.coordinator import AgentCoordinator
from models.model_manager import ModelManager

app = FastAPI(
    title="DevSwarm Backend",
    description="Multi-agent AI coding assistant backend",
    version="0.1.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
model_manager: ModelManager = None
coordinator: AgentCoordinator = None


@app.on_event("startup")
async def startup_event():
    """Initialize model and agent coordinator on startup"""
    global model_manager, coordinator
    
    print("🚀 Starting DevSwarm Backend...")
    
    print("📦 Loading AI model...")
    
    # Initialize model manager (singleton)
    model_manager = ModelManager()
    await model_manager.initialize()
    
    # Initialize agent coordinator (creates its own MCP host internally)
    coordinator = AgentCoordinator(model_manager)
    await coordinator.initialize()
    
    print("✅ DevSwarm Backend ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global model_manager, coordinator
    
    print("🛑 Shutting down DevSwarm Backend...")
    
    if coordinator:
        await coordinator.shutdown()
    
    if model_manager:
        await model_manager.shutdown()
    
    print("✅ Shutdown complete")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "agents": 8,
        "model": "phi-4-multimodal"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model_manager.is_loaded if model_manager else False,
        "agents_ready": coordinator.is_ready if coordinator else False,
        "vram_usage_gb": model_manager.get_vram_usage() if model_manager else 0
    }


# Include API routes
from api.event_routes import router as event_router
from api.project_routes import router as project_router
from api.settings_routes import router as settings_router
app.include_router(router, prefix="/api/v1")
app.include_router(event_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")


@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time agent communication via WebSocket"""
    await websocket.accept()
    
    # Get project_id from query params or default
    project_id = websocket.query_params.get("project_id", "default")
    
    try:
        # Send initial connection success
        agents = coordinator.get_agents(project_id)
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "project_id": project_id,
            "agents": [a.get_status() for a in agents.values()]
        })

        # Replay recent history (last 50 events)
        recent_events = coordinator.get_project_events(project_id, limit=50)
        for event in recent_events:
            # Map event log format to frontend message format
            if event["type"] in ["USER_MESSAGE", "AGENT_MESSAGE_SENT", "AGENT_MENTION"]:
                await websocket.send_json({
                    "type": "agent_message",
                    "data": {
                        "agent": event["agent"],
                        "message": event["payload"].get("message", ""),
                        "messageType": "response", # Treating all history as "response" style for now
                        "branch_name": event.get("branch_name", "main"),
                        "thread_id": event.get("thread_id"),
                        "timestamp": event["timestamp"],
                        "project_id": project_id
                    }
                })
        
        while True:
            data = await websocket.receive_json()
            
            # Update project context if provided
            if "project_id" in data:
                project_id = data["project_id"]
            
            branch_name = data.get("branch_name", "main")
            thread_id = data.get("thread_id")
            msg_type = data.get("type")
            
            if msg_type == "user_message":
                # Regular swarm message
                message = data.get("message")
                
                # Echo message back to user for UI visibility
                await websocket.send_json({
                    "type": "agent_message",
                    "data": {
                        "agent": "User",
                        "message": message,
                        "messageType": "response",
                        "branch_name": branch_name,
                        "thread_id": thread_id,
                        "timestamp": datetime.now().timestamp(),
                        "project_id": project_id  # CRITICAL FIX: Frontend filters by this!
                    }
                })

                await coordinator.process_user_message(
                    message, 
                    project_id=project_id,
                    branch_name=branch_name,
                    thread_id=thread_id,
                    websocket=websocket
                )
                
            elif msg_type == "direct_message":
                # Direct message to a specific agent
                recipient = data.get("recipient")
                message = data.get("message")
                
                agents = coordinator.get_agents(project_id)
                if recipient in agents:
                    # Trigger the specific agent to process the DM
                    asyncio.create_task(
                        agents[recipient].process_message(
                            f"[DM] {message}", 
                            websocket=websocket,
                            branch_name=branch_name,
                            thread_id=thread_id
                        )
                    )

                    # Echo DM back to user for UI visibility
                    await websocket.send_json({
                        "type": "agent_message",
                        "data": {
                            "agent": "User",
                            "message": message,
                            "messageType": "response",
                            "branch_name": branch_name,
                            "thread_id": thread_id,
                            "timestamp": datetime.now().timestamp(),
                            "project_id": project_id # CRITICAL FIX
                        }
                    })
                    
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        print("🔌 WebSocket closed")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
