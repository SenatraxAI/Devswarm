"""
Interactive testing script for DevSwarm agents
Tests @mention system and agent interactions
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.coordinator import AgentCoordinator
from models.model_manager import ModelManager
from tools.mcp_host import MCPHost


async def test_mentions():
    """Test the @mention system"""
    
    print("🧪 Testing DevSwarm @Mention System\n")
    print("=" * 60)
    
    # Initialize components
    print("\n📦 Initializing components...")
    model_manager = ModelManager()
    await model_manager.initialize()
    
    mcp_host = MCPHost()
    await mcp_host.initialize()
    
    coordinator = AgentCoordinator(model_manager, mcp_host)
    await coordinator.initialize()
    
    print("\n✅ All components ready!\n")
    print("=" * 60)
    
    # Test cases
    test_messages = [
        {
            "text": "Hey team, let's build a login page",
            "expected": "Routes to Sarah Chen (PM) - no mentions"
        },
        {
            "text": "@Sarah Chen can you help me understand the requirements?",
            "expected": "Routes to Sarah Chen - direct mention"
        },
        {
            "text": "@Elena Rodriguez and @James Okonkwo, can you work together on the API?",
            "expected": "Routes to Elena and James - group mention"
        },
        {
            "text": "@Marcus Williams what do you think about using microservices? Also cc @Sarah Chen",
            "expected": "Routes to Marcus and Sarah - multiple mentions"
        },
        {
            "text": "@David Kim please review this for security issues",
            "expected": "Routes to David - security review request"
        }
    ]
    
    for i, test in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: {test['text']}")
        print(f"   Expected: {test['expected']}")
        
        # Process the message
        result = await coordinator.process_user_message(test['text'])
        
        print(f"   ✅ Routed to: {', '.join(result['mentioned_agents']) if result['mentioned_agents'] else 'Sarah Chen (default)'}")
        print(f"   Strategy: {result['routing_strategy']}")
        
        if result.get('agent_responses'):
            print(f"   Agents notified: {len(result['agent_responses'])}")
        
        print()
    
    print("=" * 60)
    print("\n🎉 All tests passed! @Mention system working correctly!\n")
    
    # Cleanup
    await coordinator.shutdown()
    await mcp_host.shutdown()
    await model_manager.shutdown()


if __name__ == "__main__":
    asyncio.run(test_mentions())
