"""
Simple test script to verify WebSocket communication
Run this alongside the backend to test real-time updates
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api.websocket import manager


async def simulate_agent_activity():
    """Simulate agent activity for testing"""
    
    print("🧪 Starting agent activity simulation...")
    
    await asyncio.sleep(2)
    
    # Simulate Sarah Chen (PM) starting work
    print("📢 Sarah Chen: Thinking...")
    await manager.broadcast_agent_status("Sarah Chen", "thinking", "Analyzing requirements")
    await asyncio.sleep(2)
    
    print("📢 Sarah Chen: Speaking...")
    await manager.broadcast_agent_status("Sarah Chen", "speaking")
    await manager.broadcast_agent_message(
        "Sarah Chen",
        "I've reviewed the requirements. Let's break this down into smaller tasks.",
        "thought"
    )
    await asyncio.sleep(2)
    
    # Simulate Marcus Williams (Architect) joining
    print("📢 Marcus Williams: Thinking...")
    await manager.broadcast_agent_status("Marcus Williams", "thinking", "Designing architecture")
    await asyncio.sleep(2)
    
    print("📢 Marcus Williams: Speaking...")
    await manager.broadcast_agent_status("Marcus Williams", "speaking")
    await manager.broadcast_agent_message(
        "Marcus Williams",
        "I recommend a microservices architecture with event-driven communication.",
        "thought"
    )
    await asyncio.sleep(2)
    
    # Simulate terminal output
    print("💻 Terminal: Output...")
    await manager.broadcast_terminal_output("$ npm install", "stdout")
    await asyncio.sleep(0.5)
    await manager.broadcast_terminal_output("Installing dependencies...", "stdout")
    await asyncio.sleep(1)
    await manager.broadcast_terminal_output("✅ Dependencies installed successfully", "stdout")
    await asyncio.sleep(2)
    
    # Simulate code change
    print("📝 Code change...")
    await manager.broadcast_code_change(
        "src/app.ts",
        "+++ src/app.ts\n@@ -1,0 +1,3 @@\n+export function main() {\n+  console.log('Hello World');\n+}",
        "Elena Rodriguez"
    )
    await asyncio.sleep(2)
    
    # Reset agents to idle
    print("✅ Simulation complete - Agents returning to idle")
    await manager.broadcast_agent_status("Sarah Chen", "idle")
    await manager.broadcast_agent_status("Marcus Williams", "idle")


if __name__ == "__main__":
    print("🎯 DevSwarm WebSocket Test")
    print("Make sure the backend is running on http://localhost:8000")
    print("Then open http://localhost:3001 in your browser")
    print()
    
    # Run the simulation
    asyncio.run(simulate_agent_activity())
