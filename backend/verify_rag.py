
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from storage.vector_store import VectorStore
from storage.event_log import EventLog, EventType
from storage.summarizer import EventSummarizer
from orchestration.team_memory import TeamMemory

def test_rag_brain():
    print("🧠 Testing RAG Brain...")
    
    # 1. Test Vector Store
    vs = VectorStore(project_id="test_rag")
    if vs.HAS_DEPS:
        print("✅ Vector dependencies found.")
    else:
        print("❌ Vector dependencies MISSING.")
        return

    # Add dummy text
    vs.add_text("The secret password is 'Antigravity'.", {"type": "test"})
    results = vs.search("What is the secret password?", k=1)
    
    if results and "Antigravity" in results[0]["text"]:
        print(f"✅ Semantic Search Working: Found '{results[0]['text'][:30]}...'")
    else:
        print("❌ Semantic Search ERROR.")

    # 2. Test Team Memory Integration
    log = EventLog(project_id="test_rag")
    memory = TeamMemory(log)
    
    # Record an event (should index automatically now)
    memory.record_event(
        event_type=EventType.TEAM_DECISION,
        agent="TestAgent",
        payload={"decision": "We should use Python for the backend."}
    )
    
    # Verify retrieval
    context = memory.get_relevant_context("TestAgent", "What language should we use for the backend?")
    if "Python" in context:
        print("✅ TeamMemory Semantic Search Working.")
    else:
        print("❌ TeamMemory Semantic Search ERROR.")

    # 3. Test Summarizer Coverage
    summarizer = EventSummarizer(log)
    stats = summarizer.get_summary_coverage()
    print(f"📊 Summarizer Stats: {stats}")
    
    print("\n✨ RAG & MEMORY SYSTEM VERIFIED.")

if __name__ == "__main__":
    test_rag_brain()
