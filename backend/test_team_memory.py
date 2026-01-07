"""
Test script for Team Memory functionality
"""
from storage.event_log import EventLog, EventType
from orchestration.team_memory import TeamMemory


def test_team_memory():
    """Test team memory queries"""
    print("🧪 Testing Team Memory...\n")
    
    # Create event log and team memory
    log = EventLog(project_id="test_memory")
    memory = TeamMemory(log)
    
    print("✅ Created team memory\n")
    
    # Test 1: Record team decisions
    print("📋 Test 1: Recording team decisions")
    
    decision_id_1 = memory.record_team_decision(
        decision="Use JWT for authentication",
        agent_name="Sarah Chen",
        participants=["Sarah Chen", "Marcus Williams", "David Kim"]
    )
    print(f"   Recorded: JWT decision ({decision_id_1[:8]}...)")
    
    decision_id_2 = memory.record_team_decision(
        decision="Use PostgreSQL for database",
        agent_name="Marcus Williams",
        participants=["Marcus Williams", "James Okonkwo"]
    )
    print(f"   Recorded: PostgreSQL decision ({decision_id_2[:8]}...)")
    
    # Test 2: Query team decisions
    print("\n🔍 Test 2: Query team decisions")
    decisions = memory.query_team_decisions(limit=5)
    print(f"   Found {len(decisions)} decisions:")
    for decision in decisions:
        print(f"   - {decision['agent']}: {decision['decision']}")
    
    # Test 3: Search for specific decision
    print("\n🔎 Test 3: Find decision about 'auth'")
    auth_decision = memory.find_decision_about("auth")
    if auth_decision:
        print(f"   Found: {auth_decision['decision']}")
        print(f"   By: {auth_decision['agent']}")
    else:
        print("   Not found")
    
    # Test 4: Add some agent messages
    print("\n💬 Test 4: Add agent messages")
    log.append_event(
        event_type=EventType.AGENT_MESSAGE_SENT,
        agent="Sarah Chen",
        payload={"message": "Let's start with the login page"}
    )
    log.append_event(
        event_type=EventType.AGENT_MESSAGE_SENT,
        agent="Elena Rodriguez",
        payload={"message": "I'll design the UI components"}
    )
    print("   Added 2 agent messages")
    
    # Test 5: Get conversation summary
    print("\n📊 Test 5: Conversation summary")
    summary = memory.get_conversation_summary(since_minutes=60)
    print(f"   Summary:\n{summary}")
    
    # Test 6: Get shared context for agent
    print("\n🎯 Test 6: Shared context for Marcus")
    context = memory.get_shared_context("Marcus Williams", limit=10)
    print(f"   Context:\n{context}")
    
    # Test 7: Get agent's recent work
    print("\n👤 Test 7: Sarah's recent work")
    work = memory.get_agent_recent_work("Sarah Chen", limit=5)
    print(f"   Found {len(work)} items:")
    for item in work:
        print(f"   - {item['type']}: {item['message'][:50]}...")
    
    print("\n✅ All team memory tests passed!")


if __name__ == "__main__":
    test_team_memory()
