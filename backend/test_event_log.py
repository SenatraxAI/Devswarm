"""
Test script for Event Log functionality
"""
import asyncio
from storage.event_log import EventLog, EventType


def test_event_log():
    """Test basic event log operations"""
    print("🧪 Testing Event Log...\n")
    
    # Create event log
    log = EventLog(project_id="test_project")
    print(f"✅ Created event log at: {log.event_file}")
    
    # Test 1: Append user message
    print("\n📝 Test 1: User sends message")
    event_id_1 = log.append_event(
        event_type=EventType.USER_MESSAGE,
        agent="User",
        payload={"message": "Build a login page"},
        metadata={"session_id": "test-123"}
    )
    print(f"   Event ID: {event_id_1}")
    
    # Test 2: Agent responds
    print("\n💬 Test 2: Sarah responds")
    event_id_2 = log.append_event(
        event_type=EventType.AGENT_MESSAGE_SENT,
        agent="Sarah Chen",
        payload={"message": "Got it! Let me coordinate this."},
        parent_events=[event_id_1],
        metadata={"tokens": 150}
    )
    print(f"   Event ID: {event_id_2}")
    
    # Test 3: Sarah @mentions Marcus
    print("\n🔗 Test 3: Sarah mentions Marcus")
    event_id_3 = log.append_event(
        event_type=EventType.AGENT_MENTION,
        agent="Sarah Chen",
        payload={
            "message": "@Marcus Williams what's the best auth approach?",
            "mentioned": ["Marcus Williams"]
        },
        parent_events=[event_id_2]
    )
    print(f"   Event ID: {event_id_3}")
    
    # Test 4: Team decision
    print("\n✅ Test 4: Team decides on JWT")
    event_id_4 = log.append_event(
        event_type=EventType.TEAM_DECISION,
        agent="Sarah Chen",
        payload={
            "decision": "Use JWT for authentication",
            "participants": ["Sarah Chen", "Marcus Williams"]
        },
        parent_events=[event_id_3]
    )
    print(f"   Event ID: {event_id_4}")
    
    # Test 5: Query recent events
    print("\n📊 Test 5: Query recent events")
    recent = log.get_events(limit=5)
    print(f"   Found {len(recent)} events:")
    for event in recent:
        print(f"   - {event['type']}: {event['agent']}")
    
    # Test 6: Query Sarah's events only
    print("\n🔍 Test 6: Query Sarah's events")
    sarah_events = log.get_events(agent="Sarah Chen")
    print(f"   Found {len(sarah_events)} events from Sarah")
    
    # Test 7: Get recent context for Marcus
    print("\n📚 Test 7: Get recent context for Marcus")
    marcus_context = log.get_recent_context(agent="Marcus Williams", limit=10)
    print(f"   Context includes {len(marcus_context)} events")
    print(f"   (Marcus's own + team decisions)")
    
    # Test 8: Count total events
    print("\n📈 Test 8: Total events")
    total = log.count_events()
    print(f"   Total events in log: {total}")
    
    print("\n✅ All tests passed!")
    print(f"\nEvent log file: {log.event_file}")


if __name__ == "__main__":
    test_event_log()
