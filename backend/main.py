"""
DevSwarm Backend - Main FastAPI Application
Serves as the central orchestrator for the 8-agent team
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio

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
    print("📦 Loading Phi-4-multimodal model...")
    
    # Initialize model manager (singleton)
    model_manager = ModelManager()
    await model_manager.initialize()
    
    # Initialize agent coordinator
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
app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
