"""
DevSwarm Backend - Main FastAPI Application
Serves as the central orchestrator for the 8-agent team
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
import os
import re
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
    
    print("\n" + "="*60)
    print("🚀 STARTING DEVSWARM BACKEND...")
    print("="*60 + "\n")
    
    # Initialize model manager (singleton)
    model_manager = ModelManager()
    await model_manager.initialize()
    
    # Initialize agent coordinator
    coordinator = AgentCoordinator(model_manager)
    await coordinator.initialize()
    
    print("\n✅ DEVSWARM BACKEND READY!\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global model_manager, coordinator
    print("\n🛑 SHUTTING DOWN DEVSWARM BACKEND...")
    if coordinator:
        await coordinator.shutdown()
    if model_manager:
        await model_manager.shutdown()
    print("✅ SHUTDOWN COMPLETE\n")


@app.get("/")
async def root():
    return {"status": "running", "agents": 8}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model_manager.is_loaded if model_manager else False,
        "agents_ready": coordinator.is_ready if coordinator else False
    }


# Include API routes
from api.event_routes import router as event_router
from api.project_routes import router as project_router
from api.settings_routes import router as settings_router
from api.ide_routes import router as ide_router

from api.monitoring import router as monitoring_router

app.include_router(router, prefix="/api/v1")
app.include_router(event_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(ide_router, prefix="/api/v1")
app.include_router(monitoring_router, prefix="/api/v1/status")


@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time agent communication via WebSocket with intensive logging"""
    await websocket.accept()
    
    # Get initial project_id from query params
    project_id = websocket.query_params.get("project_id", "default")
    
    try:
        print(f"\n{'🔌'*3} NEW WEBSOCKET CONNECTION")
        print(f"   Project ID: {project_id}")
        print(f"   Client: {websocket.client}")
        
        # Get team for this project
        # get_agents is a synchronous method in coordinator.py
        agents = coordinator.get_agents(project_id)
        
        # 1. Send initial connection success with current agent statuses
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "project_id": project_id,
            "agents": [a.get_status() for a in agents.values()]
        })

        # 2. Replay recent history (briefly to avoid overwhelming)
        print(f"📜 Replaying recent history for {project_id}...")
        recent_events = coordinator.get_project_events(project_id, limit=50)
        for event in recent_events:
            if event["type"] in ["USER_MESSAGE", "AGENT_MESSAGE_SENT", "AGENT_MENTION"]:
                await websocket.send_json({
                    "type": "agent_message",
                    "data": {
                        "agent": event["agent"],
                        "message": event["payload"].get("message", ""),
                        "messageType": "response",
                        "branch_name": event.get("branch_name", "main"),
                        "thread_id": event.get("thread_id"),
                        "timestamp": event["timestamp"],
                        "project_id": project_id
                    }
                })

        # 3. Message Loop
        while True:
            data = await websocket.receive_json()
            
            # Deep Diagnostic Log
            print(f"\n{'📥'*3} WS RECEIVED:")
            print(f"   Type: {data.get('type')}")
            print(f"   Thread: {data.get('thread_id')}")
            print(f"   Project: {data.get('project_id')}")
            
            # Update project context if provided in message
            current_project = data.get("project_id", project_id)
            if current_project != project_id:
                print(f"🔄 Switched context from {project_id} to {current_project}")
                project_id = current_project
                agents = coordinator.get_agents(project_id)
            
            branch_name = data.get("branch_name", "main")
            thread_id = data.get("thread_id")
            mode = data.get("mode") # explicit mode override
            msg_type = data.get("type")
            
            # Unified User/Direct Message Echo Logic
            if msg_type in ["user_message", "direct_message"]:
                message_text = data.get("message")
                recipient = data.get("recipient")
                
                # Echo IMMEDIATELY for UI feedback
                echo_payload = {
                    "type": "agent_message",
                    "data": {
                        "agent": "User",
                        "message": message_text,
                        "messageType": "response",
                        "branch_name": branch_name,
                        "thread_id": thread_id,
                        "timestamp": datetime.now().timestamp(),
                        "project_id": project_id
                    }
                }
                print(f"📤 ECHOING BACK TO UI: {json.dumps(echo_payload, indent=2)}")
                await websocket.send_json(echo_payload)

                if msg_type == "user_message":
                    # Global project broadcast
                    asyncio.create_task(
                        coordinator.process_user_message(
                            message_text,
                            project_id=project_id,
                            branch_name=branch_name,
                            thread_id=thread_id,
                            websocket=websocket,
                            mode=mode
                        )
                    )
                else:
                    # Targeted Direct Message
                    if recipient in agents:
                        print(f"🎯 ROUTING DM TO: {recipient}")
                        asyncio.create_task(
                            agents[recipient].process_message(
                                f"[DM] {message_text}",
                                websocket=websocket,
                                branch_name=branch_name,
                                thread_id=thread_id
                            )
                        )
                    else:
                        print(f"❌ RECIPIENT NOT FOUND: {recipient}")
            
            # Agent Typing/Status updates
            elif msg_type == "agent_status":
                print(f"📊 STATUS UPDATE: {data.get('data', {}).get('agent')} -> {data.get('data', {}).get('status')}")

    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected (Project: {project_id})")
    except Exception as e:
        print(f"❌ WebSocket EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"🔌 WebSocket handler terminated (Project: {project_id})")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
