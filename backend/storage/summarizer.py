"""
Event Summarizer - Compresses old events using AI
Generates summaries to manage context window
"""
from typing import List, Dict, Any, Optional
from storage.event_log import EventLog, EventType
from datetime import datetime


class EventSummarizer:
    """
    Generates summaries of event ranges
    Uses Gemma 3 to create human-readable summaries
    """
    
    def __init__(self, event_log: EventLog, model_manager=None):
        self.event_log = event_log
        self.model_manager = model_manager
    
    async def summarize_events(
        self,
        events: List[Dict[str, Any]],
        summary_type: str = "conversation"
    ) -> str:
        """
        Generate summary of events using AI
        
        Args:
            events: Events to summarize
            summary_type: Type of summary (conversation, decisions, work)
            
        Returns:
            Summary text
        """
        if not events:
            return "No events to summarize."
        
        # Build prompt for summarization
        prompt = self._build_summary_prompt(events, summary_type)
        
        # Generate summary using model if available
        if self.model_manager:
            try:
                summary_parts = []
                async for token in self.model_manager.generate(
                    prompt=prompt,
                    system_prompt="You are a concise summarizer. Create brief, factual summaries.",
                    temperature=0.3,  # Lower temperature for factual summaries
                    max_tokens=500,
                    stream=True
                ):
                    summary_parts.append(token)
                
                return "".join(summary_parts)
            except Exception as e:
                return f"Error generating summ: {str(e)}"
        else:
            # Fallback to simple summary
            return self._simple_summary(events, summary_type)
    
    def _build_summary_prompt(
        self,
        events: List[Dict[str, Any]],
        summary_type: str
    ) -> str:
        """Build prompt for AI summarization"""
        event_texts = []
        
        for event in events:
            agent = event.get("agent", "Unknown")
            event_type = event.get("type", "")
            payload = event.get("payload", {})
            
            if event_type == "USER_MESSAGE":
                msg = payload.get("message", "")
                event_texts.append(f"User: {msg}")
            elif event_type == "AGENT_MESSAGE_SENT":
                msg = payload.get("message", "")
                event_texts.append(f"{agent}: {msg}")
            elif event_type == "TEAM_DECISION":
                decision = payload.get("decision", "")
                event_texts.append(f"Decision ({agent}): {decision}")
        
        events_text = "\n".join(event_texts[:20])  # Limit for token budget
        
        return f"""Summarize the following {summary_type} in 2-3 sentences:

{events_text}

Summary:"""
    
    def _simple_summary(
        self,
        events: List[Dict[str, Any]],
        summary_type: str
    ) -> str:
        """Generate simple non-AI summary"""
        event_count = len(events)
        agents = set(e.get("agent") for e in events)
        
        # Count event types
        type_counts = {}
        for event in events:
            event_type = event.get("type", "unknown")
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
        
        summary_parts = [
            f"{event_count} events",
            f"{len(agents)} agents: {', '.join(list(agents)[:3])}"
        ]
        
        if type_counts:
            top_type = max(type_counts, key=type_counts.get)
            summary_parts.append(f"Mostly: {top_type} ({type_counts[top_type]})")
        
        return ". ".join(summary_parts)
    
    async def create_summary_event(
        self,
        start_event_id: str,
        end_event_id: str,
        summary_text: str
    ) -> str:
        """
        Store a summary as an event
        
        Returns:
            Summary event ID
        """
        return self.event_log.append_event(
            event_type=EventType.SUMMARY_GENERATED,
            agent="System",
            payload={
                "summary": summary_text,
                "scope": f"{start_event_id} to {end_event_id}",
                "generated_at": datetime.now().isoformat()
            },
            parent_events=[start_event_id, end_event_id]
        )
    
    def get_summary_coverage(self) -> Dict[str, Any]:
        """
        Get statistics on what's summarized
        
        Returns:
            Coverage stats
        """
        all_events = self.event_log.get_events(limit=1000)
        summaries = [
            e for e in all_events
            if e.get("type") == EventType.SUMMARY_GENERATED.value
        ]
        
        return {
            "total_events": len(all_events),
            "summaries_count": len(summaries),
            "coverage_percent": (len(summaries) / len(all_events) * 100) if all_events else 0
        }
