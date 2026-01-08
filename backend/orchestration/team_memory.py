"""
Team Memory - Shared knowledge base for all agents
Allows agents to query event log for team decisions and context
"""
from typing import List, Dict, Any, Optional
from storage.event_log import EventLog, EventType
from datetime import datetime, timedelta


class TeamMemory:
    """
    Shared memory system for agent team
    Allows agents to query decisions, conversations, and context
    """
    
    def __init__(self, event_log: EventLog):
        self.event_log = event_log
        
        # Initialize Vector Store if available
        from storage.vector_store import VectorStore
        # Use simple heuristic for project_id for now
        self.vector_store = VectorStore(project_id=event_log.project_id)
    
    def query_team_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent team decisions
        
        Returns decisions in reverse chronological order
        """
        decisions = self.event_log.get_events(
            event_type=EventType.TEAM_DECISION,
            limit=limit
        )
        
        return [
            {
                "decision": event["payload"].get("decision"),
                "agent": event["agent"],
                "timestamp": event["timestamp"],
                "participants": event["payload"].get("participants", [])
            }
            for event in decisions
        ]
    
    def find_decision_about(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Find a decision containing specific topic/keyword
        
        Args:
            topic: Keyword to search for (e.g., "auth", "database", "JWT")
            
        Returns:
            Most recent decision matching topic, or None
        """
        # Try semantic search first
        if self.vector_store:
            results = self.vector_store.search(topic, k=3)
            if results:
                # Filter for decisions only (simple client-side filter for now)
                # In robust implementation, we'd filter in the query
                for res in results:
                    if res.get("metadata", {}).get("type") == "team_decision":
                        return {
                            "decision": res["text"],
                            "agent": res["metadata"].get("agent", "Unknown"),
                            "score": res["score"]
                        }
        
        # Fallback to simple keyword search
        decisions = self.event_log.get_events(
            event_type=EventType.TEAM_DECISION,
            limit=50  # Search last 50 decisions
        )
        
        topic_lower = topic.lower()
        
        for event in decisions:
            decision_text = event["payload"].get("decision", "").lower()
            if topic_lower in decision_text:
                return {
                    "decision": event["payload"].get("decision"),
                    "agent": event["agent"],
                    "timestamp": event["timestamp"],
                    "participants": event["payload"].get("participants", []),
                    "event_id": event["id"]
                }
        
        return None
    
    def get_agent_recent_work(self, agent_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get what an agent has been working on recently
        
        Args:
            agent_name: Name of agent
            limit: Max number of events
            
        Returns:
            Recent events from this agent
        """
        events = self.event_log.get_events(
            agent=agent_name,
            limit=limit
        )
        
        return [
            {
                "type": event["type"],
                "message": event["payload"].get("message", ""),
                "timestamp": event["timestamp"],
                "event_id": event["id"]
            }
            for event in events
        ]
    
    def get_conversation_summary(self, since_minutes: int = 60) -> str:
        """
        Get a summary of recent team conversation
        
        Args:
            since_minutes: How far back to look
            
        Returns:
            Text summary of conversation
        """
        cutoff_time = datetime.now().timestamp() - (since_minutes * 60)
        
        # Get recent messages
        messages = self.event_log.get_events(
            since_timestamp=cutoff_time,
            limit=100
        )
        
        # Filter to user and agent messages
        conversation = [
            event for event in messages
            if event["type"] in ["USER_MESSAGE", "AGENT_MESSAGE_SENT"]
        ]
        
        if not conversation:
            return "No recent conversation."
        
        # Build summary
        summary_parts = []
        for event in reversed(conversation):  # Chronological order
            agent = event["agent"]
            message = event["payload"].get("message", "")
            
            # Truncate long messages
            if len(message) > 100:
                message = message[:100] + "..."
            
            summary_parts.append(f"{agent}: {message}")
        
        return "\n".join(summary_parts[-10:])  # Last 10 messages
    
    def get_shared_context(self, agent_name: str, limit: int = 20) -> str:
        """
        Get shared context for an agent
        Includes recent team decisions and relevant conversations
        
        Args:
            agent_name: Agent requesting context
            limit: Max items to include
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add recent team decisions
        decisions = self.query_team_decisions(limit=5)
        if decisions:
            context_parts.append("📋 Recent Team Decisions:")
            for decision in decisions:
                context_parts.append(f"  - {decision['agent']}: {decision['decision']}")
        
        # Add conversation summary
        summary = self.get_conversation_summary(since_minutes=30)
        if summary != "No recent conversation.":
            context_parts.append("\n💬 Recent Conversation:")
            context_parts.append(summary)
        
        return "\n".join(context_parts) if context_parts else "No shared context available."
    
    def record_team_decision(
        self,
        decision: str,
        agent_name: str,
        participants: List[str] = None
    ) -> str:
        """
        Record a team decision in the event log
        """
        # Record to event log
        event_id = self.event_log.append_event(
            event_type=EventType.TEAM_DECISION,
            agent=agent_name,
            payload={
                "decision": decision,
                "participants": participants or [agent_name]
            },
            metadata={
                "recorded_at": datetime.now().isoformat()
            }
        )
        
        # Vector store indexing is now handled via record_event
        return event_id

    def record_event(self, event_type: EventType, agent: str, payload: Dict[str, Any], metadata: Dict = None) -> str:
        """
        Record ANY event and automatically index it for RAG
        """
        event_id = self.event_log.append_event(
            event_type=event_type,
            agent=agent,
            payload=payload,
            metadata=metadata
        )
        
        # Index in vector store automatically
        if self.vector_store:
            text_to_index = payload.get("message", payload.get("decision", str(payload)))
            self.vector_store.add_text(
                text=str(text_to_index),
                meta={
                    "type": event_type.value,
                    "agent": agent,
                    "event_id": event_id
                }
            )
            
        return event_id

    def record_identity_anchor(self, agent_name: str, persona_prompt: str):
        """
        Record a persona update as a 'High-Priority Identity Anchor'
        """
        return self.record_event(
            event_type=EventType.SUMMARY_GENERATED, # Using SUMMARY as a proxy for fixed "Identity"
            agent="SYSTEM",
            payload={
                "message": f"IDENTITY ANCHOR for {agent_name}: {persona_prompt}",
                "agent_target": agent_name
            },
            metadata={"is_identity_anchor": True}
        )

    def get_relevant_context(self, agent_name: str, query: str, k: int = 5) -> str:
        """
        Perform a semantic search to find the most relevant past context
        """
        if not self.vector_store:
            return "Semantic search disabled."

        # 1. Fetch relevant memories
        results = self.vector_store.search(query, k=k)
        if not results:
            return "No relevant memories found."

        # 2. Format context
        context_lines = ["🔍 RELEVANT MEMORIES:"]
        for res in results:
            agent = res["metadata"].get("agent", "Unknown")
            text = res["text"]
            # Truncate for prompt efficiency
            if len(text) > 300:
                text = text[:300] + "..."
            context_lines.append(f"  - [{agent}]: {text}")

        return "\n".join(context_lines)
    
    def query_agent_mentions(self, agent_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find when an agent was @mentioned
        
        Args:
            agent_name: Agent to search for
            limit: Max results
            
        Returns:
            Events where agent was mentioned
        """
        mention_events = self.event_log.get_events(
            event_type=EventType.AGENT_MENTION,
            limit=50
        )
        
        results = []
        for event in mention_events:
            mentioned = event["payload"].get("mentioned", [])
            if agent_name in mentioned:
                results.append({
                    "from_agent": event["agent"],
                    "message": event["payload"].get("message", ""),
                    "timestamp": event["timestamp"],
                    "event_id": event["id"]
                })
                
                if len(results) >= limit:
                    break
        
        return results
