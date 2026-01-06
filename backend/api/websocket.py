"""
WebSocket Manager for real-time agent communication
Handles streaming updates from agents to the frontend
"""
from typing import Set, Dict, Any
from fastapi import WebSocket
import asyncio
import json


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.message_queue: asyncio.Queue = asyncio.Queue()
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"✅ Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        print(f"❌ Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to a specific client"""
        await websocket.send_json(message)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)
    
    async def broadcast_agent_status(self, agent_name: str, status: str, message: str = ""):
        """Broadcast agent status update"""
        await self.broadcast({
            "type": "agent_status",
            "data": {
                "agent": agent_name,
                "status": status,
                "message": message,
                "timestamp": asyncio.get_event_loop().time()
            }
        })
    
    async def broadcast_agent_message(self, agent_name: str, message: str, message_type: str = "thought"):
        """Broadcast agent message"""
        await self.broadcast({
            "type": "agent_message",
            "data": {
                "agent": agent_name,
                "message": message,
                "messageType": message_type,
                "timestamp": asyncio.get_event_loop().time()
            }
        })
    
    async def broadcast_terminal_output(self, line: str, stream_type: str = "stdout"):
        """Broadcast terminal output"""
        await self.broadcast({
            "type": "terminal_output",
            "data": {
                "line": line,
                "streamType": stream_type,
                "timestamp": asyncio.get_event_loop().time()
            }
        })
    
    async def broadcast_code_change(self, file_path: str, diff: str, agent: str):
        """Broadcast code change event"""
        await self.broadcast({
            "type": "code_change",
            "data": {
                "filePath": file_path,
                "diff": diff,
                "agent": agent,
                "timestamp": asyncio.get_event_loop().time()
            }
        })
    
    async def stream_model_output(self, agent_name: str, websocket: WebSocket):
        """Stream model output token by token"""
        # This will be used for streaming agent responses in real-time
        # TODO: Implement actual streaming from model inference
        pass


# Global connection manager instance
manager = ConnectionManager()
