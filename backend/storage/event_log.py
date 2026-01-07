"""
Event Log - Git-like commit tracking for agent actions
Append-only JSON Lines storage for all events
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum


class EventType(Enum):
    """Event types for DevSwarm"""
    # User interactions
    USER_PROMPT_RECEIVED = "USER_PROMPT_RECEIVED"
    USER_MESSAGE = "USER_MESSAGE"
    
    # Agent communications
    AGENT_MESSAGE_SENT = "AGENT_MESSAGE_SENT"
    AGENT_MENTION = "AGENT_MENTION"
    
    # Team decisions
    TEAM_DECISION = "TEAM_DECISION"
    REQUIREMENTS_CLARIFIED = "REQUIREMENTS_CLARIFIED"
    
    # Summaries
    SUMMARY_GENERATED = "SUMMARY_GENERATED"
    
    # Future: Code, tests, deployment
    CODE_GENERATED = "CODE_GENERATED"
    TEST_EXECUTED = "TEST_EXECUTED"


class EventLog:
    """
    Git-like event log for agent memory
    Stores events in JSON Lines format (one JSON object per line)
    """
    
    def __init__(self, project_id: str = "default", data_dir: str = "data/events"):
        self.project_id = project_id
        self.data_dir = Path(data_dir)
        self.event_file = self.data_dir / project_id / "events.jsonl"
        
        # Initialize SQLite indexer (one per project for physical isolation)
        from storage.event_indexer import EventIndexer
        db_path = self.event_file.parent / "index.db"
        self.indexer = EventIndexer(db_path=str(db_path))
        
        # Create directories if needed
        self.event_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Perform initial sync (index existing events if SQLite is behind)
        self._sync_index()

    def _sync_index(self):
        """Index any events that are in .jsonl but missing from SQLite"""
        indexed_count = self.indexer.count_events(self.project_id)
        file_event_count = self.count_events()
        
        if indexed_count < file_event_count:
            print(f"🔄 Syncing SQLite index ({indexed_count}/{file_event_count})...")
            # Clear and rebuild for this project (simplest way to ensure consistency)
            # In a real system, we'd do incremental sync
            if self.event_file.exists():
                with open(self.event_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            event = json.loads(line)
                            self.indexer.index_event(event, self.project_id)
            print(f"✅ SQLite index synced for project '{self.project_id}'")
    
    def append_event(
        self,
        event_type: EventType,
        agent: str,
        payload: Dict[str, Any],
        parent_events: Optional[List[str]] = None,
        branch_name: str = "main",
        thread_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Append a new event to the log
        
        Args:
            event_type: Type of event
            agent: Which agent performed this action
            payload: Event content (message, decision, code, etc.)
            parent_events: IDs of parent events (for commit graph)
            branch_name: Name of the current exploration branch
            thread_id: ID of the message thread (for replies)
            metadata: Additional context (tokens, duration, etc.)
            
        Returns:
            Event ID (UUID)
        """
        event_id = str(uuid.uuid4())
        
        event = {
            "id": event_id,
            "timestamp": datetime.now().timestamp(),
            "agent": agent,
            "type": event_type.value,
            "parent_events": parent_events or [],
            "branch_name": branch_name,
            "thread_id": thread_id,
            "payload": payload,
            "metadata": metadata or {}
        }
        
        # Append to JSON Lines file
        with open(self.event_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
            
        # Add to SQLite index for fast lookup
        self.indexer.index_event(event, self.project_id)
        
        return event_id
    
    def get_events(
        self,
        limit: Optional[int] = None,
        agent: Optional[str] = None,
        event_type: Optional[EventType] = None,
        since_timestamp: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Query events from the log
        
        Args:
            limit: Maximum number of events to return
            agent: Filter by agent name
            event_type: Filter by event type
            since_timestamp: Only events after this timestamp
            
        Returns:
            List of events (newest first)
        """
        if not self.event_file.exists():
            return []
        
        events = []
        
        with open(self.event_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    
                    # Apply filters
                    if agent and event["agent"] != agent:
                        continue
                    if event_type and event["type"] != event_type.value:
                        continue
                    if since_timestamp and event["timestamp"] < since_timestamp:
                        continue
                    
                    events.append(event)
        
        # Reverse to get newest first
        events.reverse()
        
        # Apply limit
        if limit:
            events = events[:limit]
        
        return events
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific event by ID"""
        if not self.event_file.exists():
            return None
        
        with open(self.event_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    if event["id"] == event_id:
                        return event
        
        return None
    
    def get_recent_context(
        self,
        agent: str,
        limit: int = 20,
        include_team_decisions: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get recent context for an agent
        
        Returns recent messages from this agent + team decisions
        """
        events = []
        
        # Get agent's own messages
        agent_events = self.get_events(
            limit=limit,
            agent=agent
        )
        events.extend(agent_events)
        
        # Get team decisions if requested
        if include_team_decisions:
            decisions = self.get_events(
                limit=10,
                event_type=EventType.TEAM_DECISION
            )
            events.extend(decisions)
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda e: e["timestamp"], reverse=True)
        
        return events[:limit]
    
    def count_events(self) -> int:
        """Count total events in log"""
        if not self.event_file.exists():
            return 0
        
        count = 0
        with open(self.event_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        
        return count
